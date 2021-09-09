from django.conf import settings
from django.test.runner import DiscoverRunner

class CustomTestSuiteRunner(DiscoverRunner):
    """
    Used to override various settings when running tests.
    """
    def __init__(self, *args, **kwargs):
        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3',
            }
        }
        super(CustomTestSuiteRunner, self).__init__(*args, **kwargs)
