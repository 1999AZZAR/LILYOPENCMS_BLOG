"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Configuration Reader Utility
Reads Redis and other configuration settings from text files
"""

import os
import re
from typing import Dict, Any, Optional

class ConfigReader:
    """Reads configuration from text files"""
    
    def __init__(self, config_file: str = "config/redis_config.txt"):
        self.config_file = config_file
        self._config_cache = None
    
    def read_config(self) -> Dict[str, Any]:
        """Read configuration from the text file"""
        if self._config_cache is not None:
            return self._config_cache
        
        config = {}
        
        try:
            if not os.path.exists(self.config_file):
                print(f"⚠️  Config file not found: {self.config_file}")
                return self._get_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convert value types
                        if value.lower() in ('true', 'false'):
                            config[key] = value.lower() == 'true'
                        elif value.isdigit():
                            config[key] = int(value)
                        elif value == '':
                            config[key] = None
                        else:
                            config[key] = value
            
            self._config_cache = config
            return config
            
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file is not found"""
        return {
            'CONNECTION_TYPE': 'socket',
            'REDIS_SOCKET': '/home/username/.redis/redis.sock',
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': 6379,
            'REDIS_PASSWORD': None,
            'SOCKET_CONNECT_TIMEOUT': 1,
            'SOCKET_TIMEOUT': 1,
            'TCP_CONNECT_TIMEOUT': 2,
            'TCP_TIMEOUT': 2,
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'lilycms_'
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis-specific configuration (Env Override added)"""
        config = self.read_config()
        
        # Check Env Vars
        env_host = os.getenv('REDIS_HOST')
        env_port = os.getenv('REDIS_PORT')
        connection_type = 'tcp' if env_host else config.get('CONNECTION_TYPE', 'socket')

        return {
            'connection_type': connection_type,
            'socket_path': config.get('REDIS_SOCKET'),
            'host': env_host or config.get('REDIS_HOST', 'localhost'),
            'port': int(env_port) if env_port else config.get('REDIS_PORT', 6379),
            'password': os.getenv('REDIS_PASSWORD') or config.get('REDIS_PASSWORD'),
            'socket_connect_timeout': config.get('SOCKET_CONNECT_TIMEOUT', 1),
            'socket_timeout': config.get('SOCKET_TIMEOUT', 1),
            'tcp_connect_timeout': config.get('TCP_CONNECT_TIMEOUT', 2),
            'tcp_timeout': config.get('TCP_TIMEOUT', 2),
            'cache_default_timeout': config.get('CACHE_DEFAULT_TIMEOUT', 300),
            'cache_key_prefix': config.get('CACHE_KEY_PREFIX', 'lilycms_')
        }
    
    def validate_config(self) -> bool:
        """Validate the configuration"""
        config = self.read_config()
        
        required_fields = ['CONNECTION_TYPE']
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing required config field: {field}")
                return False
        
        connection_type = config.get('CONNECTION_TYPE', '').lower()
        if connection_type not in ['socket', 'tcp']:
            print(f"❌ Invalid CONNECTION_TYPE: {connection_type}. Must be 'socket' or 'tcp'")
            return False
        
        if connection_type == 'socket':
            if not config.get('REDIS_SOCKET'):
                print("❌ REDIS_SOCKET is required when CONNECTION_TYPE is 'socket'")
                return False
        
        print("✅ Configuration validation passed")
        return True
    
    def print_config(self):
        """Print current configuration for debugging"""
        config = self.read_config()
        print("📋 Current Redis Configuration:")
        print("=" * 40)
        for key, value in config.items():
            print(f"{key}: {value}")
        print("=" * 40)

def get_redis_config() -> Dict[str, Any]:
    """Convenience function to get Redis configuration"""
    reader = ConfigReader()
    return reader.get_redis_config()

def validate_redis_config() -> bool:
    """Convenience function to validate Redis configuration"""
    reader = ConfigReader()
    return reader.validate_config()

if __name__ == "__main__":
    # Test the configuration reader
    reader = ConfigReader()
    reader.print_config()
    print(f"Validation: {validate_redis_config()}")
