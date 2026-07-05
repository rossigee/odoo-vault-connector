# Copyright 2025 Ross Golder
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import requests
import os
import uuid
import time
import threading

# Module-level session cache: {token, expires_at}
_vault_session_cache = {}
_vault_session_lock = threading.Lock()


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
    def _get_vault_token(self):
        """Get a valid Vault token, using AppRole login or cached static token.

        Supports three auth methods in order of preference:
        1. AppRole: VAULT_ROLE_ID + VAULT_SECRET_ID (with auto-renewal)
        2. Static token: legacy VAULT_TOKEN env var (for backward compatibility)
        3. None: raises exception if neither is available
        """
        vault_addr = os.environ.get('VAULT_ADDR')
        vault_skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() == 'true'

        role_id = os.environ.get('VAULT_ROLE_ID')
        secret_id = os.environ.get('VAULT_SECRET_ID')
        static_token = os.environ.get('VAULT_TOKEN')

        with _vault_session_lock:
            current_time = time.time()

            # Try to renew or use cached token if it exists and is still valid
            if _vault_session_cache.get('token') and _vault_session_cache.get('expires_at', 0) > (current_time + 60):
                # Token is still valid (with 60s safety margin)
                return _vault_session_cache['token']

            # Try to renew cached token if it exists
            if _vault_session_cache.get('token'):
                try:
                    headers = {'X-Vault-Token': _vault_session_cache['token']}
                    renew_url = f"{vault_addr}/v1/auth/token/renew-self"
                    response = requests.post(renew_url, headers=headers, verify=not vault_skip_verify, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        lease_duration = data.get('auth', {}).get('lease_duration', 3600)
                        _vault_session_cache['expires_at'] = current_time + lease_duration
                        return _vault_session_cache['token']
                except Exception:
                    # Renewal failed, will fall through to login/static token
                    pass

            # Try AppRole login
            if role_id and secret_id:
                try:
                    login_url = f"{vault_addr}/v1/auth/approle/login"
                    response = requests.post(login_url, json={
                        'role_id': role_id,
                        'secret_id': secret_id
                    }, verify=not vault_skip_verify, timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    token = data['auth']['client_token']
                    lease_duration = data['auth'].get('lease_duration', 3600)
                    _vault_session_cache['token'] = token
                    _vault_session_cache['expires_at'] = current_time + lease_duration
                    return token
                except Exception as e:
                    raise Exception(f"AppRole login to Vault failed: {str(e)}")

            # Fall back to static token
            if static_token:
                _vault_session_cache['token'] = static_token
                _vault_session_cache['expires_at'] = current_time + 86400  # Assume 24h for static token
                return static_token

            # No auth method available
            raise Exception(
                "Vault authentication not configured. Either set VAULT_ROLE_ID+VAULT_SECRET_ID "
                "(AppRole) or VAULT_TOKEN (static token) environment variables."
            )

    @api.model
    def check_vault_status(self):
        """Check if vault is accessible and unsealed"""
        vault_addr = os.environ.get('VAULT_ADDR')
        vault_skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() == 'true'

        if not vault_addr:
            return {'accessible': False, 'error': 'VAULT_ADDR environment variable must be set'}

        try:
            vault_token = self._get_vault_token()
        except Exception as e:
            return {'accessible': False, 'error': f'Vault authentication failed: {str(e)}'}
        
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
        vault_skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() == 'true'
        if not vault_addr:
            raise Exception("VAULT_ADDR environment variable must be set.")

        vault_token = self._get_vault_token()

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
        vault_skip_verify = os.environ.get('VAULT_SKIP_VERIFY', 'false').lower() == 'true'
        if not vault_addr:
            raise Exception("VAULT_ADDR environment variable must be set.")

        vault_token = self._get_vault_token()

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