import logging
from pathlib import Path
from typing import Optional, List, Tuple

from .work import Work
from .exceptions import (ProjectLoadError, ProjectSaveError, BuffaloFileNotFoundError, WorkflowFormatError, WorkflowDescriptionError)
from .utils import load_yaml_file, save_yaml_file


class Project:
    """
    Project class is used to describe a project, including project name and project description file path.

    Please use the Buffalo class to create and operate the Project class
    """

    LAST_WORK_IN_PROGRESS = "last_work_in_progress"

    def __init__(self, workflow_description_file_path: str, name: str = "", encoding: str = "utf-8"):
        """
        Initialize a new Project class from the description file

        :param workflow_description_file_path: Project description file path (yml)
        :param name: Project name
        :param encoding: File encoding, default is utf-8
        :raises BuffaloFileNotFoundError: If the specified description file does not exist
        """
        self.name: str = name
        self.works: List[Work] = []
        self.project_path = None
        self.encoding = encoding

        if not Path(workflow_description_file_path).exists():
            raise BuffaloFileNotFoundError(f"Specified description file does not exist: {workflow_description_file_path}")

        logging.info(f"Starting to configure project {self.name} from {workflow_description_file_path}")
        self.load_workflow_description(workflow_description_file_path)
        logging.info(f"Successfully configured project {self.name} from {workflow_description_file_path}")

    def load_project_from_file(self, saved_project_file_path: str, encoding: Optional[str] = None) -> None:
        """
        Load a Project class from a saved project file
        It will first load the description file, then load the saved project file
        If the project file doesn't match the description file, loading will fail

        :param saved_project_file_path: Saved project file path (yml)
        :param encoding: File encoding, default uses the encoding set during initialization
        :raises BuffaloFileNotFoundError: If the specified project file does not exist
        :raises ProjectLoadError: If loading the project file fails
        """
        file_encoding = encoding or self.encoding

        if not Path(saved_project_file_path).exists():
            raise BuffaloFileNotFoundError(f"Specified project file does not exist: {saved_project_file_path}")

        logging.info(f"Starting to load project from {saved_project_file_path}")
        self.load_saved_project(saved_project_file_path, file_encoding)

        logging.info(f"Successfully loaded project from {saved_project_file_path}")

    def load_workflow_description(self, workflow_description_file_path: str, encoding: Optional[str] = None) -> None:
        """
        Load workflow description file
        
        :param workflow_description_file_path: Workflow description file path
        :param encoding: File encoding, default uses the encoding set during initialization
        :raises WorkflowDescriptionError: If the workflow description file format is incorrect
        :raises WorkflowFormatError: If parsing the workflow description file fails
        """
        file_encoding = encoding or self.encoding

        try:
            # Use utility function to load YAML file
            workflow_description_yaml = load_yaml_file(workflow_description_file_path, encoding=file_encoding)

            # Check if workflow_description_yaml contains the workflow field
            if "workflow" not in workflow_description_yaml:
                raise WorkflowDescriptionError(f"Specified description file {workflow_description_file_path} does not contain the workflow field")

            yml_workflow = workflow_description_yaml["workflow"]

            # Check if yml_workflow contains the works field
            if "works" not in yml_workflow:
                raise WorkflowDescriptionError(f"Specified description file {workflow_description_file_path} does not contain the works field")

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
            raise WorkflowFormatError(f"Failed to parse workflow_description file {workflow_description_file_path}: {e}") from e

    def load_saved_project(self, saved_project_file_path: str, encoding: Optional[str] = None):
        """
        Load project from a saved project file
        
        :param saved_project_file_path: Saved project file path
        :param encoding: File encoding, default uses the encoding set during initialization
        :raises ProjectLoadError: If loading the project file fails
        """
        file_encoding = encoding or self.encoding
        project_file = Path(saved_project_file_path)
        self.project_path = project_file.parent  # Project directory

        try:
            # Use utility function to load YAML file
            saved_project_yaml = load_yaml_file(saved_project_file_path, encoding=file_encoding)

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

            # Confirm the length of yml_works matches the length of self.works
            if len(yml_works) != len(self.works):
                raise ProjectLoadError(f"The number of Works in project file {saved_project_file_path} does not match the description file")

            # Check if each work contains name, status, output_file, comment fields
            for work in yml_works:
                if "name" not in work:
                    raise ProjectLoadError("Missing name field in work")
                if "status" not in work:
                    raise ProjectLoadError(f"Missing status field in work {work['name']}")
                if "output_file" not in work:
                    raise ProjectLoadError(f"Missing output_file field in work {work['name']}")
                if "comment" not in work:
                    raise ProjectLoadError(f"Missing comment field in work {work['name']}")

                # Find the corresponding work in self.works and set status, output_file, comment
                # If no match is found, raise an exception
                for work_obj in self.works:
                    if work_obj.name == work["name"]:
                        work_obj.set_status(work["status"])
                        work_obj.output_file = work["output_file"]
                        work_obj.comment = work["comment"]
                        break
                else:
                    raise ProjectLoadError(f"Work {work['name']} in project file {saved_project_file_path} not found in description file")

        except ProjectLoadError:
            # Directly rethrow wrapped exceptions
            raise
        except Exception as e:
            # Wrap all other exceptions as ProjectLoadError
            raise ProjectLoadError(f"Failed to parse project file {saved_project_file_path}: {e}") from e

    def save_project(self, project_file_path: str, encoding: Optional[str] = None):
        """
        Save project to file
        
        :param project_file_path: Project file save path
        :param encoding: File encoding, default uses the encoding set during initialization
        :raises ProjectSaveError: If saving the project file fails
        """
        file_encoding = encoding or self.encoding

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
            save_yaml_file(project_file_path, {"name": self.name, "workflow": {"works": works_dict}}, encoding=file_encoding)
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
