# HashiCorp Vault Connector

This module provides a secure connection interface to HashiCorp Vault for storing and retrieving sensitive data in Odoo.

## Features

- **Vault Connectivity**: Secure connection to HashiCorp Vault servers
- **Status Checking**: Real-time vault seal status and accessibility checks  
- **Secret Management**: Store and retrieve secrets from Vault KV stores
- **Error Handling**: Comprehensive error categorization and user-friendly messages
- **Environment Configuration**: Configurable via environment variables
- **Multi-tenant**: Automatic KV store naming based on database

## Configuration

Set these environment variables for your Odoo instance:

```bash
# Required
export VAULT_ADDR="https://your-vault-server:8200"
export VAULT_TOKEN="your-vault-token"

# Optional
export VAULT_SKIP_VERIFY="true"              # Skip TLS verification (dev only)
export VAULT_KV_STORE="my-custom-store"      # Custom KV store name
```

If `VAULT_KV_STORE` is not set, it defaults to `odoo-{database_name}`.

## Usage in Other Modules

Add `vault_connector` as a dependency in your module's `__manifest__.py`:

```python
{
    "depends": [
        "base",
        "vault_connector",  # Add this dependency
    ],
    # ...
}
```

Then use the vault connector in your models:

```python
# Store a secret
self.env['vault.connector'].set_secret('my-secret-id', {
    'username': 'admin',
    'password': 'secret123'
})

# Retrieve a secret
secret_data = self.env['vault.connector'].get_secret('my-secret-id')
username = secret_data['username']

# Check vault status
status = self.env['vault.connector'].check_vault_status()
if status['accessible']:
    print("Vault is accessible")
else:
    print(f"Vault error: {status['error']}")
```

## Security Notes

- Always use HTTPS for vault connections in production
- Rotate vault tokens regularly
- Use appropriate Vault policies to limit access
- Never log or display vault tokens or secrets
- The vault connector uses AbstractModel - it doesn't store any data in Odoo's database

## Dependencies

- Python `requests` library
- HashiCorp Vault server (tested with v2.2.2)
- Odoo 16.0+