import os
import logging
from typing import Optional, Tuple, Dict

from .work import Work
from .project import Project
from .exceptions import (BuffaloError, ConfigurationError, BuffaloFileNotFoundError, ProjectLoadError, ProjectSaveError)


class Buffalo:
    """
    Buffalo class is used to manage projects and workflow processing

    It is recommended not to keep an instance of this class for a long time, as it does not monitor file changes in the base_dir directory.
    After a period of work, please destroy the class instance and then reinstantiate it, or use the Buffalo.load_projects() method to reload projects.

    Usage:
     - Specify a base_dir as the root directory for project folders
     - Specify a wf_template_file as the template for project description files
     - After initialization, the Buffalo class instance will automatically load all existing projects from the base_dir directory
     - Workers get an unstarted job through the get_a_job method of the Buffalo class instance
      - If a job is obtained, a Project object and a Work object are returned
      - If a worker intends to start working, please call the update_work_status method of the Buffalo class instance to update
        the specified job's status to Work.IN_PROGRESS
      - If a worker completes the job, please call the update_work_status method to update the specified job's status to Work.DONE
      - If a worker fails, please call the update_work_status method to roll back the specified job's status to Work.NOT_STARTED
      - Each call to the update_work_status method will save the project file to the project folder
     - To create a new project, use the create_project method of the Buffalo class instance
      - If the project (or project directory) already exists, the project will be loaded and refreshed;
        even if loading fails, a new project will be created with the latest description file and overwrite the existing one without error
      - If the project directory doesn't exist, the project directory will be created, and a new project will be created 
        with the latest description file and saved
      - This operation will not interfere with any files in the project folder other than the project file
     - No method is provided to delete projects because it's unnecessary
      - It is recommended to remove completed projects from the base_dir directory through folder operations
    """

    WF_FILE_NAME = "wf.yml"

    def __init__(self, base_dir: str, template_path: str):
        """
        Initialize Buffalo instance
        
        :param base_dir: Project root directory
        :param template_path: Workflow template file path, defaults to "wf_template.yml" in current directory
        :raises BuffaloFileNotFoundError: If the template file does not exist
        :raises ConfigurationError: If the specified base_dir is not a directory
        """
        # Set workflow template file path
        self.template_path = template_path
        self.encoding = "utf-8"

        # Confirm if template_path exists
        if not os.path.exists(self.template_path):
            # If user-specified template doesn't exist, try to use the built-in template
            from . import get_template_path
            built_in_template = get_template_path()
            if os.path.exists(built_in_template):
                self.template_path = built_in_template
                logging.warning(f"User template '{template_path}' not found, using built-in template: {built_in_template}")
            else:
                raise BuffaloFileNotFoundError(f"Could not find project description file: {self.template_path}")

        # Confirm if base_dir exists, create it if not
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Confirm if base_dir is a directory
        if not os.path.isdir(base_dir):
            raise ConfigurationError(f"Specified base_dir is not a directory: {base_dir}, your Buffalo initialization failed")

        # Convert base_dir to absolute path
        self.base_dir = os.path.abspath(base_dir)

        # Initialize self.projects object, [project directory name, Project object]
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
        # Get first-level subdirectories under base_dir, iterate through each subdir, if there is a wf.yml file in the subdir, create a Project object
        for directory in os.listdir(self.base_dir):
            dir_full_path = os.path.join(self.base_dir, directory)
            if os.path.isdir(dir_full_path):
                if os.path.exists(os.path.join(dir_full_path, self.WF_FILE_NAME)):
                    logging.debug(f"Loading project from directory {dir_full_path}")
                    self.load_project(directory)

    def load_project(self, project_folder_name: str) -> Optional[Project]:
        """
        Load a project from the project directory into Buffalo

        :param project_folder_name: Project directory name (do not provide the path)
        :return: Project object or None if project cannot be loaded
        """
        # Check cache, return if exists
        if self.projects.get(project_folder_name, None):
            return self.projects[project_folder_name]

        # Project directory
        project_folder_path = os.path.join(self.base_dir, project_folder_name)

        # Confirm if project directory exists
        if not os.path.exists(project_folder_path):
            return None

        try:
            # Load project from project directory
            project = Project(self.template_path, encoding=self.encoding)
            project.load_saved_project(os.path.join(project_folder_path, self.WF_FILE_NAME), encoding=self.encoding)

            # Add project object to self.projects
            self.projects[project_folder_name] = project
            return project
        except (ProjectLoadError, BuffaloFileNotFoundError) as e:
            logging.error(f"Failed to load project from directory {project_folder_name}: {e}")
            return None

    def create_project(self, project_folder_name: str, project_name: str) -> Optional[Project]:
        """
        Create a new project. If the project already exists, it will load the project and refresh it.
        If the wf.yml file in the project directory cannot be loaded, a new project will be created and overwritten (the project will be reset).

        :param project_folder_name: Project folder name (do not provide the path)
        :param project_name: Project name
        :return: Project object or None if project cannot be created
        """
        project_folder_path = os.path.join(self.base_dir, project_folder_name)

        # Confirm if project folder name exists
        if os.path.exists(project_folder_path):
            try:
                # Try to load project
                project = self.load_project(project_folder_name)
                if project is not None:
                    # Successfully loaded
                    return project
                else:
                    # Folder exists but cannot load project, create new project and save
                    project = Project(self.template_path, name=project_name, encoding=self.encoding)
                    project.save_project(os.path.join(project_folder_path, self.WF_FILE_NAME), encoding=self.encoding)
                    self.projects[project_folder_name] = project

                    return project
            except (ProjectLoadError, ProjectSaveError) as e:
                logging.error(f"Failed to create/load project in directory {project_folder_name}: {e}")
                return None

        # Project folder doesn't exist, create project folder
        os.makedirs(project_folder_path)

        try:
            project = Project(self.template_path, name=project_name, encoding=self.encoding)
            project.save_project(os.path.join(project_folder_path, self.WF_FILE_NAME), encoding=self.encoding)
            self.projects[project_folder_name] = project

            return project
        except (ProjectSaveError, BuffaloFileNotFoundError) as e:
            logging.error(f"Failed to create project in directory {project_folder_name}: {e}")
            return None

    def get_a_job(self, job_name: str, without_check: bool = False) -> Tuple[Optional[str], Optional[Work]]:
        """
        Get a not started job with the specified name

        :param job_name: Job name (to match with the name field of Work)
        :param without_check: Whether to skip checking the status of previous works and directly return the first not started work matching the name
        :return: A not started work (project_folder_name, Work) matching job_name, returns (None, None) if not found
        """
        # Iterate through all projects, find a not started work
        for project_folder_name, project in self.projects.items():
            # If without_check=True, directly find the work by name, regardless of its status
            if without_check:
                for work in project.works:
                    if work.name == job_name:
                        return project_folder_name, work
            else:
                # Normal process, get the next not started work
                work, last_work_status = project.get_next_not_started_work()
                if work is not None and last_work_status is None:
                    if work.name == job_name:
                        return project_folder_name, work

        return None, None

    def update_work_status(self, project_folder_name: str, work: Work, status: str) -> None:
        """
        Update the status of the specified work

        :param project_folder_name: Project folder name
        :param work: Work object
        :param status: Work status
        :raises BuffaloFileNotFoundError: If the project folder does not exist
        :raises ProjectSaveError: If saving the project file fails
        """
        # Project folder path
        project_folder_path = os.path.join(self.base_dir, project_folder_name)

        # Confirm if project folder exists
        if not os.path.exists(project_folder_path):
            raise BuffaloFileNotFoundError(f"Project folder does not exist: {project_folder_path}")

        # Confirm if the project exists in the project dictionary, load project from file if not
        project = self.projects.get(project_folder_name, None)
        if project is None:
            project = Project(self.template_path, encoding=self.encoding)
            project.load_saved_project(os.path.join(project_folder_path, self.WF_FILE_NAME), encoding=self.encoding)
            self.projects[project_folder_name] = project

        # Confirm if work belongs to this project
        for w in project.works:
            if w.name == work.name:
                break
        else:
            # Don't update if not found
            return

        # Update work status
        work.set_status(status)

        # Save project to file
        project.save_project(os.path.join(project_folder_path, self.WF_FILE_NAME), encoding=self.encoding)
