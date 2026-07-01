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
	"context"
	"fmt"
	"log"
	"net"
	"os"

	pb "github.com/1999AZZAR/lilyopencms/sidecars/hermes/pb"
	"github.com/h2non/bimg"
	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedHermesMediaServer
}

func (s *server) ProcessImage(ctx context.Context, req *pb.ImageProcessRequest) (*pb.ImageProcessResponse, error) {
	log.Printf("Received image processing request. Initial size: %d bytes, Target: %dx%d, Format: %s", 
		len(req.ImageData), req.TargetWidth, req.TargetHeight, req.TargetFormat)

	img := bimg.NewImage(req.ImageData)

	// Determine format
	format := bimg.WEBP // Default to WebP
	if req.TargetFormat == "png" {
		format = bimg.PNG
	} else if req.TargetFormat == "jpeg" || req.TargetFormat == "jpg" {
		format = bimg.JPEG
	}

	options := bimg.Options{
		Type:    format,
		Quality: int(req.Quality),
	}
	
	if options.Quality <= 0 {
		options.Quality = 85
	}

	// Handle dimensions and aspect ratio
	if req.TargetWidth > 0 && req.TargetHeight > 0 {
		options.Width = int(req.TargetWidth)
		options.Height = int(req.TargetHeight)
		options.Crop = true   // Force exact dimensions with smart cropping
		options.Enlarge = true // Ensure it fills the requested dimensions
	} else if req.TargetWidth > 0 || req.TargetHeight > 0 {
		options.Width = int(req.TargetWidth)
		options.Height = int(req.TargetHeight)
		options.Enlarge = false // Maintain aspect ratio
	}

	processed, err := img.Process(options)
	if err != nil {
		return &pb.ImageProcessResponse{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to process image: %v", err),
		}, nil
	}

	// Determine Max Size limit (Default to 500KiB if not specified or for covers)
	// We'll use the quality reduction loop for all non-PNG images
	maxSizeKiB := 500
	// Heuristic: if width/height are thumbnail-sized, use 170KiB limit
	if req.TargetWidth > 0 && req.TargetWidth <= 800 {
		maxSizeKiB = 170
	}
	
	maxSizeBytes := maxSizeKiB * 1024
	currentQuality := options.Quality

	// Loop to reduce quality if still too large
	if format != bimg.PNG {
		for len(processed) > maxSizeBytes && currentQuality > 10 {
			currentQuality -= 5
			options.Quality = currentQuality
			processed, err = bimg.NewImage(req.ImageData).Process(options)
			if err != nil {
				log.Printf("Failed to process image during size reduction: %v", err)
				break
			}
		}
	}

	// If still too large, reduce dimensions further (emergency fall-back)
	if len(processed) > maxSizeBytes {
		scale := 0.9
		for len(processed) > maxSizeBytes && scale > 0.1 {
			options.Width = int(float64(options.Width) * scale)
			if options.Height > 0 {
				options.Height = int(float64(options.Height) * scale)
			}
			processed, err = bimg.NewImage(req.ImageData).Process(options)
			if err != nil {
				break
			}
			scale -= 0.1
		}
	}

	log.Printf("Final image size: %d bytes (Target: %dKiB, Quality: %d)", len(processed), maxSizeKiB, currentQuality)

	return &pb.ImageProcessResponse{
		Success:        true,
		ProcessedImage: processed,
	}, nil
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "50052"
	}

	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%s", port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterHermesMediaServer(s, &server{})

	log.Printf("Hermes (Go Sidecar) listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
