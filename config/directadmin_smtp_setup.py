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
DirectAdmin SMTP Setup
Optimized for DirectAdmin hosting providers
"""

import os
import sys
import socket
from pathlib import Path

def get_config_path():
    """Get the path to smtp_config.txt"""
    return Path(__file__).parent / "smtp_config.txt"

def test_directadmin_smtp(domain):
    """Test DirectAdmin SMTP connectivity"""
    smtp_servers = [
        f"mail.{domain}",
        f"smtp.{domain}",
        f"mail.{domain.split('.')[-2]}.{domain.split('.')[-1]}",  # For subdomains
    ]
    
    ports = [587, 465, 25]
    
    print(f"🔍 Testing DirectAdmin SMTP for domain: {domain}")
    print("-" * 50)
    
    working_configs = []
    
    for server in smtp_servers:
        for port in ports:
            print(f"Testing {server}:{port}...", end=" ")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((server, port))
                sock.close()
                
                if result == 0:
                    print("✅ CONNECTED")
                    working_configs.append((server, port))
                else:
                    print("❌ BLOCKED")
            except Exception as e:
                print(f"❌ ERROR: {e}")
    
    return working_configs

def setup_directadmin_smtp():
    """Setup DirectAdmin SMTP configuration"""
    print("📧 DirectAdmin SMTP Setup")
    print("=" * 50)
    print("DirectAdmin hosting providers typically use:")
    print("• mail.yourdomain.com as SMTP server")
    print("• Port 587 (TLS) or 465 (SSL)")
    print("• Your domain email credentials")
    print()
    
    # Get domain
    domain = input("Enter your domain (e.g., example.com): ").strip()
    if not domain:
        print("❌ Domain is required!")
        return False
    
    # Test connectivity
    working_configs = test_directadmin_smtp(domain)
    
    if not working_configs:
        print(f"\n❌ No working SMTP servers found for {domain}")
        print("\n💡 Try these alternatives:")
        print("1. Contact your hosting provider for SMTP settings")
        print("2. Check your DirectAdmin panel for email settings")
        print("3. Use a different email provider (Gmail, Outlook)")
        return False
    
    # Choose the best configuration
    print(f"\n✅ Found {len(working_configs)} working SMTP server(s):")
    for i, (server, port) in enumerate(working_configs, 1):
        protocol = "SSL" if port == 465 else "TLS"
        print(f"   {i}. {server}:{port} ({protocol})")
    
    if len(working_configs) == 1:
        server, port = working_configs[0]
        print(f"\n🎯 Using: {server}:{port}")
    else:
        while True:
            try:
                choice = int(input(f"\nChoose SMTP server (1-{len(working_configs)}): ")) - 1
                if 0 <= choice < len(working_configs):
                    server, port = working_configs[choice]
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    # Get email credentials
    print(f"\n📧 Email Configuration for {server}:{port}")
    print("-" * 40)
    
    email = input(f"Enter your email address (e.g., admin@{domain}): ").strip()
    if not email:
        print("❌ Email address is required!")
        return False
    
    password = input("Enter your email password: ").strip()
    if not password:
        print("❌ Password is required!")
        return False
    
    # Determine protocol settings
    use_tls = port == 587
    use_ssl = port == 465
    
    # Create configuration
    config = {
        'smtp_server': server,
        'smtp_port': str(port),
        'smtp_use_tls': 'true' if use_tls else 'false',
        'smtp_use_ssl': 'true' if use_ssl else 'false',
        'smtp_username': email,
        'smtp_password': password,
        'mail_default_sender': email,
        'mail_sender_name': 'LilyOpenCMS',
        'mail_reply_to': email,
        'smtp_verify_ssl': 'true',
        'smtp_timeout': '30',
        'smtp_debug': 'false',
        'smtp_suppress_send': 'false'
    }
    
    # Write configuration
    write_directadmin_config(config)
    
    print(f"\n✅ DirectAdmin SMTP configuration saved!")
    print(f"📧 SMTP Server: {server}:{port}")
    print(f"📧 Email: {email}")
    print(f"🔒 Protocol: {'SSL' if use_ssl else 'TLS'}")
    
    return config

def write_directadmin_config(config):
    """Write DirectAdmin SMTP configuration to file"""
    config_path = get_config_path()
    
    with open(config_path, 'w') as f:
        f.write("# SMTP Configuration for LilyOpenCMS (DirectAdmin)\n")
        f.write("# This file contains SMTP settings for email delivery\n\n")
        
        # SMTP Server Configuration
        f.write("# SMTP Server Configuration (DirectAdmin)\n")
        f.write(f"smtp_server={config['smtp_server']}\n")
        f.write(f"smtp_port={config['smtp_port']}\n")
        f.write(f"smtp_use_tls={config['smtp_use_tls']}\n")
        f.write(f"smtp_use_ssl={config['smtp_use_ssl']}\n\n")
        
        # Authentication
        f.write("# Authentication (DirectAdmin Email)\n")
        f.write(f"smtp_username={config['smtp_username']}\n")
        f.write(f"smtp_password={config['smtp_password']}\n\n")
        
        # Email Settings
        f.write("# Email Settings\n")
        f.write(f"mail_default_sender={config['mail_default_sender']}\n")
        f.write(f"mail_sender_name={config['mail_sender_name']}\n")
        f.write(f"mail_reply_to={config['mail_reply_to']}\n\n")
        
        # Rate Limiting
        f.write("# Rate Limiting\n")
        f.write("email_rate_limit_per_hour=10\n")
        f.write("email_rate_limit_per_day=50\n\n")
        
        # Security
        f.write("# Security\n")
        f.write(f"smtp_verify_ssl={config['smtp_verify_ssl']}\n")
        f.write(f"smtp_timeout={config['smtp_timeout']}\n\n")
        
        # Development/Testing
        f.write("# Development/Testing\n")
        f.write(f"smtp_debug={config['smtp_debug']}\n")
        f.write(f"smtp_suppress_send={config['smtp_suppress_send']}\n")

def setup_directadmin_common_configs():
    """Setup common DirectAdmin SMTP configurations"""
    print("📧 Common DirectAdmin SMTP Configurations")
    print("=" * 50)
    
    configs = [
        {
            'name': 'Standard DirectAdmin (mail.domain.com:587)',
            'server': 'mail.{domain}',
            'port': 587,
            'tls': True,
            'ssl': False
        },
        {
            'name': 'DirectAdmin SSL (mail.domain.com:465)',
            'server': 'mail.{domain}',
            'port': 465,
            'tls': False,
            'ssl': True
        },
        {
            'name': 'DirectAdmin Legacy (mail.domain.com:25)',
            'server': 'mail.{domain}',
            'port': 25,
            'tls': False,
            'ssl': False
        }
    ]
    
    print("Choose a common DirectAdmin configuration:")
    for i, config in enumerate(configs, 1):
        print(f"   {i}. {config['name']}")
    
    while True:
        try:
            choice = int(input(f"\nChoose configuration (1-{len(configs)}): ")) - 1
            if 0 <= choice < len(configs):
                selected_config = configs[choice]
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")
    
    domain = input("Enter your domain (e.g., example.com): ").strip()
    if not domain:
        print("❌ Domain is required!")
        return False
    
    email = input(f"Enter your email address (e.g., admin@{domain}): ").strip()
    if not email:
        print("❌ Email address is required!")
        return False
    
    password = input("Enter your email password: ").strip()
    if not password:
        print("❌ Password is required!")
        return False
    
    # Create configuration
    server = selected_config['server'].format(domain=domain)
    config = {
        'smtp_server': server,
        'smtp_port': str(selected_config['port']),
        'smtp_use_tls': 'true' if selected_config['tls'] else 'false',
        'smtp_use_ssl': 'true' if selected_config['ssl'] else 'false',
        'smtp_username': email,
        'smtp_password': password,
        'mail_default_sender': email,
        'mail_sender_name': 'LilyOpenCMS',
        'mail_reply_to': email,
        'smtp_verify_ssl': 'true',
        'smtp_timeout': '30',
        'smtp_debug': 'false',
        'smtp_suppress_send': 'false'
    }
    
    write_directadmin_config(config)
    
    print(f"\n✅ DirectAdmin SMTP configuration saved!")
    print(f"📧 SMTP Server: {server}:{selected_config['port']}")
    print(f"📧 Email: {email}")
    print(f"🔒 Protocol: {'SSL' if selected_config['ssl'] else 'TLS' if selected_config['tls'] else 'None'}")
    
    return config

def main():
    print("🔧 DirectAdmin SMTP Setup")
    print("=" * 50)
    print("This tool is optimized for DirectAdmin hosting providers.")
    print()
    print("Choose setup method:")
    print("1. Auto-detect DirectAdmin SMTP (Recommended)")
    print("2. Use common DirectAdmin configurations")
    print("3. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            setup_directadmin_smtp()
            break
        elif choice == '2':
            setup_directadmin_common_configs()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1-3.")
    
    print("\n📋 Next Steps:")
    print("1. Test the configuration: python config/smtp_config_helper.py test")
    print("2. Send a test email: python config/smtp_config_helper.py send-test your-email@example.com")
    print("3. If still having issues, run: python config/network_diagnostic.py")

if __name__ == "__main__":
    main()
