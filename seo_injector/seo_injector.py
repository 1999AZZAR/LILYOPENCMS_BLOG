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
Main SEO Injector for LilyOpenCMS
Handles all SEO injection operations for news, albums, chapters, and root pages.
"""

import sys
import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import app and db from the local main module
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(project_root, "main.py"))
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
app = main.app
db = main.db

# Import the individual injector modules with fallback for different import contexts
try:
    # Try relative imports first (when used as a package)
    from .inject_news_seo import inject_news_seo as inject_news_seo_func
    from .inject_album_seo import inject_album_seo as inject_album_seo_func
    from .inject_chapter_seo import inject_chapter_seo as inject_chapter_seo_func
    from .inject_root_seo import inject_root_seo as inject_root_seo_func
    
    # Import stats functions
    from .inject_news_seo import show_news_seo_stats as show_news_seo_stats_func
    from .inject_album_seo import show_album_seo_stats as show_album_seo_stats_func
    from .inject_chapter_seo import show_chapter_seo_stats as show_chapter_seo_stats_func
    from .inject_root_seo import show_root_seo_stats as show_root_seo_stats_func
except ImportError:
    # Fallback to absolute imports (when imported from outside the package)
    from seo_injector.inject_news_seo import inject_news_seo as inject_news_seo_func
    from seo_injector.inject_album_seo import inject_album_seo as inject_album_seo_func
    from seo_injector.inject_chapter_seo import inject_chapter_seo as inject_chapter_seo_func
    from seo_injector.inject_root_seo import inject_root_seo as inject_root_seo_func
    
    # Import stats functions
    from seo_injector.inject_news_seo import show_news_seo_stats as show_news_seo_stats_func
    from seo_injector.inject_album_seo import show_album_seo_stats as show_album_seo_stats_func
    from seo_injector.inject_chapter_seo import show_chapter_seo_stats as show_chapter_seo_stats_func
    from seo_injector.inject_root_seo import show_root_seo_stats as show_root_seo_stats_func

class SEOInjector:
    """Main SEO Injector class for handling all SEO operations."""
    
    def __init__(self):
        self.results = {
            'news': {'status': 'pending', 'message': '', 'details': {}},
            'albums': {'status': 'pending', 'message': '', 'details': {}},
            'chapters': {'status': 'pending', 'message': '', 'details': {}},
            'root': {'status': 'pending', 'message': '', 'details': {}}
        }
        self.start_time = datetime.now(timezone.utc)
    
    def run_news_seo_injection(self) -> Dict[str, Any]:
        """Run SEO injection for news articles."""
        try:
            print("🎯 Starting News SEO Injection...")
            
            # Capture the output by redirecting stdout temporarily
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                inject_news_seo_func()
            
            output_text = output.getvalue()
            
            # Parse the output to extract statistics
            details = self._parse_injection_output(output_text)
            
            self.results['news'] = {
                'status': 'completed',
                'message': 'News SEO injection completed successfully',
                'details': details,
                'output': output_text
            }
            
            return self.results['news']
            
        except Exception as e:
            error_msg = f"Error during news SEO injection: {str(e)}"
            self.results['news'] = {
                'status': 'error',
                'message': error_msg,
                'details': {},
                'error': str(e)
            }
            return self.results['news']
    
    def run_album_seo_injection(self) -> Dict[str, Any]:
        """Run SEO injection for albums."""
        try:
            print("🎯 Starting Album SEO Injection...")
            
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                inject_album_seo_func()
            
            output_text = output.getvalue()
            details = self._parse_injection_output(output_text)
            
            self.results['albums'] = {
                'status': 'completed',
                'message': 'Album SEO injection completed successfully',
                'details': details,
                'output': output_text
            }
            
            return self.results['albums']
            
        except Exception as e:
            error_msg = f"Error during album SEO injection: {str(e)}"
            self.results['albums'] = {
                'status': 'error',
                'message': error_msg,
                'details': {},
                'error': str(e)
            }
            return self.results['albums']
    
    def run_chapter_seo_injection(self) -> Dict[str, Any]:
        """Run SEO injection for chapters."""
        try:
            print("🎯 Starting Chapter SEO Injection...")
            
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                inject_chapter_seo_func()
            
            output_text = output.getvalue()
            details = self._parse_injection_output(output_text)
            
            self.results['chapters'] = {
                'status': 'completed',
                'message': 'Chapter SEO injection completed successfully',
                'details': details,
                'output': output_text
            }
            
            return self.results['chapters']
            
        except Exception as e:
            error_msg = f"Error during chapter SEO injection: {str(e)}"
            self.results['chapters'] = {
                'status': 'error',
                'message': error_msg,
                'details': {},
                'error': str(e)
            }
            return self.results['chapters']
    
    def run_root_seo_injection(self) -> Dict[str, Any]:
        """Run SEO injection for root pages."""
        try:
            print("🎯 Starting Root SEO Injection...")
            
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                inject_root_seo_func()
            
            output_text = output.getvalue()
            details = self._parse_injection_output(output_text)
            
            self.results['root'] = {
                'status': 'completed',
                'message': 'Root SEO injection completed successfully',
                'details': details,
                'output': output_text
            }
            
            return self.results['root']
            
        except Exception as e:
            error_msg = f"Error during root SEO injection: {str(e)}"
            self.results['root'] = {
                'status': 'error',
                'message': error_msg,
                'details': {},
                'error': str(e)
            }
            return self.results['root']
    
    def run_all_injections(self) -> Dict[str, Any]:
        """Run all SEO injections."""
        print("🚀 Starting Comprehensive SEO Injection...")
        print("=" * 60)
        
        # Run all injections
        news_result = self.run_news_seo_injection()
        album_result = self.run_album_seo_injection()
        chapter_result = self.run_chapter_seo_injection()
        root_result = self.run_root_seo_injection()
        
        # Calculate overall statistics
        total_updated = 0
        total_errors = 0
        total_locked = 0
        
        for result in [news_result, album_result, chapter_result, root_result]:
            if result['status'] == 'completed':
                details = result.get('details', {})
                total_updated += details.get('updated_count', 0)
                total_errors += details.get('error_count', 0)
                total_locked += details.get('locked_count', 0)
            elif result['status'] == 'error':
                total_errors += 1
        
        # Create summary
        end_time = datetime.now(timezone.utc)
        duration = (end_time - self.start_time).total_seconds()
        
        summary = {
            'status': 'completed' if total_errors == 0 else 'completed_with_errors',
            'message': f'SEO injection completed in {duration:.2f} seconds',
            'total_updated': total_updated,
            'total_errors': total_errors,
            'total_locked': total_locked,
            'duration_seconds': duration,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'results': self.results
        }
        
        print("=" * 60)
        print("📊 COMPREHENSIVE SEO INJECTION SUMMARY")
        print("=" * 60)
        print(f"✅ Total items updated: {total_updated}")
        print(f"🔒 Total items locked: {total_locked}")
        print(f"❌ Total errors: {total_errors}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print("=" * 60)
        
        return summary
    
    def get_seo_stats(self) -> Dict[str, Any]:
        """Get SEO statistics for all content types."""
        try:
            import io
            import contextlib
            
            stats = {}
            
            # Get news stats
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                show_news_seo_stats_func()
            stats['news'] = output.getvalue()
            
            # Get album stats
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                show_album_seo_stats_func()
            stats['albums'] = output.getvalue()
            
            # Get chapter stats
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                show_chapter_seo_stats_func()
            stats['chapters'] = output.getvalue()
            
            # Get root stats
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                show_root_seo_stats_func()
            stats['root'] = output.getvalue()
            
            return {
                'status': 'success',
                'stats': stats
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error getting SEO stats: {str(e)}",
                'error': str(e)
            }
    
    def _parse_injection_output(self, output_text: str) -> Dict[str, Any]:
        """Parse injection output to extract statistics."""
        details = {
            'updated_count': 0,
            'skipped_count': 0,
            'error_count': 0,
            'locked_count': 0,
            'total_processed': 0
        }
        
        # Parse summary lines
        lines = output_text.split('\n')
        for line in lines:
            if 'Successfully updated:' in line:
                try:
                    count = int(line.split(':')[1].strip().split()[0])
                    details['updated_count'] = count
                except:
                    pass
            elif 'Skipped' in line and 'locked' in line.lower():
                try:
                    count = int(line.split('(')[1].split()[0])
                    details['locked_count'] = count
                except:
                    pass
            elif 'Errors:' in line:
                try:
                    count = int(line.split(':')[1].strip().split()[0])
                    details['error_count'] = count
                except:
                    pass
            elif 'Total' in line and 'processed:' in line:
                try:
                    count = int(line.split(':')[1].strip().split()[0])
                    details['total_processed'] = count
                except:
                    pass
        
        return details

def run_seo_injection(injection_type: str = 'all') -> Dict[str, Any]:
    """Run SEO injection for specified type."""
    injector = SEOInjector()
    
    with app.app_context():
        if injection_type == 'news':
            return injector.run_news_seo_injection()
        elif injection_type == 'albums':
            return injector.run_album_seo_injection()
        elif injection_type == 'chapters':
            return injector.run_chapter_seo_injection()
        elif injection_type == 'root':
            return injector.run_root_seo_injection()
        elif injection_type == 'all':
            return injector.run_all_injections()
        else:
            return {
                'status': 'error',
                'message': f'Unknown injection type: {injection_type}'
            }

def get_seo_statistics() -> Dict[str, Any]:
    """Get SEO statistics for all content types."""
    injector = SEOInjector()
    
    with app.app_context():
        return injector.get_seo_stats()

# Legacy function for backward compatibility
def run_seo_injection(injection_type='all'):
    """
    Legacy function for backward compatibility with existing routes.
    Runs SEO injection for the specified content type.
    
    Args:
        injection_type (str): Type of injection to run ('news', 'albums', 'chapters', 'root', 'all')
    
    Returns:
        dict: Results of the SEO injection operation
    """
    try:
        injector = SEOInjector()
        
        if injection_type == 'news':
            return injector.run_news_seo_injection()
        elif injection_type == 'albums':
            return injector.run_albums_seo_injection()
        elif injection_type == 'chapters':
            return injector.run_chapters_seo_injection()
        elif injection_type == 'root':
            return injector.run_root_seo_injection()
        elif injection_type == 'all':
            return injector.run_all_injections()
        else:
            return {
                'status': 'error',
                'message': f'Unknown injection type: {injection_type}',
                'details': {}
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error running SEO injection: {str(e)}',
            'details': {}
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run SEO injection for LilyOpenCMS")
    parser.add_argument("--type", choices=['news', 'albums', 'chapters', 'root', 'all'], 
                       default='all', help="Type of SEO injection to run")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    
    args = parser.parse_args()
    
    if args.stats:
        result = get_seo_statistics()
        print(json.dumps(result, indent=2))
    else:
        result = run_seo_injection(args.type)
        print(json.dumps(result, indent=2)) 