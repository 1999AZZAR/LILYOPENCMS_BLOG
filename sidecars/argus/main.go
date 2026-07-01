/*
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
*/

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"time"

	pb "github.com/1999AZZAR/lilyopencms/sidecars/argus/pb"

	"github.com/elastic/go-elasticsearch/v8"
	"github.com/elastic/go-elasticsearch/v8/esapi"
	"google.golang.org/grpc"
)

type indexJob struct {
	indexName string
	doc       map[string]interface{}
}

type server struct {
	pb.UnimplementedArgusServer
	es         *elasticsearch.Client
	indexQueue chan indexJob
}

func (s *server) startWorkers(count int) {
	for i := 0; i < count; i++ {
		go func(workerID int) {
			log.Printf("[INFO] Worker %d started", workerID)
			for job := range s.indexQueue {
				// Use context with timeout for indexing to prevent blocking workers indefinitely
				ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
				if err := s.indexDocument(ctx, job.indexName, job.doc); err != nil {
					log.Printf("[ERROR] Worker %d: Failed to index to %s: %v", workerID, job.indexName, err)
				}
				cancel()
			}
		}(i)
	}
}

func (s *server) enqueueIndexJob(indexName string, doc map[string]interface{}) {
	select {
	case s.indexQueue <- indexJob{indexName: indexName, doc: doc}:
	default:
		log.Printf("[WARN] Index queue full, dropping %s document", indexName)
	}
}

func (s *server) indexDocument(ctx context.Context, indexName string, doc map[string]interface{}) error {
	if s.es == nil {
		log.Printf("[WARN] Elasticsearch client not initialized. Skipping index to %s", indexName)
		return nil
	}

	data, err := json.Marshal(doc)
	if err != nil {
		return fmt.Errorf("error marshaling document: %w", err)
	}

	req := esapi.IndexRequest{
		Index:   indexName,
		Body:    bytes.NewReader(data),
		Refresh: "true",
	}

	res, err := req.Do(ctx, s.es)
	if err != nil {
		return fmt.Errorf("error indexing document: %w", err)
	}
	defer res.Body.Close()

	if res.IsError() {
		return fmt.Errorf("error response from ES: %s", res.String())
	}
	return nil
}

func (s *server) Log(ctx context.Context, in *pb.LogRequest) (*pb.LogResponse, error) {
	log.Printf("[%s] [%s] %s", in.Level, in.Service, in.Message)
	
	doc := map[string]interface{}{
		"level":     in.Level,
		"message":   in.Message,
		"service":   in.Service,
		"trace_id":  in.TraceId,
		"metadata":  in.Metadata,
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	}
	
	if in.Timestamp != nil {
		doc["timestamp"] = in.Timestamp.AsTime().UTC().Format(time.RFC3339)
	}

	s.enqueueIndexJob("argus-logs", doc)

	return &pb.LogResponse{Success: true}, nil
}

func (s *server) TrackEvent(ctx context.Context, in *pb.AnalyticsRequest) (*pb.AnalyticsResponse, error) {
	log.Printf("[ANALYTICS] Event: %s, User: %s", in.EventType, in.UserId)
	
	doc := map[string]interface{}{
		"event_type": in.EventType,
		"user_id":    in.UserId,
		"session_id": in.SessionId,
		"properties": in.Properties,
		"timestamp":  time.Now().UTC().Format(time.RFC3339),
	}
	
	if in.Timestamp != nil {
		doc["timestamp"] = in.Timestamp.AsTime().UTC().Format(time.RFC3339)
	}

	s.enqueueIndexJob("argus-analytics", doc)

	return &pb.AnalyticsResponse{Success: true}, nil
}

func (s *server) SubmitMetrics(ctx context.Context, in *pb.MetricsRequest) (*pb.MetricsResponse, error) {
	log.Printf("[METRICS] %s: %f", in.Name, in.Value)
	
	doc := map[string]interface{}{
		"name":      in.Name,
		"value":     in.Value,
		"tags":      in.Tags,
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	}

	if in.Timestamp != nil {
		doc["timestamp"] = in.Timestamp.AsTime().UTC().Format(time.RFC3339)
	}

	s.enqueueIndexJob("argus-metrics", doc)

	return &pb.MetricsResponse{Success: true}, nil
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "50051"
	}

	esURL := os.Getenv("ELASTICSEARCH_URL")
	if esURL == "" {
		esURL = "http://localhost:9200"
	}

	// Wait briefly for ES to be available if starting concurrently in docker-compose
	log.Printf("Connecting to Elasticsearch at %s...", esURL)
	cfg := elasticsearch.Config{
		Addresses: []string{esURL},
	}
	
	var es *elasticsearch.Client
	var err error
	
	// Retry loop for ES connection
	for i := 0; i < 15; i++ {
		es, err = elasticsearch.NewClient(cfg)
		if err == nil {
			res, err := es.Info()
			if err == nil {
				if !res.IsError() {
					res.Body.Close()
					log.Println("Successfully connected to Elasticsearch")
					break
				}
				log.Printf("Elasticsearch returned error: %s", res.String())
				res.Body.Close()
			}
		}
		log.Printf("Elasticsearch not ready yet, retrying in 5 seconds... (err: %v)", err)
		time.Sleep(5 * time.Second)
	}

	if es == nil {
		log.Println("WARNING: Failed to connect to Elasticsearch after retries. Argus will run without persistence.")
	}

	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%s", port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	
	s := grpc.NewServer()
	srv := &server{
		es:         es,
		indexQueue: make(chan indexJob, 1000), // Buffered queue
	}
	srv.startWorkers(5) // Start 5 indexing workers
	
	pb.RegisterArgusServer(s, srv)
	
	log.Printf("Argus (Go Sidecar) listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
