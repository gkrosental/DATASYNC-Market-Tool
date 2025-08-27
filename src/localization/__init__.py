"""
Localization module for DATASYNC Market Tool
Supports multiple languages: Portuguese, English, Spanish
"""

from .language_manager import LanguageManager, get_text, set_language, get_language, get_available_languages

__all__ = ['LanguageManager', 'get_text', 'set_language', 'get_language', 'get_available_languages']
