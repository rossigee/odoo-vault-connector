=============
API Reference
=============

This document provides detailed API documentation for the Vault Connector module.

VaultConnector Model
====================

The ``vault.connector`` model provides the main API for interacting with Vault servers.

**Model Name**: ``vault.connector``

**Model Type**: ``AbstractModel`` (no database storage)

**Description**: Secure interface for HashiCorp Vault and OpenBao operations

Methods
=======

check_vault_status()
--------------------

Check if Vault is accessible and unsealed.

**Signature**::

    @api.model
    def check_vault_status(self) -> dict

**Returns**:
    Dictionary with status information:
    
    * ``accessible`` (bool): Whether Vault is accessible
    * ``error`` (str|None): Error message if not accessible, None if accessible

**Return Examples**::

    # Successful connection
    {
        'accessible': True,
        'error': None
    }
    
    # Vault is sealed
    {
        'accessible': False,
        'error': 'Vault is sealed'
    }
    
    # Invalid token
    {
        'accessible': False,
        'error': 'Vault token is invalid or expired'
    }
    
    # Connection timeout
    {
        'accessible': False,
        'error': 'Vault connection timeout'
    }

**Usage Example**::

    status = self.env['vault.connector'].check_vault_status()
    if status['accessible']:
        print("Vault is ready for operations")
    else:
        print(f"Vault error: {status['error']}")

**Environment Variables Used**:
    * ``VAULT_ADDR`` (required)
    * ``VAULT_TOKEN`` (required) 
    * ``VAULT_SKIP_VERIFY`` (optional)

**Error Conditions**:
    * Missing environment variables
    * Network connectivity issues
    * Vault server sealed
    * Invalid or expired token
    * Connection timeout (5 second default)

get_secret(secret_id)
--------------------

Retrieve a secret from Vault.

**Signature**::

    @api.model
    def get_secret(self, secret_id: str) -> dict

**Parameters**:
    * ``secret_id`` (str): UUID of the secret to retrieve

**Returns**:
    Dictionary containing the secret data as stored in Vault

**Raises**:
    * ``ValidationError``: Invalid or empty secret_id format
    * ``Exception``: Vault connectivity or retrieval errors

**Usage Example**::

    try:
        secret_id = "123e4567-e89b-12d3-a456-426614174000"
        secret_data = self.env['vault.connector'].get_secret(secret_id)
        
        username = secret_data['username']
        password = secret_data['password']
        
    except ValidationError as e:
        print(f"Invalid secret ID: {e}")
    except Exception as e:
        print(f"Failed to retrieve secret: {e}")

**Validation Rules**:
    * ``secret_id`` must not be empty
    * ``secret_id`` must be a valid UUID format
    * Vault must be accessible (checked automatically)

**Error Messages**:
    * ``"Secret ID cannot be empty"``
    * ``"Invalid secret ID format: {secret_id}. Must be a valid UUID"``
    * ``"Vault is not accessible: {error}"``
    * ``"Access denied: Vault token may be invalid or expired"``
    * ``"Secret '{secret_id}' not found in Vault"``
    * ``"Vault is sealed or unavailable"``

set_secret(secret_id, data)
--------------------------

Store a secret in Vault.

**Signature**::

    @api.model
    def set_secret(self, secret_id: str, data: dict) -> bool

**Parameters**:
    * ``secret_id`` (str): UUID for the secret
    * ``data`` (dict): Secret data to store

**Returns**:
    ``True`` if successful

**Raises**:
    * ``ValidationError``: Invalid or empty secret_id format
    * ``Exception``: Vault connectivity or storage errors

**Usage Example**::

    import uuid
    
    try:
        secret_id = str(uuid.uuid4())
        secret_data = {
            'username': 'admin',
            'password': 'secure_password_123',
            'api_key': 'abc123def456',
            'created_at': '2025-01-01T00:00:00Z'
        }
        
        result = self.env['vault.connector'].set_secret(secret_id, secret_data)
        if result:
            print(f"Secret stored with ID: {secret_id}")
            
    except ValidationError as e:
        print(f"Invalid secret ID: {e}")
    except Exception as e:
        print(f"Failed to store secret: {e}")

**Validation Rules**:
    * ``secret_id`` must not be empty
    * ``secret_id`` must be a valid UUID format
    * ``data`` must be a dictionary
    * Data will be JSON-serializable

**Error Messages**:
    * ``"Secret ID cannot be empty"``
    * ``"Invalid secret ID format: {secret_id}. Must be a valid UUID"``
    * ``"VAULT_ADDR and VAULT_TOKEN environment variables must be set"``
    * ``"Failed to set secret in Vault: {error}"``

_get_kv_store_name()
-------------------

Get the KV store name for secret storage (internal method).

**Signature**::

    @api.model
    def _get_kv_store_name(self) -> str

**Returns**:
    String name of the KV store to use

**Logic**:
    * If ``VAULT_KV_STORE`` environment variable is set, use that value
    * Otherwise, generate ``odoo-{database_name}``

**Usage Example**::

    kv_store = self.env['vault.connector']._get_kv_store_name()
    print(f"Using KV store: {kv_store}")

**Environment Variables**:
    * ``VAULT_KV_STORE`` (optional): Custom KV store name

Configuration
=============

Environment Variables
--------------------

The module requires several environment variables for configuration:

**Required Variables**

``VAULT_ADDR``
    **Type**: String
    
    **Description**: URL of the Vault server
    
    **Format**: ``https://vault.example.com:8200``
    
    **Security**: Must use HTTPS in production

``VAULT_TOKEN``
    **Type**: String
    
    **Description**: Vault authentication token
    
    **Format**: Vault service token (e.g., ``hvs.CAESIJ...``)
    
    **Security**: Keep secret, rotate regularly

**Optional Variables**

``VAULT_SKIP_VERIFY``
    **Type**: Boolean string
    
    **Description**: Skip TLS certificate verification
    
    **Values**: ``"true"`` or ``"false"`` (default: ``"false"``)
    
    **Security Warning**: Only use ``"true"`` in development

``VAULT_KV_STORE``
    **Type**: String
    
    **Description**: Custom KV store mount path
    
    **Default**: ``odoo-{database_name}``
    
    **Example**: ``"my-secrets"``

Data Formats
============

Secret Data Structure
--------------------

Secrets are stored as JSON objects in Vault. The connector supports any JSON-serializable data:

**Simple Credentials**::

    {
        "username": "admin",
        "password": "secret123"
    }

**API Configuration**::

    {
        "api_key": "abc123def456",
        "api_secret": "secret789",
        "base_url": "https://api.example.com",
        "timeout": 30
    }

**Database Connection**::

    {
        "host": "db.example.com",
        "port": 5432,
        "database": "myapp",
        "username": "dbuser",
        "password": "dbpass",
        "ssl_mode": "require"
    }

**Complex Configuration**::

    {
        "environment": "production",
        "services": {
            "redis": {
                "host": "redis.example.com",
                "port": 6379,
                "password": "redis_secret"
            },
            "elasticsearch": {
                "hosts": ["es1.example.com", "es2.example.com"],
                "username": "elastic",
                "password": "elastic_secret"
            }
        },
        "metadata": {
            "created_by": "admin",
            "created_at": "2025-01-01T00:00:00Z",
            "version": "1.0"
        }
    }

Status Response Format
---------------------

The ``check_vault_status()`` method returns a standardized response:

**Success Response**::

    {
        "accessible": True,
        "error": None
    }

**Error Response**::

    {
        "accessible": False,
        "error": "Description of the error"
    }

**Common Error Messages**:
    * ``"VAULT_ADDR and VAULT_TOKEN environment variables must be set"``
    * ``"Vault is sealed"``
    * ``"Vault token is invalid or expired"``
    * ``"Vault connection timeout"``
    * ``"Cannot connect to Vault server"``
    * ``"Vault authentication failed: {status_code}"``

Error Handling
==============

Exception Types
---------------

**ValidationError**
    Raised for input validation failures:
    
    * Empty or invalid UUID format for secret_id
    * Missing required parameters

**Exception** (Generic)
    Raised for operational failures:
    
    * Missing environment variables
    * Vault connectivity issues
    * Authentication failures
    * Network timeouts

Error Handling Pattern
---------------------

Recommended error handling pattern for robust applications::

    def safe_vault_operation(self, secret_id):
        """Example of robust error handling"""
        try:
            # Check vault status first
            status = self.env['vault.connector'].check_vault_status()
            if not status['accessible']:
                # Handle specific vault errors
                if 'sealed' in status['error'].lower():
                    raise UserError("Vault is sealed - contact administrator")
                elif 'token' in status['error'].lower():
                    raise UserError("Vault authentication failed - check configuration")
                else:
                    raise UserError(f"Vault unavailable: {status['error']}")
            
            # Perform vault operation
            return self.env['vault.connector'].get_secret(secret_id)
            
        except ValidationError as e:
            # Handle validation errors
            raise UserError(f"Invalid input: {e}")
            
        except Exception as e:
            # Handle unexpected errors
            _logger.error(f"Vault operation failed: {e}")
            raise UserError("Secret operation failed - check logs for details")

Security Considerations
======================

API Security Notes
------------------

* **No Caching**: Secrets are never cached in memory or database
* **No Logging**: Secret values are never logged or displayed
* **UUID Validation**: Prevents path traversal and injection attacks
* **Token Validation**: All operations validate Vault token before proceeding
* **HTTPS Enforcement**: TLS verification enabled by default
* **Error Sanitization**: Error messages don't expose sensitive information

Access Control
--------------

* Users must be in the ``group_vault_user`` security group
* Vault policies control server-side access permissions
* Each database uses isolated KV store by default
* Abstract model prevents direct database access

Usage Patterns
==============

Integration Examples
-------------------

**Basic Secret Storage**::

    # Store and retrieve a simple secret
    import uuid
    
    secret_id = str(uuid.uuid4())
    self.env['vault.connector'].set_secret(secret_id, {
        'api_key': 'my-secret-key'
    })
    
    # Later retrieval
    secret = self.env['vault.connector'].get_secret(secret_id)
    api_key = secret['api_key']

**Configuration Management**::

    class MyService(models.Model):
        _name = 'my.service'
        
        name = fields.Char('Service Name')
        config_secret_id = fields.Char('Config Secret ID')
        
        def configure_service(self, config_data):
            secret_id = str(uuid.uuid4())
            self.env['vault.connector'].set_secret(secret_id, config_data)
            self.config_secret_id = secret_id
        
        def get_service_config(self):
            if not self.config_secret_id:
                return {}
            return self.env['vault.connector'].get_secret(self.config_secret_id)

**Health Check Integration**::

    def system_health_check(self):
        """Include vault status in system health"""
        health_status = {
            'database': self.check_database_health(),
            'cache': self.check_cache_health(),
        }
        
        # Add vault status
        vault_status = self.env['vault.connector'].check_vault_status()
        health_status['vault'] = {
            'status': 'healthy' if vault_status['accessible'] else 'unhealthy',
            'message': vault_status['error'] or 'Connected'
        }
        
        return health_status

This API reference provides comprehensive documentation for integrating with the Vault Connector. Always follow security best practices and validate your implementation in a test environment.