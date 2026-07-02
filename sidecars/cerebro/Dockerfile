FROM golang:1.24-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY cerebro/ ./cerebro/
RUN CGO_ENABLED=0 GOOS=linux go build -o cerebro-service ./cerebro/main.go

FROM alpine:latest

WORKDIR /root/
COPY --from=builder /app/cerebro-service .

EXPOSE 8080
CMD ["./cerebro-service"]
