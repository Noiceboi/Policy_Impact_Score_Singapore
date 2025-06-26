"""
Logging configuration for the Policy Impact Assessment Framework.

This module provides centralized logging configuration with appropriate
handlers, formatters, and log levels for the entire framework.
"""

import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Default logging configuration
DEFAULT_LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(funcName)s %(lineno)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/policy_assessment.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        'policy_impact': {
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'error_file'],
            'propagate': False
        },
        'policy_impact.models': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': True
        },
        'policy_impact.mcda': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': True
        },
        'policy_impact.validation': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': True
        }
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console']
    }
}


def setup_logging(
    config_path: str = None,
    log_level: str = 'INFO',
    log_dir: str = 'logs'
) -> logging.Logger:
    """
    Set up logging configuration for the framework.
    
    Args:
        config_path: Path to logging configuration file (JSON/YAML)
        log_level: Default logging level
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Update file paths in config
    config = DEFAULT_LOGGING_CONFIG.copy()
    config['handlers']['file']['filename'] = str(log_path / 'policy_assessment.log')
    config['handlers']['error_file']['filename'] = str(log_path / 'errors.log')
    
    # Load custom config if provided
    if config_path and Path(config_path).exists():
        if config_path.endswith('.json'):
            import json
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
        elif config_path.endswith(('.yml', '.yaml')):
            import yaml
            with open(config_path, 'r') as f:
                custom_config = yaml.safe_load(f)
        else:
            raise ValueError("Config file must be JSON or YAML format")
        
        config.update(custom_config)
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get main logger
    logger = logging.getLogger('policy_impact')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Add system info to initial log
    logger.info("=" * 50)
    logger.info("Policy Impact Assessment Framework - Logging Started")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Log level: {log_level.upper()}")
    logger.info("=" * 50)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger('policy_impact')
    
    # Ensure name starts with policy_impact
    if not name.startswith('policy_impact'):
        if name == '__main__':
            name = 'policy_impact.main'
        else:
            name = f'policy_impact.{name}'
    
    return logging.getLogger(name)


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        logger.debug(f"Entering {func.__name__} with args={args}, kwargs={kwargs}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log success
            logger.debug(f"Completed {func.__name__} in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log error
            logger.error(f"Error in {func.__name__} after {execution_time:.3f}s: {str(e)}")
            raise
    
    return wrapper


def log_performance(operation: str, start_time: float, logger: logging.Logger = None):
    """
    Log performance metrics for operations.
    
    Args:
        operation: Name of the operation
        start_time: Start time from time.time()
        logger: Logger instance (optional)
    """
    if logger is None:
        logger = get_logger()
    
    import time
    duration = time.time() - start_time
    
    if duration < 1:
        logger.info(f"{operation} completed in {duration*1000:.1f}ms")
    else:
        logger.info(f"{operation} completed in {duration:.2f}s")


# Context manager for logging blocks
class LogContext:
    """Context manager for logging operation blocks."""
    
    def __init__(self, operation: str, logger: logging.Logger = None, level: str = 'INFO'):
        self.operation = operation
        self.logger = logger or get_logger()
        self.level = getattr(logging, level.upper())
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.log(self.level, f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.log(self.level, f"Completed {self.operation} in {duration:.2f}s")
        else:
            self.logger.error(f"Failed {self.operation} after {duration:.2f}s: {exc_val}")
        
        return False  # Don't suppress exceptions


# Initialize logging when module is imported
_logger = setup_logging()
