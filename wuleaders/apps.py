"""
apps.py
Main app configuration file to connect with database

Last edited:
4.27.25 by Jenna - added additional documentation comments
"""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    """
    Configures app with name 'wuleaders'
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wuleaders'
