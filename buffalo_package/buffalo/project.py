import logging
from pathlib import Path
from typing import Optional, List, Tuple
import shutil
import os

from .work import Work
from .exceptions import (ProjectLoadError, ProjectSaveError, BuffaloFileNotFoundError, WorkflowFormatError, WorkflowDescriptionError, ConfigurationError)
from .utils import load_yaml_file, save_yaml_file


class Project:
    """
    Project class is used to describe a project, including project name and project description file path.

    Please use the Buffalo class to create and operate the Project class
    """

    LAST_WORK_IN_PROGRESS = "last_work_in_progress"

    def __init__(self, name: str, base_dir: Path, template_path: Optional[Path] = None):
        """
        Initialize a new Project class.

        :param name: Project name (must be a valid folder name)
        :param base_dir: Project base directory
        :param template_path: Template file path, optional for loading existing projects
        :raises ConfigurationError: If the project name is not a valid folder name
        :raises ProjectSaveError: If saving the project file fails
        """
        # Initialize basic attributes
        self.name: str = ""
        self.works: List[Work] = []
        self.project_path = None
        self.template_path = template_path

        # Validate project name first
        if not self._is_valid_folder_name(name):
            raise ConfigurationError(f"Invalid project name: {name}. Project name must be a valid folder name.")

        # Set project name and path after validation
        self.name = name
        if base_dir:
            self.project_path = base_dir / name

        # Load workflow description if template_path is provided
        if template_path and self.project_path:
            # Create project directory if it doesn't exist
            self.project_path.mkdir(parents=True, exist_ok=True)

            self.load_workflow_description(template_path)

            # Save project file
            self.save_project(str(self.project_path / "workflow.yml"))

    @classmethod
    def load(cls, name: str, base_dir: Path) -> Optional['Project']:
        """
        Load an existing project.

        :param name: Project name
        :param base_dir: Project base directory
        :return: Project object or None if project cannot be loaded
        """
        project_path = base_dir / name
        project_file = project_path / "workflow.yml"

        if not project_path.exists():
            return None

        try:
            # Create project instance without template_path
            project = cls(name, base_dir)

            # Load saved project
            project.load_saved_project(project_file)
            return project
        except (ProjectLoadError, BuffaloFileNotFoundError) as e:
            logging.error(f"Failed to load project {name}: {e}")
            return None

    def get_work_by_name(self, work_name: str, without_check: bool = False) -> Optional[Work]:
        """
        Get a work by name.

        :param work_name: Work name to find
        :param without_check: Whether to skip checking the status of previous works
        :return: Work object or None if not found
        """
        if without_check:
            # Directly find work by name
            for work in self.works:
                if work.name == work_name:
                    return work
        else:
            # Get next not started work
            work, last_work_status = self.get_next_not_started_work()
            if work is not None and last_work_status is None and work.name == work_name:
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
            self.save_project(str(self.project_path / "workflow.yml"))

    @staticmethod
    def _is_valid_folder_name(name: str) -> bool:
        """
        Check if the project name is a valid folder name

        :param name: Project name to check
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

    def load_project_from_file(self, saved_project_file_path: str) -> None:
        """
        Load a Project class from a saved project file
        It will first load the description file, then load the saved project file
        If the project file doesn't match the description file, loading will fail

        :param saved_project_file_path: Saved project file path (yml)
        :raises BuffaloFileNotFoundError: If the specified project file does not exist
        :raises ProjectLoadError: If loading the project file fails
        """
        if not Path(saved_project_file_path).exists():
            raise BuffaloFileNotFoundError(f"Specified project file does not exist: {saved_project_file_path}")

        logging.info(f"Starting to load project from {saved_project_file_path}")
        self.load_saved_project(str(saved_project_file_path))

        logging.info(f"Successfully loaded project from {saved_project_file_path}")

    def load_workflow_description(self, template_path: Path) -> None:
        """
        Load workflow description file
        
        :param template_path: Workflow description file path
        :raises WorkflowDescriptionError: If the workflow description file format is incorrect
        :raises WorkflowFormatError: If parsing the workflow description file fails
        """
        try:
            # Use utility function to load YAML file
            workflow_description_yaml = load_yaml_file(str(template_path))

            # Check if workflow_description_yaml contains the workflow field
            if "workflow" not in workflow_description_yaml:
                raise WorkflowDescriptionError(f"Specified description file {template_path} does not contain the workflow field")

            yml_workflow = workflow_description_yaml["workflow"]

            # Check if yml_workflow contains the works field
            if "works" not in yml_workflow:
                raise WorkflowDescriptionError(f"Specified description file {template_path} does not contain the works field")

            yml_works = yml_workflow["works"]

            work_count = 0
            # Check if each work contains name, status, output_file, comment fields
            for work in yml_works:
                if "name" not in work:
                    raise WorkflowDescriptionError("Missing name field in work")
                if "status" not in work:
                    raise WorkflowDescriptionError(f"Missing status field in work {work['name']}")
                if "output_file" not in work:
                    raise WorkflowDescriptionError(f"Missing output_file field in work {work['name']}")
                if "comment" not in work:
                    raise WorkflowDescriptionError(f"Missing comment field in work {work['name']}")
                work_count += 1
                # Create Work object
                work_obj = Work(
                    index=work_count,
                    name=work["name"],
                    output_file=work["output_file"],
                    comment=work["comment"],
                )
                self.works.append(work_obj)

        except (WorkflowDescriptionError, WorkflowFormatError) as e:
            # Directly rethrow our custom exceptions
            raise e
        except Exception as e:
            # Wrap all other exceptions as WorkflowFormatError
            raise WorkflowFormatError(f"Failed to parse workflow_description file {template_path}: {e}") from e

    def load_saved_project(self, saved_project_file_path: Path) -> None:
        """
        Load project from a saved project file
        
        :param saved_project_file_path: Saved project file path
        :raises ProjectLoadError: If loading the project file fails
        """
        try:
            # Use utility function to load YAML file
            saved_project_yaml = load_yaml_file(str(saved_project_file_path))

            # Check if saved_project_yaml contains the name field
            if "name" not in saved_project_yaml:
                raise ProjectLoadError(f"Project file {saved_project_file_path} does not contain the name field")

            self.name = saved_project_yaml["name"]

            if "workflow" not in saved_project_yaml:
                raise ProjectLoadError(f"Project file {saved_project_file_path} does not contain the workflow field")

            yml_workflow = saved_project_yaml["workflow"]

            # Check if yml_workflow contains the works field
            if "works" not in yml_workflow:
                raise ProjectLoadError(f"Project file {saved_project_file_path} does not contain the works field")

            yml_works = yml_workflow["works"]

            # Create works from saved project file
            work_count = 0
            for work in yml_works:
                if "name" not in work:
                    raise ProjectLoadError("Missing name field in work")
                if "status" not in work:
                    raise ProjectLoadError(f"Missing status field in work {work['name']}")
                if "output_file" not in work:
                    raise ProjectLoadError(f"Missing output_file field in work {work['name']}")
                if "comment" not in work:
                    raise ProjectLoadError(f"Missing comment field in work {work['name']}")
                work_count += 1
                # Create Work object
                work_obj = Work(
                    index=work_count,
                    name=work["name"],
                    output_file=work["output_file"],
                    comment=work["comment"],
                )
                work_obj.set_status(work["status"])
                self.works.append(work_obj)

        except ProjectLoadError:
            # Directly rethrow wrapped exceptions
            raise
        except Exception as e:
            # Wrap all other exceptions as ProjectLoadError
            raise ProjectLoadError(f"Failed to parse project file {saved_project_file_path}: {e}") from e

    def save_project(self, project_file_path: str):
        """
        Save project to file
        
        :param project_file_path: Project file save path
        :raises ProjectSaveError: If saving the project file fails
        """
        # Organize data
        works_dict = []
        for work in self.works:
            works_dict.append({
                "name": work.name,
                "status": work.status,
                "output_file": work.output_file,
                "comment": work.comment,
            })

        # Use utility function to save YAML file
        try:
            save_yaml_file(project_file_path, {"name": self.name, "workflow": {"works": works_dict}})
        except Exception as e:
            raise ProjectSaveError(f"Failed to save project file {project_file_path}: {e}") from e

    def get_current_work(self) -> Optional[Work]:
        """
        Returns the current work

        :return: Current work; if current work doesn't exist, returns None
        """
        for work in self.works:
            if work.is_in_progress():
                return work
        return None

    def get_next_not_started_work(self) -> Tuple[Optional[Work], Optional[str]]:
        """
        Returns the next not started work

        :return: Returns the next not started work; if no such work exists, returns None; 
         note that you need to check if the second element of the return value is LAST_WORK_IN_PROGRESS
        """
        # Return the next not started work
        is_last_work_done = None
        for work in self.works:
            if work.is_not_started():
                if is_last_work_done is None:
                    # This is the first work, directly return the current work
                    return work, None
                # If current Work is not the first Work, need to check if the previous Work is done
                else:
                    if is_last_work_done:
                        return work, None
                    else:
                        return work, self.LAST_WORK_IN_PROGRESS

            # Assign the is_done status of current work to is_last_work_done
            is_last_work_done = work.is_done()

        logging.debug("No not started work found")
        return None, None

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
        name={self.name}
            workflow:
                works:\n"""
        for work in self.works:
            output += f"            {work}\n"
        return output

    def copy_to_project(self, source_path: str) -> None:
        """
        将指定路径的文件或文件夹复制到项目目录中

        :param source_path: 源文件或文件夹的路径
        :raises FileNotFoundError: 如果源文件或文件夹不存在
        :raises PermissionError: 如果没有足够的权限进行复制操作
        """
        if not self.project_path:
            raise ProjectLoadError("项目路径未设置")

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"源路径不存在: {source_path}")

        # 确保项目目录存在
        self.project_path.mkdir(parents=True, exist_ok=True)
        target = self.project_path / source.name

        try:
            if source.is_file():
                shutil.copy2(source, target)
            elif source.is_dir():
                shutil.copytree(source, target, dirs_exist_ok=True)
            else:
                raise ValueError(f"不支持的文件类型: {source_path}")
        except (shutil.Error, OSError) as e:
            raise ProjectSaveError(f"复制文件失败: {e}") from e

    def move_to_project(self, source_path: str) -> None:
        """
        将指定路径的文件或文件夹移动到项目目录中

        :param source_path: 源文件或文件夹的路径
        :raises FileNotFoundError: 如果源文件或文件夹不存在
        :raises PermissionError: 如果没有足够的权限进行移动操作
        """
        if not self.project_path:
            raise ProjectLoadError("项目路径未设置")

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"源路径不存在: {source_path}")

        # 确保项目目录存在
        self.project_path.mkdir(parents=True, exist_ok=True)
        target = self.project_path / source.name

        try:
            if source.is_file():
                shutil.move(source, target)
            elif source.is_dir():
                # 如果目标目录已存在，先删除它
                if target.exists():
                    shutil.rmtree(target)
                shutil.move(source, target)
            else:
                raise ValueError(f"不支持的文件类型: {source_path}")
        except (shutil.Error, OSError) as e:
            raise ProjectSaveError(f"移动文件失败: {e}") from e
