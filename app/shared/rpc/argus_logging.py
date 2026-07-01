"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from services.rpc.argus_client import ArgusLogHandler

def setup_unified_logging(service_name="monolith", level=logging.INFO):
    """
    Setup unified logging for LilyOpenCMS components.
    Routes logs to Console, File, and Argus (gRPC).
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        try:
            os.makedirs("logs", exist_ok=True)
        except OSError:
            pass

    log_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s - %(message)s [in %(pathname)s:%(lineno)d]"
    )

    # Base handlers
    handlers = []

    # 1. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    handlers.append(console_handler)

    # 2. File Handler (Rotating)
    log_file = os.path.join("logs", f"{service_name}.log")
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(log_formatter)
        handlers.append(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging for {service_name}: {e}", file=sys.stderr)

    # 3. Argus gRPC Handler
    try:
        argus_handler = ArgusLogHandler(service_name=service_name)
        argus_handler.setFormatter(log_formatter)
        argus_handler.setLevel(level)
        handlers.append(argus_handler)
    except Exception as e:
        print(f"Failed to setup Argus logging for {service_name}: {e}", file=sys.stderr)

    # Configure root logger
    root_logger = logging.getLogger()
    
    # Identify existing handler types to avoid duplicates
    existing_types = {type(h) for h in root_logger.handlers}
    
    # Add new handlers only if they don't already exist or if we want to augment
    for h in handlers:
        # Check if we already have a handler of this type to avoid double logging
        # Especially important for StreamHandler (Console)
        if type(h) not in existing_types:
            root_logger.addHandler(h)
    
    root_logger.setLevel(level)

    # Specific logger overrides
    # Silence overly verbose loggers
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('grpc').setLevel(logging.WARNING)
    logging.getLogger('elasticsearch').setLevel(logging.WARNING)
    
    # Ensure Celery loggers also use these handlers if we are in a celery worker
    # This will be handled specifically via signals in celery_app
    
    logging.info(f"✅ Unified logging initialized for {service_name}")

def setup_celery_logging(service_name="celery-worker", **kwargs):
    """Hook for Celery logger setup signal."""
    setup_unified_logging(service_name=service_name)
    return logging.getLogger()
