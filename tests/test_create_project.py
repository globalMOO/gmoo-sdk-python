import pytest
from globalmoo.request.create_project import CreateProject
from globalmoo.exceptions.invalid_argument import InvalidArgumentException
from globalmoo.enums.input_type import InputType

def test_valid_create_project():
    """Test that a valid project creation works."""
    request = CreateProject(
        model_id=1,
        name="Test Project",
        input_count=3,
        minimums=[0.0, 0.0, 0.0],
        maximums=[10.0, 10.0, 10.0],
        input_types=[InputType.FLOAT, InputType.FLOAT, InputType.FLOAT],
        categories=[]
    )
    assert request.model_id == 1
    assert request.input_count == 3
    assert request.minimums == [0.0, 0.0, 0.0]
    assert request.maximums == [10.0, 10.0, 10.0]
    assert request.input_types == [InputType.FLOAT, InputType.FLOAT, InputType.FLOAT]
    assert request.categories == []

def test_project_name_validation():
    """Test that project name is validated correctly."""
    # Test invalid name - too short
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="abc",  # Less than 4 characters
            input_count=1,
            minimums=[0.0],
            maximums=[1.0],
            input_types=[InputType.FLOAT],
            categories=[]
        )
    assert "must be a non-empty string of at least 4 characters" in str(exc.value)

    # Test invalid name - not a string
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name=123,  # Not a string
            input_count=1,
            minimums=[0.0],
            maximums=[1.0],
            input_types=[InputType.FLOAT],
            categories=[]
        )
    assert "must be a non-empty string" in str(exc.value)

def test_mixed_numeric_types():
    """Test that mixed int/float inputs work."""
    request = CreateProject(
        model_id=1,
        name="Test Mixed Types",
        input_count=3,
        minimums=[0, 0.0, 1],
        maximums=[10, 10.0, 10],
        input_types=[InputType.FLOAT, InputType.FLOAT, InputType.INTEGER],
        categories=[]
    )
    assert request.minimums == [0, 0.0, 1]
    assert request.maximums == [10, 10.0, 10]

def test_none_categories_defaults_to_empty():
    """Test that None categories defaults to empty list."""
    request = CreateProject(
        model_id=1,
        name="Test Categories",
        input_count=1,
        minimums=[0.0],
        maximums=[1.0],
        input_types=[InputType.FLOAT],
        categories=None
    )
    assert request.categories == []

def test_invalid_length_minimums():
    """Test that wrong length minimums raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Invalid Minimums",
            input_count=3,
            minimums=[0.0, 0.0],  # Only 2 values for input_count=3
            maximums=[10.0, 10.0, 10.0],
            input_types=[InputType.FLOAT, InputType.FLOAT, InputType.FLOAT],
            categories=[]
        )
    assert "Length of minimums" in str(exc.value)

def test_invalid_length_maximums():
    """Test that wrong length maximums raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Invalid Maximums",
            input_count=3,
            minimums=[0.0, 0.0, 0.0],
            maximums=[10.0, 10.0],  # Only 2 values for input_count=3
            input_types=[InputType.FLOAT, InputType.FLOAT, InputType.FLOAT],
            categories=[]
        )
    assert "Length of maximums" in str(exc.value)

def test_invalid_length_input_types():
    """Test that wrong length input_types raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Invalid Types Length",
            input_count=3,
            minimums=[0.0, 0.0, 0.0],
            maximums=[10.0, 10.0, 10.0],
            input_types=[InputType.FLOAT, InputType.FLOAT],  # Only 2 values for input_count=3
            categories=[]
        )
    assert "Length of input_types" in str(exc.value)

def test_non_numeric_minimums():
    """Test that non-numeric minimums raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Non-numeric Minimums",
            input_count=3,
            minimums=[0.0, "0.0", 0.0],  # String instead of number
            maximums=[10.0, 10.0, 10.0],
            input_types=[InputType.FLOAT, InputType.FLOAT, InputType.FLOAT],
            categories=[]
        )
    assert "must be numbers" in str(exc.value)

def test_non_numeric_maximums():
    """Test that non-numeric maximums raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Non-numeric Maximums",
            input_count=3,
            minimums=[0.0, 0.0, 0.0],
            maximums=[10.0, "10.0", 10.0],  # String instead of number
            input_types=[InputType.FLOAT, InputType.FLOAT, InputType.FLOAT],
            categories=[]
        )
    assert "must be numbers" in str(exc.value)

def test_invalid_input_type():
    """Test that invalid input type raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Invalid Type",
            input_count=3,
            minimums=[0.0, 0.0, 0.0],
            maximums=[10.0, 10.0, 10.0],
            input_types=[InputType.FLOAT, "INVALID", InputType.FLOAT],  # Invalid type
            categories=[]
        )
    assert "Invalid input type:" in str(exc.value)

def test_non_string_categories():
    """Test that non-string categories raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Invalid Categories",
            input_count=1,
            minimums=[0.0],
            maximums=[1.0],
            input_types=[InputType.CATEGORY],
            categories=["valid", 123, "also_valid"]  # Number instead of string
        )
    assert "each category must be a string" in str(exc.value)

def test_non_list_categories():
    """Test that non-list categories raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        CreateProject(
            model_id=1,
            name="Test Categories Type",
            input_count=1,
            minimums=[0.0],
            maximums=[1.0],
            input_types=[InputType.FLOAT],
            categories="not_a_list"  # String instead of list
        )
    assert "categories must be a list" in str(exc.value)
