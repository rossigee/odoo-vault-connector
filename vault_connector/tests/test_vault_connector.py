# Copyright 2025 Ross Golder
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import unittest
from unittest.mock import patch, MagicMock
import os
import uuid
import requests
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestVaultConnector(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.vault_connector = self.env['vault.connector']
        
        # Store original environment
        self.original_env = {}
        for key in ['VAULT_ADDR', 'VAULT_TOKEN', 'VAULT_SKIP_VERIFY', 'VAULT_KV_STORE']:
            self.original_env[key] = os.environ.get(key)
        
        # Set up test environment variables
        os.environ['VAULT_ADDR'] = 'https://vault.example.com:8200'
        os.environ['VAULT_TOKEN'] = 'test-token-123'
        os.environ['VAULT_SKIP_VERIFY'] = 'false'
        
    def tearDown(self):
        # Restore original environment
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        super().tearDown()

    def test_get_kv_store_name_from_env(self):
        """Test KV store name is retrieved from environment variable"""
        os.environ['VAULT_KV_STORE'] = 'custom-store'
        result = self.vault_connector._get_kv_store_name()
        self.assertEqual(result, 'custom-store')

    def test_get_kv_store_name_from_db(self):
        """Test KV store name defaults to database name when env var not set"""
        os.environ.pop('VAULT_KV_STORE', None)
        result = self.vault_connector._get_kv_store_name()
        expected = f'odoo-{self.env.cr.dbname}'
        self.assertEqual(result, expected)

    @patch('requests.get')
    def test_check_vault_status_success(self, mock_get):
        """Test successful vault status check"""
        # Mock seal status response
        mock_seal_response = MagicMock()
        mock_seal_response.raise_for_status.return_value = None
        mock_seal_response.json.return_value = {'sealed': False}
        
        # Mock auth response
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        
        mock_get.side_effect = [mock_seal_response, mock_auth_response]
        
        result = self.vault_connector.check_vault_status()
        self.assertTrue(result['accessible'])
        self.assertIsNone(result['error'])
        
        # Verify requests were made with correct parameters
        self.assertEqual(mock_get.call_count, 2)
        calls = mock_get.call_args_list
        
        # Check seal status call
        self.assertEqual(calls[0][0][0], 'https://vault.example.com:8200/v1/sys/seal-status')
        self.assertTrue(calls[0][1]['verify'])
        
        # Check auth call
        self.assertEqual(calls[1][0][0], 'https://vault.example.com:8200/v1/auth/token/lookup-self')
        self.assertEqual(calls[1][1]['headers']['X-Vault-Token'], 'test-token-123')

    def test_check_vault_status_missing_env_vars(self):
        """Test vault status check with missing environment variables"""
        os.environ.pop('VAULT_ADDR', None)
        os.environ.pop('VAULT_TOKEN', None)
        
        result = self.vault_connector.check_vault_status()
        self.assertFalse(result['accessible'])
        self.assertIn('VAULT_ADDR and VAULT_TOKEN', result['error'])

    @patch('requests.get')
    def test_check_vault_status_sealed(self, mock_get):
        """Test vault status check when vault is sealed"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'sealed': True}
        mock_get.return_value = mock_response
        
        result = self.vault_connector.check_vault_status()
        self.assertFalse(result['accessible'])
        self.assertEqual(result['error'], 'Vault is sealed')

    @patch('requests.get')
    def test_check_vault_status_invalid_token(self, mock_get):
        """Test vault status check with invalid token"""
        mock_seal_response = MagicMock()
        mock_seal_response.raise_for_status.return_value = None
        mock_seal_response.json.return_value = {'sealed': False}
        
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 403
        
        mock_get.side_effect = [mock_seal_response, mock_auth_response]
        
        result = self.vault_connector.check_vault_status()
        self.assertFalse(result['accessible'])
        self.assertEqual(result['error'], 'Vault token is invalid or expired')

    @patch('requests.get')
    def test_check_vault_status_timeout(self, mock_get):
        """Test vault status check with timeout"""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = self.vault_connector.check_vault_status()
        self.assertFalse(result['accessible'])
        self.assertEqual(result['error'], 'Vault connection timeout')

    @patch('requests.get')
    def test_check_vault_status_connection_error(self, mock_get):
        """Test vault status check with connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = self.vault_connector.check_vault_status()
        self.assertFalse(result['accessible'])
        self.assertEqual(result['error'], 'Cannot connect to Vault server')

    @patch('odoo.addons.vault_connector.models.vault_connector.VaultConnector.check_vault_status')
    @patch('requests.get')
    def test_get_secret_success(self, mock_get, mock_status):
        """Test successful secret retrieval"""
        # Mock vault status check
        mock_status.return_value = {'accessible': True, 'error': None}
        
        # Mock secret retrieval
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': {
                'data': {
                    'username': 'admin',
                    'password': 'secret123'
                }
            }
        }
        mock_get.return_value = mock_response
        
        secret_id = str(uuid.uuid4())
        result = self.vault_connector.get_secret(secret_id)
        
        self.assertEqual(result['username'], 'admin')
        self.assertEqual(result['password'], 'secret123')
        
        # Verify correct URL was called
        expected_url = f'https://vault.example.com:8200/v1/odoo-{self.env.cr.dbname}/data/{secret_id}'
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args[0][0], expected_url)

    def test_get_secret_invalid_uuid(self):
        """Test get_secret with invalid UUID"""
        with self.assertRaises(ValidationError) as cm:
            self.vault_connector.get_secret('invalid-uuid')
        self.assertIn('Invalid secret ID format', str(cm.exception))

    def test_get_secret_empty_id(self):
        """Test get_secret with empty secret ID"""
        with self.assertRaises(ValidationError) as cm:
            self.vault_connector.get_secret('')
        self.assertIn('Secret ID cannot be empty', str(cm.exception))

    def test_get_secret_missing_env_vars(self):
        """Test get_secret with missing environment variables"""
        os.environ.pop('VAULT_ADDR', None)
        os.environ.pop('VAULT_TOKEN', None)
        
        secret_id = str(uuid.uuid4())
        with self.assertRaises(Exception) as cm:
            self.vault_connector.get_secret(secret_id)
        self.assertIn('VAULT_ADDR and VAULT_TOKEN', str(cm.exception))

    @patch('odoo.addons.vault_connector.models.vault_connector.VaultConnector.check_vault_status')
    def test_get_secret_vault_not_accessible(self, mock_status):
        """Test get_secret when vault is not accessible"""
        mock_status.return_value = {'accessible': False, 'error': 'Vault is sealed'}
        
        secret_id = str(uuid.uuid4())
        with self.assertRaises(Exception) as cm:
            self.vault_connector.get_secret(secret_id)
        self.assertIn('Vault is not accessible', str(cm.exception))

    @patch('odoo.addons.vault_connector.models.vault_connector.VaultConnector.check_vault_status')
    @patch('requests.get')
    def test_get_secret_not_found(self, mock_get, mock_status):
        """Test get_secret when secret is not found"""
        mock_status.return_value = {'accessible': True, 'error': None}
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        secret_id = str(uuid.uuid4())
        with self.assertRaises(Exception) as cm:
            self.vault_connector.get_secret(secret_id)
        self.assertIn('not found in Vault', str(cm.exception))

    @patch('requests.post')
    def test_set_secret_success(self, mock_post):
        """Test successful secret storage"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        secret_id = str(uuid.uuid4())
        secret_data = {'username': 'admin', 'password': 'secret123'}
        
        result = self.vault_connector.set_secret(secret_id, secret_data)
        self.assertTrue(result)
        
        # Verify correct URL and data were sent
        expected_url = f'https://vault.example.com:8200/v1/odoo-{self.env.cr.dbname}/data/{secret_id}'
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args[0][0], expected_url)
        self.assertEqual(mock_post.call_args[1]['json']['data'], secret_data)

    def test_set_secret_invalid_uuid(self):
        """Test set_secret with invalid UUID"""
        with self.assertRaises(ValidationError) as cm:
            self.vault_connector.set_secret('invalid-uuid', {'key': 'value'})
        self.assertIn('Invalid secret ID format', str(cm.exception))

    def test_set_secret_empty_id(self):
        """Test set_secret with empty secret ID"""
        with self.assertRaises(ValidationError) as cm:
            self.vault_connector.set_secret('', {'key': 'value'})
        self.assertIn('Secret ID cannot be empty', str(cm.exception))

    def test_set_secret_missing_env_vars(self):
        """Test set_secret with missing environment variables"""
        os.environ.pop('VAULT_ADDR', None)
        os.environ.pop('VAULT_TOKEN', None)
        
        secret_id = str(uuid.uuid4())
        with self.assertRaises(Exception) as cm:
            self.vault_connector.set_secret(secret_id, {'key': 'value'})
        self.assertIn('VAULT_ADDR and VAULT_TOKEN', str(cm.exception))

    @patch('requests.post')
    def test_set_secret_request_exception(self, mock_post):
        """Test set_secret with request exception"""
        mock_post.side_effect = requests.exceptions.RequestException('Network error')
        
        secret_id = str(uuid.uuid4())
        with self.assertRaises(Exception) as cm:
            self.vault_connector.set_secret(secret_id, {'key': 'value'})
        self.assertIn('Failed to set secret', str(cm.exception))

    def test_vault_skip_verify_option(self):
        """Test that VAULT_SKIP_VERIFY option is properly handled"""
        os.environ['VAULT_SKIP_VERIFY'] = 'true'
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {'sealed': False}
            mock_auth_response = MagicMock()
            mock_auth_response.status_code = 200
            mock_get.side_effect = [mock_response, mock_auth_response]
            
            self.vault_connector.check_vault_status()
            
            # Verify verify=False was passed to requests
            calls = mock_get.call_args_list
            self.assertFalse(calls[0][1]['verify'])
            self.assertFalse(calls[1][1]['verify'])

    @patch('odoo.addons.vault_connector.models.vault_connector.VaultConnector.check_vault_status')
    @patch('requests.get')
    def test_custom_kv_store_path(self, mock_get, mock_status):
        """Test that custom KV store path is used correctly"""
        os.environ['VAULT_KV_STORE'] = 'custom-kv-store'
        mock_status.return_value = {'accessible': True, 'error': None}
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'data': {'data': {'key': 'value'}}}
        mock_get.return_value = mock_response
        
        secret_id = str(uuid.uuid4())
        self.vault_connector.get_secret(secret_id)
        
        # Verify custom KV store path was used
        expected_url = f'https://vault.example.com:8200/v1/custom-kv-store/data/{secret_id}'
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args[0][0], expected_url)