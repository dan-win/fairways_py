INSTALLED_APPS = [
    "examples.dummy_pool",
]

# ENTRYPOINTS = "pools.entries"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,    
    "handlers": {
        "console": {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'            
        },
        "rmq": {
			'level': 'DEBUG',
			'class': 'python_logging_rabbitmq.RabbitMQHandler',
			'host': 'localhost',
			'port': 5672,
			'username': 'guest',
			'password': 'guest',
			'exchange': 'log',
			'declare_exchange': False,
			'connection_params': {
				'virtual_host': '/',
				'connection_attempts': 3,
				'socket_timeout': 5000
			},
			'fields': {
				'source': 'MainAPI',
				'env': 'production'
			},
			'fields_under_root': True            
        }
    },

    "formatters": {
        "standard": {
            "format": "%(levelname)-8s %(asctime)s %(message)s"
        },
        "color": {
            "()": "api.helpers.ColoredFormatterFactory",
            "format_template": "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
            "datefmt": None,
            "reset": True,
            "log_colors": {
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            "secondary_log_colors": {},
            "style": '%'
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "formatter": "standard"
        },
        "app": {
            "handlers": ["console"],
            "level": "DEBUG",
            "formatter": "color"
        },
        "rmq": {
            "handlers": ["rmq"]
        }
    }

}