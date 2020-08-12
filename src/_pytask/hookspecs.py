import click
import pluggy


hookspec = pluggy.HookspecMarker("pytask")


@hookspec
def pytask_add_hooks(pm: pluggy.PluginManager) -> None:
    """Add hook specifications and implementations to the plugin manager.

    This hook is called very early in the application to load the base functionality
    from plugins.

    If you want to register plugins dynamically depending on the configuration, use
    :func:`pytask_post_parse` instead.

    """


# Hooks for the command-line interface.


@hookspec
def pytask_add_parameters_to_cli(command: click.Command) -> None:
    """Add parameter to :class:`click.Command`.

    Use this hook if you want to add more command line arguments to the interface. Do it
    by extending `command.params` attribute, a list, of the command with other options
    and arguments. See :func:`pytask.cli.pytask_add_parameters_to_cli` as an example.

    """


# Hooks for the pytask_main interface.


@hookspec(firstresult=True)
def pytask_main(config_from_cli: dict):
    """Take the cli config, create the configuration and start the session."""


# Hooks for the configuration.


@hookspec(firstresult=True)
def pytask_configure(pm: pluggy.PluginManager, config_from_cli: dict) -> dict:
    """Configure pytask.

    The main hook implementation which controls the configuration and calls subordinated
    hooks.

    """


@hookspec
def pytask_parse_config(
    config: dict, config_from_cli: dict, config_from_file: dict
) -> None:
    """Parse configuration from the CLI or from file.

    This hook can be used to unify the configuration from the command line interface,
    the configuration file and provided defaults. The function
    :func:`pytask.shared.get_first_not_none_value` might be helpful for that.

    Note that, the configuration is changed in-place.

    """


@hookspec
def pytask_post_parse(config: dict) -> None:
    """Post parsing.

    This hook allows to consolidate the configuration in case some plugins might be
    mutually exclusive. For example, the parallel execution provided by pytask-parallel
    does not work with any form of debugging. If debugging is turned on, parallelization
    can be turned of in this step.

    """


# Hooks for the collection.


@hookspec(firstresult=True)
def pytask_collect(session):
    """Collect tasks from paths.

    The main hook implementation which controls the collection and calls subordinated
    hooks.

    """


@hookspec(firstresult=True)
def pytask_ignore_collect(path, config):
    """Ignore collected path.

    This hook is indicates for each directory and file whether it should be ignored.
    This speeds up the collection.

    """


@hookspec
def pytask_collect_modify_tasks(session, tasks):
    """Modify tasks after they have been collected.

    This hook can be used to deselect tasks when they match a certain keyword or mark.

    Warning
    -------
    This hook is a placeholder since selecting tasks via markers and keywords has not
    been implemented yet. Also add an entry to the log.

    """


@hookspec(firstresult=True)
def pytask_collect_file_protocol(session, path, reports):
    """Start protocol to collect files.

    The protocol calls the subordinate hook :func:`pytask_collect_file` which might
    error if the file has a :class:`SyntaxError`.

    """


@hookspec(firstresult=True)
def pytask_collect_file(session, path, reports):
    """Collect tasks from a file.

    If you want to collect tasks from other files, modify this hook.

    """


@hookspec(firstresult=True)
def pytask_collect_task_protocol(session, reports, path, name, obj):
    """Start protocol to collect tasks."""


@hookspec
def pytask_collect_task_setup(session, reports, path, name, obj):
    """Steps before collecting a task.

    For example, an error can be raised if two tasks with the same name are collected.

    """


@hookspec(firstresult=True)
def pytask_collect_task(session, path, name, obj):
    """Collect a single task."""


@hookspec(firstresult=True)
def pytask_collect_node(path, node):
    """Collect a node which is a dependency or a product of a task."""


@hookspec(firstresult=True)
def pytask_collect_log(session, reports, tasks):
    """Log errors occurring during the collection.

    This hook reports errors during the collection.

    """


# Hooks to parametrize tasks.


@hookspec(firstresult=True)
def pytask_parametrize_task(session, name, obj):
    """Generate multiple tasks from name and object with parametrization."""


@hookspec
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Add some keyword arguments as markers to object.

    This hook moves arguments defined in the parametrization to marks of the same
    function. This allows an argument like ``depends_on`` be transformed to the usual
    ``@pytask.mark.depends_on`` marker which receives special treatment.

    """


# Hooks for resolving dependencies.


@hookspec(firstresult=True)
def pytask_resolve_dependencies(session):
    """Resolve dependencies.

    The main hook implementation which controls the resolution of dependencies and calls
    subordinated hooks.

    """


@hookspec(firstresult=True)
def pytask_resolve_dependencies_create_dag(tasks):
    """Create the DAG.

    This hook creates the DAG from tasks, dependencies and products. The DAG can be used
    by a scheduler to find an execution order.

    """


@hookspec(firstresult=True)
def pytask_resolve_dependencies_select_execution_dag(dag):
    """Select the subgraph which needs to be executed.

    This hook determines which of the tasks have to be re-run because something has
    changed.

    """


@hookspec(firstresult=True)
def pytask_resolve_dependencies_validate_dag(dag):
    """Validate the DAG.

    This hook validates the DAG. For example, there can be cycles in the DAG if tasks,
    dependencies and products have been misspecified.

    """


@hookspec
def pytask_resolve_dependencies_log(session, report):
    """Log errors during resolving dependencies."""


# Hooks for running tasks.


@hookspec(firstresult=True)
def pytask_execute(session):
    """Loop over all tasks for the execution.

    The main hook implementation which controls the execution and calls subordinated
    hooks.

    """


@hookspec
def pytask_execute_log_start(session):
    """Start logging of execution.

    This hook allows to provide a header with information before the execution starts.

    """


@hookspec(firstresult=True)
def pytask_execute_create_scheduler(session):
    """Create a scheduler for the execution.

    The scheduler provides information on which tasks are able to be executed. Its
    foundation is likely a topological ordering of the tasks based on the DAG.

    """


@hookspec(firstresult=True)
def pytask_execute_build(session):
    """Execute the build.

    This hook implements the main loop to execute tasks.

    """


@hookspec(firstresult=True)
def pytask_execute_task_protocol(session, task):
    """Run the protocol for executing a test.

    This hook runs all stages of the execution process, setup, execution, and teardown
    and catches any exception.

    Then, the exception or success is stored in a report and logged.

    """


@hookspec
def pytask_execute_task_log_start(session, task):
    """Start logging of task execution.

    This hook can be used to provide more verbose output during the execution.

    """


@hookspec
def pytask_execute_task_setup(session, task):
    """Set up the task execution.

    This hook is called before the task is executed and can provide an entry-point to
    fast-fail a task. For example, raise and exception if a dependency is missing
    instead of letting the error occur in the execution.

    """


@hookspec(firstresult=True)
def pytask_execute_task(session, task):
    """Execute a task."""


@hookspec
def pytask_execute_task_teardown(session, task):
    """Tear down task execution.

    This hook is executed after the task has been executed. It allows to perform
    clean-up operations or checks for missing products.

    """


@hookspec(firstresult=True)
def pytask_execute_task_process_report(session, report):
    """Process the report of a task.

    This hook allows to process each report generated by a task. It is either based on
    an exception or a success.

    Some exceptions are intentionally raised like skips, but they should not be reported
    as failures.

    """


@hookspec(firstresult=True)
def pytask_execute_task_log_end(session, task, report):
    """Log the end of a task execution."""


@hookspec
def pytask_execute_log_end(session, reports):
    """Log the footer of the execution report."""


# Hooks for general logging.


@hookspec
def pytask_log_session_header(session):
    """Log session information at the begin of a run."""