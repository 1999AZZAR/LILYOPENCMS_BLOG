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
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/patrickmn/go-cache"
	"github.com/redis/go-redis/v9"
	"github.com/elastic/go-elasticsearch/v8"
	"github.com/jackc/pgx/v5/pgxpool"
)

type App struct {
	DB     *pgxpool.Pool
	Redis  *redis.Client
	Cache  *cache.Cache
	ES     *elasticsearch.Client
	Router *gin.Engine
}

func main() {
	app := &App{}
	
	// Initialize L1 Cache (In-Memory)
	app.Cache = cache.New(5*time.Minute, 10*time.Minute)

	// Initialize L2 Cache (Redis)
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		redisURL = "redis://redis-redesign:6379/0"
	}
	opts, err := redis.ParseURL(redisURL)
	if err == nil {
		app.Redis = redis.NewClient(opts)
		if err := app.Redis.Ping(context.Background()).Err(); err != nil {
			log.Printf("Warning: Redis connection failed: %v", err)
		} else {
			log.Println("Connected to Redis successfully")
			// Start Redis Pub/Sub listener for cache invalidation
			go app.ListenForInvalidations()
		}
	} else {
		log.Printf("Warning: Invalid Redis URL: %v", err)
	}

	// Initialize Postgres
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://lilyuser:lilypass@db-redesign:5432/lilyopencms"
	}
	poolConfig, err := pgxpool.ParseConfig(dbURL)
	if err == nil {
		app.DB, err = pgxpool.NewWithConfig(context.Background(), poolConfig)
		if err != nil {
			log.Printf("Warning: Postgres connection failed: %v", err)
		} else {
			log.Println("Connected to Postgres successfully")
		}
	}

	// Initialize Elasticsearch
	esURL := os.Getenv("ELASTICSEARCH_URL")
	if esURL == "" {
		esURL = "http://elasticsearch-redesign:9200"
	}
	cfg := elasticsearch.Config{
		Addresses: []string{esURL},
	}
	app.ES, err = elasticsearch.NewClient(cfg)
	if err != nil {
		log.Printf("Warning: Elasticsearch connection failed: %v", err)
	} else {
		res, err := app.ES.Info()
		if err != nil || res.IsError() {
			log.Printf("Warning: Elasticsearch info failed: %v", err)
		} else {
			log.Println("Connected to Elasticsearch successfully")
		}
	}

	app.Router = gin.Default()

	// Setup routes
	api := app.Router.Group("/api/public")
	{
		api.GET("/ping", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{
				"message": "pong from cerebro",
				"status":  "healthy",
			})
		})

		api.GET("/search", app.SearchHandler)
		api.GET("/news/list", app.NewsListHandler)
	}

	port := os.Getenv("PORT")

	// Liveness health check — checks if the Go process is alive to avoid cascading restarts
	app.Router.GET("/healthz", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "ok",
			"service": "cerebro",
		})
	})

	// Readiness health check — checks connectivity to backing services
	healthHandler := func(c *gin.Context) {
		status := "ok"
		code := http.StatusOK
		checks := gin.H{}

		// Redis check
		if app.Redis != nil {
			if err := app.Redis.Ping(c.Request.Context()).Err(); err != nil {
				checks["redis"] = "unreachable"
				status = "degraded"
				code = http.StatusServiceUnavailable
			} else {
				checks["redis"] = "ok"
			}
		} else {
			checks["redis"] = "disabled"
		}

		// Postgres check
		if app.DB != nil {
			if err := app.DB.Ping(c.Request.Context()); err != nil {
				checks["postgres"] = "unreachable"
				status = "degraded"
				code = http.StatusServiceUnavailable
			} else {
				checks["postgres"] = "ok"
			}
		} else {
			checks["postgres"] = "disabled"
		}

		// Elasticsearch check
		if app.ES != nil {
			res, err := app.ES.Ping(app.ES.Ping.WithContext(c.Request.Context()))
			if err != nil || (res != nil && res.IsError()) {
				checks["elasticsearch"] = "unreachable"
				status = "degraded"
				code = http.StatusServiceUnavailable
			} else {
				checks["elasticsearch"] = "ok"
			}
			if res != nil {
				res.Body.Close()
			}
		} else {
			checks["elasticsearch"] = "disabled"
		}

		c.JSON(code, gin.H{
			"status":  status,
			"checks":  checks,
			"service": "cerebro",
		})
	}

	app.Router.GET("/health", healthHandler)
	app.Router.GET("/readyz", healthHandler)

	if port == "" {
		port = "8080"
	}

	log.Printf("Cerebro (Go Gateway) listening on :%s", port)
	app.Router.Run(fmt.Sprintf("0.0.0.0:%s", port))
}

func (app *App) ListenForInvalidations() {
	if app.Redis == nil {
		return
	}

	for {
		ctx := context.Background()
		pubsub := app.Redis.Subscribe(ctx, "cache_invalidation")
		
		ch := pubsub.Channel()
		log.Println("Started listening for cache invalidations on Redis channel 'cache_invalidation'")

		for msg := range ch {
			log.Printf("Received cache invalidation event: %s", msg.Payload)
			
			var event struct {
				Event string      `json:"event"`
				Table string      `json:"table"`
				ID    interface{} `json:"id"`
			}
			
			if err := json.Unmarshal([]byte(msg.Payload), &event); err != nil {
				log.Printf("Error unmarshaling invalidation event: %v", err)
				app.Cache.Flush()
				continue
			}

			// Flush whole cache for tables that affect lists (news, album) to prevent stale list views.
			if event.Table == "news" || event.Table == "album" {
				log.Printf("Table %s updated, flushing cache to prevent stale lists", event.Table)
				app.Cache.Flush()
			} else {
				// Fallback to full flush for unknown tables or generic updates
				app.Cache.Flush()
			}
		}

		log.Println("Redis Pub/Sub channel closed, reconnecting in 5 seconds...")
		pubsub.Close()
		time.Sleep(5 * time.Second)
	}
}

func (app *App) SearchHandler(c *gin.Context) {
	query := c.Query("q")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Query parameter 'q' is required"})
		return
	}

	cacheKey := fmt.Sprintf("search:%s", query)

	// 1. Try L1 Cache (Go Memory)
	if cachedData, found := app.Cache.Get(cacheKey); found {
		c.Data(http.StatusOK, "application/json", cachedData.([]byte))
		return
	}

	// 2. Try L2 Cache (Redis)
	if app.Redis != nil {
		val, err := app.Redis.Get(c.Request.Context(), cacheKey).Bytes()
		if err == nil {
			app.Cache.Set(cacheKey, val, cache.DefaultExpiration)
			c.Data(http.StatusOK, "application/json", val)
			return
		}
	}

	// 3. Query Elasticsearch
	if app.ES == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Elasticsearch not configured"})
		return
	}

	// Build ES query
	esQuery := map[string]interface{}{
		"query": map[string]interface{}{
			"multi_match": map[string]interface{}{
				"query": query,
				"fields": []string{"title", "content", "description"},
				"fuzziness": "AUTO",
			},
		},
	}
	
	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(esQuery); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to encode query"})
		return
	}

	res, err := app.ES.Search(
		app.ES.Search.WithContext(c.Request.Context()),
		app.ES.Search.WithIndex("lilycms_news", "lilycms_albums", "lilycms_users", "lilycms_comments"),
		app.ES.Search.WithBody(&buf),
		app.ES.Search.WithTrackTotalHits(true),
	)

	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Search failed"})
		return
	}
	defer res.Body.Close()

	if res.IsError() {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Search returned error: %s", res.Status())})
		return
	}

	var raw map[string]interface{}
	if err := json.NewDecoder(res.Body).Decode(&raw); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse search response"})
		return
	}

	// Structure response
	result := map[string]interface{}{
		"source": "database/elasticsearch",
		"data":   raw["hits"],
	}
	
	responseBytes, _ := json.Marshal(result)

	// Save to caches
	app.Cache.Set(cacheKey, responseBytes, cache.DefaultExpiration)
	if app.Redis != nil {
		app.Redis.Set(c.Request.Context(), cacheKey, responseBytes, 10*time.Minute)
	}

	c.Data(http.StatusOK, "application/json", responseBytes)
}

func (app *App) NewsListHandler(c *gin.Context) {
	limitStr := c.DefaultQuery("limit", "20")
	limit, _ := strconv.Atoi(limitStr)
	if limit > 100 {
		limit = 100
	}

	cacheKey := fmt.Sprintf("news_list:%d", limit)

	// 1. Try L1 Cache
	if cachedData, found := app.Cache.Get(cacheKey); found {
		c.Data(http.StatusOK, "application/json", cachedData.([]byte))
		return
	}

	// 2. Try L2 Cache
	if app.Redis != nil {
		val, err := app.Redis.Get(c.Request.Context(), cacheKey).Bytes()
		if err == nil {
			app.Cache.Set(cacheKey, val, cache.DefaultExpiration)
			c.Data(http.StatusOK, "application/json", val)
			return
		}
	}

	// 3. Query PostgreSQL
	if app.DB == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database not configured"})
		return
	}

	query := `
		SELECT n.id, n.title, n.seo_slug, n.content_status, n.date, i.filename, i.filepath
		FROM news n
		LEFT JOIN image i ON n.image_id = i.id
		WHERE n.is_visible = true 
		ORDER BY n.date DESC 
		LIMIT $1
	`
	rows, err := app.DB.Query(c.Request.Context(), query, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Database query failed: %v", err)})
		return
	}
	defer rows.Close()

	var newsList []map[string]interface{}
	for rows.Next() {
		var id int
		var title, slug, status string
		var date time.Time
		var filename, filepath *string
		if err := rows.Scan(&id, &title, &slug, &status, &date, &filename, &filepath); err != nil {
			continue
		}
		
		var image map[string]interface{}
		if filename != nil {
			image = map[string]interface{}{
				"filename": *filename,
				"filepath": *filepath,
			}
		}

		newsList = append(newsList, map[string]interface{}{
			"id":             id,
			"title":          title,
			"slug":           slug,
			"content_status": status,
			"date":           date,
			"image":          image,
		})
	}

	result := map[string]interface{}{
		"source": "database/postgresql",
		"data":   newsList,
	}

	responseBytes, _ := json.Marshal(result)

	// Save to caches
	app.Cache.Set(cacheKey, responseBytes, cache.DefaultExpiration)
	if app.Redis != nil {
		app.Redis.Set(c.Request.Context(), cacheKey, responseBytes, 10*time.Minute)
	}

	c.Data(http.StatusOK, "application/json", responseBytes)
}
