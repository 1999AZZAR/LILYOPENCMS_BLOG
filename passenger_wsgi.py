"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

import sys
import os

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment to prevent Flask from starting development server
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app object from main.py
from main import app

# Define the WSGI application object
application = app

# Prevent running the development server when imported
if __name__ == "__main__":
    print("This is a WSGI file for production servers.")
    print("Use 'python main.py' to run the development server.")
    print("Use 'flask run' to run with Flask CLI.")
    sys.exit(0)
