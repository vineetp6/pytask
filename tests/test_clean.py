import textwrap

import pytest
from pytask import cli


@pytest.fixture()
def sample_project_path(tmp_path):
    source = """
    import pytask

    @pytask.mark.depends_on("in.txt")
    @pytask.mark.produces("out.txt")
    def task_dummy(produces):
        produces.write_text("a")
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))
    tmp_path.joinpath("in.txt").touch()

    tmp_path.joinpath("to_be_deleted_file_1.txt").touch()
    tmp_path.joinpath("to_be_deleted_folder_1").mkdir()
    tmp_path.joinpath("to_be_deleted_folder_1", "to_be_deleted_file_2.txt").touch()

    return tmp_path


@pytest.mark.end_to_end
def test_clean_dry_run(sample_project_path, runner):
    result = runner.invoke(cli, ["clean", sample_project_path.as_posix()])

    assert "Would remove" in result.output
    assert "to_be_deleted_file_1.txt" in result.output
    assert sample_project_path.joinpath("to_be_deleted_file_1.txt").exists()
    assert "to_be_deleted_file_2.txt" in result.output
    assert sample_project_path.joinpath(
        "to_be_deleted_folder_1", "to_be_deleted_file_2.txt"
    ).exists()


@pytest.mark.end_to_end
def test_clean_dry_run_w_directories(sample_project_path, runner):
    result = runner.invoke(cli, ["clean", "-d", sample_project_path.as_posix()])

    assert "Would remove" in result.output
    assert "to_be_deleted_file_1.txt" in result.output
    assert "to_be_deleted_file_2.txt" not in result.output
    assert "to_be_deleted_folder_1" in result.output


@pytest.mark.end_to_end
def test_clean_force(sample_project_path, runner):
    result = runner.invoke(
        cli, ["clean", "-m", "force", sample_project_path.as_posix()]
    )

    assert "Remove" in result.output
    assert "to_be_deleted_file_1.txt" in result.output
    assert not sample_project_path.joinpath("to_be_deleted_file_1.txt").exists()
    assert "to_be_deleted_file_2.txt" in result.output
    assert not sample_project_path.joinpath(
        "to_be_deleted_folder_1", "to_be_deleted_file_2.txt"
    ).exists()


@pytest.mark.end_to_end
def test_clean_force_w_directories(sample_project_path, runner):
    result = runner.invoke(
        cli, ["clean", "-d", "-m", "force", sample_project_path.as_posix()]
    )

    assert "Remove" in result.output
    assert "to_be_deleted_file_1.txt" in result.output
    assert "to_be_deleted_file_2.txt" not in result.output
    assert "to_be_deleted_folder_1" in result.output


@pytest.mark.end_to_end
def test_clean_interactive(sample_project_path, runner):
    result = runner.invoke(
        cli,
        ["clean", "-m", "interactive", sample_project_path.as_posix()],
        # Three instead of two because the compiled .pyc file is also present.
        input="y\ny\ny",
    )

    assert "Remove" in result.output
    assert "to_be_deleted_file_1.txt" in result.output
    assert not sample_project_path.joinpath("to_be_deleted_file_1.txt").exists()
    assert "to_be_deleted_file_2.txt" in result.output
    assert not sample_project_path.joinpath(
        "to_be_deleted_folder_1", "to_be_deleted_file_2.txt"
    ).exists()


@pytest.mark.end_to_end
def test_clean_interactive_w_directories(sample_project_path, runner):
    result = runner.invoke(
        cli,
        ["clean", "-d", "-m", "interactive", sample_project_path.as_posix()],
        # Three instead of two because the compiled .pyc file is also present.
        input="y\ny\ny",
    )

    assert "Remove" in result.output
    assert "to_be_deleted_file_1.txt" in result.output
    assert not sample_project_path.joinpath("to_be_deleted_file_1.txt").exists()
    assert "to_be_deleted_file_2.txt" not in result.output
    assert "to_be_deleted_folder_1" in result.output
    assert not sample_project_path.joinpath("to_be_deleted_folder_1").exists()