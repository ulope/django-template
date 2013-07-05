USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = [
    '*'
]

RAVEN_CONFIG = {
    'dsn': '',
}

INSTALLED_APPS = (
    'gunicorn',
    'raven.contrib.django.raven_compat',
)

LOG_FILE = '/var/log/pythonapps/{{ project_name }}.log'

LOGGING = {
    'handlers': {
        'filelog': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            'filename': LOG_FILE,
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'requests': {
            'level': 'WARNING'
        }
    },
    'root': {
        'handlers': ['filelog', 'sentry'],
        'level': 'INFO',
    },
}
