===============================
Vault Connector Usage Guide
===============================

This guide provides step-by-step instructions and examples for using the HashiCorp Vault Connector in your Odoo modules.

🚀 **Getting Started**
======================

After installation and configuration, the Vault Connector provides a secure API for storing and retrieving secrets. The module operates as a utility library for other modules to use.

**Note**: This is a technical module designed for developers building secure Odoo applications.

📋 **Basic API Usage**
======================

1. **Import the Connector** → 2. **Store Secrets** → 3. **Retrieve Secrets** → 4. **Handle Errors**

💡 **Core Concepts**
=====================

Understanding the Vault Connector
----------------------------------

The Vault Connector provides a secure interface between Odoo and HashiCorp Vault for:

* **Secret Storage**: Store sensitive data outside Odoo database
* **Token Management**: Generate and manage UUID tokens for secret references
* **Secure Retrieval**: Retrieve secrets using tokens with proper authentication
* **Error Handling**: Robust error handling and status reporting
* **UUID Enforcement**: Secret keys must be in valid UUID format, enforced by the connector to ensure uniqueness and security

🔧 **API Reference**
====================

Importing the Connector
------------------------

In your Odoo module, import the VaultConnector class::

    from odoo.addons.vault_connector.models.vault_connector import VaultConnector

Basic Usage Pattern
-------------------

1. **Create Connector Instance**::

    vault = VaultConnector()

2. **Check Vault Status**::

    status = vault.check_status()
    if status['status'] == 'connected':
        print("Vault is ready")
    else:
        print(f"Vault error: {status['message']}")

3. **Store a Secret**::

    secret_data = {
        'api_key': 'your-secret-api-key',
        'database_url': 'postgres://user:pass@host:5432/db'
    }
    token = vault.store_secret(secret_data)
    # Store only the token in your Odoo model
    your_model.vault_token = token

    # Note: The token must be a valid UUID. The connector enforces this format for security and uniqueness.

4. **Retrieve a Secret**::

    secret_data = vault.get_secret(token)
    api_key = secret_data.get('api_key')
    database_url = secret_data.get('database_url')

    # Note: The token must be a valid UUID. The connector will raise an exception if an invalid format is used.

📚 **Advanced API Methods**
===========================

Available Methods
-----------------

The VaultConnector provides these methods for secret management:

**Connection Methods**::

    # Check Vault connection and status
    status = vault.check_status()
    
    # Get detailed connection info
    info = vault.get_connection_info()

**Secret Management Methods**::

    # Store a secret and get a token
    token = vault.store_secret(data_dict)
    
    # Retrieve secret by token
    data = vault.get_secret(token)
    
    # Update existing secret
    success = vault.update_secret(token, new_data_dict)
    
    # Delete secret (optional - secrets can be left to expire)
    success = vault.delete_secret(token)

**Error Handling**::

    try:
        token = vault.store_secret(sensitive_data)
    except VaultConnectionError as e:
        # Handle connection issues
        _logger.error(f"Vault connection failed: {e}")
    except VaultAuthenticationError as e:
        # Handle authentication issues
        _logger.error(f"Vault authentication failed: {e}")
    except Exception as e:
        # Handle other errors
        _logger.error(f"Unexpected error: {e}")

Method Parameters and Returns
-----------------------------

**store_secret(data)**:

* **Parameter**: `data` (dict) - The secret data to store
* **Returns**: `str` - UUID token for retrieving the secret
* **Raises**: VaultConnectionError, VaultAuthenticationError
* **Note**: The returned token is guaranteed to be a valid UUID, enforced by the connector.

**get_secret(token)**:

* **Parameter**: `token` (str) - UUID token from store_secret
* **Returns**: `dict` - The stored secret data
* **Raises**: VaultConnectionError, VaultNotFoundError, ValidationError (if token is not a valid UUID)
* **Note**: The token must be a valid UUID, or an exception will be raised.

**check_status()**:

* **Returns**: `dict` with keys:
  * `status`: 'connected', 'error', or 'unavailable'
  * `message`: Descriptive status message
  * `vault_url`: Configured Vault URL
  * `authenticated`: Boolean authentication status

🏗️ **Integration Examples**
============================

Example 1: Secure API Key Storage
----------------------------------

Store third-party API keys securely in your Odoo module::

    from odoo import models, fields, api
    from odoo.addons.vault_connector.models.vault_connector import VaultConnector
    
    class PaymentProvider(models.Model):
        _name = 'payment.provider'
        
        name = fields.Char('Provider Name')
        vault_token = fields.Char('Vault Token', readonly=True)
        
        @api.model
        def store_api_credentials(self, api_key, secret_key):
            """Store API credentials securely in Vault"""
            vault = VaultConnector()
            credentials = {
                'api_key': api_key,
                'secret_key': secret_key,
                'provider': self.name
            }
            self.vault_token = vault.store_secret(credentials)
            return True
        
        def get_api_credentials(self):
            """Retrieve API credentials from Vault"""
            if not self.vault_token:
                return None
            vault = VaultConnector()
            return vault.get_secret(self.vault_token)

Example 2: Database Connection Strings
---------------------------------------

Securely manage database connections::

    class DatabaseConnection(models.Model):
        _name = 'database.connection'
        
        name = fields.Char('Connection Name')
        vault_token = fields.Char('Vault Token', readonly=True)
        
        def store_connection_string(self, connection_string):
            """Store database connection string securely"""
            vault = VaultConnector()
            data = {
                'connection_string': connection_string,
                'connection_name': self.name,
                'created_date': fields.Datetime.now().isoformat()
            }
            self.vault_token = vault.store_secret(data)
        
        def get_connection_string(self):
            """Get database connection string"""
            vault = VaultConnector()
            data = vault.get_secret(self.vault_token)
            return data.get('connection_string')

Example 3: Certificate Management
----------------------------------

Store SSL certificates and private keys::

    class SSLCertificate(models.Model):
        _name = 'ssl.certificate'
        
        name = fields.Char('Certificate Name')
        vault_token = fields.Char('Vault Token', readonly=True)
        
        def store_certificate(self, cert_data, private_key):
            """Store SSL certificate and private key"""
            vault = VaultConnector()
            data = {
                'certificate': cert_data,
                'private_key': private_key,
                'name': self.name,
                'expiry_date': self.calculate_expiry(cert_data)
            }
            self.vault_token = vault.store_secret(data)
        
        def get_certificate_data(self):
            """Retrieve certificate data"""
            vault = VaultConnector()
            return vault.get_secret(self.vault_token)

🔒 **Security Best Practices**
==============================

Data Handling Guidelines
-------------------------

**Never Store Secrets in Odoo**:

* Always use Vault for sensitive data storage
* Only store UUID tokens in Odoo database
* Never log or print sensitive data
* Use proper exception handling to avoid data leaks

**Token Management**:

* Store tokens in readonly fields when possible
* Implement proper access controls on token fields
* Consider token rotation for long-lived secrets
* Clean up unused tokens periodically
* Ensure tokens are valid UUIDs as enforced by the connector

**Error Handling**:

* Always use try/except blocks for Vault operations
* Log errors without exposing sensitive data
* Provide meaningful error messages to users
* Implement fallback mechanisms where appropriate

Example Secure Implementation
-----------------------------

Here's a secure pattern for handling secrets::

    import logging
    from odoo import models, fields, api
    from odoo.addons.vault_connector.models.vault_connector import (
        VaultConnector, VaultConnectionError, VaultNotFoundError
    )
    
    _logger = logging.getLogger(__name__)
    
    class SecureModel(models.Model):
        _name = 'secure.model'
        
        name = fields.Char('Name', required=True)
        vault_token = fields.Char('Vault Token', readonly=True)
        
        def store_sensitive_data(self, data):
            """Securely store sensitive data"""
            try:
                vault = VaultConnector()
                # Check connection first
                status = vault.check_status()
                if status['status'] != 'connected':
                    raise UserError("Vault is not available")
                
                # Store the secret
                self.vault_token = vault.store_secret(data)
                _logger.info(f"Secret stored for {self.name}")
                return True
                
            except VaultConnectionError:
                _logger.error("Failed to connect to Vault")
                raise UserError("Unable to store sensitive data - connection failed")
            except Exception as e:
                _logger.error(f"Unexpected error storing secret: {str(e)}")
                raise UserError("Unable to store sensitive data")
        
        def get_sensitive_data(self):
            """Securely retrieve sensitive data"""
            if not self.vault_token:
                return None
                
            try:
                vault = VaultConnector()
                return vault.get_secret(self.vault_token)
            except VaultNotFoundError:
                _logger.warning(f"Secret not found for {self.name}")
                return None
            except VaultConnectionError:
                _logger.error("Failed to connect to Vault")
                return None
            except Exception as e:
                _logger.error(f"Error retrieving secret: {str(e)}")
                return None

📋 **Common Workflows**
=======================

Workflow 1: API Key Management
-------------------------------

**Scenario**: Securely manage third-party API keys for payment processors

1. **Create Model**: Define a model for payment providers
2. **Store Credentials**: Use Vault to store API keys and secrets::

    provider = self.env['payment.provider'].create({
        'name': 'Stripe Payment Gateway'
    })
    provider.store_api_credentials(api_key, secret_key)

3. **Use Credentials**: Retrieve when making API calls::

    credentials = provider.get_api_credentials()
    api_key = credentials['api_key']
    # Make secure API call

4. **Rotate Keys**: Update credentials when needed::

    provider.store_api_credentials(new_api_key, new_secret_key)

Workflow 2: Database Connection Security
-----------------------------------------

**Scenario**: Securely store database connection strings for integrations

1. **Define Connection Model**: Create model for external database connections
2. **Store Connection String**: Use Vault for connection details::

    connection = self.env['database.connection'].create({
        'name': 'Customer CRM Database'
    })
    connection.store_connection_string('postgres://user:password@host:5432/db')

3. **Use Connection**: Retrieve for database operations::

    conn_string = connection.get_connection_string()
    # Establish database connection securely

4. **Monitor & Rotate**: Regular credential rotation for security

Workflow 3: Certificate Management
-----------------------------------

**Scenario**: Manage SSL certificates and private keys for integrations

1. **Certificate Storage**: Store certificates securely::

    cert = self.env['ssl.certificate'].create({
        'name': 'API Gateway Certificate'
    })
    cert.store_certificate(cert_data, private_key_data)

2. **Certificate Usage**: Retrieve for HTTPS connections::

    cert_data = cert.get_certificate_data()
    certificate = cert_data['certificate']
    private_key = cert_data['private_key']

3. **Expiry Management**: Monitor and renew certificates
4. **Automated Deployment**: Update systems with new certificates

Workflow 4: Multi-Environment Secrets
--------------------------------------

**Scenario**: Different secrets for development, staging, and production

1. **Environment-Specific Storage**: Use different Vault paths or instances
2. **Configuration Management**: Environment variables for Vault selection::

    # Different Vault configurations per environment
    VAULT_ADDR=https://vault-prod.company.com:8200  # Production
    VAULT_ADDR=https://vault-staging.company.com:8200  # Staging

3. **Secret Versioning**: Track secret versions across environments
4. **Deployment Automation**: Automated secret deployment with CI/CD

🔍 **Advanced Topics**
======================

Performance Considerations
---------------------------

**Connection Pooling**: The VaultConnector creates new connections for each request. For high-volume applications, consider:

* Implementing connection pooling in your module
* Caching Vault status checks
* Batching multiple secret operations

**Error Recovery**: Implement robust error handling:

* Retry logic for temporary network issues
* Graceful degradation when Vault is unavailable
* Fallback mechanisms for critical operations

**Monitoring**: Track Vault operations:

* Log all Vault interactions (without sensitive data)
* Monitor connection performance
* Set up alerts for Vault failures

Custom Configuration
--------------------

**Environment Variables**: Customize Vault connection:

* `VAULT_ADDR`: Vault server URL
* `VAULT_TOKEN`: Authentication token
* `VAULT_KV_PATH`: Custom KV store path (default: 'secret')
* `VAULT_TIMEOUT`: Request timeout in seconds

**Multiple Vault Instances**: For complex deployments:

* Different Vault instances per environment
* Vault clustering for high availability
* Geographic distribution for global deployments

Migration and Backup
--------------------

**Secret Migration**: When changing Vault instances:

1. Export secrets from old Vault (if possible)
2. Re-encrypt and import to new Vault
3. Update tokens in Odoo records
4. Verify all secrets accessible

**Backup Strategy**: Ensure business continuity:

* Regular Vault backups (follow HashiCorp guidelines)
* Token inventory and mapping
* Recovery procedures documentation
* Test restoration processes

📞 **Troubleshooting**
======================

Common Issues
-------------

**"Vault not accessible" Error**:

* Check VAULT_ADDR and VAULT_TOKEN environment variables
* Verify network connectivity to Vault server
* Check Vault server status and unseal state
* Verify token has proper permissions

**"Import Error" for VaultConnector**:

* Ensure module is properly installed
* Check module is in correct addons path
* Restart Odoo server after installation
* Verify no circular import dependencies

**"Secret not found" Error**:

* Verify token exists and is correct
* Check if secret has been deleted from Vault
* Verify KV store path configuration
* Check Vault token permissions for read access

**"Invalid secret ID format" Error**:

* Ensure the token provided is a valid UUID
* Verify that the token was generated or stored correctly
* Check for any manual edits to token fields that might have corrupted the UUID format

**Performance Issues**:

* Check network latency to Vault server
* Monitor Vault server performance
* Implement connection pooling if needed
* Consider caching for frequently accessed secrets

Debugging Tips
--------------

**Enable Debug Logging**: Add to Odoo configuration::

    [logger_vault_connector]
    level = DEBUG
    handlers = console
    qualname = odoo.addons.vault_connector

**Test Connection Manually**::

    # In Odoo shell
    from odoo.addons.vault_connector.models.vault_connector import VaultConnector
    vault = VaultConnector()
    print(vault.check_status())

**Verify Environment Variables**::

    import os
    print("VAULT_ADDR:", os.environ.get('VAULT_ADDR'))
    print("VAULT_TOKEN:", os.environ.get('VAULT_TOKEN', 'Not set'))

Getting Help
------------

For advanced troubleshooting, check:

1. **Odoo Logs**: Review server logs for detailed error messages
2. **Vault Logs**: Check Vault audit logs for access attempts
3. **Network Connectivity**: Test HTTPS connection to Vault
4. **Token Permissions**: Verify Vault token policies and capabilities