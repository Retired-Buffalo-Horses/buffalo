"""
Buffalo Utility Module

Provides common utility functions, such as safe YAML handling and file operations
"""
import yaml
from typing import Any, Dict, TextIO, Optional, Union
import os
from pathlib import Path

from .exceptions import FileFormatError, BuffaloFileNotFoundError


def safe_load_yaml(yaml_string: str) -> Dict[str, Any]:
    """
    Safely load YAML string

    Args:
        yaml_string: YAML format string

    Returns:
        Parsed YAML content
    """
    try:
        return yaml.safe_load(yaml_string) or {}
    except yaml.YAMLError as e:
        raise FileFormatError(f"Unable to parse YAML content: {e}")


def dump_yaml(data: Dict[str, Any]) -> str:
    """
    Convert data to YAML string

    Args:
        data: Data to convert

    Returns:
        YAML format string
    """
    try:
        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    except yaml.YAMLError as e:
        raise FileFormatError(f"Unable to convert to YAML string: {e}")


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read file content

    Args:
        file_path: File path
        encoding: File encoding, default is utf-8

    Returns:
        File content
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except OSError as e:
        if isinstance(e, FileNotFoundError):  # Built-in FileNotFoundError
            raise BuffaloFileNotFoundError(f"File does not exist: {file_path}")
        raise FileFormatError(f"Error reading file: {e}")
    except UnicodeDecodeError:
        raise FileFormatError(f"Cannot read file with {encoding} encoding: {file_path}")
    except Exception as e:
        raise FileFormatError(f"Error reading file: {e}")


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """
    Write file content

    Args:
        file_path: File path
        content: Content to write
        encoding: File encoding, default is utf-8
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise FileFormatError(f"Error writing file: {e}")


def load_yaml_file(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    Load YAML file

    Args:
        file_path: File path
        encoding: File encoding, default is utf-8

    Returns:
        Parsed YAML content
    """
    content = read_file(file_path, encoding)
    return safe_load_yaml(content)


def save_yaml_file(file_path: str, data: Dict[str, Any], encoding: str = "utf-8") -> None:
    """
    Save data to YAML file

    Args:
        file_path: File path
        data: Data to save
        encoding: File encoding, default is utf-8
    """
    yaml_content = dump_yaml(data)
    write_file(file_path, yaml_content, encoding) 