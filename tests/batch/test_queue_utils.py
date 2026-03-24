import pytest
import ribbon.batch.queue_utils as queue_utils

def test_parse_slurm_output():
    """Test extracting job ID from Slurm submission output."""
    output = "Submitted batch job 12345"
    assert queue_utils.parse_slurm_output(output) == 12345

def test_parse_sge_output():
    """Test extracting job ID from SGE submission output."""
    output = "Your job 12345 (\"my_job\") has been submitted"
    assert queue_utils.parse_sge_output(output) == 12345

def test_parse_slurm_resources_basic():
    """Test basic Slurm resource parsing."""
    resources = {'time': '1:00:00', 'mem': '4G', 'gpus': 1}
    result = queue_utils.parse_slurm_resources(resources)
    assert '--time=1:00:00' in result
    assert '--mem=4G' in result
    assert '--gpus=1' in result

def test_parse_slurm_resources_dependency_single():
    """Test Slurm dependency parsing with a single job ID."""
    resources = {'dependency': '12345'}
    result = queue_utils.parse_slurm_resources(resources)
    assert '--dependency=afterok:12345' in result

def test_parse_slurm_resources_dependency_list():
    """Test Slurm dependency parsing with a list of job IDs."""
    resources = {'dependency': ['12345', '67890']}
    result = queue_utils.parse_slurm_resources(resources)
    assert '--dependency=afterok:12345:67890' in result

def test_parse_slurm_resources_flags():
    """Test Slurm boolean flags."""
    resources = {'requeue': True}
    result = queue_utils.parse_slurm_resources(resources)
    assert '--requeue' in result
    assert '--requeue' in result
    assert '--requeue=' not in result

def test_parse_sge_resources_basic():
    """Test basic SGE resource parsing."""
    resources = {'time': '1:00:00', 'mem': '4G', 'gpus': 1}
    result = queue_utils.parse_sge_resources(resources)
    assert '-l h_rt=1:00:00' in result
    assert '-l mem_free=4G' in result
    assert '-l gpu=1' in result

def test_parse_sge_resources_dependency_list():
    """Test SGE dependency parsing with a list of job IDs."""
    resources = {'dependency': ['12345', '67890']}
    result = queue_utils.parse_sge_resources(resources)
    assert '-hold_jid 12345,67890' in result

def test_parse_sge_resources_other():
    """Test SGE other resource types (not -l)."""
    resources = {'job-name': 'my_job', 'output': '/path/to/out'}
    result = queue_utils.parse_sge_resources(resources)
    assert '-N my_job' in result
    assert '-o /path/to/out' in result
