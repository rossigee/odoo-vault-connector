# Copyright 2025 Ross Golder
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import requests
import os
import uuid


class VaultConnector(models.AbstractModel):
    _name = 'vault.connector'
    _description = 'Vault Connector'
    
    @api.model
    def _get_kv_store_name(self):
        """Get the KV store name from environment or generate from database name"""
        kv_store = os.environ.get('VAULT_KV_STORE')
        if not kv_store:
            # Fallback to database name prefixed with 'odoo-'
            db_name = self.env.cr.dbname
            kv_store = f'odoo-{db_name}'
        return kv_store

    @api.model
    def check_vault_status(self):
        """Check if vault is accessible and unsealed"""
        vault_addr = os.environ.get('VAULT_ADDR')
        vault_token = os.environ.get('VAULT_TOKEN')
        vault_skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() == 'true'
        
        if not vault_addr or not vault_token:
            return {'accessible': False, 'error': 'VAULT_ADDR and VAULT_TOKEN environment variables must be set'}
        
        try:
            # Check vault seal status
            status_url = f"{vault_addr}/v1/sys/seal-status"
            response = requests.get(status_url, verify=not vault_skip_verify, timeout=5)
            response.raise_for_status()
            status_data = response.json()
            
            if status_data.get('sealed', True):
                return {'accessible': False, 'error': 'Vault is sealed'}
            
            # Check if token is valid by testing a simple auth call
            headers = {'X-Vault-Token': vault_token}
            auth_url = f"{vault_addr}/v1/auth/token/lookup-self"
            auth_response = requests.get(auth_url, headers=headers, verify=not vault_skip_verify, timeout=5)
            
            if auth_response.status_code == 403:
                return {'accessible': False, 'error': 'Vault token is invalid or expired'}
            elif auth_response.status_code != 200:
                return {'accessible': False, 'error': f'Vault authentication failed: {auth_response.status_code}'}
                
            return {'accessible': True, 'error': None}
            
        except requests.exceptions.Timeout:
            return {'accessible': False, 'error': 'Vault connection timeout'}
        except requests.exceptions.ConnectionError:
            return {'accessible': False, 'error': 'Cannot connect to Vault server'}
        except Exception as e:
            return {'accessible': False, 'error': f'Vault status check failed: {str(e)}'}

    @api.model
    def get_secret(self, secret_id):
        vault_addr = os.environ.get('VAULT_ADDR')
        vault_token = os.environ.get('VAULT_TOKEN')
        vault_skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() == 'true'
        if not vault_addr or not vault_token:
            raise Exception("VAULT_ADDR and VAULT_TOKEN environment variables must be set.")

        # Validate that secret_id is a valid UUID
        try:
            if not secret_id:
                raise ValidationError("Secret ID cannot be empty.")
            uuid.UUID(secret_id)
        except ValueError:
            raise ValidationError(f"Invalid secret ID format: {secret_id}. Must be a valid UUID.")

        # Check vault status first
        vault_status = self.check_vault_status()
        if not vault_status['accessible']:
            raise Exception(f"Vault is not accessible: {vault_status['error']}")

        kv_store = self._get_kv_store_name()

        headers = {'X-Vault-Token': vault_token}
        url = f"{vault_addr}/v1/{kv_store}/data/{secret_id}"
        try:
            response = requests.get(url, headers=headers, verify=not vault_skip_verify)
            response.raise_for_status()
            return response.json()['data']['data']
        except requests.exceptions.RequestException as e:
            # Parse specific error messages
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 403:
                    raise Exception("Access denied: Vault token may be invalid or expired")
                elif e.response.status_code == 404:
                    raise Exception(f"Secret '{secret_id}' not found in Vault")
                elif e.response.status_code == 503:
                    raise Exception("Vault is sealed or unavailable")
            raise Exception(f"Failed to retrieve secret from Vault: {str(e)}")


    @api.model
    def set_secret(self, secret_id, data):
        vault_addr = os.environ.get('VAULT_ADDR')
        vault_token = os.environ.get('VAULT_TOKEN')
        vault_skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() == 'true'
        if not vault_addr or not vault_token:
            raise Exception("VAULT_ADDR and VAULT_TOKEN environment variables must be set.")

        # Validate that secret_id is a valid UUID
        try:
            if not secret_id:
                raise ValidationError("Secret ID cannot be empty.")
            uuid.UUID(secret_id)
        except ValueError:
            raise ValidationError(f"Invalid secret ID format: {secret_id}. Must be a valid UUID.")

        kv_store = self._get_kv_store_name()

        headers = {'X-Vault-Token': vault_token}
        url = f"{vault_addr}/v1/{kv_store}/data/{secret_id}"
        try:
            response = requests.post(url, headers=headers, json={'data': data}, verify=not vault_skip_verify)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to set secret in Vault: {str(e)}")