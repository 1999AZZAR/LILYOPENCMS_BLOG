"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import os
import grpc
import logging
import io
from services.rpc import hermes_pb2
from services.rpc import hermes_pb2_grpc
import socket
from PIL import Image as PILImage
from celery_app.circuit_breaker import get_circuit_breaker_registry, CircuitBreakerOpenException

def _get_hermes_breaker():
    return get_circuit_breaker_registry().get_or_create(
        'hermes_process', failure_threshold=3, recovery_timeout=60
    )

class HermesClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HermesClient, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        host = os.environ.get("HERMES_HOST", "hermes-sidecar")
        port = os.environ.get("HERMES_PORT", "50052")

        try:
            target_ip = socket.gethostbyname(host)
            target = f"{target_ip}:{port}"
        except Exception:
            target = f"{host}:{port}"

        self.channel = grpc.insecure_channel(target)
        self.stub = hermes_pb2_grpc.HermesMediaStub(self.channel)
        self.logger = logging.getLogger(__name__)

    def _call_process(self, image_data, target_format, target_width, target_height, quality):
        req = hermes_pb2.ImageProcessRequest(
            image_data=image_data,
            target_format=target_format,
            target_width=target_width,
            target_height=target_height,
            quality=quality
        )
        return self.stub.ProcessImage(req, timeout=10.0)

    def process_image(self, image_data, target_format="webp", target_width=0, target_height=0, quality=85):
        """Send image to Hermes for processing with Circuit Breaker and PIL fallback."""
        try:
            res = _get_hermes_breaker().call(
                self._call_process, image_data, target_format, target_width, target_height, quality
            )
            if res and res.success:
                return res
            elif res:
                self.logger.warning(f"Hermes returned success=False: {res.error_message}")
        except (CircuitBreakerOpenException, Exception) as e:
            if not isinstance(e, CircuitBreakerOpenException):
                self.logger.error(f"Hermes gRPC call failed: {e}")

        return self._pil_fallback(image_data, target_format, target_width, target_height, quality)

    def _pil_fallback(self, image_data, target_format, target_width, target_height, quality):
        """Fallback to local PIL processing if Hermes is unavailable."""
        self.logger.info("Using local PIL fallback for image processing")
        try:
            img = PILImage.open(io.BytesIO(image_data))

            fmt = target_format.upper()
            if fmt == "JPG":
                fmt = "JPEG"

            # Only strip alpha for formats that don't support transparency (JPEG)
            if fmt in ("JPEG",) and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            if target_width > 0 or target_height > 0:
                if target_width > 0 and target_height > 0:
                    img = img.resize((target_width, target_height), PILImage.Resampling.LANCZOS)
                elif target_width > 0:
                    aspect_ratio = target_width / img.width
                    img = img.resize((target_width, int(img.height * aspect_ratio)), PILImage.Resampling.LANCZOS)
                else:
                    aspect_ratio = target_height / img.height
                    img = img.resize((int(img.width * aspect_ratio), target_height), PILImage.Resampling.LANCZOS)

            output = io.BytesIO()
            img.save(output, format=fmt, quality=quality)

            class MockResponse:
                def __init__(self, data):
                    self.success = True
                    self.processed_image = data
                    self.error_message = ""

            return MockResponse(output.getvalue())

        except Exception as fallback_err:
            self.logger.critical(f"PIL Fallback also failed: {fallback_err}")
            return None


# Singleton instance
hermes_client = HermesClient()
