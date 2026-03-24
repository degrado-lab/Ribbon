import pytest
from ribbon.runner import Task

def test_task_initialization():
    """Test that the Task class initializes correctly with default values."""
    task = Task()
    assert task.device == 'cpu' # Default is 'cpu' as seen in __init__
    assert task.extra_args == ""
    assert task.task_name is None

def test_task_initialization_custom():
    """Test that the Task class initializes correctly with custom values."""
    task = Task(device='gpu', extra_args="--test")
    assert task.device == 'gpu'
    assert task.extra_args == "--test"

def test_task_run_not_implemented():
    """Test that calling run() on a base Task raises NotImplementedError."""
    task = Task()
    with pytest.raises(NotImplementedError):
        task.run()
