"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Email Template Loader for LilyOpenCMS
Handles loading and rendering of email templates using Jinja2
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, Optional
from flask import current_app

class EmailTemplateLoader:
    """Email template loader using Jinja2"""

    def __init__(self, template_dir: str = "templates/emails"):
        self.template_dir = template_dir
        self.env = None
        self._initialized = False

    def init_app(self, app):
        """Initialize template loader with Flask app"""
        template_path = os.path.join(app.root_path, self.template_dir)
        self.env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self._initialized = True

    def _ensure_initialized(self):
        """Ensure template loader is initialized"""
        if not self._initialized:
            if hasattr(current_app, 'root_path'):
                self.init_app(current_app)
            else:
                raise RuntimeError("Template loader not initialized. Call init_app() first.")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with given context"""
        self._ensure_initialized()

        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            current_app.logger.error(f"Failed to render template {template_name}: {e}")
            raise

    def get_html_and_text(self, template_base: str, context: Dict[str, Any]) -> tuple[str, str]:
        """Get both HTML and plain text versions of a template"""
        html_template = f"{template_base}.html"
        text_template = f"{template_base}.txt"

        html_content = self.render_template(html_template, context)
        text_content = self.render_template(text_template, context)

        return html_content, text_content

# Global template loader instance
email_template_loader = EmailTemplateLoader()
