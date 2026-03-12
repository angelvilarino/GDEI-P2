"""
Services package for FIWARE Smart Store.
Provides a unified CRUD layer that dispatches to SQLite or Orion.
"""
from app.services import entity_service, orion_client

__all__ = ['entity_service', 'orion_client']
