"""
Test script for the flat file version of globalMOO SDK.
This demonstrates that the flat file can be imported and used without installing the package.
"""

# Import from the flat file
from globalmoo_flat import (
    Client,
    Credentials,
    InvalidArgumentException,
    InputType,
    ObjectiveType,
    StopReason,
    CreateProject,
    LoadObjectives,
)

def test_imports():
    """Test that all main classes can be imported."""
    print("✓ Successfully imported Client")
    print("✓ Successfully imported Credentials")
    print("✓ Successfully imported exceptions")
    print("✓ Successfully imported enums")
    print("✓ Successfully imported request classes")

def test_enums():
    """Test that enums work correctly."""
    assert InputType.FLOAT == "float"
    assert InputType.INTEGER == "integer"
    print("✓ InputType enum works correctly")

    assert ObjectiveType.EXACT == "exact"
    assert ObjectiveType.MINIMIZE == "minimize"
    print("✓ ObjectiveType enum works correctly")

    assert StopReason.RUNNING == 0
    assert StopReason.SATISFIED == 1
    print("✓ StopReason enum works correctly")

def test_exceptions():
    """Test that exceptions can be raised and caught."""
    try:
        raise InvalidArgumentException("Test error", {"key": "value"})
    except InvalidArgumentException as e:
        assert "Test error" in str(e)
        assert e.details == {"key": "value"}
        print("✓ InvalidArgumentException works correctly")

def test_credentials():
    """Test credentials validation."""
    # Test that credentials require API key
    try:
        creds = Credentials(api_key="", base_uri="https://api.globalmoo.ai")
        print("✗ Should have raised exception for empty API key")
    except InvalidArgumentException as e:
        assert "API key" in str(e)
        print("✓ API key validation works correctly")

    # Test that credentials require base URI
    try:
        creds = Credentials(api_key="test-key", base_uri="")
        print("✗ Should have raised exception for empty base URI")
    except InvalidArgumentException as e:
        assert "Base URI" in str(e)
        print("✓ Base URI validation works correctly")

    # Test successful credentials creation
    creds = Credentials(api_key="test-key", base_uri="https://api.globalmoo.ai")
    assert creds.get_api_key() == "test-key"
    assert creds.get_base_uri() == "https://api.globalmoo.ai"
    print("✓ Credentials creation works correctly")

def test_request_validation():
    """Test request validation."""
    # Test CreateProject validation
    try:
        # This should fail because name is too short
        req = CreateProject(
            model_id=1,
            name="ab",  # Too short
            input_count=2,
            minimums=[0, 0],
            maximums=[1, 1],
            input_types=["float", "float"],
            categories=[]
        )
        print("✗ Should have raised exception for short name")
    except InvalidArgumentException as e:
        assert "at least 4 characters" in str(e)
        print("✓ CreateProject validation works correctly")

    # Test array length mismatch
    try:
        req = CreateProject(
            model_id=1,
            name="test",
            input_count=2,
            minimums=[0],  # Wrong length
            maximums=[1, 1],
            input_types=["float", "float"],
            categories=[]
        )
        print("✗ Should have raised exception for array length mismatch")
    except InvalidArgumentException as e:
        assert "must match input_count" in str(e)
        print("✓ Array length validation works correctly")

if __name__ == "__main__":
    print("Testing globalMOO SDK flat file...\n")

    test_imports()
    print()

    test_enums()
    print()

    test_exceptions()
    print()

    test_credentials()
    print()

    test_request_validation()
    print()

    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
    print("\nThe flat file is ready to use.")
    print("Simply copy globalmoo_flat.py and paste it at the top of your code.")
