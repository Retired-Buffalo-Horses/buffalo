import logging
from typing import Optional, List, Dict, Any

from .exceptions import WorkStatusError


class Work:
    """
    Work class is used to describe a work unit, including work name, work status, work output file, and work description
    
    Each Work object represents a step or task in the workflow
    """

    # Work status constants
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"

    def __init__(self, index: int, name: str, output_file: str, comment: str):
        """
        Initialize a Work object
        
        :param index: Work index number
        :param name: Work name
        :param output_file: Work output file path
        :param comment: Work description or comment
        """
        self.index: int = index
        self.name: str = name
        self.status: str = Work.NOT_STARTED
        self.output_file: str = output_file
        self.comment: str = comment

    def __str__(self) -> str:
        """
        Return string representation of Work object
        
        :return: String representation of Work object
        """
        return f"Work(index={self.index}, name={self.name}, status={self.status}, output_file={self.output_file}, comment={self.comment})"

    def set_status(self, status: str) -> None:
        """
        Set work status
        
        :param status: Work status, must be one of NOT_STARTED, IN_PROGRESS, DONE
        :raises WorkStatusError: Raised when status is not one of the three predefined statuses
        """
        if status not in [Work.NOT_STARTED, Work.IN_PROGRESS, Work.DONE]:
            raise WorkStatusError(f"Invalid work status: {status}")
        self.status = status

    def is_done(self) -> bool:
        """
        Check if work is done
        
        :return: Returns True if work status is DONE, otherwise returns False
        """
        return self.status == Work.DONE

    def is_not_started(self) -> bool:
        """
        Check if work is not started
        
        :return: Returns True if work status is NOT_STARTED, otherwise returns False
        """
        return self.status == Work.NOT_STARTED

    def is_in_progress(self) -> bool:
        """
        Check if work is in progress
        
        :return: Returns True if work status is IN_PROGRESS, otherwise returns False
        """
        return self.status == Work.IN_PROGRESS 