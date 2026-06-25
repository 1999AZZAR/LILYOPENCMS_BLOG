import os
from jinja2 import FileSystemLoader, TemplateNotFound
from flask import g

EXCLUDED_PREFIXES = ('admin_base', 'error.html', 'settings/', 'email/')


class DesignFileSystemLoader(FileSystemLoader):
    def get_source(self, environment, template):
        try:
            design = g.design
        except (RuntimeError, AttributeError):
            design = None

        if design and design != 'default' and not template.startswith(EXCLUDED_PREFIXES):
            design_template = os.path.join('designs', design, template).replace(os.sep, '/')
            try:
                source, filename, uptodate = super().get_source(environment, design_template)
                _design = design
                def _uptodate():
                    current = g.design if hasattr(g, 'design') else None
                    return uptodate() and current == _design
                return source, filename, _uptodate
            except TemplateNotFound:
                pass

        if design and design not in ('default', 'news') and not template.startswith(EXCLUDED_PREFIXES):
            news_fallback = os.path.join('designs', 'news', template).replace(os.sep, '/')
            try:
                source, filename, uptodate = super().get_source(environment, news_fallback)
                _design = 'news'
                def _uptodate():
                    current = g.design if hasattr(g, 'design') else None
                    return uptodate() and current == _design
                return source, filename, _uptodate
            except TemplateNotFound:
                pass

        return super().get_source(environment, template)
