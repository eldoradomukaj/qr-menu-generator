from apiclient.discovery import build
from django.apps import AppConfig
from django.conf import settings
from oauth2client.service_account import ServiceAccountCredentials


class DashboardConfig(AppConfig):
    name = 'dashboard'

    def ready(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            settings.GCP_KEY, settings.GCP_SCOPES)
        self.analytics = build('analyticsreporting', 'v4', credentials=credentials)
        