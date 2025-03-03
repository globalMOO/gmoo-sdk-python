import pytest
from globalmoo.request.load_output_cases import LoadOutputCases
from globalmoo.exceptions.invalid_argument import InvalidArgumentException

def test_valid_load_output_cases():
    """Test that valid output cases load correctly."""
    request = LoadOutputCases(
        project_id=1,
        output_count=3,
        output_cases=[
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0]
        ]
    )
    assert request.output_count == 3
    assert len(request.output_cases) == 3
    assert all(len(case) == 3 for case in request.output_cases)

def test_mixed_numeric_types():
    """Test that mixed int/float values work."""
    request = LoadOutputCases(
        project_id=1,
        output_count=3,
        output_cases=[
            [1, 2.0, 3],
            [4.0, 5, 6.0]
        ]
    )
    assert len(request.output_cases) == 2
    assert all(len(case) == 3 for case in request.output_cases)

def test_non_list_output_cases():
    """Test that non-list output_cases raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        LoadOutputCases(
            project_id=1,
            output_count=3,
            output_cases="not_a_list"
        )
    assert "must be a list" in str(exc.value)

def test_non_list_inner_cases():
    """Test that non-list inner cases raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        LoadOutputCases(
            project_id=1,
            output_count=3,
            output_cases=[
                [1.0, 2.0, 3.0],
                "not_a_list",
                [7.0, 8.0, 9.0]
            ]
        )
    assert "must be a list of lists" in str(exc.value)

def test_inconsistent_lengths():
    """Test that inconsistent inner list lengths raises error."""
    with pytest.raises(InvalidArgumentException) as exc:
        LoadOutputCases(
            project_id=1,
            output_count=3,
            output_cases=[
                [1.0, 2.0, 3.0],
                [4.0, 5.0],  # Only 2 values
                [7.0, 8.0, 9.0]
            ]
        )
    assert "must have length matching output_count" in str(exc.value)

def test_non_numeric_values():
    """Test that non-numeric values raise error."""
    with pytest.raises(InvalidArgumentException) as exc:
        LoadOutputCases(
            project_id=1,
            output_count=3,
            output_cases=[
                [1.0, "2.0", 3.0],  # String instead of number
                [4.0, 5.0, 6.0]
            ]
        )
    assert "must be numbers" in str(exc.value)

def test_empty_output_cases():
    """Test that empty output_cases list works."""
    request = LoadOutputCases(
        project_id=1,
        output_count=3,
        output_cases=[]
    )
    assert request.output_cases == []

def test_single_case():
    """Test that a single output case works."""
    request = LoadOutputCases(
        project_id=1,
        output_count=3,
        output_cases=[[1.0, 2.0, 3.0]]
    )
    assert len(request.output_cases) == 1
    assert len(request.output_cases[0]) == 3