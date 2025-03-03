# tests/test_credentials.py
import os
import pytest
from unittest import mock

from globalmoo.credentials import Credentials
from globalmoo.exceptions.invalid_argument import InvalidArgumentException

class TestCredentials:
    """Tests for credentials handling."""

    def test_init_with_provided_values(self):
        """Should use provided values when initializing."""
        credentials = Credentials(
            api_key="test-key",
            base_uri="https://api.test.com"
        )
        assert credentials.get_api_key() == "test-key"
        assert credentials.get_base_uri() == "https://api.test.com"

    def test_init_from_environment(self):
        """Should load from environment variables when no values provided."""
        with mock.patch.dict(os.environ, {
            'GMOO_API_KEY': 'env-key',
            'GMOO_API_URI': 'https://api.env.com'
        }):
            credentials = Credentials(skip_dotenv=True)
            assert credentials.get_api_key() == "env-key"
            assert credentials.get_base_uri() == "https://api.env.com"

    def test_missing_api_key(self):
        """Should raise when API key is missing."""
        with mock.patch.dict(os.environ, {'GMOO_API_URI': 'https://api.test.com'}, clear=True):
            with pytest.raises(InvalidArgumentException):
                Credentials(skip_dotenv=True)

    def test_missing_base_uri(self):
        """Should raise when base URI is missing."""
        with mock.patch.dict(os.environ, {'GMOO_API_KEY': 'test-key'}, clear=True):
            with pytest.raises(InvalidArgumentException):
                Credentials(skip_dotenv=True)

    def test_provided_values_override_environment(self):
        """Should prefer provided values over environment variables."""
        with mock.patch.dict(os.environ, {
            'GMOO_API_KEY': 'env-key',
            'GMOO_API_URI': 'https://api.env.com'
        }):
            credentials = Credentials(
                api_key="test-key",
                base_uri="https://api.test.com"
            )
            assert credentials.get_api_key() == "test-key"
            assert credentials.get_base_uri() == "https://api.test.com"