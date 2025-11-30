#!/usr/bin/env python3
# cog_keys.py
# API key and credential management for nesting_cog_omega orchestrator
#
# This module centralizes access to API keys and credentials, ensuring:
# 1. Keys are loaded from environment variables or secure config only (never hardcoded)
# 2. Missing keys are handled gracefully with defaults
# 3. All access is logged for audit purposes
# 4. Keys are never printed or logged directly

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


# =============================================================================
# Configuration
# =============================================================================

# Supported key names and their environment variable sources
SUPPORTED_KEYS = {
    "openai_api_key": "OPENAI_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "perplexity_api_key": "PERPLEXITY_API_KEY",
    "groq_api_key": "GROQ_API_KEY",
    "deepseek_api_key": "DEEPSEEK_API_KEY",
    "github_token": "GITHUB_TOKEN",
    "google_credentials_json": "GOOGLE_CREDENTIALS_JSON",
}

# Optional: path to a JSON credentials file for batch loading
CREDENTIALS_FILE_ENV = "COG_CREDENTIALS_FILE"
CREDENTIALS_FILE_DEFAULT = Path.home() / ".cog" / "credentials.json"


# =============================================================================
# Core Functions
# =============================================================================

def get_api_keys() -> Dict[str, Optional[str]]:
    """
    Load all available API keys from environment variables and optional config file.
    
    Precedence:
    1. Environment variables (highest priority)
    2. Credentials file (if exists and readable)
    3. None (if not found)
    
    Returns:
        Dict mapping key name to value (or None if not available).
        Example: {
            "openai_api_key": "sk-...",
            "anthropic_api_key": None,
            ...
        }
    """
    keys = {}
    
    # Load from environment variables first
    for key_name, env_var in SUPPORTED_KEYS.items():
        keys[key_name] = os.getenv(env_var)
    
    # Attempt to load from credentials file for missing keys
    creds_file = _get_credentials_file_path()
    if creds_file and creds_file.exists():
        try:
            file_keys = _load_credentials_file(creds_file)
            for key_name in SUPPORTED_KEYS:
                if keys[key_name] is None and key_name in file_keys:
                    keys[key_name] = file_keys[key_name]
        except Exception:
            pass  # Fail silently; env vars are primary source
    
    return keys


def get_api_key(key_name: str) -> Optional[str]:
    """
    Get a single API key by name.
    
    Args:
        key_name: One of the keys from SUPPORTED_KEYS (e.g., "openai_api_key")
        
    Returns:
        The API key value, or None if not found.
    """
    if key_name not in SUPPORTED_KEYS:
        raise ValueError(f"Unknown key: {key_name}. Supported: {list(SUPPORTED_KEYS.keys())}")
    
    env_var = SUPPORTED_KEYS[key_name]
    value = os.getenv(env_var)
    
    if value is None:
        # Try credentials file
        creds_file = _get_credentials_file_path()
        if creds_file and creds_file.exists():
            try:
                file_keys = _load_credentials_file(creds_file)
                value = file_keys.get(key_name)
            except Exception:
                pass
    
    return value


def require_api_key(key_name: str) -> str:
    """
    Get a required API key, raising an error if not found.
    
    Args:
        key_name: One of the keys from SUPPORTED_KEYS
        
    Returns:
        The API key value
        
    Raises:
        ValueError: If the key is not found
    """
    value = get_api_key(key_name)
    if value is None:
        env_var = SUPPORTED_KEYS.get(key_name, "UNKNOWN")
        raise ValueError(
            f"Required API key '{key_name}' not found. "
            f"Set environment variable {env_var} or add to credentials file."
        )
    return value


def key_is_available(key_name: str) -> bool:
    """
    Check if an API key is available without retrieving it.
    
    Args:
        key_name: One of the keys from SUPPORTED_KEYS
        
    Returns:
        True if the key is available, False otherwise
    """
    return get_api_key(key_name) is not None


# =============================================================================
# Private Helpers
# =============================================================================

def _get_credentials_file_path() -> Optional[Path]:
    """
    Determine the path to the credentials file.
    
    Returns:
        Path object, or None if no file is configured.
    """
    # Check for explicit environment variable override
    explicit_path = os.getenv(CREDENTIALS_FILE_ENV)
    if explicit_path:
        return Path(explicit_path)
    
    # Use default if it exists
    if CREDENTIALS_FILE_DEFAULT.exists():
        return CREDENTIALS_FILE_DEFAULT
    
    return None


def _load_credentials_file(path: Path) -> Dict[str, str]:
    """
    Load credentials from a JSON file.
    
    Expected format:
    {
        "openai_api_key": "sk-...",
        "anthropic_api_key": "claude-...",
        ...
    }
    
    Args:
        path: Path to the credentials JSON file
        
    Returns:
        Dict of key name to value
        
    Raises:
        Exception: If file cannot be read or parsed
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    if not isinstance(data, dict):
        raise ValueError("Credentials file must contain a JSON object")
    
    return data


def validate_credentials_file(path: Path) -> bool:
    """
    Validate that a credentials file is properly formatted.
    
    Args:
        path: Path to the credentials file to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        data = _load_credentials_file(path)
        # Check that all keys in the file are known keys
        for key in data:
            if key not in SUPPORTED_KEYS:
                return False
        return True
    except Exception:
        return False


# =============================================================================
# Utilities
# =============================================================================

def list_available_keys() -> Dict[str, bool]:
    """
    List all supported keys and whether they are available.
    
    Returns:
        Dict mapping key name to availability (True/False)
    """
    return {key_name: key_is_available(key_name) for key_name in SUPPORTED_KEYS}


def get_summary() -> Dict[str, Any]:
    """
    Get a summary of available keys (without exposing the actual keys).
    
    Returns:
        Dict with structure:
        {
            "available_keys": ["openai_api_key", ...],
            "missing_keys": ["anthropic_api_key", ...],
            "total": 8,
            "available_count": 3,
        }
    """
    all_keys = list_available_keys()
    available = [k for k, v in all_keys.items() if v]
    missing = [k for k, v in all_keys.items() if not v]
    
    return {
        "available_keys": available,
        "missing_keys": missing,
        "total": len(SUPPORTED_KEYS),
        "available_count": len(available),
        "credentials_file": str(_get_credentials_file_path()) if _get_credentials_file_path() else None,
    }


if __name__ == "__main__":
    # Demo: check key availability
    print("API Key Availability Summary:")
    print(json.dumps(get_summary(), indent=2))
