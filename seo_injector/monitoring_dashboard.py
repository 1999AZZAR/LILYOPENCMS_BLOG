#!/usr/bin/env python3

"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
SEO Injection Monitoring Dashboard
Real-time progress tracking and analytics for SEO injection processes.
"""

import sys
import os
import json
import time
import threading
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@dataclass
class ProgressUpdate:
    """Progress update data."""
    timestamp: datetime
    processed: int
    total: int
    current_item: str
    status: str  # processing, completed, error
    message: str = ""

@dataclass
class PerformanceMetrics:
    """Performance metrics for SEO injection."""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_items: int = 0
    processed_items: int = 0
    updated_items: int = 0
    skipped_items: int = 0
    error_items: int = 0
    locked_items: int = 0
    items_per_second: float = 0.0
    average_processing_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

@dataclass
class SEOAnalytics:
    """SEO analytics data."""
    total_seo_score: int = 0
    average_seo_score: float = 0.0
    seo_score_distribution: Dict[str, int] = None
    content_quality_scores: List[float] = None
    keyword_density: Dict[str, float] = None
    content_length_distribution: Dict[str, int] = None

class RealTimeMonitor:
    """Real-time monitoring for SEO injection processes."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.progress_history: deque = deque(maxlen=max_history)
        self.metrics = PerformanceMetrics(start_time=datetime.now(timezone.utc))
        self.analytics = SEOAnalytics()
        self.callbacks: List[Callable] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Initialize analytics
        self.analytics.seo_score_distribution = defaultdict(int)
        self.analytics.content_quality_scores = []
        self.analytics.keyword_density = defaultdict(float)
        self.analytics.content_length_distribution = defaultdict(int)
    
    def start_monitoring(self):
        """Start real-time monitoring."""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                self._update_metrics()
                self._notify_callbacks()
                time.sleep(1.0)  # Update every second
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5.0)
    
    def _update_metrics(self):
        """Update performance metrics."""
        if self.metrics.start_time:
            elapsed = (datetime.now(timezone.utc) - self.metrics.start_time).total_seconds()
            if elapsed > 0:
                self.metrics.items_per_second = self.metrics.processed_items / elapsed
        
        # Update memory and CPU usage
        self.metrics.memory_usage_mb = self._get_memory_usage()
        self.metrics.cpu_usage_percent = self._get_cpu_usage()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        # System/baremetal metrics are intentionally disabled.
        return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        # System/baremetal metrics are intentionally disabled.
        return 0.0
    
    def update_progress(self, processed: int, total: int, current_item: str = "", status: str = "processing", message: str = ""):
        """Update progress information."""
        update = ProgressUpdate(
            timestamp=datetime.now(timezone.utc),
            processed=processed,
            total=total,
            current_item=current_item,
            status=status,
            message=message
        )
        
        self.progress_history.append(update)
        
        # Update metrics
        self.metrics.processed_items = processed
        self.metrics.total_items = total
        
        if status == "completed":
            self.metrics.updated_items += 1
        elif status == "error":
            self.metrics.error_items += 1
        elif status == "skipped":
            self.metrics.skipped_items += 1
        elif status == "locked":
            self.metrics.locked_items += 1
    
    def add_callback(self, callback: Callable):
        """Add a progress callback."""
        self.callbacks.append(callback)
    
    def _notify_callbacks(self):
        """Notify all callbacks of current status."""
        for callback in self.callbacks:
            try:
                callback(self.get_current_status())
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': asdict(self.metrics),
            'analytics': asdict(self.analytics),
            'progress_history': [asdict(update) for update in list(self.progress_history)[-10:]]  # Last 10 updates
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        if self.analytics.content_quality_scores:
            avg_quality = sum(self.analytics.content_quality_scores) / len(self.analytics.content_quality_scores)
        else:
            avg_quality = 0.0
        
        return {
            'total_items_processed': self.metrics.processed_items,
            'average_seo_score': self.analytics.average_seo_score,
            'average_content_quality': avg_quality,
            'seo_score_distribution': dict(self.analytics.seo_score_distribution),
            'content_length_distribution': dict(self.analytics.content_length_distribution),
            'top_keywords': dict(sorted(self.analytics.keyword_density.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def add_seo_analytics(self, seo_score: int, content_quality: float, keywords: List[str], content_length: int):
        """Add SEO analytics data."""
        self.analytics.total_seo_score += seo_score
        self.analytics.average_seo_score = self.analytics.total_seo_score / max(1, self.metrics.processed_items)
        
        # Update distributions
        score_range = f"{(seo_score // 10) * 10}-{(seo_score // 10) * 10 + 9}"
        self.analytics.seo_score_distribution[score_range] += 1
        
        self.analytics.content_quality_scores.append(content_quality)
        
        # Update keyword density
        for keyword in keywords:
            self.analytics.keyword_density[keyword.lower()] += 1
        
        # Update content length distribution
        length_range = f"{(content_length // 100) * 100}-{(content_length // 100) * 100 + 99}"
        self.analytics.content_length_distribution[length_range] += 1

class WebSocketDashboard:
    """WebSocket-based real-time dashboard."""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.clients: List[Any] = []
        self.monitor: Optional[RealTimeMonitor] = None
    
    def start_server(self):
        """Start WebSocket server."""
        try:
            import websockets
            import asyncio
            
            async def handle_client(websocket, path):
                self.clients.append(websocket)
                try:
                    while True:
                        if self.monitor:
                            status = self.monitor.get_current_status()
                            await websocket.send(json.dumps(status))
                        await asyncio.sleep(1.0)
                except websockets.exceptions.ConnectionClosed:
                    pass
                finally:
                    self.clients.remove(websocket)
            
            start_server = websockets.serve(handle_client, "localhost", self.port)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
            
        except ImportError:
            print("WebSocket support not available. Install websockets package.")
        except Exception as e:
            print(f"Error starting WebSocket server: {e}")
    
    def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected clients."""
        if self.clients:
            message = json.dumps(data)
            for client in self.clients:
                try:
                    client.send(message)
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")

class ConsoleDashboard:
    """Console-based real-time dashboard."""
    
    def __init__(self, monitor: RealTimeMonitor):
        self.monitor = monitor
        self.last_update = None
    
    def start_dashboard(self):
        """Start console dashboard."""
        import os
        
        def clear_screen():
            os.system('cls' if os.name == 'nt' else 'clear')
        
        def display_status():
            clear_screen()
            status = self.monitor.get_current_status()
            metrics = status['metrics']
            
            print("🎯 SEO Injection Real-Time Dashboard")
            print("=" * 60)
            print(f"📊 Progress: {metrics['processed_items']}/{metrics['total_items']} items")
            print(f"✅ Updated: {metrics['updated_items']}")
            print(f"⏭️  Skipped: {metrics['skipped_items']}")
            print(f"❌ Errors: {metrics['error_items']}")
            print(f"🔒 Locked: {metrics['locked_items']}")
            print(f"⚡ Speed: {metrics['items_per_second']:.2f} items/sec")
            print(f"💾 Memory: {metrics['memory_usage_mb']:.1f} MB")
            print(f"🖥️  CPU: {metrics['cpu_usage_percent']:.1f}%")
            
            if metrics['processed_items'] > 0:
                elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(metrics['start_time'])).total_seconds()
                remaining = (metrics['total_items'] - metrics['processed_items']) / max(1, metrics['items_per_second'])
                print(f"⏱️  Elapsed: {elapsed:.1f}s")
                print(f"⏳ Remaining: {remaining:.1f}s")
            
            print("=" * 60)
            
            # Show recent progress
            if status['progress_history']:
                print("📈 Recent Activity:")
                for update in status['progress_history'][-5:]:
                    timestamp = datetime.fromisoformat(update['timestamp']).strftime("%H:%M:%S")
                    print(f"  {timestamp} - {update['current_item'][:50]}... ({update['status']})")
        
        # Add callback to monitor
        self.monitor.add_callback(lambda status: display_status())
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        try:
            while self.monitor.is_monitoring:
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
        finally:
            self.monitor.stop_monitoring()

class JSONDashboard:
    """JSON-based dashboard for API integration."""
    
    def __init__(self, monitor: RealTimeMonitor, output_file: str = "seo_dashboard.json"):
        self.monitor = monitor
        self.output_file = Path(output_file)
    
    def start_dashboard(self):
        """Start JSON dashboard."""
        def update_file(status):
            try:
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(status, f, indent=2, default=str)
            except Exception as e:
                print(f"Error writing dashboard file: {e}")
        
        # Add callback to monitor
        self.monitor.add_callback(update_file)
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        try:
            while self.monitor.is_monitoring:
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
        finally:
            self.monitor.stop_monitoring()

def create_monitor() -> RealTimeMonitor:
    """Create a new real-time monitor."""
    return RealTimeMonitor()

def create_console_dashboard(monitor: RealTimeMonitor) -> ConsoleDashboard:
    """Create a console dashboard."""
    return ConsoleDashboard(monitor)

def create_json_dashboard(monitor: RealTimeMonitor, output_file: str = "seo_dashboard.json") -> JSONDashboard:
    """Create a JSON dashboard."""
    return JSONDashboard(monitor, output_file)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SEO Injection Monitoring Dashboard")
    parser.add_argument("--type", choices=['console', 'json', 'websocket'], default='console', help="Dashboard type")
    parser.add_argument("--output", help="Output file for JSON dashboard")
    parser.add_argument("--port", type=int, default=8765, help="Port for WebSocket dashboard")
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = create_monitor()
    
    if args.type == 'console':
        dashboard = create_console_dashboard(monitor)
        dashboard.start_dashboard()
    elif args.type == 'json':
        output_file = args.output or "seo_dashboard.json"
        dashboard = create_json_dashboard(monitor, output_file)
        dashboard.start_dashboard()
    elif args.type == 'websocket':
        dashboard = WebSocketDashboard(args.port)
        dashboard.start_server()
