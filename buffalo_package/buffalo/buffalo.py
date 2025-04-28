import logging
from typing import Optional, Tuple, Dict
from pathlib import Path

from .work import Work
from .project import Project
from .exceptions import (BuffaloError, ConfigurationError, BuffaloFileNotFoundError, ProjectLoadError, ProjectSaveError)


class Buffalo:
    """
    Buffalo class is used to manage projects and workflow processing.

    It is recommended not to keep an instance of this class for a long time, as it does not monitor file changes in the base_dir directory.
    After a period of work, please destroy the class instance and then reinstantiate it, or use the Buffalo.load_projects() method to reload projects.
    """

    WF_FILE_NAME = "workflow.yml"
    WF_DESCRIPTION_FILE_NAME = "workflow_description.yml"

    def __init__(self, base_dir: Path, template_path: Path):
        """
        Initialize Buffalo instance
        
        :param base_dir: Project root directory
        :param template_path: Workflow template file path
        :raises BuffaloFileNotFoundError: If the template file does not exist
        :raises ConfigurationError: If the specified base_dir is not a directory
        """
        # Set workflow template file path
        self.template_path = template_path
        self.base_dir = base_dir

        # Confirm if template_path exists
        if not self.template_path.exists():
            # If user-specified template doesn't exist, try to use the built-in template
            from . import get_template_path
            built_in_template = Path(get_template_path())
            if built_in_template.exists():
                self.template_path = built_in_template
                logging.warning(f"User template '{template_path}' not found, using built-in template: {built_in_template}")
            else:
                raise BuffaloFileNotFoundError(f"Could not find project description file: {self.template_path}")

        # Confirm if base_dir exists, create it if not
        if not self.base_dir.exists():
            self.base_dir.mkdir(parents=True)

        # Confirm if base_dir is a directory
        if not self.base_dir.is_dir():
            raise ConfigurationError(f"Specified base_dir is not a directory: {self.base_dir}")

        # Initialize self.projects object, [project name, Project object]
        self.projects: Dict[str, Project] = {}

        logging.info(f"Loading projects from directory {self.base_dir}")
        try:
            self.load_projects()
            logging.info(f"Successfully loaded {len(self.projects)} projects from directory {self.base_dir}")
        except BuffaloError as e:
            logging.error(f"Failed to load projects from directory {self.base_dir}: {e}")

    def load_projects(self) -> None:
        """
        Load all existing projects from the base_dir directory into Buffalo
        """
        logging.debug(f"Starting to scan {self.base_dir}")
        # Get first-level subdirectories under base_dir
        for directory in self.base_dir.iterdir():
            if directory.is_dir():
                if (directory / self.WF_FILE_NAME).exists():
                    logging.debug(f"Loading project from directory {directory}")
                    self.load_project(directory.name)

    def load_project(self, project_name: str) -> Optional[Project]:
        """
        Load a project from the project directory into Buffalo

        :param project_name: Project name
        :return: Project object or None if project cannot be loaded
        """
        # Check cache, return if exists
        if project_name in self.projects:
            return self.projects[project_name]

        # Load project
        project = Project.load(project_name, self.base_dir)
        if project:
            self.projects[project_name] = project
        return project

    def create_project(self, project_name: str) -> Optional[Project]:
        """
        Create a new project. If the project already exists, it will load the project and refresh it.
        If the project file cannot be loaded, a new project will be created and overwritten.

        :param project_name: Project name (will be used as folder name)
        :return: Project object or None if project cannot be created
        """
        try:
            # Try to load existing project first
            project = self.load_project(project_name)
            if project:
                return project

            # Create new project
            project = Project(project_name, self.base_dir, self.template_path)
            self.projects[project_name] = project
            return project
        except (ProjectLoadError, ProjectSaveError, ConfigurationError) as e:
            logging.error(f"Failed to create project {project_name}: {e}")
            return None

    def get_a_job(self, job_name: str, without_check: bool = False) -> Tuple[Optional[str], Optional[Work]]:
        """
        Get a not started job with the specified name

        :param job_name: Job name (to match with the name field of Work)
        :param without_check: Whether to skip checking the status of previous works
        :return: A tuple of (project_name, Work) matching job_name, returns (None, None) if not found
        """
        # Iterate through all projects, find a not started work
        for project_name, project in self.projects.items():
            work = project.get_work_by_name(job_name, without_check)
            if work:
                return project_name, work
        return None, None

    def update_work_status(self, project_name: str, work: Work, status: str) -> None:
        """
        Update the status of the specified work

        :param project_name: Project name
        :param work: Work object
        :param status: Work status
        :raises BuffaloFileNotFoundError: If the project does not exist
        :raises ProjectSaveError: If saving the project file fails
        """
        # Get project
        project = self.projects.get(project_name)
        if not project:
            project = self.load_project(project_name)
            if not project:
                raise BuffaloFileNotFoundError(f"Project does not exist: {project_name}")

        # Update work status
        project.update_work_status(work, status)

    def save_project(self, project: Project, project_name: str) -> None:
        """
        Save a project

        :param project: Project object
        :param project_name: Project name
        :raises ProjectSaveError: If saving the project file fails
        """
        project_folder_path = self.base_dir / project_name
        project_folder_path.mkdir(exist_ok=True)

        project.save_project()
