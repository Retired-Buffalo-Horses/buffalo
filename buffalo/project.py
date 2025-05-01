import logging
from pathlib import Path
from typing import Optional, List, Tuple
import shutil

from .work import Work
from .exceptions import (ProjectLoadError, ProjectSaveError, BuffaloFileNotFoundError, WorkflowFormatError, ConfigurationError)
from .utils import load_yaml_file, save_yaml_file


class Project:
    """
    Project class is used to describe a project, including project folder name and project description file path.

    Please use the Buffalo class to create and operate the Project class
    """

    LAST_WORK_IN_PROGRESS = "last_work_in_progress"
    WORKFLOW_FILE_NAME = "buffalo.yml"

    def __init__(self, folder_name: str, base_dir: Path, template_path: Optional[Path] = None):
        """
        Initialize a new Project class.

        :param folder_name: Project folder name (must be a valid folder name)
        :param base_dir: Project base directory
        :param template_path: Template file path, optional for loading existing projects
        :raises ConfigurationError: If the project folder name is not a valid folder name
        :raises ProjectSaveError: If saving the project file fails
        """
        # Initialize basic attributes
        self.folder_name: str = ""
        self.works: List[Work] = []
        self.project_path: Optional[Path] = None
        self.template_path: Optional[Path] = template_path

        # Validate project folder name first
        if not self._is_valid_folder_name(folder_name):
            raise ConfigurationError(f"Invalid project folder name: {folder_name}. Project folder name must be a valid folder name.")

        # Set project folder name and path after validation
        self.folder_name = folder_name
        if base_dir:
            self.project_path = base_dir / folder_name

        # Load workflow description if template_path is provided
        if template_path and self.project_path:
            # Create project directory if it doesn't exist
            self.project_path.mkdir(parents=True, exist_ok=True)

            self._load_yaml_file(template_path)

            # Save project file
            self.save_project()

    @classmethod
    def load(cls, folder_name: str, base_dir: Path) -> Optional['Project']:
        """
        Load an existing project.

        :param folder_name: Project folder name
        :param base_dir: Project base directory
        :return: Project object or None if project cannot be loaded
        """
        project_path = base_dir / folder_name

        if not project_path.exists():
            return None

        try:
            # Create project instance without template_path
            project = cls(folder_name, base_dir)

            # Load saved project
            saved_project_file_path = project.project_path / project.WORKFLOW_FILE_NAME
            project._load_yaml_file(saved_project_file_path, require_folder_name=True)
            return project
        except (ProjectLoadError, BuffaloFileNotFoundError) as e:
            logging.error(f"Failed to load project {folder_name}: {e}")
            return None

    def get_work_by_name(self, work_name: str, without_check: bool = False) -> Optional[Work]:
        """
        Get a work by name.

        This method has two modes of operation:
        1. When without_check=True, it directly searches for a work by name without considering work status
        2. When without_check=False, it checks the next not started work and verifies if its name matches
           If the previous work is not completed, it will return None

        :param work_name: Name of the work to find
        :param without_check: Whether to skip checking the status of previous works
        :return: Work object if found, None otherwise
        """
        if without_check:
            # Directly find work by name
            for work in self.works:
                if work.name == work_name:
                    return work
        else:
            # Get next not started work
            work = self.get_next_not_started_work()
            if work is not None and work.name == work_name:
                return work
        return None

    def update_work_status(self, work: Work, status: str) -> None:
        """
        Update work status and save project.

        :param work: Work object to update
        :param status: New status
        :raises ProjectSaveError: If saving the project file fails
        """
        # Verify work belongs to this project
        if not any(w.name == work.name for w in self.works):
            return

        # Update status
        work.set_status(status)

        # Save project
        if self.project_path:
            self.save_project()

    @staticmethod
    def _is_valid_folder_name(name: str) -> bool:
        """
        Check if the project folder name is a valid folder name

        :param name: Project folder name to check
        :return: True if the name is valid, False otherwise
        """
        # Check if name is None or empty
        if not name or not name.strip():
            return False

        # Check if name contains invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in name for char in invalid_chars):
            return False

        # Check if name starts or ends with a dot or space
        if name.startswith('.') or name.endswith('.') or name.startswith(' ') or name.endswith(' '):
            return False

        # Check if name is too long (Windows has a 255 character limit for paths)
        if len(name) > 255:
            return False

        return True

    def _process_yaml_workflow(self, yaml_data: dict, file_path: Path, require_folder_name: bool = False) -> None:
        """
        Validate YAML file structure and process works.

        :param yaml_data: YAML data to validate
        :param file_path: Path of the YAML file (for error messages)
        :param require_folder_name: Whether this is a project file (True) or workflow file (False)
        :raises WorkflowFormatError: If workflow file structure is invalid
        :raises ProjectLoadError: If project file structure is invalid
        """
        error_class = ProjectLoadError if require_folder_name else WorkflowFormatError

        # Validate YAML structure
        if "workflow" not in yaml_data:
            raise error_class(f"Specified file {file_path} does not contain the workflow field")

        yml_workflow = yaml_data["workflow"]

        if "works" not in yml_workflow:
            raise error_class(f"Specified file {file_path} does not contain the works field")

        # Process works
        work_count = 0
        for work in yml_workflow["works"]:
            if "name" not in work:
                raise error_class("Missing name field in work")
            if "status" not in work:
                raise error_class(f"Missing status field in work {work['name']}")
            if "comment" not in work:
                raise error_class(f"Missing comment field in work {work['name']}")
            if "index" not in work:
                raise error_class(f"Missing index field in work {work['name']}")
            try:
                index = int(work["index"])
            except (ValueError, TypeError) as e:
                raise error_class(f"Invalid index value in work {work['name']}: {work['index']}. Index must be an integer.") from e
            work_count += 1
            # Create Work object
            work_obj = Work(
                index=index,
                name=work["name"],
                comment=work["comment"],
            )
            if "status" in work:
                work_obj.set_status(work["status"])
            self.works.append(work_obj)

        # Sort works by index
        self.works.sort(key=lambda x: x.index)

    def _load_yaml_file(self, file_path: Path, require_folder_name: bool = False) -> None:
        """
        Load and process a YAML file.

        :param file_path: Path to the YAML file
        :param require_folder_name: Whether to require and process folder_name field
        :raises WorkflowFormatError: If loading or processing the workflow file fails
        :raises ProjectLoadError: If loading or processing the project file fails
        :raises BuffaloFileNotFoundError: If the file does not exist
        """
        if not file_path.exists():
            raise BuffaloFileNotFoundError(f"Specified file does not exist: {file_path}")

        try:
            # Load YAML file
            yaml_data = load_yaml_file(str(file_path))

            # Process folder_name if required
            if require_folder_name:
                if "folder_name" not in yaml_data:
                    raise ProjectLoadError(f"File {file_path} does not contain the folder_name field")
                self.folder_name = yaml_data["folder_name"]

            # Process YAML workflow
            self._process_yaml_workflow(yaml_data, file_path, require_folder_name)

        except Exception as e:
            if isinstance(e, (WorkflowFormatError, ProjectLoadError, BuffaloFileNotFoundError)):
                raise
            raise (WorkflowFormatError if not require_folder_name else ProjectLoadError)(f"Failed to parse file {file_path}: {e}") from e

    def _load_saved_project(self) -> None:
        """
        Load project from a saved project file

        :raises ProjectLoadError: If loading the project file fails
        """
        if not self.project_path:
            raise ProjectLoadError("Project path not set")

        saved_project_file_path = self.project_path / self.WORKFLOW_FILE_NAME
        self._load_yaml_file(saved_project_file_path, require_folder_name=True)

    def save_project(self):
        """
        Save project to file

        :raises ProjectSaveError: If saving the project file fails
        """
        if not self.project_path:
            raise ProjectSaveError("Project path not set")

        # Organize data
        works_dict = []
        for work in self.works:
            works_dict.append({
                "name": work.name,
                "status": work.status,
                "comment": work.comment,
                "index": work.index,
            })

        # Use utility function to save YAML file
        try:
            save_yaml_file(str(self.project_path / self.WORKFLOW_FILE_NAME), {"folder_name": self.folder_name, "workflow": {"works": works_dict}})
        except Exception as e:
            raise ProjectSaveError(f"Failed to save project file: {e}") from e

    def get_current_work(self) -> Optional[Work]:
        """
        Returns the current work

        :return: Current work; if current work doesn't exist, returns None
        """
        for work in self.works:
            if work.is_in_progress():
                return work
        return None

    def get_next_not_started_work(self, without_check: bool = False) -> Optional[Work]:
        """
        Returns the next not started work

        This method has two modes of operation:
        1. When without_check=True, it directly returns the next not started work without checking the status of previous works
        2. When without_check=False, it checks the status of previous works and returns the next not started work

        :param without_check: Whether to skip checking the status of previous works
        :return: Returns the next not started work; if no such work exists, returns None
        """
        # Return the next not started work
        is_last_work_done = True

        for work in self.works:
            if work.is_not_started():
                if without_check:
                    # Just return the current work
                    return work
                else:
                    # Should check if the last work is done
                    if is_last_work_done:
                        # done, or this is the first work of the project
                        return work
                    else:
                        return None

            # Assign the is_done status of current work to is_last_work_done
            is_last_work_done = work.is_done()

        return None

    def is_all_done(self) -> bool:
        """
        Check if all works are done

        :return: True if all works are done, False otherwise
        """
        # Check if all works are done
        for work in self.works:
            if not work.is_done():
                return False
        return True

    def __str__(self) -> str:
        output = f"""Project:
        folder_name={self.folder_name}
            workflow:
                works:\n"""
        for work in self.works:
            output += f"            {work}\n"
        return output

    def copy_to_project(self, source_path: Path, target_name: Optional[str] = None) -> None:
        """
        Copy a file or directory to the project directory

        :param source_path: Path of the source file or directory
        :param target_name: Optional custom name for the target file or directory
        :raises FileNotFoundError: If the source file or directory does not exist
        :raises PermissionError: If there are insufficient permissions for the copy operation
        :raises ValueError: If the target name is invalid
        """
        if not self.project_path:
            raise ProjectLoadError("Project path not set")

        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        # Ensure project directory exists
        self.project_path.mkdir(parents=True, exist_ok=True)

        # Use custom target name if provided, otherwise use source name
        target = self.project_path / (target_name if target_name else source_path.name)

        # Validate target name if provided
        if target_name and not self._is_valid_folder_name(target_name):
            raise ValueError(f"Invalid target name: {target_name}. Name must be a valid file/folder name.")

        try:
            if source_path.is_file():
                shutil.copy2(source_path, target)
            elif source_path.is_dir():
                shutil.copytree(source_path, target, dirs_exist_ok=True)
            else:
                raise ValueError(f"Unsupported file type: {source_path}")
        except (shutil.Error, OSError) as e:
            raise ProjectSaveError(f"Failed to copy file: {e}") from e

    def move_to_project(self, source_path: Path, target_name: Optional[str] = None) -> None:
        """
        Move a file or directory to the project directory

        :param source_path: Path of the source file or directory
        :param target_name: Optional custom name for the target file or directory
        :raises FileNotFoundError: If the source file or directory does not exist
        :raises PermissionError: If there are insufficient permissions for the move operation
        :raises ValueError: If the target name is invalid
        """
        if not self.project_path:
            raise ProjectLoadError("Project path not set")

        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        # Ensure project directory exists
        self.project_path.mkdir(parents=True, exist_ok=True)

        # Use custom target name if provided, otherwise use source name
        target = self.project_path / (target_name if target_name else source_path.name)

        # Validate target name if provided
        if target_name and not self._is_valid_folder_name(target_name):
            raise ValueError(f"Invalid target name: {target_name}. Name must be a valid file/folder name.")

        try:
            if source_path.is_file():
                shutil.move(source_path, target)
            elif source_path.is_dir():
                # If target directory exists, remove it first
                if target.exists():
                    shutil.rmtree(target)
                shutil.move(source_path, target)
            else:
                raise ValueError(f"Unsupported file type: {source_path}")
        except (shutil.Error, OSError) as e:
            raise ProjectSaveError(f"Failed to move file: {e}") from e
