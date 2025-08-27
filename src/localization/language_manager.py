"""
Language Manager for DATASYNC Market Tool
Handles multi-language support and translations
"""

import json
import os
from typing import Dict, Any

class LanguageManager:
    def __init__(self):
        self.current_language = 'pt'  # Default: Portuguese
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        languages = ['pt', 'en', 'es']
        current_dir = os.path.dirname(__file__)
        
        for lang in languages:
            file_path = os.path.join(current_dir, f'{lang}.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            except FileNotFoundError:
                # If file doesn't exist, create basic structure
                self.translations[lang] = {}
    
    def set_language(self, language_code: str):
        """Set the current language"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get_language(self) -> str:
        """Get current language code"""
        return self.current_language
    
    def get_text(self, key: str, **kwargs) -> str:
        """Get translated text by key"""
        try:
            # Navigate through nested keys (e.g., "menu.main.title")
            keys = key.split('.')
            text = self.translations[self.current_language]
            
            for k in keys:
                text = text[k]
            
            # Format with parameters if provided
            if kwargs:
                text = text.format(**kwargs)
            
            return text
        except (KeyError, TypeError):
            # Fallback to English, then to key itself
            try:
                if self.current_language != 'en':
                    keys = key.split('.')
                    text = self.translations['en']
                    for k in keys:
                        text = text[k]
                    if kwargs:
                        text = text.format(**kwargs)
                    return text
            except:
                pass
            
            return key  # Return key if no translation found
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their names"""
        return {
            'pt': 'Português',
            'en': 'English', 
            'es': 'Español'
        }

# Global instance
_language_manager = LanguageManager()

def get_text(key: str, **kwargs) -> str:
    """Global function to get translated text"""
    return _language_manager.get_text(key, **kwargs)

def set_language(language_code: str) -> bool:
    """Global function to set language"""
    return _language_manager.set_language(language_code)

def get_language() -> str:
    """Global function to get current language"""
    return _language_manager.get_language()

def get_available_languages() -> Dict[str, str]:
    """Global function to get available languages"""
    return _language_manager.get_available_languages()
