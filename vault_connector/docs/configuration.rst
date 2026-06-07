==============
Configuration
==============

The HashiCorp Vault Connector requires proper configuration of environment variables and Vault server setup before use.

Environment Variables
=====================

Required Variables
------------------

These environment variables must be set for the module to function:

``VAULT_ADDR``
    The URL of your HashiCorp Vault server.
    
    **Example**: ``https://vault.company.com:8200``
    
    **Required**: Yes
    
    **Security Note**: Always use HTTPS in production

``VAULT_TOKEN``
    Authentication token for accessing Vault.
    
    **Example**: ``hvs.CAESIJ2B...`` (Vault service token)
    
    **Required**: Yes
    
    **Security Note**: Use a dedicated service token with minimal required permissions

Optional Variables
------------------

``VAULT_SKIP_VERIFY``
    Skip TLS certificate verification (development only).
    
    **Default**: ``false``
    
    **Values**: ``true`` or ``false``
    
    **Security Warning**: Never use ``true`` in production environments

``VAULT_KV_STORE``
    Custom name for the KV secrets engine mount.
    
    **Default**: ``odoo-{database_name}``
    
    **Example**: ``my-custom-kv-store``

Setting Environment Variables
=============================

Linux/Unix Systems
------------------

Add to your shell profile or systemd service file::

    export VAULT_ADDR="https://vault.company.com:8200"
    export VAULT_TOKEN="hvs.CAESIJ2B..."
    export VAULT_SKIP_VERIFY="false"

For systemd services, add to the ``[Service]`` section::

    [Service]
    Environment=VAULT_ADDR=https://vault.company.com:8200
    Environment=VAULT_TOKEN=hvs.CAESIJ2B...

Docker Environments
-------------------

In ``docker-compose.yml``::

    services:
      odoo:
        environment:
          - VAULT_ADDR=https://vault.company.com:8200
          - VAULT_TOKEN=hvs.CAESIJ2B...
          - VAULT_SKIP_VERIFY=false

Or use an environment file (``.env``)::

    VAULT_ADDR=https://vault.company.com:8200
    VAULT_TOKEN=hvs.CAESIJ2B...
    VAULT_SKIP_VERIFY=false

Kubernetes
----------

Create a secret::

    kubectl create secret generic vault-config \
      --from-literal=VAULT_ADDR=https://vault.company.com:8200 \
      --from-literal=VAULT_TOKEN=hvs.CAESIJ2B...

Reference in deployment::

    spec:
      containers:
      - name: odoo
        envFrom:
        - secretRef:
            name: vault-config

Vault Server Configuration
==========================

KV Secrets Engine
-----------------

Enable the KV version 2 secrets engine if not already enabled::

    # Enable KV v2 at default path
    vault secrets enable -version=2 kv
    
    # Or enable at custom path
    vault secrets enable -path=odoo-secrets -version=2 kv

Create Vault Policy
-------------------

Create a policy file (``odoo-policy.hcl``)::

    # Allow reading and writing secrets in the designated KV store
    path "odoo-*" {
      capabilities = ["create", "read", "update", "delete", "list"]
    }
    
    # Allow token self-lookup for authentication verification
    path "auth/token/lookup-self" {
      capabilities = ["read"]
    }

Apply the policy::

    vault policy write odoo-policy odoo-policy.hcl

Create Service Token
--------------------

Generate a token with the policy::

    vault token create -policy=odoo-policy -display-name="odoo-service"

**Important**: Save the token securely and use it as the ``VAULT_TOKEN`` environment variable.

Network Configuration
=====================

Firewall Rules
--------------

Ensure Odoo server can reach Vault on the configured port (typically 8200)::

    # Allow outbound HTTPS to Vault server
    iptables -A OUTPUT -p tcp --dport 8200 -d vault.company.com -j ACCEPT

TLS Certificates
----------------

For production deployments:

1. **Use Valid Certificates**: Ensure Vault has proper TLS certificates
2. **Certificate Chain**: Include intermediate certificates if needed
3. **Certificate Verification**: Keep ``VAULT_SKIP_VERIFY=false``

Testing Configuration
=====================

Test Vault Connectivity
------------------------

Use the module's status check method::

    # In Odoo shell or through API
    status = self.env['vault.connector'].check_vault_status()
    print(f"Vault accessible: {status['accessible']}")
    if not status['accessible']:
        print(f"Error: {status['error']}")

Manual Vault Test
-----------------

Test directly with curl::

    curl -H "X-Vault-Token: $VAULT_TOKEN" \
         $VAULT_ADDR/v1/sys/seal-status

Expected response should show ``"sealed": false``.

Configuration Validation
=========================

Common Configuration Issues
---------------------------

**Connection Refused**
    * Check ``VAULT_ADDR`` is correct and reachable
    * Verify firewall rules allow connection
    * Ensure Vault server is running

**403 Forbidden**
    * Verify ``VAULT_TOKEN`` is valid and not expired
    * Check token has required policies attached
    * Ensure KV secrets engine is enabled

**Certificate Errors**
    * Use valid TLS certificates in production
    * Set ``VAULT_SKIP_VERIFY=true`` only for development
    * Check certificate chain is complete

**Seal Status Errors**
    * Ensure Vault is unsealed
    * Check Vault server logs for errors
    * Verify Vault cluster status if using HA setup

Security Best Practices
========================

Token Management
----------------
* **Rotate Regularly**: Implement token rotation schedules
* **Minimal Permissions**: Use least-privilege access policies
* **Monitor Usage**: Track token usage through Vault audit logs
* **Secure Storage**: Never log or display tokens in plain text

Network Security
----------------
* **HTTPS Only**: Always use encrypted connections in production
* **Network Isolation**: Use private networks when possible
* **Certificate Validation**: Enable full TLS verification
* **Firewall Rules**: Restrict access to necessary ports only

Environment Security
--------------------
* **Secure Variables**: Protect environment variable access
* **No Hardcoding**: Never hardcode credentials in configuration files
* **Access Control**: Limit who can modify environment variables
* **Audit Access**: Monitor configuration changes

The module is now properly configured and ready for secure operation.