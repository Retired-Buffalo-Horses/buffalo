"""Unit test module for Buffalo package, providing tests for Buffalo class core functionalities"""
import os
import tempfile
import unittest

from buffalo import Buffalo, Work, Project


class TestBuffalo(unittest.TestCase):
    """Test suite for Buffalo class, testing project creation, job retrieval, and status updates"""

    def setUp(self):
        """Set up test environment by creating temporary directory and template file"""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.temp_dir.name

        # Create example template file
        self.template_file = os.path.join(self.base_dir, "wf_template.yml")
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

    def test_create_project(self):
        """Test project creation functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        project = buffalo.create_project("test_project", "Test Project")

        # Check if project was created successfully
        self.assertIsNotNone(project)
        self.assertEqual(project.name, "Test Project")

        # Check if project file was created
        project_file = os.path.join(self.base_dir, "test_project", "wf.yml")
        self.assertTrue(os.path.exists(project_file))

    def test_get_a_job(self):
        """Test job retrieval functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        buffalo.create_project("test_project", "Test Project")

        # Get work
        project_folder_name, work = buffalo.get_a_job("test_work")

        # Check if work was retrieved successfully
        self.assertIsNotNone(work)
        self.assertEqual(work.name, "test_work")
        self.assertEqual(project_folder_name, "test_project")

    def test_update_work_status(self):
        """Test work status update functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        buffalo.create_project("test_project", "Test Project")

        # Get work
        project_folder_name, work = buffalo.get_a_job("test_work")

        # Update work status
        buffalo.update_work_status(project_folder_name, work, Work.IN_PROGRESS)

        # Check if work status was updated
        self.assertEqual(work.status, Work.IN_PROGRESS)

        # Get it again
        project = buffalo.projects[project_folder_name]
        current_work = project.get_current_work()

        # Check if current work is the updated work
        self.assertIsNotNone(current_work)
        self.assertEqual(current_work.name, "test_work")
        self.assertEqual(current_work.status, Work.IN_PROGRESS)

    def test_encoding_parameter(self):
        """Test encoding parameter functionality"""
        # Create Buffalo instance, now using fixed utf-8 encoding
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        project = buffalo.create_project("encoding_test", "Encoding Test Project")

        # Check if project was created successfully
        self.assertIsNotNone(project)
        self.assertEqual(project.encoding, "utf-8")  # 验证固定使用utf-8编码

        # Get work
        project_folder_name, work = buffalo.get_a_job("test_work")

        # Test updating work status
        buffalo.update_work_status(project_folder_name, work, Work.IN_PROGRESS)
        self.assertEqual(work.status, Work.IN_PROGRESS)

    def test_load_project(self):
        """Test loading existing project functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        buffalo.create_project("load_test", "Load Test")

        # Create new Buffalo instance to reload project
        buffalo2 = Buffalo(self.base_dir, self.template_file)

        # Load existing project
        project = buffalo2.load_project("load_test")

        # Check if project was loaded successfully
        self.assertIsNotNone(project)
        self.assertEqual(project.name, "Load Test")

    def test_get_a_job_with_without_check(self):
        """Test without_check parameter functionality"""
        # Create Buffalo instance
        buffalo = Buffalo(self.base_dir, self.template_file)

        # Create project
        project: Project = buffalo.create_project("test_project", "Test Project")
        self.assertIsNotNone(project)

        # First get test_work and set it to completed
        project_folder_name, work = buffalo.get_a_job("test_work")
        self.assertIsNotNone(work)
        buffalo.update_work_status(project_folder_name, work, Work.DONE)

        # Get second work
        project_folder_name, second_work = buffalo.get_a_job("second_work")
        self.assertIsNotNone(second_work)
        self.assertEqual(second_work.name, "second_work")

        # Test without_check=True parameter, should be able to get completed test_work
        project_folder_name, test_work = buffalo.get_a_job("test_work", without_check=True)
        self.assertIsNotNone(test_work)
        self.assertEqual(test_work.name, "test_work")
        self.assertEqual(test_work.status, Work.DONE)


if __name__ == "__main__":
    unittest.main()
