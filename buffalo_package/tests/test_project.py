from pathlib import Path
import shutil
import pytest

from buffalo.project import Project, ProjectLoadError


@pytest.fixture(name="project")
def project_fixture():
    # 创建临时项目目录
    base_dir = Path("test_temp")
    base_dir.mkdir(exist_ok=True)
    project = Project("test_project", base_dir)
    # 确保项目目录存在
    project.project_path.mkdir(parents=True, exist_ok=True)
    yield project
    # 清理测试文件
    if base_dir.exists():
        shutil.rmtree(base_dir)


@pytest.fixture(name="files")
def test_files():
    # 创建测试文件
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    # 创建测试文件
    (test_dir / "test.txt").write_text("test content")

    # 创建测试子目录和文件
    sub_dir = test_dir / "subdir"
    sub_dir.mkdir(exist_ok=True)
    (sub_dir / "subfile.txt").write_text("subfile content")

    yield test_dir
    # 清理测试文件
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_copy_file_to_project(project, files):
    # 测试复制单个文件
    source_file = files / "test.txt"
    project.copy_to_project(str(source_file))

    # 验证文件是否被正确复制
    target_file = project.project_path / "test.txt"
    assert target_file.exists()
    assert target_file.read_text() == "test content"


def test_copy_dir_to_project(project, files):
    # 测试复制整个目录
    project.copy_to_project(str(files))

    # 验证目录结构是否被正确复制
    target_dir = project.project_path / "test_files"
    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").read_text() == "subfile content"


def test_move_file_to_project(project, files):
    # 测试移动单个文件
    source_file = files / "test.txt"
    project.move_to_project(str(source_file))

    # 验证文件是否被正确移动
    target_file = project.project_path / "test.txt"
    assert target_file.exists()
    assert target_file.read_text() == "test content"
    assert not source_file.exists()


def test_move_dir_to_project(project, files):
    # 测试移动整个目录
    project.move_to_project(str(files))

    # 验证目录结构是否被正确移动
    target_dir = project.project_path / "test_files"
    assert target_dir.exists()
    assert (target_dir / "test.txt").exists()
    assert (target_dir / "subdir" / "subfile.txt").exists()
    assert not files.exists()


def test_copy_nonexistent_file(project):
    # 测试复制不存在的文件
    with pytest.raises(FileNotFoundError):
        project.copy_to_project("nonexistent.txt")


def test_move_nonexistent_file(project):
    # 测试移动不存在的文件
    with pytest.raises(FileNotFoundError):
        project.move_to_project("nonexistent.txt")


def test_copy_without_project_path():
    # 测试没有项目路径的情况
    project = Project("test_project", None)
    with pytest.raises(ProjectLoadError):
        project.copy_to_project("test.txt")


def test_move_without_project_path():
    # 测试没有项目路径的情况
    project = Project("test_project", None)
    with pytest.raises(ProjectLoadError):
        project.move_to_project("test.txt")
