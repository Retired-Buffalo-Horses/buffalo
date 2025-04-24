"""
Buffalo Exception Class Definition Module
"""


class BuffaloError(Exception):
    """Buffalo Base Exception Class"""


class BuffaloFileNotFoundError(BuffaloError):
    """File Not Found Exception"""


class FileFormatError(BuffaloError):
    """File Format Error Exception"""


class ConfigError(BuffaloError):
    """Configuration Error Exception"""


class CommandError(BuffaloError):
    """Command Execution Error Exception"""


class ProjectError(BuffaloError):
    """Project Related Error Exception"""


class ValidationError(BuffaloError):
    """Data Validation Error Exception"""


class ConfigurationError(BuffaloError):
    """Configuration Related Error"""


class WorkflowError(BuffaloError):
    """Workflow Error"""


class WorkError(BuffaloError):
    """Work Related Error"""


class WorkStatusError(WorkError):
    """Work Status Error"""


class ProjectLoadError(ProjectError):
    """Project Loading Error"""


class ProjectSaveError(ProjectError):
    """Project Saving Error"""


class WorkflowFormatError(FileFormatError):
    """Workflow File Format Error"""


class WorkflowDescriptionError(WorkflowError):
    """Workflow Description Error""" 