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
SMTP Diagnostic Tool for LilyOpenCMS
Comprehensive testing and troubleshooting for email functionality
"""

import os
import sys
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_network_connectivity():
    """Test basic network connectivity to SMTP server"""
    print("🌐 Testing Network Connectivity...")

    config_file = "config/smtp_config.txt"
    smtp_server = "localhost"
    smtp_port = 587

    # Load config
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('smtp_server='):
                    smtp_server = line.split('=', 1)[1].strip()
                elif line.startswith('smtp_port='):
                    try:
                        smtp_port = int(line.split('=', 1)[1].strip())
                    except ValueError:
                        pass

    print(f"   Target: {smtp_server}:{smtp_port}")

    try:
        # Test DNS resolution
        ip = socket.gethostbyname(smtp_server)
        print(f"   DNS Resolution: ✅ {smtp_server} -> {ip}")

        # Test basic connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((smtp_server, smtp_port))
        sock.close()

        if result == 0:
            print(f"   Port Connectivity: ✅ Port {smtp_port} is open")
            return True
        else:
            print(f"   Port Connectivity: ❌ Port {smtp_port} is closed/filtered")
            return False

    except socket.gaierror as e:
        print(f"   DNS Resolution: ❌ Failed - {e}")
        return False
    except Exception as e:
        print(f"   Network Test: ❌ Error - {e}")
        return False

def test_smtp_connection():
    """Test SMTP connection with detailed diagnostics"""
    print("\n📧 Testing SMTP Connection...")

    config_file = "config/smtp_config.txt"
    config = {}

    # Load config
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.lower() in ('true', 'false'):
                        config[key] = value.lower() == 'true'
                    elif value.isdigit():
                        config[key] = int(value)
                    else:
                        config[key] = value

    print(f"   Server: {config.get('smtp_server', 'localhost')}")
    print(f"   Port: {config.get('smtp_port', 587)}")
    print(f"   TLS: {config.get('smtp_use_tls', True)}")
    print(f"   Username: {config.get('smtp_username', 'Not set')}")
    print(f"   Timeout: {config.get('smtp_timeout', 30)}s")

    try:
        # Create SMTP connection
        print("   Step 1: Connecting to SMTP server...")
        server = smtplib.SMTP(
            config.get('smtp_server', 'localhost'),
            config.get('smtp_port', 587),
            timeout=config.get('smtp_timeout', 30)
        )

        # Get server info
        print(f"   Server Response: {server.ehlo()[1].decode() if server.ehlo()[1] else 'No response'}")

        # Start TLS if required
        if config.get('smtp_use_tls', True):
            print("   Step 2: Starting TLS encryption...")
            server.starttls()
            print(f"   TLS Response: {server.ehlo()[1].decode() if server.ehlo()[1] else 'No response'}")

        # Authenticate if credentials provided
        if config.get('smtp_username') and config.get('smtp_password'):
            print("   Step 3: Authenticating...")
            server.login(
                config.get('smtp_username'),
                config.get('smtp_password')
            )
            print("   Authentication: ✅ Success")
        else:
            print("   Step 3: No authentication required")

        server.quit()
        print("   Connection Test: ✅ SUCCESS")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"   Authentication: ❌ FAILED - {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"   Connection: ❌ FAILED - {e}")
        return False
    except smtplib.SMTPHeloError as e:
        print(f"   HELO: ❌ FAILED - {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"   SMTP: ❌ FAILED - {e}")
        return False
    except OSError as e:
        print(f"   Network: ❌ FAILED - {e}")
        return False
    except Exception as e:
        print(f"   Unexpected Error: ❌ {e}")
        return False

def test_email_sending():
    """Test actual email sending"""
    print("\n📤 Testing Email Sending...")

    config_file = "config/smtp_config.txt"
    config = {}

    # Load config
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.lower() in ('true', 'false'):
                        config[key] = value.lower() == 'true'
                    elif value.isdigit():
                        config[key] = int(value)
                    else:
                        config[key] = value

    # Skip if suppressed
    if config.get('smtp_suppress_send', False):
        print("   Email sending is suppressed (testing mode)")
        return True

    # Get recipient email (handle non-interactive mode)
    try:
        recipient = input("   Enter recipient email address (or press Enter to skip): ").strip()
        if not recipient:
            print("   Skipping email send test")
            return True
    except EOFError:
        # Non-interactive mode - skip email sending test
        print("   Non-interactive mode detected, skipping email send test")
        return True

    print(f"   Sending test email to: {recipient}")

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config.get('mail_default_sender', 'test@lilyopencms.com')
        msg['To'] = recipient
        msg['Subject'] = f"SMTP Diagnostic Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = f"""
SMTP Diagnostic Test from LilyOpenCMS

This is a test email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you received this email, SMTP is working correctly!

Server: {config.get('smtp_server', 'localhost')}:{config.get('smtp_port', 587)}
TLS: {config.get('smtp_use_tls', True)}
Sender: {config.get('mail_default_sender', 'test@lilyopencms.com')}

Best regards,
LilyOpenCMS Diagnostic Tool
        """.strip()

        html_body = f"""
<html>
<body>
    <h1>SMTP Diagnostic Test</h1>
    <p>This is a test email sent at <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong></p>
    <p>If you received this email, <strong>SMTP is working correctly!</strong></p>

    <h3>Configuration:</h3>
    <ul>
        <li>Server: {config.get('smtp_server', 'localhost')}:{config.get('smtp_port', 587)}</li>
        <li>TLS: {config.get('smtp_use_tls', True)}</li>
        <li>Sender: {config.get('mail_default_sender', 'test@lilyopencms.com')}</li>
    </ul>

    <p>Best regards,<br>LilyOpenCMS Diagnostic Tool</p>
</body>
</html>
        """.strip()

        msg.attach(MIMEText(body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Send email
        print("   Connecting to SMTP server...")
        server = smtplib.SMTP(
            config.get('smtp_server', 'localhost'),
            config.get('smtp_port', 587),
            timeout=config.get('smtp_timeout', 30)
        )

        if config.get('smtp_use_tls', True):
            print("   Starting TLS...")
            server.starttls()

        if config.get('smtp_username') and config.get('smtp_password'):
            print("   Authenticating...")
            server.login(
                config.get('smtp_username'),
                config.get('smtp_password')
            )

        print("   Sending email...")
        server.sendmail(
            config.get('mail_default_sender', 'test@lilyopencms.com'),
            recipient,
            msg.as_string()
        )

        server.quit()
        print("   Email Send: ✅ SUCCESS")
        return True

    except Exception as e:
        print(f"   Email Send: ❌ FAILED - {e}")
        return False

def main():
    """Run comprehensive SMTP diagnostics"""
    print("🔧 LilyOpenCMS SMTP Diagnostic Tool")
    print("=" * 50)

    results = []

    # Test network connectivity
    results.append(("Network Connectivity", test_network_connectivity()))

    # Test SMTP connection
    results.append(("SMTP Connection", test_smtp_connection()))

    # Test actual email sending
    results.append(("Email Sending", test_email_sending()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Diagnostic Results:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20}: {status}")
        if result:
            passed += 1

    print("=" * 50)
    print(f"Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All diagnostics passed! SMTP is fully functional.")
    else:
        print("⚠️  Some issues detected. Check the output above for details.")

    print("\n📋 Troubleshooting Tips:")
    print("1. Network unreachable: Check firewall, DNS, and internet connectivity")
    print("2. Connection refused: Verify SMTP server and port are correct")
    print("3. Authentication failed: Check username/password credentials")
    print("4. TLS errors: Ensure SSL/TLS settings match server requirements")
    print("5. Port blocked: Contact hosting provider about SMTP port restrictions")

if __name__ == '__main__':
    main()
