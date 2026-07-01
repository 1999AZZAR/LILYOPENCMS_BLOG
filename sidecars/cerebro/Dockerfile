FROM golang:1.24-alpine AS builder

WORKDIR /app
COPY sidecars/ ./
RUN CGO_ENABLED=0 GOOS=linux go build -mod=vendor -o cerebro-service ./cerebro/main.go

FROM alpine:latest

WORKDIR /root/
COPY --from=builder /app/cerebro-service .

EXPOSE 8080
CMD ["./cerebro-service"]
