from fastapi import Depends
from app.config import settings

def get_settings():
    """
    Dependency that provides app settings.
    """
    return settings
