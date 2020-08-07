import sys
import textwrap

import pytask
import pytest
from pytask.cli import main
from pytask.main import pytask_main
from pytask.mark_ import MarkGenerator


@pytest.mark.unit
@pytest.mark.parametrize("attribute", ["hookimpl", "mark"])
def test_mark_exists_in_pytask_namespace(attribute):
    assert attribute in sys.modules["pytask"].__all__


@pytest.mark.unit
def test_pytask_mark_notcallable() -> None:
    mark = MarkGenerator()
    with pytest.raises(TypeError):
        mark()


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:Unknown pytask.mark.foo")
def test_mark_with_param():
    def some_function(abc):
        pass

    class SomeClass:
        pass

    assert pytask.mark.foo(some_function) is some_function
    marked_with_args = pytask.mark.foo.with_args(some_function)
    assert marked_with_args is not some_function

    assert pytask.mark.foo(SomeClass) is SomeClass
    assert pytask.mark.foo.with_args(SomeClass) is not SomeClass


@pytest.mark.unit
def test_pytask_mark_name_starts_with_underscore():
    mark = MarkGenerator()
    with pytest.raises(AttributeError):
        mark._some_name


@pytest.mark.end_to_end
@pytest.mark.parametrize("config_name", ["pytask.ini", "tox.ini", "setup.cfg"])
def test_ini_markers(tmp_path, config_name):
    tmp_path.joinpath(config_name).write_text(
        textwrap.dedent(
            """
            [pytask]
            markers =
                a1: this is a webtest marker
                a2: this is a smoke marker
            """
        )
    )

    session = pytask_main({"paths": tmp_path})

    assert session.exit_code == 0
    assert "a1" in session.config["markers"]
    assert "a2" in session.config["markers"]


@pytest.mark.end_to_end
@pytest.mark.parametrize("config_name", ["pytask.ini", "tox.ini", "setup.cfg"])
def test_markers_option(capsys, tmp_path, config_name):
    tmp_path.joinpath(config_name).write_text(
        textwrap.dedent(
            """
            [pytask]
            markers =
                a1: this is a webtest marker
                a2: this is a smoke marker
                nodescription
            """
        )
    )

    session = main({"paths": tmp_path, "markers": True})

    assert session.exit_code == 0

    captured = capsys.readouterr()
    for out in ["pytask.mark.a1", "pytask.mark.a2", "pytask.mark.nodescription"]:
        assert out in captured.out


@pytest.mark.end_to_end
@pytest.mark.filterwarnings("ignore:Unknown pytask.mark.")
@pytest.mark.parametrize("config_name", ["pytask.ini", "tox.ini", "setup.cfg"])
def test_ini_markers_whitespace(tmp_path, config_name):
    tmp_path.joinpath(config_name).write_text(
        textwrap.dedent(
            """
            [pytask]
            markers =
                a1 : this is a whitespace marker
            """
        )
    )
    tmp_path.joinpath("task_dummy.py").write_text(
        textwrap.dedent(
            """
            import pytask
            @pytask.mark.a1
            def test_markers():
                assert True
            """
        )
    )

    session = main({"paths": tmp_path, "strict_markers": True})
    assert session.exit_code == 2
    assert isinstance(session.collection_reports[0].exc_info[1], ValueError)


@pytest.mark.filterwarnings("ignore:Unknown pytask.mark.")
@pytest.mark.parametrize(
    ("expr", "expected_passed"),
    [
        ("xyz", ["task_one"]),
        ("(((  xyz))  )", ["task_one"]),
        ("not not xyz", ["task_one"]),
        ("xyz and xyz2", []),
        ("xyz2", ["task_two"]),
        ("xyz or xyz2", ["task_one", "task_two"]),
    ],
)
def test_mark_option(tmp_path, expr: str, expected_passed: str) -> None:
    tmp_path.joinpath("task_dummy.py").write_text(
        textwrap.dedent(
            """
            import pytask
            @pytask.mark.xyz
            def task_one():
                pass
            @pytask.mark.xyz2
            def task_two():
                pass
            """
        )
    )
    session = main({"paths": tmp_path, "marker_expression": expr})

    tasks_that_run = [report.task.name for report in session.execution_reports]
    assert set(tasks_that_run) == set(expected_passed)


@pytest.mark.parametrize(
    ("expr", "expected_passed"),
    [
        ("interface", ["task_interface"]),
        ("not interface", ["task_nointer", "task_pass", "task_1", "task_2"]),
        ("pass", ["task_pass"]),
        ("not pass", ["task_interface", "task_nointer", "task_1", "task_2"]),
        ("not not not (pass)", ["task_interface", "task_nointer", "task_1", "task_2"]),
        ("1 or 2", ["task_1", "task_2"]),
        ("not (1 or 2)", ["task_interface", "task_nointer", "task_pass"]),
    ],
)
def test_keyword_option_custom(tmp_path, expr: str, expected_passed: str) -> None:
    tmp_path.joinpath("task_dummy.py").write_text(
        textwrap.dedent(
            """
            def task_interface():
                pass
            def task_nointer():
                pass
            def task_pass():
                pass
            def task_1():
                pass
            def task_2():
                pass
            """
        )
    )
    session = main({"paths": tmp_path, "expression": expr})
    assert session.exit_code == 0

    tasks_that_run = [report.task.name for report in session.execution_reports]
    assert set(tasks_that_run) == set(expected_passed)


@pytest.mark.parametrize(
    ("expr", "expected_passed"),
    [
        ("arg0", ["task_func[arg0]"]),
        ("arg1", ["task_func[arg1]"]),
        ("arg2", ["task_func[arg2]"]),
    ],
)
def test_keyword_option_parametrize(tmp_path, expr: str, expected_passed: str) -> None:
    tmp_path.joinpath("task_dummy.py").write_text(
        textwrap.dedent(
            """
            import pytask
            @pytask.mark.parametrize("arg", [None, 1.3, "2-3"])
            def task_func(arg):
                pass
            """
        )
    )

    session = main({"paths": tmp_path, "expression": expr})
    assert session.exit_code == 0

    tasks_that_run = [report.task.name for report in session.execution_reports]
    assert set(tasks_that_run) == set(expected_passed)


@pytest.mark.parametrize(
    ("expr", "expected_error"),
    [
        (
            "foo or",
            "at column 7: expected not OR left parenthesis OR identifier; got end of "
            "input",
        ),
        (
            "foo or or",
            "at column 8: expected not OR left parenthesis OR identifier; got or",
        ),
        ("(foo", "at column 5: expected right parenthesis; got end of input",),
        ("foo bar", "at column 5: expected end of input; got identifier",),
        (
            "or or",
            "at column 1: expected not OR left parenthesis OR identifier; got or",
        ),
        (
            "not or",
            "at column 5: expected not OR left parenthesis OR identifier; got or",
        ),
    ],
)
def test_keyword_option_wrong_arguments(
    tmp_path, capsys, expr: str, expected_error: str
) -> None:
    tmp_path.joinpath("task_dummy.py").write_text(
        textwrap.dedent(
            """
            def task_func(arg):
                pass
            """
        )
    )
    session = main({"paths": tmp_path, "expression": expr})
    assert session.exit_code == 2

    err = capsys.readouterr().err
    assert expected_error in err