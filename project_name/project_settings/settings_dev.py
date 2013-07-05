import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG


DEVSERVER_MODULES = (
    #'devserver.modules.sql.SQLRealTimeModule',
    'devserver.modules.sql.SQLSummaryModule',
    'devserver.modules.profile.ProfileSummaryModule',

    # Modules not enabled by default
    #'devserver.modules.profile.MemoryUseModule',
    'devserver.modules.cache.CacheSummaryModule',
)

INSTALLED_APPS = (
    'devserver',
)

LOG_FILE = os.path.expanduser('~/Library/Logs/django/{{ project_name }}.log')

LOGGING = {
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'devlog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': LOG_FILE
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'INFO'
        },
        'south': {
            'level': 'INFO'
        },
        'requests': {
            'level': 'WARNING'
        }
    },
    'root': {
        'handlers': ['console', 'devlog'],
        'level': 'DEBUG',
    }
}

