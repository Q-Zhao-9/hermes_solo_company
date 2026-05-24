"""Outbound CRM connector package for Solo CRM."""
from .base import CRMConnector, NoopConnector
from .google_sheets import GoogleSheetsConnector
from .hubspot import HubSpotConnector

__all__ = ["CRMConnector", "NoopConnector", "GoogleSheetsConnector", "HubSpotConnector"]
