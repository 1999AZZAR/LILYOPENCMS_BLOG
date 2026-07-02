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
Alternative SMTP Setup for Shared Hosting Providers
Provides multiple SMTP configuration options when Gmail is blocked
"""

import os
import sys
from pathlib import Path

def get_config_path():
    """Get the path to smtp_config.txt"""
    return Path(__file__).parent / "smtp_config.txt"

def read_config():
    """Read current SMTP configuration"""
    config_path = get_config_path()
    config = {}
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

def write_config(config):
    """Write SMTP configuration to file"""
    config_path = get_config_path()
    
    with open(config_path, 'w') as f:
        f.write("# SMTP Configuration for LilyOpenCMS\n")
        f.write("# This file contains SMTP settings for email delivery\n\n")
        
        # SMTP Server Configuration
        f.write("# SMTP Server Configuration\n")
        f.write(f"smtp_server={config.get('smtp_server', 'smtp.gmail.com')}\n")
        f.write(f"smtp_port={config.get('smtp_port', '587')}\n")
        f.write(f"smtp_use_tls={config.get('smtp_use_tls', 'true')}\n")
        f.write(f"smtp_use_ssl={config.get('smtp_use_ssl', 'false')}\n\n")
        
        # Authentication
        f.write("# Authentication\n")
        f.write(f"smtp_username={config.get('smtp_username', 'your-email@gmail.com')}\n")
        f.write(f"smtp_password={config.get('smtp_password', 'your-app-password')}\n\n")
        
        # Email Settings
        f.write("# Email Settings\n")
        f.write(f"mail_default_sender={config.get('mail_default_sender', 'your-email@gmail.com')}\n")
        f.write(f"mail_sender_name={config.get('mail_sender_name', 'LilyOpenCMS')}\n")
        f.write(f"mail_reply_to={config.get('mail_reply_to', 'your-email@gmail.com')}\n\n")
        
        # Rate Limiting
        f.write("# Rate Limiting\n")
        f.write(f"email_rate_limit_per_hour={config.get('email_rate_limit_per_hour', '10')}\n")
        f.write(f"email_rate_limit_per_day={config.get('email_rate_limit_per_day', '50')}\n\n")
        
        # Security
        f.write("# Security\n")
        f.write(f"smtp_verify_ssl={config.get('smtp_verify_ssl', 'true')}\n")
        f.write(f"smtp_timeout={config.get('smtp_timeout', '30')}\n\n")
        
        # Development/Testing
        f.write("# Development/Testing\n")
        f.write(f"smtp_debug={config.get('smtp_debug', 'false')}\n")
        f.write(f"smtp_suppress_send={config.get('smtp_suppress_send', 'false')}\n")

def setup_hostinger_smtp():
    """Setup Hostinger SMTP configuration"""
    print("📧 Setting up Hostinger SMTP Configuration")
    print("=" * 50)
    
    email = input("Enter your Hostinger email address: ").strip()
    password = input("Enter your Hostinger email password: ").strip()
    
    config = {
        'smtp_server': 'mail.hostinger.com',
        'smtp_port': '587',
        'smtp_use_tls': 'true',
        'smtp_use_ssl': 'false',
        'smtp_username': email,
        'smtp_password': password,
        'mail_default_sender': email,
        'mail_sender_name': 'LilyOpenCMS',
        'mail_reply_to': email,
        'smtp_suppress_send': 'false'
    }
    
    write_config(config)
    print("✅ Hostinger SMTP configuration saved!")
    return config

def setup_outlook_smtp():
    """Setup Outlook/Hotmail SMTP configuration"""
    print("📧 Setting up Outlook/Hotmail SMTP Configuration")
    print("=" * 50)
    
    email = input("Enter your Outlook/Hotmail email address: ").strip()
    password = input("Enter your Outlook/Hotmail password: ").strip()
    
    config = {
        'smtp_server': 'smtp.outlook.com',
        'smtp_port': '587',
        'smtp_use_tls': 'true',
        'smtp_use_ssl': 'false',
        'smtp_username': email,
        'smtp_password': password,
        'mail_default_sender': email,
        'mail_sender_name': 'LilyOpenCMS',
        'mail_reply_to': email,
        'smtp_suppress_send': 'false'
    }
    
    write_config(config)
    print("✅ Outlook SMTP configuration saved!")
    return config

def setup_yahoo_smtp():
    """Setup Yahoo SMTP configuration"""
    print("📧 Setting up Yahoo SMTP Configuration")
    print("=" * 50)
    
    email = input("Enter your Yahoo email address: ").strip()
    password = input("Enter your Yahoo App Password: ").strip()
    
    config = {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': '587',
        'smtp_use_tls': 'true',
        'smtp_use_ssl': 'false',
        'smtp_username': email,
        'smtp_password': password,
        'mail_default_sender': email,
        'mail_sender_name': 'LilyOpenCMS',
        'mail_reply_to': email,
        'smtp_suppress_send': 'false'
    }
    
    write_config(config)
    print("✅ Yahoo SMTP configuration saved!")
    return config

def setup_development_mode():
    """Setup development mode (suppress sending)"""
    print("🔧 Setting up Development Mode")
    print("=" * 50)
    print("This will log emails instead of sending them.")
    print("Useful for testing when SMTP is blocked.")
    
    config = read_config()
    config['smtp_suppress_send'] = 'true'
    config['smtp_debug'] = 'true'
    
    write_config(config)
    print("✅ Development mode enabled!")
    print("📝 Emails will be logged instead of sent.")
    return config

def setup_custom_smtp():
    """Setup custom SMTP configuration"""
    print("📧 Setting up Custom SMTP Configuration")
    print("=" * 50)
    
    smtp_server = input("SMTP Server: ").strip()
    smtp_port = input("SMTP Port [587]: ").strip() or "587"
    use_tls = input("Use TLS? (y/n) [y]: ").strip().lower() or "y"
    use_ssl = input("Use SSL? (y/n) [n]: ").strip().lower() or "n"
    
    email = input("Email address: ").strip()
    password = input("Password: ").strip()
    
    config = {
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'smtp_use_tls': 'true' if use_tls == 'y' else 'false',
        'smtp_use_ssl': 'true' if use_ssl == 'y' else 'false',
        'smtp_username': email,
        'smtp_password': password,
        'mail_default_sender': email,
        'mail_sender_name': 'LilyOpenCMS',
        'mail_reply_to': email,
        'smtp_suppress_send': 'false'
    }
    
    write_config(config)
    print("✅ Custom SMTP configuration saved!")
    return config

def main():
    print("🔧 Alternative SMTP Setup for Shared Hosting")
    print("=" * 50)
    print("Choose an SMTP provider that works with your hosting:")
    print()
    print("1. Hostinger SMTP (Recommended for Hostinger hosting)")
    print("2. Outlook/Hotmail SMTP")
    print("3. Yahoo SMTP")
    print("4. Custom SMTP Server")
    print("5. Development Mode (Log emails instead of sending)")
    print("6. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            setup_hostinger_smtp()
            break
        elif choice == '2':
            setup_outlook_smtp()
            break
        elif choice == '3':
            setup_yahoo_smtp()
            break
        elif choice == '4':
            setup_custom_smtp()
            break
        elif choice == '5':
            setup_development_mode()
            break
        elif choice == '6':
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1-6.")
    
    print("\n📋 Next Steps:")
    print("1. Test the configuration: python config/smtp_config_helper.py test")
    print("2. Send a test email: python config/smtp_config_helper.py send-test your-email@example.com")
    print("3. If still having issues, run: python config/network_diagnostic.py")

if __name__ == "__main__":
    main()
