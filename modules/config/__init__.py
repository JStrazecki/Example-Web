"""
Configuration module for modular application
"""

from .config_manager import ConfigManager, get_config_manager, reload_configuration

__all__ = ['ConfigManager', 'get_config_manager', 'reload_configuration']