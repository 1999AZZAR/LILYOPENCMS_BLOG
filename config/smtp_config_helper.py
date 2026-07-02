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
SMTP Configuration Helper and Delivery Tester
Provides tools for configuring and testing SMTP settings
"""

import os
import sys
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SMTPConfigHelper:
    """Helper class for SMTP configuration and testing"""
    
    def __init__(self, config_file: str = "config/smtp_config.txt"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load SMTP configuration from file"""
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
            
            return config
            
        except Exception as e:
            print(f"❌ Error reading config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'smtp_server': 'localhost',
            'smtp_port': 587,
            'smtp_use_tls': True,
            'smtp_use_ssl': False,
            'smtp_username': None,
            'smtp_password': None,
            'mail_default_sender': 'noreply@hystory.id',
            'mail_sender_name': 'HYstory.id',
            'mail_reply_to': 'noreply@hystory.id',
            'email_rate_limit_per_hour': 10,
            'email_rate_limit_per_day': 50,
            'smtp_verify_ssl': True,
            'smtp_timeout': 30,
            'smtp_debug': False,
            'smtp_suppress_send': False
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test SMTP connection"""
        result = {
            'success': False,
            'message': '',
            'config': self.config
        }
        
        try:
            print(f"🔍 Testing SMTP connection to {self.config.get('smtp_server')}:{self.config.get('smtp_port')}")
            
            if self.config.get('smtp_suppress_send', False):
                result['success'] = True
                result['message'] = 'SMTP is configured but suppressed (testing mode)'
                print("✅ SMTP is in testing mode (suppress_send=true)")
                return result
            
            # Test connection
            server = smtplib.SMTP(
                self.config.get('smtp_server', 'localhost'),
                self.config.get('smtp_port', 587),
                timeout=self.config.get('smtp_timeout', 30)
            )
            
            if self.config.get('smtp_debug', False):
                server.set_debuglevel(1)
            
            if self.config.get('smtp_use_tls', True):
                print("🔒 Starting TLS...")
                server.starttls()
            
            if self.config.get('smtp_username') and self.config.get('smtp_password'):
                print("🔐 Authenticating...")
                server.login(
                    self.config.get('smtp_username'),
                    self.config.get('smtp_password')
                )
                print("✅ Authentication successful")
            else:
                print("⚠️  No authentication configured")
            
            server.quit()
            
            result['success'] = True
            result['message'] = 'SMTP connection successful'
            print("✅ SMTP connection test successful")
            
        except smtplib.SMTPAuthenticationError as e:
            result['message'] = f'Authentication failed: {str(e)}'
            print(f"❌ Authentication failed: {e}")
        except smtplib.SMTPConnectError as e:
            result['message'] = f'Connection failed: {str(e)}'
            print(f"❌ Connection failed: {e}")
        except smtplib.SMTPHeloError as e:
            result['message'] = f'SMTP HELO error: {str(e)}'
            print(f"❌ SMTP HELO error: {e}")
        except smtplib.SMTPException as e:
            result['message'] = f'SMTP error: {str(e)}'
            print(f"❌ SMTP error: {e}")
        except OSError as e:
            result['message'] = f'Network/OS error: {str(e)}'
            print(f"❌ Network/OS error: {e}")
        except Exception as e:
            result['message'] = f'Unexpected error: {str(e)}'
            print(f"❌ Unexpected error: {e}")
        
        return result
    
    def send_test_email(self, to_email: str, subject: str = "SMTP Test Email") -> bool:
        """Send a test email"""
        try:
            print(f"📧 Sending test email to {to_email}...")
            
            if self.config.get('smtp_suppress_send', False):
                print("✅ Test email would be sent (suppress_send=true)")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.get('mail_sender_name', 'HYstory.id')} <{self.config.get('mail_default_sender', 'noreply@hystory.id')}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Email body
            body = f"""
This is a test email from HYstory.id SMTP configuration helper.

Test Details:
- Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- SMTP Server: {self.config.get('smtp_server')}:{self.config.get('smtp_port')}
- TLS Enabled: {self.config.get('smtp_use_tls', True)}
- SSL Enabled: {self.config.get('smtp_use_ssl', False)}

If you received this email, your SMTP configuration is working correctly!

Best regards,
HYstory.id Team
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(
                self.config.get('smtp_server', 'localhost'),
                self.config.get('smtp_port', 587),
                timeout=self.config.get('smtp_timeout', 30)
            )
            
            if self.config.get('smtp_debug', False):
                server.set_debuglevel(1)
            
            if self.config.get('smtp_use_tls', True):
                server.starttls()
            
            if self.config.get('smtp_username') and self.config.get('smtp_password'):
                server.login(
                    self.config.get('smtp_username'),
                    self.config.get('smtp_password')
                )
            
            server.send_message(msg)
            server.quit()
            
            print("✅ Test email sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False
    
    def show_config(self):
        """Display current configuration"""
        print("📋 Current SMTP Configuration:")
        print("=" * 50)
        
        for key, value in self.config.items():
            if 'password' in key.lower() and value:
                display_value = '*' * len(str(value))
            else:
                display_value = value
            
            print(f"{key:25}: {display_value}")
        
        print("=" * 50)
    
    def update_config(self, key: str, value: str):
        """Update a configuration value"""
        try:
            # Read current config
            lines = []
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # Update or add the key
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{key}="):
                    lines[i] = f"{key}={value}\n"
                    updated = True
                    break
            
            if not updated:
                lines.append(f"{key}={value}\n")
            
            # Write back to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ Updated {key} = {value}")
            
            # Reload config
            self.config = self._load_config()
            
        except Exception as e:
            print(f"❌ Failed to update config: {e}")
    
    def interactive_setup(self):
        """Interactive SMTP setup"""
        print("🔧 Interactive SMTP Setup")
        print("=" * 50)
        
        # SMTP Server
        server = input(f"SMTP Server [{self.config.get('smtp_server', 'localhost')}]: ").strip()
        if server:
            self.update_config('smtp_server', server)
        
        # SMTP Port
        port = input(f"SMTP Port [{self.config.get('smtp_port', 587)}]: ").strip()
        if port:
            self.update_config('smtp_port', port)
        
        # Use TLS
        use_tls = input(f"Use TLS (y/n) [{'y' if self.config.get('smtp_use_tls', True) else 'n'}]: ").strip().lower()
        if use_tls in ['y', 'yes', 'n', 'no']:
            self.update_config('smtp_use_tls', 'true' if use_tls in ['y', 'yes'] else 'false')
        
        # Username
        username = input(f"SMTP Username [{self.config.get('smtp_username', '')}]: ").strip()
        if username:
            self.update_config('smtp_username', username)
        
        # Password
        password = input(f"SMTP Password: ").strip()
        if password:
            self.update_config('smtp_password', password)
        
        # Default sender
        sender = input(f"Default Sender Email [{self.config.get('mail_default_sender', 'noreply@hystory.id')}]: ").strip()
        if sender:
            self.update_config('mail_default_sender', sender)
        
        # Sender name
        sender_name = input(f"Sender Name [{self.config.get('mail_sender_name', 'HYstory.id')}]: ").strip()
        if sender_name:
            self.update_config('mail_sender_name', sender_name)
        
        print("\n✅ Configuration updated!")
        self.show_config()
        
        # Test connection
        test = input("\nTest connection now? (y/n): ").strip().lower()
        if test in ['y', 'yes']:
            self.test_connection()

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='SMTP Configuration Helper')
    parser.add_argument('--config', default='config/smtp_config.txt', help='SMTP config file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test connection
    subparsers.add_parser('test', help='Test SMTP connection')
    
    # Send test email
    test_email_parser = subparsers.add_parser('send-test', help='Send test email')
    test_email_parser.add_argument('email', help='Recipient email address')
    test_email_parser.add_argument('--subject', default='SMTP Test Email', help='Email subject')
    
    # Show config
    subparsers.add_parser('show', help='Show current configuration')
    
    # Update config
    update_parser = subparsers.add_parser('update', help='Update configuration value')
    update_parser.add_argument('key', help='Configuration key')
    update_parser.add_argument('value', help='Configuration value')
    
    # Interactive setup
    subparsers.add_parser('setup', help='Interactive SMTP setup')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    helper = SMTPConfigHelper(args.config)
    
    if args.command == 'test':
        helper.test_connection()
    elif args.command == 'send-test':
        helper.send_test_email(args.email, args.subject)
    elif args.command == 'show':
        helper.show_config()
    elif args.command == 'update':
        helper.update_config(args.key, args.value)
    elif args.command == 'setup':
        helper.interactive_setup()

if __name__ == '__main__':
    main()
