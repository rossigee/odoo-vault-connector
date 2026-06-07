=====
Usage
=====

This document provides comprehensive examples of how to use the HashiCorp Vault Connector in your Odoo modules.

Basic API Usage
===============

The vault connector provides a simple, secure API for managing secrets. All operations are performed through the ``vault.connector`` model.

Storing Secrets
---------------

Store a secret in Vault::

    # Generate a UUID for the secret
    import uuid
    secret_id = str(uuid.uuid4())
    
    # Define the secret data
    secret_data = {
        'username': 'admin',
        'password': 'secret123',
        'api_key': 'abc123def456'
    }
    
    # Store the secret
    try:
        result = self.env['vault.connector'].set_secret(secret_id, secret_data)
        if result:
            print(f"Secret stored successfully with ID: {secret_id}")
    except Exception as e:
        print(f"Failed to store secret: {e}")

Retrieving Secrets
------------------

Retrieve a secret from Vault::

    # Retrieve the secret using its UUID
    try:
        secret_data = self.env['vault.connector'].get_secret(secret_id)
        username = secret_data['username']
        password = secret_data['password']
        print(f"Retrieved credentials for user: {username}")
    except Exception as e:
        print(f"Failed to retrieve secret: {e}")

Checking Vault Status
---------------------

Verify Vault connectivity and status::

    # Check if Vault is accessible
    status = self.env['vault.connector'].check_vault_status()
    
    if status['accessible']:
        print("Vault is accessible and ready")
    else:
        print(f"Vault error: {status['error']}")

Module Integration
==================

Using in Your Odoo Module
--------------------------

1. **Add Dependency**

In your module's ``__manifest__.py``::

    {
        "name": "My Secure Module",
        "depends": [
            "base",
            "vault_connector",  # Add this dependency
        ],
        # ... rest of manifest
    }

2. **Store Configuration Secrets**

Example for storing database connection strings::

    class MyConfiguration(models.Model):
        _name = 'my.configuration'
        _description = 'My Module Configuration'
        
        name = fields.Char('Configuration Name', required=True)
        secret_id = fields.Char('Secret ID', readonly=True)
        
        def create_db_connection(self, connection_params):
            """Store database connection securely"""
            import uuid
            
            # Generate UUID for this secret
            secret_id = str(uuid.uuid4())
            
            # Store connection parameters securely
            try:
                self.env['vault.connector'].set_secret(secret_id, {
                    'host': connection_params['host'],
                    'port': connection_params['port'],
                    'database': connection_params['database'],
                    'username': connection_params['username'],
                    'password': connection_params['password']
                })
                
                # Store only the UUID in Odoo database
                self.secret_id = secret_id
                
            except Exception as e:
                raise ValidationError(f"Failed to store connection: {e}")
        
        def get_db_connection(self):
            """Retrieve database connection securely"""
            if not self.secret_id:
                raise ValidationError("No connection configured")
            
            try:
                return self.env['vault.connector'].get_secret(self.secret_id)
            except Exception as e:
                raise ValidationError(f"Failed to retrieve connection: {e}")

3. **API Key Management**

Example for managing third-party API keys::

    class ThirdPartyIntegration(models.Model):
        _name = 'third.party.integration'
        _description = 'Third Party Integration'
        
        name = fields.Char('Integration Name', required=True)
        api_key_id = fields.Char('API Key ID', readonly=True)
        base_url = fields.Char('Base URL')  # Not sensitive, can be stored normally
        
        def set_api_credentials(self, api_key, api_secret):
            """Store API credentials securely"""
            import uuid
            
            secret_id = str(uuid.uuid4())
            
            try:
                self.env['vault.connector'].set_secret(secret_id, {
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'created_date': fields.Datetime.now().isoformat()
                })
                
                self.api_key_id = secret_id
                
            except Exception as e:
                raise ValidationError(f"Failed to store API credentials: {e}")
        
        def make_api_call(self, endpoint, data=None):
            """Make authenticated API call"""
            if not self.api_key_id:
                raise ValidationError("API credentials not configured")
            
            try:
                # Retrieve credentials
                credentials = self.env['vault.connector'].get_secret(self.api_key_id)
                
                # Make API call
                headers = {
                    'Authorization': f"Bearer {credentials['api_key']}",
                    'Content-Type': 'application/json'
                }
                
                import requests
                response = requests.post(
                    f"{self.base_url}/{endpoint}",
                    json=data,
                    headers=headers
                )
                
                return response.json()
                
            except Exception as e:
                raise ValidationError(f"API call failed: {e}")

Advanced Usage Patterns
========================

Batch Secret Operations
-----------------------

For managing multiple related secrets::

    def setup_multi_environment_config(self):
        """Setup configuration for multiple environments"""
        environments = ['dev', 'staging', 'prod']
        config_ids = {}
        
        for env in environments:
            secret_id = str(uuid.uuid4())
            
            # Environment-specific configuration
            config_data = {
                'environment': env,
                'database_url': f"postgres://user:pass@{env}-db:5432/myapp",
                'redis_url': f"redis://{env}-redis:6379/0",
                'api_base_url': f"https://api-{env}.company.com",
                'secret_key': self.generate_secret_key()
            }
            
            try:
                self.env['vault.connector'].set_secret(secret_id, config_data)
                config_ids[env] = secret_id
            except Exception as e:
                # Rollback on failure
                for existing_id in config_ids.values():
                    try:
                        # Note: Deletion would require additional Vault API implementation
                        pass
                    except:
                        pass
                raise ValidationError(f"Failed to setup {env} config: {e}")
        
        return config_ids

Error Handling Patterns
-----------------------

Robust error handling for production use::

    def secure_operation_with_retry(self, secret_id, max_retries=3):
        """Perform vault operation with retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                # Check vault status first
                status = self.env['vault.connector'].check_vault_status()
                if not status['accessible']:
                    if 'sealed' in status['error'].lower():
                        raise ValidationError("Vault is sealed - manual intervention required")
                    elif 'token' in status['error'].lower():
                        raise ValidationError("Vault token is invalid - check configuration")
                    else:
                        raise ValidationError(f"Vault is not accessible: {status['error']}")
                
                # Perform the operation
                return self.env['vault.connector'].get_secret(secret_id)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    raise ValidationError(f"Failed after {max_retries} attempts: {e}")
                
                # Wait before retry
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise ValidationError("Maximum retries exceeded")

Security Best Practices
========================

Secret Lifecycle Management
---------------------------

::

    class SecureSecretManager(models.TransientModel):
        _name = 'secure.secret.manager'
        _description = 'Secure Secret Manager'
        
        def rotate_secret(self, old_secret_id):
            """Rotate a secret safely"""
            try:
                # Retrieve current secret
                current_secret = self.env['vault.connector'].get_secret(old_secret_id)
                
                # Generate new secret ID
                new_secret_id = str(uuid.uuid4())
                
                # Update secret data (e.g., new password)
                updated_secret = current_secret.copy()
                updated_secret['password'] = self.generate_new_password()
                updated_secret['rotated_date'] = fields.Datetime.now().isoformat()
                
                # Store new secret
                self.env['vault.connector'].set_secret(new_secret_id, updated_secret)
                
                # Update references to use new secret ID
                # (This depends on your specific model structure)
                
                return new_secret_id
                
            except Exception as e:
                raise ValidationError(f"Secret rotation failed: {e}")

Data Validation
---------------

Always validate data before storing::

    def validate_and_store_secret(self, secret_data):
        """Validate secret data before storage"""
        
        # Validate required fields
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in secret_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate data types
        if not isinstance(secret_data['username'], str):
            raise ValidationError("Username must be a string")
        
        # Validate password strength
        password = secret_data['password']
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        # Store the validated secret
        secret_id = str(uuid.uuid4())
        self.env['vault.connector'].set_secret(secret_id, secret_data)
        
        return secret_id

Testing Your Integration
========================

Unit Testing with Mocks
-----------------------

When testing modules that use vault_connector::

    from unittest.mock import patch
    from odoo.tests import common
    
    class TestMySecureModule(common.TransactionCase):
        
        @patch('vault_connector.models.vault_connector.VaultConnector.check_vault_status')
        @patch('vault_connector.models.vault_connector.VaultConnector.set_secret')
        def test_store_credentials(self, mock_set_secret, mock_status):
            """Test credential storage"""
            
            # Mock vault status as accessible
            mock_status.return_value = {'accessible': True, 'error': None}
            mock_set_secret.return_value = True
            
            # Test your module's functionality
            result = self.my_model.store_api_credentials('key123', 'secret456')
            
            # Verify vault methods were called
            mock_set_secret.assert_called_once()
            self.assertTrue(result)

Common Usage Patterns
=====================

Configuration Management
------------------------
* Store database connection strings
* Manage API keys and tokens
* Secure SSL certificate private keys
* Handle OAuth client secrets

Integration Scenarios
--------------------
* Payment gateway credentials
* Email service authentication
* Third-party API access tokens
* Cryptocurrency wallet private keys

Development Workflow
-------------------
* Separate secrets from code
* Environment-specific configurations
* Secure CI/CD pipeline secrets
* Team secret sharing

This comprehensive guide covers the primary usage patterns for the HashiCorp Vault Connector. Always follow security best practices and validate your implementation in a test environment before production deployment.