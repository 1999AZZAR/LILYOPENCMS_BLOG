"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Circuit Breaker Pattern Implementation
Provides fault tolerance for external API calls by preventing cascading failures
"""

import os
import time
import logging
import threading
from enum import Enum
from typing import Callable, Any, Dict, Optional
from datetime import datetime, timezone, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for external service calls."""

    def __init__(self, service_name: str, failure_threshold: int = 5,
                 recovery_timeout: int = 60, expected_exception: Exception = Exception,
                 success_threshold: int = 3, timeout: float = 10.0):
        """
        Initialize circuit breaker.

        Args:
            service_name: Name of the service being protected
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying half-open state
            expected_exception: Exception type to count as failure
            success_threshold: Number of successes needed to close circuit from half-open
            timeout: Timeout for individual calls
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        self.timeout = timeout

        # State management
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._call_count = 0
        self._error_count = 0

        # Thread safety
        self._lock = threading.RLock()

        # Metrics
        self._metrics = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rejected_calls': 0,
            'state_changes': [],
            'last_call_time': None,
            'avg_response_time': 0.0
        }

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        with self._lock:
            self._call_count += 1
            self._metrics['total_calls'] += 1

            # Check if circuit should be opened
            if self._state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._set_state(CircuitBreakerState.HALF_OPEN)
                else:
                    self._metrics['rejected_calls'] += 1
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker is OPEN for {self.service_name}"
                    )

            # Execute the call
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                self._on_success(execution_time)
                self._metrics['successful_calls'] += 1
                self._metrics['last_call_time'] = datetime.now(timezone.utc)
                self._update_avg_response_time(execution_time)

                return result

            except self.expected_exception as e:
                execution_time = time.time() - start_time
                self._on_failure(e, execution_time)
                self._metrics['failed_calls'] += 1
                self._metrics['last_call_time'] = datetime.now(timezone.utc)
                self._update_avg_response_time(execution_time)
                raise

            except Exception as e:
                # For unexpected exceptions, still count as failure but re-raise
                execution_time = time.time() - start_time
                self._on_failure(e, execution_time)
                self._metrics['failed_calls'] += 1
                self._metrics['last_call_time'] = datetime.now(timezone.utc)
                self._update_avg_response_time(execution_time)
                raise

    def _on_success(self, execution_time: float):
        """Handle successful call."""
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._set_state(CircuitBreakerState.CLOSED)
                self._reset_counts()
        elif self._state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    def _on_failure(self, exception: Exception, execution_time: float):
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = datetime.now(timezone.utc)
        self._error_count += 1

        if self._state == CircuitBreakerState.HALF_OPEN:
            # Failed during recovery test, go back to open
            self._set_state(CircuitBreakerState.OPEN)
            self._success_count = 0
        elif (self._state == CircuitBreakerState.CLOSED and
              self._failure_count >= self.failure_threshold):
            # Too many failures, open circuit
            self._set_state(CircuitBreakerState.OPEN)

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit."""
        if self._last_failure_time is None:
            return True

        elapsed = (datetime.now(timezone.utc) - self._last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _set_state(self, new_state: CircuitBreakerState):
        """Set new circuit breaker state."""
        old_state = self._state
        self._state = new_state

        # Record state change
        state_change = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'from_state': old_state.value,
            'to_state': new_state.value,
            'service': self.service_name
        }
        self._metrics['state_changes'].append(state_change)

        logger.info(f"🔄 Circuit breaker {self.service_name}: {old_state.value} -> {new_state.value}")

    def _reset_counts(self):
        """Reset failure and success counts."""
        self._failure_count = 0
        self._success_count = 0
        self._error_count = 0

    def _update_avg_response_time(self, execution_time: float):
        """Update rolling average response time."""
        current_avg = self._metrics['avg_response_time']
        total_calls = self._metrics['total_calls']

        if total_calls == 1:
            self._metrics['avg_response_time'] = execution_time
        else:
            # Exponential moving average
            alpha = 0.1
            self._metrics['avg_response_time'] = (alpha * execution_time) + ((1 - alpha) * current_avg)

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    @property
    def success_count(self) -> int:
        """Get current success count."""
        return self._success_count

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker status."""
        return {
            'service_name': self.service_name,
            'state': self._state.value,
            'failure_count': self._failure_count,
            'success_count': self._success_count,
            'error_count': self._error_count,
            'last_failure_time': self._last_failure_time.isoformat() if self._last_failure_time else None,
            'can_attempt_reset': self._should_attempt_reset(),
            'metrics': self._metrics.copy(),
            'configuration': {
                'failure_threshold': self.failure_threshold,
                'recovery_timeout': self.recovery_timeout,
                'success_threshold': self.success_threshold,
                'timeout': self.timeout,
                'expected_exception': self.expected_exception.__name__
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def reset(self):
        """Manually reset the circuit breaker."""
        with self._lock:
            self._set_state(CircuitBreakerState.CLOSED)
            self._reset_counts()
            logger.info(f"🔄 Circuit breaker {self.service_name} manually reset")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
        self._breakers = {}
        self._lock = threading.RLock()

    def get_or_create(self, service_name: str, **kwargs) -> CircuitBreaker:
        """Get existing circuit breaker or create new one."""
        with self._lock:
            if service_name not in self._breakers:
                self._breakers[service_name] = CircuitBreaker(service_name, **kwargs)
            return self._breakers[service_name]

    def get_breaker(self, service_name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by service name."""
        return self._breakers.get(service_name)

    def get_all_breakers(self) -> Dict[str, CircuitBreaker]:
        """Get all registered circuit breakers."""
        return self._breakers.copy()

    def get_status_report(self) -> Dict[str, Any]:
        """Get status report for all circuit breakers."""
        report = {
            'total_breakers': len(self._breakers),
            'breakers': {},
            'summary': {
                'open_breakers': 0,
                'half_open_breakers': 0,
                'closed_breakers': 0,
                'total_calls': 0,
                'total_failures': 0
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        total_calls = 0
        total_failures = 0

        for name, breaker in self._breakers.items():
            status = breaker.get_status()
            report['breakers'][name] = status

            # Update summary counts
            if breaker.state == CircuitBreakerState.OPEN:
                report['summary']['open_breakers'] += 1
            elif breaker.state == CircuitBreakerState.HALF_OPEN:
                report['summary']['half_open_breakers'] += 1
            else:
                report['summary']['closed_breakers'] += 1

            total_calls += status['metrics']['total_calls']
            total_failures += status['metrics']['failed_calls']

        report['summary']['total_calls'] = total_calls
        report['summary']['total_failures'] = total_failures

        return report

    def reset_all(self):
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()
            logger.info(f"🔄 All {len(self._breakers)} circuit breakers reset")


# Global circuit breaker registry
circuit_breaker_registry = CircuitBreakerRegistry()


def circuit_breaker(service_name: str, **kwargs):
    """
    Decorator to apply circuit breaker pattern to functions.

    Args:
        service_name: Name of the service
        **kwargs: Circuit breaker configuration options
    """
    def decorator(func):
        breaker = circuit_breaker_registry.get_or_create(service_name, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs_inner):
            return breaker.call(func, *args, **kwargs_inner)

        # Attach breaker to function for inspection
        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    return circuit_breaker_registry


# Pre-configured circuit breakers for common services
def get_email_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for email services."""
    return circuit_breaker_registry.get_or_create(
        'email_service',
        failure_threshold=int(os.getenv('EMAIL_CIRCUIT_FAILURE_THRESHOLD', '3')),
        recovery_timeout=int(os.getenv('EMAIL_CIRCUIT_RECOVERY_TIMEOUT', '300')),  # 5 minutes
        success_threshold=int(os.getenv('EMAIL_CIRCUIT_SUCCESS_THRESHOLD', '2')),
        timeout=float(os.getenv('EMAIL_CIRCUIT_TIMEOUT', '30.0'))
    )


def get_payment_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for payment services."""
    return circuit_breaker_registry.get_or_create(
        'payment_service',
        failure_threshold=int(os.getenv('PAYMENT_CIRCUIT_FAILURE_THRESHOLD', '2')),
        recovery_timeout=int(os.getenv('PAYMENT_CIRCUIT_RECOVERY_TIMEOUT', '600')),  # 10 minutes
        success_threshold=int(os.getenv('PAYMENT_CIRCUIT_SUCCESS_THRESHOLD', '3')),
        timeout=float(os.getenv('PAYMENT_CIRCUIT_TIMEOUT', '60.0'))
    )


def get_external_api_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get circuit breaker for generic external API services."""
    return circuit_breaker_registry.get_or_create(
        f'external_api_{service_name}',
        failure_threshold=int(os.getenv('EXTERNAL_API_CIRCUIT_FAILURE_THRESHOLD', '5')),
        recovery_timeout=int(os.getenv('EXTERNAL_API_CIRCUIT_RECOVERY_TIMEOUT', '120')),
        success_threshold=int(os.getenv('EXTERNAL_API_CIRCUIT_SUCCESS_THRESHOLD', '2')),
        timeout=float(os.getenv('EXTERNAL_API_CIRCUIT_TIMEOUT', '15.0'))
    )
