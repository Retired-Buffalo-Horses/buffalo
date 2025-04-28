"""Unit test module for Buffalo package, providing tests for Buffalo class core functionalities"""
import tempfile
import unittest
from pathlib import Path
import shutil

from buffalo import Buffalo, Work, Project
from buffalo.exceptions import ConfigurationError


class TestBuffalo(unittest.TestCase):
    """Test suite for Buffalo class, testing project creation, job retrieval, and status updates"""

    def setUp(self):
        """Set up test environment by creating temporary directory and template file"""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

        # Create example template file
        self.template_file = self.base_dir / "wf_template.yml"
        with open(self.template_file, "w", encoding="utf-8") as f:
            f.write("""workflow:
  works:
    - name: "test_work"
      status: not_started
      output_file: "test.md"
      comment: "Test work"
    - name: "second_work"
      status: not_started
      output_file: "second.md"
      comment: "Second test work"
""")

    def tearDown(self):
        """Clean up test environment by removing temporary directory"""
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def test_project_name_validation_invalid(self):
        """Test project name validation with invalid names"""
        # Test invalid project names
        invalid_names = [
            "",  # Empty name
            "   ",  # Only whitespace
            "test/project",  # Contains invalid character
            "test\\project",  # Contains invalid character
            "test:project",  # Contains invalid character
            "test*project",  # Contains invalid character
            "test?project",  # Contains invalid character
            "test<project",  # Contains invalid character
            "test>project",  # Contains invalid character
            "test|project",  # Contains invalid character
            "test\"project",  # Contains invalid character
            ".test_project",  # Starts with dot
            "test_project.",  # Ends with dot
            " test_project",  # Starts with space
            "test_project ",  # Ends with space
        ]

        for name in invalid_names:
            with self.assertRaises(ConfigurationError, msg=f"Project name '{name}' should be invalid"):
                Project(name, self.base_dir, self.template_file)
            # Verify that no directory was created, but skip empty string as it would point to base_dir
            if name.strip():  # Only check if name is not empty or whitespace
                project_dir = self.base_dir / name
                self.assertFalse(project_dir.exists(), f"Directory should not be created for invalid name '{name}'")

    def test_project_name_validation_valid(self):
        """Test project name validation with valid names"""
        # Test valid project name
        project = Project("test_project", self.base_dir, self.template_file)
        self.assertIsNotNone(project)
        if project is not None:
            self.assertEqual(project.folder_name, "test_project")

            # Verify that directory was created
            project_dir = self.base_dir / "test_project"
            self.assertTrue(project_dir.exists(), "Project directory should exist")
            self.assertTrue(project_dir.is_dir(), "Project directory should be a directory")

            # Verify that project file was created
            project_file = project_dir / "workflow.yml"
            self.assertTrue(project_file.exists(), "Project file should exist")
            self.assertTrue(project_file.is_file(), "Project file should be a file")

    def test_create_project(self):
        """Test project creation functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        project = buffalo.create_project("test_project")

        # Check if project was created successfully
        self.assertIsNotNone(project)
        if project is not None:
            self.assertEqual(project.folder_name, "test_project")

            # Check if project directory exists
            project_dir = self.base_dir / "test_project"
            self.assertTrue(project_dir.exists(), "Project directory should exist")
            self.assertTrue(project_dir.is_dir(), "Project directory should be a directory")

            # Check if project file exists
            project_file = project_dir / "workflow.yml"
            self.assertTrue(project_file.exists(), "Project file should exist")
            self.assertTrue(project_file.is_file(), "Project file should be a file")

            # Check project file content
            with open(project_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("folder_name: test_project", content, "Project file should contain project name")
                self.assertIn("workflow:", content, "Project file should contain workflow section")
                self.assertIn("works:", content, "Project file should contain works section")
                self.assertIn("test_work", content, "Project file should contain test work")
                self.assertIn("second_work", content, "Project file should contain second work")

    def test_create_project_with_existing_directory(self):
        """Test project creation when directory already exists"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create a directory with the same name
        project_dir = self.base_dir / "test_project"
        project_dir.mkdir()

        # Create project
        project = buffalo.create_project("test_project")

        # Check if project was created successfully
        self.assertIsNotNone(project)
        if project is not None:
            self.assertEqual(project.folder_name, "test_project")

            # Check if project file exists
            project_file = project_dir / "workflow.yml"
            self.assertTrue(project_file.exists(), "Project file should exist")
            self.assertTrue(project_file.is_file(), "Project file should be a file")

            # Check project file content
            with open(project_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("folder_name: test_project", content, "Project file should contain project name")
                self.assertIn("workflow:", content, "Project file should contain workflow section")
                self.assertIn("works:", content, "Project file should contain works section")

    def test_get_a_job(self):
        """Test job retrieval functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        buffalo.create_project("test_project")

        # Get work
        project_folder_name, work = buffalo.get_a_job("test_work")

        # Check if work was retrieved successfully
        self.assertIsNotNone(work)
        self.assertIsNotNone(project_folder_name)
        if work is not None and project_folder_name is not None:
            self.assertEqual(work.name, "test_work")
            self.assertEqual(project_folder_name, "test_project")

    def test_update_work_status(self):
        """Test work status update functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        buffalo.create_project("test_project")

        # Get work
        project_folder_name, work = buffalo.get_a_job("test_work")
        self.assertIsNotNone(project_folder_name)
        self.assertIsNotNone(work)

        if project_folder_name is not None and work is not None:
            # Update work status
            buffalo.update_work_status(project_folder_name, work, Work.IN_PROGRESS)

            # Check if work status was updated
            self.assertEqual(work.status, Work.IN_PROGRESS)

            # Get it again
            project = buffalo.projects[project_folder_name]
            current_work = project.get_current_work()

            # Check if current work is the updated work
            self.assertIsNotNone(current_work)
            if current_work is not None:
                self.assertEqual(current_work.name, "test_work")
                self.assertEqual(current_work.status, Work.IN_PROGRESS)

    def test_load_project(self):
        """Test loading existing project functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        buffalo.create_project("load_test")

        # Create new Buffalo instance to reload project
        buffalo2 = Buffalo(self.base_dir, self.template_file)

        # Load existing project
        project = buffalo2.load_project("load_test")

        # Check if project was loaded successfully
        self.assertIsNotNone(project)
        if project is not None:
            self.assertEqual(project.folder_name, "load_test")

    def test_get_a_job_with_without_check(self):
        """Test without_check parameter functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        project = buffalo.create_project("test_project")
        self.assertIsNotNone(project)

        # First get test_work and set it to completed
        project_folder_name, work = buffalo.get_a_job("test_work")
        self.assertIsNotNone(work)
        self.assertIsNotNone(project_folder_name)

        if work is not None and project_folder_name is not None:
            buffalo.update_work_status(project_folder_name, work, Work.DONE)

            # Get second work
            project_folder_name, second_work = buffalo.get_a_job("second_work")
            self.assertIsNotNone(second_work)
            self.assertIsNotNone(project_folder_name)

            if second_work is not None and project_folder_name is not None:
                self.assertEqual(second_work.name, "second_work")

                # Test without_check=True parameter, should be able to get completed test_work
                project_folder_name, test_work = buffalo.get_a_job("test_work", without_check=True)
                self.assertIsNotNone(test_work)
                self.assertIsNotNone(project_folder_name)

                if test_work is not None and project_folder_name is not None:
                    self.assertEqual(test_work.name, "test_work")
                    self.assertEqual(test_work.status, Work.DONE)

    def test_save_project(self):
        """Test project saving functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        project = buffalo.create_project("test_project")
        self.assertIsNotNone(project)

        if project is not None:
            # Save project
            buffalo.save_project(project, "test_project")

            # Check if project file exists
            project_file = self.base_dir / "test_project" / "workflow.yml"
            self.assertTrue(project_file.exists(), "Project file should exist")
            self.assertTrue(project_file.is_file(), "Project file should be a file")

            # Check project file content
            with open(project_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("folder_name: test_project", content, "Project file should contain project name")
                self.assertIn("workflow:", content, "Project file should contain workflow section")
                self.assertIn("works:", content, "Project file should contain works section")

    def test_save_project_with_nonexistent_directory(self):
        """Test saving project to nonexistent directory"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        project = buffalo.create_project("test_project")
        self.assertIsNotNone(project)

        if project is not None:
            # Remove project directory
            project_dir = self.base_dir / "test_project"
            if project_dir.exists():
                shutil.rmtree(project_dir)

            # Save project
            buffalo.save_project(project, "test_project")

            # Check if project directory and file were created
            self.assertTrue(project_dir.exists(), "Project directory should be created")
            project_file = project_dir / "workflow.yml"
            self.assertTrue(project_file.exists(), "Project file should exist")


if __name__ == "__main__":
    unittest.main()
