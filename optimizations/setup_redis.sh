#!/bin/bash

# Redis Setup Script for LilyOpenCMS Performance Optimizations
# This script helps install and configure Redis for the caching system

echo "🚀 Setting up Redis for LilyOpenCMS Performance Optimizations"
echo "=============================================================="

# Check if Redis is already installed
if command -v redis-server &> /dev/null; then
    echo "✅ Redis is already installed"
    redis-server --version
else
    echo "📦 Installing Redis..."
    
    # Detect OS and install Redis
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y redis-server
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            sudo yum install -y redis
        elif command -v dnf &> /dev/null; then
            # Fedora
            sudo dnf install -y redis
        else
            echo "❌ Unsupported Linux distribution. Please install Redis manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install redis
        else
            echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
    else
        echo "❌ Unsupported operating system. Please install Redis manually."
        exit 1
    fi
fi

# Start Redis service
echo "🔧 Starting Redis service..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start redis
fi

# Test Redis connection
echo "🧪 Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is running and responding"
else
    echo "❌ Redis connection failed. Please check Redis installation."
    exit 1
fi

# Configure Redis for better performance (optional)
echo "⚙️  Configuring Redis for better performance..."
cat > redis-performance.conf << EOF
# Redis Performance Configuration
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
tcp-keepalive 300
timeout 0
tcp-backlog 511
databases 16
EOF

echo "📝 Redis performance configuration saved to redis-performance.conf"
echo "💡 To use this configuration, start Redis with: redis-server redis-performance.conf"

# Create .env template
echo "📄 Creating .env template for Redis configuration..."
cat > .env.redis << EOF
# Redis Configuration for LilyOpenCMS
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Performance Settings
FLASK_ENV=production
DATABASE_URI=sqlite:///exposeur.db
EOF

echo "✅ Redis setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.redis to .env (if not exists)"
echo "2. Install Python dependencies: pip install -r requirements.txt"
echo "3. Run the application: python main.py"
echo "4. Access performance dashboard at: http://localhost:5000/admin/performance"
echo ""
echo "🔧 Redis Management Commands:"
echo "- Start Redis: redis-server"
echo "- Stop Redis: redis-cli shutdown"
echo "- Monitor Redis: redis-cli monitor"
echo "- Check Redis info: redis-cli info"
echo ""
echo "📊 Performance Dashboard:"
echo "- Access at: /admin/performance"
echo "- Monitor system metrics"
echo "- View cache statistics"
echo "- Manage cache invalidation" 