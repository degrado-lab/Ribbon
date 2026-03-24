import os
import pytest
from pathlib import Path
from ribbon.utils import make_directories, list_files, serialize, deserialize

def test_make_directories(tmp_path):
    """Test that make_directories creates the specified directories."""
    dir1 = tmp_path / "subdir1"
    dir2 = tmp_path / "subdir2"
    
    # Run the function
    returned_dirs = make_directories(dir1, str(dir2))
    
    # Assertions
    assert dir1.exists()
    assert dir1.is_dir()
    assert dir2.exists()
    assert dir2.is_dir()
    
    assert isinstance(returned_dirs[0], Path)
    assert isinstance(returned_dirs[1], Path)
    assert returned_dirs[0] == dir1
    assert returned_dirs[1] == dir2

def test_list_files(tmp_path):
    """Test that list_files filters files by extension correctly."""
    # Create test files
    (tmp_path / "test1.txt").write_text("hello")
    (tmp_path / "test2.txt").write_text("world")
    (tmp_path / "test3.csv").write_text("1,2,3")
    
    # Run the function
    txt_files = list_files(str(tmp_path), ".txt")
    csv_files = list_files(str(tmp_path), ".csv")
    none_files = list_files(str(tmp_path), ".log")
    
    # Assertions
    assert len(txt_files) == 2
    assert any("test1.txt" in f for f in txt_files)
    assert any("test2.txt" in f for f in txt_files)
    
    assert len(csv_files) == 1
    assert "test3.csv" in csv_files[0]
    
    assert len(none_files) == 0

def test_serialization(tmp_path):
    """Test that serialize and deserialize work correctly."""
    # Test data
    test_data = {"key": "value", "list": [1, 2, 3], "nested": {"a": 1}}
    
    # Run serialize
    saved_file = serialize(test_data, save_dir=tmp_path)
    
    # Assertions
    assert saved_file.exists()
    assert saved_file.suffix == ".pkl"
    
    # Run deserialize
    loaded_data = deserialize(saved_file, cache_dir=tmp_path)
    
    # Assertion
    assert loaded_data == test_data

def test_deserialize_non_absolute(tmp_path):
    """Test deserialize with a non-absolute path relative to cache_dir."""
    test_data = [1, 2, 3]
    saved_file = serialize(test_data, save_dir=tmp_path)
    filename_only = saved_file.name
    
    # Run deserialize using only the filename and providing the cache_dir
    loaded_data = deserialize(filename_only, cache_dir=tmp_path)
    
    assert loaded_data == test_data
