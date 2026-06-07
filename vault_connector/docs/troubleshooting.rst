===============
Troubleshooting
===============

This document provides solutions to common issues when using the Vault Connector.

Common Issues
=============

Connection Problems
------------------

**Vault Connection Timeout**

*Symptoms*:
    * Error: "Vault connection timeout"
    * Operations hang for 5+ seconds before failing

*Causes*:
    * Network connectivity issues
    * Firewall blocking connections
    * Vault server down or overloaded
    * Incorrect ``VAULT_ADDR`` configuration

*Solutions*::

    # Test network connectivity
    curl -I $VAULT_ADDR/v1/sys/health
    
    # Check firewall rules
    telnet vault.example.com 8200
    
    # Verify DNS resolution
    nslookup vault.example.com
    
    # Test with increased timeout (temporary debug)
    curl -m 10 $VAULT_ADDR/v1/sys/seal-status

**Cannot Connect to Vault Server**

*Symptoms*:
    * Error: "Cannot connect to Vault server"
    * Immediate connection failure

*Causes*:
    * Wrong ``VAULT_ADDR`` URL
    * Vault server not running
    * Network routing issues
    * DNS resolution failure

*Solutions*::

    # Verify VAULT_ADDR format
    echo $VAULT_ADDR
    # Should be: https://vault.example.com:8200
    
    # Test basic connectivity
    ping vault.example.com
    
    # Check port accessibility
    nc -zv vault.example.com 8200
    
    # Verify Vault server status
    systemctl status vault  # On Vault server

Authentication Issues
--------------------

**Vault Token Invalid or Expired**

*Symptoms*:
    * Error: "Vault token is invalid or expired"
    * Error: "Access denied: Vault token may be invalid or expired"

*Causes*:
    * Token has expired (TTL exceeded)
    * Token was revoked
    * Wrong token in ``VAULT_TOKEN``
    * Token lacks required policies

*Solutions*::

    # Check token status
    vault token lookup $VAULT_TOKEN
    
    # Check token TTL
    vault token lookup -format=json $VAULT_TOKEN | jq '.data.ttl'
    
    # Renew token if possible
    vault token renew $VAULT_TOKEN
    
    # Create new token with policy
    vault token create -policy=odoo-policy -display-name="odoo-service"

**Permission Denied in Odoo**

*Symptoms*:
    * Users cannot access vault functionality
    * "Access Denied" errors in Odoo

*Causes*:
    * User not in ``Vault User`` group
    * Security permissions not properly configured

*Solutions*:

1. Check user group membership:
    * Go to Settings → Users & Companies → Users
    * Select the user
    * Verify "Vault User" group is assigned

2. Verify security configuration::

    # Check security group exists
    # Settings → Technical → Security → Groups
    # Search for "Vault User"

Vault Server Issues
------------------

**Vault is Sealed**

*Symptoms*:
    * Error: "Vault is sealed"
    * All operations fail

*Causes*:
    * Vault server restarted and requires unsealing
    * Vault sealed due to error threshold
    * Manual sealing operation

*Solutions*::

    # Check seal status
    vault status
    
    # Unseal vault (requires unseal keys)
    vault operator unseal <key1>
    vault operator unseal <key2>
    vault operator unseal <key3>
    
    # Verify unsealed
    vault status

**KV Secrets Engine Not Found**

*Symptoms*:
    * Error: "Secret 'uuid' not found in Vault"
    * 404 errors when accessing secrets

*Causes*:
    * KV secrets engine not enabled
    * Wrong KV store path configuration
    * Vault policy doesn't allow access to path

*Solutions*::

    # List enabled secrets engines
    vault secrets list
    
    # Enable KV v2 secrets engine
    vault secrets enable -version=2 kv
    
    # Enable at custom path
    vault secrets enable -path=odoo-mydb -version=2 kv
    
    # Check policy allows access
    vault policy read odoo-policy

Configuration Issues
-------------------

**Missing Environment Variables**

*Symptoms*:
    * Error: "VAULT_ADDR and VAULT_TOKEN environment variables must be set"

*Causes*:
    * Environment variables not set
    * Variables not exported to Odoo process
    * Typos in variable names

*Solutions*::

    # Check environment variables
    echo $VAULT_ADDR
    echo $VAULT_TOKEN
    
    # For systemd services, check environment
    systemctl show odoo --property=Environment
    
    # For Docker, check container environment
    docker exec odoo env | grep VAULT

**Certificate/TLS Issues**

*Symptoms*:
    * SSL certificate verification errors
    * TLS handshake failures

*Causes*:
    * Self-signed certificates
    * Certificate chain incomplete
    * Certificate expired
    * ``VAULT_SKIP_VERIFY`` misconfiguration

*Solutions*::

    # Test certificate validity
    openssl s_client -connect vault.example.com:8200 -servername vault.example.com
    
    # Check certificate expiration
    echo | openssl s_client -connect vault.example.com:8200 2>/dev/null | openssl x509 -noout -dates
    
    # Temporary bypass (development only)
    export VAULT_SKIP_VERIFY=true
    
    # Fix certificate chain
    # Ensure intermediate certificates are included in server config

Diagnostic Commands
==================

System Diagnostics
------------------

**Check Vault Connector Status**

Use Odoo shell to test the connector::

    # Enter Odoo shell
    odoo shell -d your_database
    
    # Test vault status
    status = env['vault.connector'].check_vault_status()
    print(f"Accessible: {status['accessible']}")
    print(f"Error: {status['error']}")

**Network Connectivity Test**::

    # Test basic connectivity
    curl -I $VAULT_ADDR/v1/sys/health
    
    # Test with authentication
    curl -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/sys/seal-status
    
    # Test KV store access
    curl -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/odoo-mydb/metadata

**Environment Validation**::

    # Check all required variables
    env | grep VAULT
    
    # Validate VAULT_ADDR format
    echo $VAULT_ADDR | grep -E '^https?://[^/]+:[0-9]+$'
    
    # Test token format
    echo $VAULT_TOKEN | grep -E '^hvs\.'

Vault Server Diagnostics
------------------------

**Server Status Check**::

    # Overall status
    vault status
    
    # Detailed system info
    vault read sys/health
    
    # List mounted secrets engines
    vault secrets list
    
    # Check audit logs
    vault audit list

**Token Diagnostics**::

    # Token information
    vault token lookup $VAULT_TOKEN
    
    # Token capabilities on path
    vault token capabilities $VAULT_TOKEN odoo-mydb/data/test
    
    # Policy information
    vault policy read odoo-policy

**Performance Diagnostics**::

    # Vault server metrics (if enabled)
    curl $VAULT_ADDR/v1/sys/metrics
    
    # Check for rate limiting
    vault read sys/quotas/rate-limit
    
    # Monitor vault logs
    journalctl -u vault -f

Debugging Mode
==============

Enable Detailed Logging
-----------------------

**Odoo Logging**

Add to Odoo configuration::

    [logger_vault_connector]
    level = DEBUG
    handlers = console
    qualname = vault_connector

**Vault Server Logging**

Increase Vault log level::

    # In vault.hcl
    log_level = "DEBUG"
    
    # Or set environment variable
    export VAULT_LOG_LEVEL=DEBUG

**Network Debugging**

Capture network traffic::

    # Using tcpdump
    tcpdump -i any -A host vault.example.com and port 8200
    
    # Using curl verbose mode
    curl -v -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/sys/seal-status

Performance Issues
==================

Slow Response Times
------------------

**Symptoms**:
    * Operations take several seconds
    * Timeouts under load

**Causes & Solutions**:

1. **Network Latency**::

    # Test latency
    ping vault.example.com
    
    # Use closer Vault instance
    # Configure load balancer

2. **Vault Server Overload**::

    # Check Vault metrics
    vault read sys/metrics
    
    # Scale Vault cluster
    # Optimize Vault configuration

3. **Large Secret Sizes**::

    # Check secret size
    vault kv get -format=json odoo-mydb/uuid | jq '.data | length'
    
    # Split large secrets
    # Use references for large data

Memory Usage
-----------

**High Memory Usage**

*Causes*:
    * Large secrets being processed
    * Memory leaks in requests library
    * Multiple concurrent operations

*Solutions*:
    * Monitor Odoo memory usage
    * Implement connection pooling
    * Use streaming for large operations
    * Regular Odoo restarts if needed

Error Recovery
==============

Automatic Recovery Strategies
----------------------------

**Retry Logic Example**::

    def robust_vault_operation(self, secret_id, max_retries=3):
        """Implement retry logic for vault operations"""
        import time
        
        for attempt in range(max_retries):
            try:
                return self.env['vault.connector'].get_secret(secret_id)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                error_msg = str(e).lower()
                if 'timeout' in error_msg or 'connection' in error_msg:
                    # Retry on network issues
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    # Don't retry on auth/permission errors
                    raise

**Fallback Mechanisms**::

    def get_secret_with_fallback(self, secret_id, fallback_config=None):
        """Get secret with fallback to default configuration"""
        try:
            return self.env['vault.connector'].get_secret(secret_id)
        except Exception as e:
            _logger.warning(f"Vault access failed: {e}")
            
            if fallback_config:
                _logger.info("Using fallback configuration")
                return fallback_config
            else:
                raise ValidationError("Vault unavailable and no fallback configured")

Manual Recovery Procedures
-------------------------

**Service Recovery Steps**:

1. **Check Vault Server**
    * Verify Vault is running and unsealed
    * Check Vault logs for errors
    * Restart Vault if necessary

2. **Verify Network**
    * Test connectivity from Odoo server
    * Check firewall rules
    * Verify DNS resolution

3. **Validate Configuration**
    * Check environment variables
    * Verify token is valid
    * Test token permissions

4. **Restart Services**
    * Restart Odoo to reload environment
    * Clear any cached connections
    * Monitor logs during restart

**Emergency Procedures**:

If Vault is completely unavailable:

1. **Assess Impact**
    * Identify which services depend on Vault
    * Document affected functionality
    * Communicate to stakeholders

2. **Temporary Measures**
    * Use fallback configurations where possible
    * Disable features that require secrets
    * Monitor for service degradation

3. **Recovery Actions**
    * Restore Vault from backup if needed
    * Recreate secrets if necessary
    * Validate all services after recovery

Getting Help
============

Information to Collect
---------------------

When seeking support, gather this information:

**Environment Details**:
    * Odoo version and edition
    * Vault Connector module version
    * Vault server version (HashiCorp Vault or OpenBao)
    * Operating system and version

**Configuration Information**:
    * ``VAULT_ADDR`` (sanitized)
    * Environment variable settings (without token values)
    * Network topology (Odoo → Vault path)

**Error Details**:
    * Complete error messages
    * Relevant log entries
    * Steps to reproduce
    * Frequency of occurrence

**Diagnostic Output**::

    # Vault status from Odoo
    status = env['vault.connector'].check_vault_status()
    
    # Vault server status
    vault status
    
    # Network connectivity
    curl -I $VAULT_ADDR/v1/sys/health

Support Channels
---------------

* **GitHub Issues**: Report bugs and feature requests
* **Documentation**: Check latest documentation for updates
* **Community Forums**: Search for similar issues
* **Professional Support**: Available for enterprise deployments

This troubleshooting guide covers the most common issues. For complex problems, enable debug logging and gather detailed diagnostic information before seeking support.