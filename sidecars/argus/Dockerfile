FROM golang:1.24-alpine AS builder

WORKDIR /app

# Copy the rest of the source code including vendor
COPY sidecars/ ./

# Build the application
RUN go build -mod=vendor -o argus-service ./argus/main.go

# Use a minimal runtime image
FROM alpine:latest

WORKDIR /root/

# Copy the binary from the builder
COPY --from=builder /app/argus-service .

# Expose the gRPC port
EXPOSE 50051

# Command to run the service
CMD ["./argus-service"]
