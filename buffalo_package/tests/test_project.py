import sys
from pathlib import Path
import shutil
import pytest

from buffalo.project import Project, ProjectLoadError
from buffalo.exceptions import BuffaloFileNotFoundError


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
    assert (target_dir / "subdir" /
            "subfile.txt").read_text() == "subfile content"


def test_copy_dir_with_custom_name(project, files):
    # Test copying directory with custom name
    project.copy_to_project(files, "custom_dir")

    # Verify directory was copied with custom name
    target_dir = project.project_path / "custom_dir"
    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()
    assert (target_dir / "subdir" /
            "subfile.txt").read_text() == "subfile content"


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
        assert loaded_project.works[i].output_file == work.output_file
        assert loaded_project.works[i].comment == work.comment


def test_load_nonexistent_project():
    """Test loading non-existent project"""
    # Try to load non-existent project
    loaded_project = Project.load("nonexistent_project", Path("."))
    assert loaded_project is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
