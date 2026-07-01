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
from google.protobuf.timestamp_pb2 import Timestamp
import traceback
import sys

from services.rpc import argus_pb2
from services.rpc import argus_pb2_grpc
from celery_app.circuit_breaker import get_circuit_breaker_registry, CircuitBreakerOpenException

# Module-level circuit breakers — created once, reused across all calls
def _get_breaker(name, failure_threshold=5, recovery_timeout=60):
    return get_circuit_breaker_registry().get_or_create(
        name, failure_threshold=failure_threshold, recovery_timeout=recovery_timeout
    )

class ArgusClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArgusClient, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        host = os.environ.get("ARGUS_HOST", "argus-sidecar")
        port = os.environ.get("ARGUS_PORT", "50051")

        import socket
        try:
            target_ip = socket.gethostbyname(host)
            target = f"{target_ip}:{port}"
        except Exception:
            target = f"{host}:{port}"

        self.channel = grpc.insecure_channel(target)
        self.stub = argus_pb2_grpc.ArgusStub(self.channel)
        self.logger = logging.getLogger(__name__)

    def _get_timestamp(self):
        ts = Timestamp()
        ts.GetCurrentTime()
        return ts

    def _call_log(self, level, message, service, trace_id, metadata):
        req = argus_pb2.LogRequest(
            level=level, message=message, service=service,
            trace_id=trace_id, metadata=metadata or {},
            timestamp=self._get_timestamp()
        )
        return self.stub.Log(req, timeout=1.0)

    def _call_track(self, event_type, user_id, session_id, properties):
        req = argus_pb2.AnalyticsRequest(
            event_type=event_type, user_id=user_id,
            session_id=session_id, properties=properties or {},
            timestamp=self._get_timestamp()
        )
        return self.stub.TrackEvent(req, timeout=1.0)

    def _call_metrics(self, name, value, tags):
        req = argus_pb2.MetricsRequest(
            name=name, value=float(value),
            tags=tags or {}, timestamp=self._get_timestamp()
        )
        return self.stub.SubmitMetrics(req, timeout=1.0)

    def log(self, level, message, service="monolith", trace_id="", metadata=None):
        try:
            breaker = _get_breaker('argus_log')
            return breaker.call(self._call_log, level, message, service, trace_id, metadata)
        except (CircuitBreakerOpenException, Exception) as e:
            fallback_msg = f"[FALLBACK-LOG] [{level}] [{service}] {message}"
            if metadata:
                fallback_msg += f" | Metadata: {metadata}"
            print(fallback_msg, file=sys.stderr)
            if not isinstance(e, CircuitBreakerOpenException):
                print(f"ArgusClient log error: {e}", file=sys.stderr)

    def track_event(self, event_type, user_id="", session_id="", properties=None):
        try:
            breaker = _get_breaker('argus_analytics')
            return breaker.call(self._call_track, event_type, user_id, session_id, properties)
        except (CircuitBreakerOpenException, Exception) as e:
            print(f"[FALLBACK-ANALYTICS] {event_type} | User: {user_id} | Props: {properties}", file=sys.stderr)
            if not isinstance(e, CircuitBreakerOpenException):
                self.logger.error(f"Failed to track event with Argus: {e}")

    def submit_metrics(self, name, value, tags=None):
        try:
            breaker = _get_breaker('argus_metrics')
            return breaker.call(self._call_metrics, name, value, tags)
        except (CircuitBreakerOpenException, Exception) as e:
            print(f"[FALLBACK-METRICS] {name}: {value} | Tags: {tags}", file=sys.stderr)
            if not isinstance(e, CircuitBreakerOpenException):
                self.logger.error(f"Failed to submit metrics to Argus: {e}")


class ArgusLogHandler(logging.Handler):
    """Custom logging handler that forwards to Argus via gRPC."""

    def __init__(self, service_name="monolith"):
        super().__init__()
        self.client = ArgusClient()
        self.service_name = service_name

    def emit(self, record):
        try:
            log_entry = self.format(record)
            metadata = {
                "logger_name": record.name,
                "file": record.filename,
                "line": str(record.lineno)
            }
            if record.exc_info:
                metadata["exc_info"] = traceback.format_exc()
            self.client.log(
                level=record.levelname,
                message=log_entry,
                service=self.service_name,
                metadata=metadata
            )
        except Exception as e:
            print(f"ArgusLogHandler emit error: {e}", file=sys.stderr)
            self.handleError(record)


# Singleton instance
argus_client = ArgusClient()
