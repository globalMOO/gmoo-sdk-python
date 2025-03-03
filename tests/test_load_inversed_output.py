import pytest
from globalmoo.request.load_inversed_output import LoadInversedOutput
from globalmoo.exceptions.invalid_argument import InvalidArgumentException

def test_valid_load_inversed_output():
    """Test that valid output loads correctly."""
    request = LoadInversedOutput(
        inverse_id=1,
        output=[1.0, 2.0, 3.0]
    )
    assert len(request.output) == 3
    assert request.output == [1.0, 2.0, 3.0]

def test_mixed_numeric_types():
    """Test that mixed int/float values work."""
    request = LoadInversedOutput(
        inverse_id=1,
        output=[1, 2.0, 3]
    )
    assert len(request.output) == 3
    assert request.output == [1, 2.0, 3]

def test_non_list_output():
    """Test that non-list output raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        LoadInversedOutput(
            inverse_id=1,
            output="not_a_list"
        )
    assert "must be a list" in str(exc.value)

def test_non_numeric_values():
    """Test that non-numeric values raise error."""
    with pytest.raises(InvalidArgumentException) as exc:
        LoadInversedOutput(
            inverse_id=1,
            output=[1.0, "2.0", 3.0]  # String instead of number
        )
    assert "must be numbers" in str(exc.value)

def test_empty_output():
    """Test that empty output list works."""
    request = LoadInversedOutput(
        inverse_id=1,
        output=[]
    )
    assert request.output == []

def test_single_value():
    """Test that single value output works."""
    request = LoadInversedOutput(
        inverse_id=1,
        output=[1.0]
    )
    assert len(request.output) == 1
    assert request.output == [1.0]