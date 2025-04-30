"""Buffalo - A toolkit for quickly creating and managing projects"""

__version__ = "0.1.0"
__author__ = "Buffalo Team"
__email__ = "buffalo@example.com"
__copyright__ = "Copyright 2023 Buffalo Team"

import os
import pkg_resources
from pathlib import Path
import logging

# Import exceptions
from .exceptions import (
    BuffaloError,
    BuffaloFileNotFoundError,
    FileFormatError,
    ConfigError,
    CommandError,
    ProjectError,
    ValidationError,
    ConfigurationError,
    WorkflowError,
    WorkError,
    WorkStatusError,
    ProjectLoadError,
    ProjectSaveError,
    WorkflowFormatError,
    WorkflowDescriptionError
)

# Import utility functions
from .utils import (
    safe_load_yaml,
    dump_yaml,
    read_file,
    write_file,
    load_yaml_file,
    save_yaml_file
)

# Import other functions
from .work import Work
from .project import Project
from .buffalo import Buffalo

__all__ = [
    # Exception classes
    "BuffaloError",
    "BuffaloFileNotFoundError",
    "FileFormatError",
    "ConfigError",
    "CommandError",
    "ProjectError",
    "ValidationError",
    "ConfigurationError",
    "WorkflowError",
    "WorkError",
    "WorkStatusError",
    "ProjectLoadError",
    "ProjectSaveError",
    "WorkflowFormatError",
    "WorkflowDescriptionError",
    
    # Utility functions
    "safe_load_yaml",
    "dump_yaml",
    "read_file",
    "write_file",
    "load_yaml_file",
    "save_yaml_file",
    
    # Other functions
    "get_template_dir",
    "get_template_path",
    "Buffalo",
    "Work",
    "Project",
]

def get_template_dir() -> Path:
    """
    Get template folder path
    
    Returns:
        Path: Path object for the template folder
    """
    return Path(os.path.join(os.path.dirname(__file__), "templates"))

def get_template_path() -> str:
    """
    获取默认模板文件路径
    
    Returns:
        str: 默认模板文件的路径
    """
    template_dir = get_template_dir()
    return str(template_dir / "wf_template.yml") 