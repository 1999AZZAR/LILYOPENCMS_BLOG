#!/usr/bin/env python3
"""
Redis Connection Test Script
Tests Redis availability and provides fallback options
"""

import os
import sys

def test_redis_connection():
    """Test if Redis is available"""
    try:
        import redis
        print("✅ Redis module is available")
        
        # Test Unix socket first (for DirectAdmin hosting)
        redis_socket = os.getenv('REDIS_SOCKET', '/home/newenerg/.redis/redis.sock')
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        print(f"🔍 Testing Unix socket: {redis_socket}")
        try:
            # Test Unix socket connection
            client = redis.Redis(
                unix_socket_path=redis_socket,
                password=os.getenv('REDIS_PASSWORD', None),
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Test ping
            response = client.ping()
            client.close()
            
            if response:
                print("✅ Redis connection successful via Unix socket")
                return True
            else:
                print("❌ Redis ping failed via Unix socket")
        except Exception as socket_error:
            print(f"❌ Unix socket connection failed: {socket_error}")
        
        # Fallback to TCP connection
        print(f"🔍 Testing TCP connection: {redis_host}:{redis_port}")
        try:
            client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=os.getenv('REDIS_PASSWORD', None),
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Test ping
            response = client.ping()
            client.close()
            
            if response:
                print("✅ Redis connection successful via TCP")
                return True
            else:
                print("❌ Redis ping failed via TCP")
                return False
        except Exception as tcp_error:
            print(f"❌ TCP connection failed: {tcp_error}")
            return False
            
    except ImportError:
        print("❌ Redis module not installed")
        return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def check_environment():
    """Check Redis environment variables"""
    print("\n🔍 Checking Redis environment variables:")
    
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = os.getenv('REDIS_PORT', 6379)
    redis_password = os.getenv('REDIS_PASSWORD', None)
    redis_url = os.getenv('REDIS_URL', None)
    redis_socket = os.getenv('REDIS_SOCKET', '/home/newenerg/.redis/redis.sock')
    
    print(f"REDIS_HOST: {redis_host}")
    print(f"REDIS_PORT: {redis_port}")
    print(f"REDIS_PASSWORD: {'***' if redis_password else 'None'}")
    print(f"REDIS_URL: {redis_url}")
    print(f"REDIS_SOCKET: {redis_socket}")
    
    # Check if socket file exists
    if os.path.exists(redis_socket):
        print(f"✅ Redis socket file exists: {redis_socket}")
    else:
        print(f"⚠️  Redis socket file not found: {redis_socket}")

def provide_solutions():
    """Provide solutions for Redis issues"""
    print("\n💡 Solutions:")
    print("1. Install Redis on your server:")
    print("   - Ubuntu/Debian: sudo apt-get install redis-server")
    print("   - CentOS/RHEL: sudo yum install redis")
    print("   - Or use a managed Redis service")
    
    print("\n2. Configure Redis environment variables:")
    print("   export REDIS_HOST=your_redis_host")
    print("   export REDIS_PORT=6379")
    print("   export REDIS_PASSWORD=your_password")
    
    print("\n3. The application will automatically fall back to simple caching")
    print("   when Redis is not available (no action needed)")
    
    print("\n4. For DirectAdmin hosting:")
    print("   - Contact your hosting provider to enable Redis")
    print("   - Or use a managed Redis service (Redis Cloud, AWS ElastiCache, etc.)")

if __name__ == "__main__":
    print("🔧 Redis Connection Test")
    print("=" * 40)
    
    check_environment()
    
    print("\n🧪 Testing Redis connection...")
    redis_available = test_redis_connection()
    
    if redis_available:
        print("\n✅ Redis is working correctly!")
        print("Your application should work with full caching capabilities.")
    else:
        print("\n⚠️  Redis is not available")
        print("The application will use simple in-memory caching as fallback.")
        provide_solutions() 