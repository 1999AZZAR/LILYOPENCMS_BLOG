FROM golang:1.24 AS builder

# Install vips and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libvips-dev gcc g++

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY hermes/ ./hermes/
COPY proto/ ./proto/
RUN CGO_ENABLED=1 GOOS=linux go build -o hermes-service ./hermes/main.go

FROM debian:bookworm-slim

# Install runtime vips dependency
RUN apt-get update && apt-get install -y --no-install-recommends libvips42 && rm -rf /var/lib/apt/lists/*

WORKDIR /root/
COPY --from=builder /app/hermes-service .

EXPOSE 50052
CMD ["./hermes-service"]
