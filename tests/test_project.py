import sys
from pathlib import Path
import shutil
import pytest

from buffalo.project import Project, ProjectLoadError
from buffalo.work import Work


@pytest.fixture(name="project")
def project_fixture():
    # Create temporary project directory
    base_dir = Path("test_temp")
    base_dir.mkdir(exist_ok=True)
    project = Project("test_project", base_dir)
    # Ensure project directory exists
    if project.project_path:
        project.project_path.mkdir(parents=True, exist_ok=True)
    yield project
    # Clean up test files
    if base_dir.exists():
        shutil.rmtree(base_dir)


@pytest.fixture(name="files")
def test_files():
    # Create test files
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    # Create test file
    (test_dir / "test.txt").write_text("test content")

    # Create test subdirectory and file
    sub_dir = test_dir / "subdir"
    sub_dir.mkdir(exist_ok=True)
    (sub_dir / "subfile.txt").write_text("subfile content")

    yield test_dir
    # Clean up test files
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_copy_file_to_project(project, files):
    # Test copying a single file
    source_file = files / "test.txt"
    project.copy_to_project(source_file)

    # Verify file was copied correctly
    target_file = project.project_path / "test.txt"
    assert target_file.exists()
    assert target_file.read_text() == "test content"


def test_copy_file_with_custom_name(project, files):
    # Test copying a file with custom name
    source_file = files / "test.txt"
    project.copy_to_project(source_file, "custom.txt")

    # Verify file was copied with custom name
    target_file = project.project_path / "custom.txt"
    assert target_file.exists()
    assert target_file.read_text() == "test content"


def test_copy_dir_to_project(project, files):
    # Test copying entire directory
    project.copy_to_project(files)

    # Verify directory structure was copied correctly
    target_dir = project.project_path / "test_files"
    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").read_text() == "subfile content"


def test_copy_dir_with_custom_name(project, files):
    # Test copying directory with custom name
    project.copy_to_project(files, "custom_dir")

    # Verify directory was copied with custom name
    target_dir = project.project_path / "custom_dir"
    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").read_text() == "subfile content"


def test_move_file_to_project(project, files):
    # Test moving a single file
    source_file = files / "test.txt"
    project.move_to_project(source_file)

    # Verify file was moved correctly
    target_file = project.project_path / "test.txt"
    assert target_file.exists()
    assert target_file.read_text() == "test content"
    assert not source_file.exists()


def test_move_file_with_custom_name(project, files):
    # Test moving a file with custom name
    source_file = files / "test.txt"
    project.move_to_project(source_file, "custom.txt")

    # Verify file was moved with custom name
    target_file = project.project_path / "custom.txt"
    assert target_file.exists()
    assert target_file.read_text() == "test content"
    assert not source_file.exists()


def test_move_dir_to_project(project, files):
    # Test moving entire directory
    project.move_to_project(files)

    # Verify directory structure was moved correctly
    target_dir = project.project_path / "test_files"
    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()
    assert not files.exists()


def test_move_dir_with_custom_name(project, files):
    # Test moving directory with custom name
    project.move_to_project(files, "custom_dir")

    # Verify directory was moved with custom name
    target_dir = project.project_path / "custom_dir"
    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()
    assert not files.exists()


def test_copy_nonexistent_file(project):
    # Test copying non-existent file
    with pytest.raises(FileNotFoundError):
        project.copy_to_project(Path("nonexistent.txt"))


def test_move_nonexistent_file(project):
    # Test moving non-existent file
    with pytest.raises(FileNotFoundError):
        project.move_to_project(Path("nonexistent.txt"))


def test_copy_without_project_path():
    # Test without project path
    project = Project("test_project", Path("."))
    project.project_path = None
    with pytest.raises(ProjectLoadError):
        project.copy_to_project(Path("test.txt"))


def test_move_without_project_path():
    # Test without project path
    project = Project("test_project", Path("."))
    project.project_path = None
    with pytest.raises(ProjectLoadError):
        project.move_to_project(Path("test.txt"))


def test_copy_with_invalid_target_name(project, files):
    # Test copying with invalid target name
    source_file = files / "test.txt"
    with pytest.raises(ValueError):
        project.copy_to_project(source_file, "invalid/name.txt")


def test_move_with_invalid_target_name(project, files):
    # Test moving with invalid target name
    source_file = files / "test.txt"
    with pytest.raises(ValueError):
        project.move_to_project(source_file, "invalid/name.txt")


def test_load_project(project: Project):
    """Test loading project from saved project file"""
    # Create a test project file
    project.save_project()

    assert project.project_path is not None

    # Load project using the class method
    loaded_project = Project.load("test_project", project.project_path.parent)

    # Verify project was loaded correctly
    assert loaded_project is not None
    assert loaded_project.folder_name == project.folder_name
    assert len(loaded_project.works) == len(project.works)
    for i, work in enumerate(project.works):
        assert loaded_project.works[i].name == work.name
        assert loaded_project.works[i].status == work.status
        assert loaded_project.works[i].comment == work.comment


def test_load_nonexistent_project():
    """Test loading non-existent project"""
    # Try to load non-existent project
    loaded_project = Project.load("nonexistent_project", Path("."))
    assert loaded_project is None


def test_save_and_load_chinese_project():
    """Test saving and loading project with Chinese characters"""
    # Create a project with Chinese name
    base_dir = Path("test_temp")
    base_dir.mkdir(exist_ok=True)
    project = Project("测试项目", base_dir)

    # Ensure project directory exists
    assert project.project_path is not None
    project.project_path.mkdir(parents=True, exist_ok=True)

    try:
        # Save project
        project.save_project()

        # Load project
        loaded_project = Project.load("测试项目", base_dir)

        # Verify project was loaded correctly
        assert loaded_project is not None
        assert loaded_project.folder_name == "测试项目"

        # Verify YAML file content
        project_file = project.project_path / "buffalo.yml"
        assert project_file.exists()
        content = project_file.read_text(encoding="utf-8")
        assert "folder_name: 测试项目" in content
        assert "\\u" not in content  # Ensure no Unicode escape sequences
    finally:
        # Clean up
        if base_dir.exists():
            shutil.rmtree(base_dir)


def test_work_index_ordering():
    """Test that works are ordered by index regardless of their order in the template"""
    # Create a test template with works in random index order
    template_content = """workflow:
  works:
    - name: "Work 6"
      status: not_started
      comment: "Sixth work"
      index: 6
    - name: "Work 4"
      status: not_started
      comment: "Fourth work"
      index: 4
    - name: "Work 2"
      status: not_started
      comment: "Second work"
      index: 2
    - name: "Work 1"
      status: not_started
      comment: "First work"
      index: 1
"""
    # Create temporary directory and template file
    base_dir = Path("test_temp")
    base_dir.mkdir(exist_ok=True)
    template_path = base_dir / "test_template.yml"
    template_path.write_text(template_content)

    try:
        # Create project with the template
        project = Project("test_project", base_dir, template_path)

        # Verify works are ordered by index
        assert len(project.works) == 4
        assert project.works[0].index == 1
        assert project.works[0].name == "Work 1"
        assert project.works[1].index == 2
        assert project.works[1].name == "Work 2"
        assert project.works[2].index == 4
        assert project.works[2].name == "Work 4"
        assert project.works[3].index == 6
        assert project.works[3].name == "Work 6"

        # Save project
        project.save_project()

        # Load project
        loaded_project = Project.load("test_project", base_dir)
        assert loaded_project is not None

        # Verify loaded works are still ordered by index
        assert len(loaded_project.works) == 4
        assert loaded_project.works[0].index == 1
        assert loaded_project.works[0].name == "Work 1"
        assert loaded_project.works[1].index == 2
        assert loaded_project.works[1].name == "Work 2"
        assert loaded_project.works[2].index == 4
        assert loaded_project.works[2].name == "Work 4"
        assert loaded_project.works[3].index == 6
        assert loaded_project.works[3].name == "Work 6"

    finally:
        # Clean up
        if base_dir.exists():
            shutil.rmtree(base_dir)


def test_get_next_not_started_work():
    """Test get_next_not_started_work method with different scenarios"""
    # Create a test template with multiple works
    template_content = """workflow:
  works:
    - name: "Work 1"
      status: not_started
      comment: "First work"
      index: 1
    - name: "Work 2"
      status: not_started
      comment: "Second work"
      index: 2
    - name: "Work 3"
      status: not_started
      comment: "Third work"
      index: 3
"""
    # Create temporary directory and template file
    base_dir = Path("test_temp")
    base_dir.mkdir(exist_ok=True)
    template_path = base_dir / "test_template.yml"
    template_path.write_text(template_content)

    try:
        # Create project with the template
        project = Project("test_project", base_dir, template_path)

        # Test 1: Get next work without check (should return first work)
        next_work = project.get_next_not_started_work(without_check=True)
        assert next_work is not None
        assert next_work.name == "Work 1"

        # Test 2: Get next work with check (should return first work as no previous work)
        next_work = project.get_next_not_started_work(without_check=False)
        assert next_work is not None
        assert next_work.name == "Work 1"

        # Test 3: Complete first work and get next work
        next_work.set_status(Work.DONE)
        next_work = project.get_next_not_started_work(without_check=False)
        assert next_work is not None
        assert next_work.name == "Work 2"

        # Test 4: Set first work to in_progress and try to get next work (should return None)
        project.works[0].set_status(Work.IN_PROGRESS)
        next_work = project.get_next_not_started_work(without_check=False)
        assert next_work is None

        # Test 5: Get next work without check (should return Work 2 despite Work 1 being in progress)
        next_work = project.get_next_not_started_work(without_check=True)
        assert next_work is not None
        assert next_work.name == "Work 2"

    finally:
        # Clean up
        if base_dir.exists():
            shutil.rmtree(base_dir)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
