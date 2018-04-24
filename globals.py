import json
import logging
import sys

__all__ = ['get_config', 'get_logger']
_name_to_level = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}
try:
    with open('config.json') as f:
        config = json.load(f)
    level = _name_to_level.get(config['logging_level'])
    if not level:
        sys.stderr.write('Unrecognized logging level: %s\n' % config['logging_level'])
        sys.exit(1)
    logger = logging.Logger('bus_bot')
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
except json.JSONDecodeError:
    sys.stderr.write('Invalid config\n')
    sys.exit(1)
except FileNotFoundError:
    sys.stderr.write('Configuration file not found\n')
    sys.exit(1)


def get_config():
    return config


def get_logger():
    return logger
