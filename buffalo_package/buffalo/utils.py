"""
Buffalo Utility Module

Provides common utility functions, such as safe YAML handling and file operations
"""

from typing import Any, Dict

import yaml

from .exceptions import FileFormatError


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
        raise FileFormatError(f"Unable to parse YAML content: {e}") from e


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
        raise FileFormatError(f"Unable to convert to YAML string: {e}") from e


def read_file(file_path: str) -> str:
    """
    Read file content

    :param file_path: File path
    :return: File content
    :raises FileFormatError: If file cannot be read
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise FileFormatError(f"Cannot read file with utf-8 encoding: {file_path}") from e


def write_file(file_path: str, content: str) -> None:
    """
    Write content to file

    :param file_path: File path
    :param content: Content to write
    :raises FileFormatError: If file cannot be written
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise FileFormatError(f"Cannot write file: {file_path}") from e


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load YAML file

    :param file_path: YAML file path
    :return: YAML content
    :raises FileFormatError: If file cannot be read or parsed
    """
    content = read_file(file_path)
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise FileFormatError(f"Cannot parse YAML file: {file_path}") from e


def save_yaml_file(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save data to YAML file

    :param file_path: YAML file path
    :param data: Data to save
    :raises FileFormatError: If file cannot be written
    """
    yaml_content = yaml.dump(data, default_flow_style=False)
    write_file(file_path, yaml_content)
