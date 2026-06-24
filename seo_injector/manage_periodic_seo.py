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
Management script for Periodic SEO Injection System
Allows manual control and monitoring of the periodic SEO injection tasks
"""

import sys
import os
import argparse

# Add the parent directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from seo_injector.periodic_seo_tasks import (
    trigger_periodic_seo_injection,
    trigger_seo_health_check,
    SEO_INJECTION_CONFIG
)


def print_banner():
    """Print a nice banner for the management script."""
    print("🎯 LilyOpenCMS Periodic SEO Injection Manager")
    print("=" * 50)
    print()


def show_status():
    """Show current status and configuration."""
    print("📊 Current Configuration:")
    print(f"   Enabled: {SEO_INJECTION_CONFIG['enabled']}")
    print(f"   Batch Size: {SEO_INJECTION_CONFIG['batch_size']} articles")
    print(f"   Max Runtime: {SEO_INJECTION_CONFIG['max_runtime_seconds']} seconds")
    print(f"   Min SEO Score Threshold: {SEO_INJECTION_CONFIG['min_seo_score_threshold']}")
    print(f"   Max Article Age: {SEO_INJECTION_CONFIG['max_age_days']} days")
    print(f"   Respect SEO Lock: {SEO_INJECTION_CONFIG['respect_seo_lock']}")
    print(f"   Dry Run Mode: {SEO_INJECTION_CONFIG['dry_run']}")
    print()

    # Show health check
    print("🔍 Running SEO Health Check...")
    health_result = trigger_seo_health_check()

    if health_result['status'] == 'success':
        stats = health_result['statistics']
        print("✅ SEO Health Status:")
        print(f"   Total Articles: {stats['total_articles']}")
        print(f"   Published Articles: {stats['published_articles']}")
        print(f"   SEO Locked Articles: {stats['seo_locked_articles']}")
        print()
        print("📈 SEO Coverage (All Articles):")
        for metric, percentage in stats['seo_coverage'].items():
            print(".1f")
        print()
        if stats['published_seo_coverage']:
            print("📈 SEO Coverage (Published Articles):")
            for metric, percentage in stats['published_seo_coverage'].items():
                print(".1f")
    else:
        print(f"❌ Health check failed: {health_result.get('message', 'Unknown error')}")


def run_injection(args):
    """Run SEO injection manually."""
    print(f"🚀 Running SEO injection...")
    print(f"   Batch size: {args.batch_size or 'default'}")
    print(f"   Dry run: {args.dry_run}")
    print()

    result = trigger_periodic_seo_injection(
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )

    if result['status'] == 'completed':
        print("✅ SEO injection completed successfully!")
        print(f"   Articles processed: {result['articles_processed']}")
        print(f"   Successful injections: {result['successful_injections']}")
        print(f"   Errors: {result['errors_count']}")
        print(".2f")
        if result.get('dry_run'):
            print("   📝 This was a dry run - no actual changes made")
    elif result['status'] == 'disabled':
        print("ℹ️ Periodic SEO injection is currently disabled")
    else:
        print(f"❌ SEO injection failed: {result.get('message', 'Unknown error')}")

    if result.get('errors'):
        print("\n⚠️ Errors encountered:")
        for error in result['errors'][:5]:  # Show first 5 errors
            print(f"   • {error}")


def run_health_check(args):
    """Run SEO health check."""
    print("🔍 Running detailed SEO health check...")

    result = trigger_seo_health_check()

    if result['status'] == 'success':
        stats = result['statistics']
        print("✅ SEO Health Check Results:")
        print(f"   Timestamp: {result['timestamp']}")
        print(f"   Total Articles: {stats['total_articles']}")
        print(f"   Published Articles: {stats['published_articles']}")
        print(f"   SEO Locked Articles: {stats['seo_locked_articles']}")
        print()

        print("📊 Detailed SEO Coverage:")
        print("   Metric                  | All Articles | Published Only")
        print("   ------------------------|--------------|----------------")
        metrics = ['meta_description', 'meta_keywords', 'seo_slug', 'og_title', 'schema_markup']
        for metric in metrics:
            stats['seo_coverage'].get(metric, 0)
            stats['published_seo_coverage'].get(metric, 0) if stats['published_seo_coverage'] else 0
            print("20")
    else:
        print(f"❌ Health check failed: {result.get('message', 'Unknown error')}")


def main():
    """Main function for the management script."""
    print_banner()

    parser = argparse.ArgumentParser(
        description="Manage LilyOpenCMS Periodic SEO Injection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_periodic_seo.py status                    # Show current status
  python manage_periodic_seo.py inject                    # Run SEO injection
  python manage_periodic_seo.py inject --dry-run         # Test injection without changes
  python manage_periodic_seo.py inject --batch-size 5    # Process only 5 articles
  python manage_periodic_seo.py health                   # Run detailed health check
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show current status and configuration')

    # Inject command
    inject_parser = subparsers.add_parser('inject', help='Run SEO injection manually')
    inject_parser.add_argument('--batch-size', type=int, help='Number of articles to process')
    inject_parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (no changes)')

    # Health command
    health_parser = subparsers.add_parser('health', help='Run detailed SEO health check')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'status':
        show_status()
    elif args.command == 'inject':
        run_injection(args)
    elif args.command == 'health':
        run_health_check(args)


if __name__ == "__main__":
    main()
