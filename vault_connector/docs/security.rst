==========
Security
==========

This document covers the security considerations, best practices, and implementation details for the Vault Connector.

Security Architecture
=====================

Defense in Depth
-----------------

The Vault Connector implements multiple layers of security:

**1. External Storage**
    * All sensitive data stored in Vault, never in Odoo database
    * Only UUID references maintained in Odoo
    * No plain text secrets in logs or displays

**2. Secure Communication**
    * HTTPS/TLS encryption for all Vault communications
    * Certificate validation enforced by default
    * Configurable TLS verification for development environments

**3. Authentication & Authorization**
    * Token-based authentication with Vault
    * Dedicated Odoo security group for access control
    * Principle of least privilege through Vault policies

**4. Data Validation**
    * UUID format validation for secret identifiers
    * Input sanitization and validation
    * Comprehensive error handling without information disclosure

Access Control
==============

Odoo Security Groups
--------------------

The module creates a dedicated security group:

**Vault User Group**
    * **Name**: ``Vault User``
    * **Technical Name**: ``group_vault_user``
    * **Purpose**: Controls who can access vault functionality
    * **Assignment**: Must be manually assigned to users

Only users in this group can:
    * Call vault connector methods
    * Store secrets in Vault
    * Retrieve secrets from Vault
    * Check vault status

Vault Policies
--------------

Recommended Vault policy for the Odoo service token::

    # Vault policy: odoo-policy.hcl
    
    # Allow CRUD operations on designated KV stores
    path "odoo-*" {
      capabilities = ["create", "read", "update", "delete", "list"]
    }
    
    # Allow token self-lookup for authentication verification
    path "auth/token/lookup-self" {
      capabilities = ["read"]
    }
    
    # Deny access to sensitive Vault operations
    path "sys/*" {
      capabilities = ["deny"]
    }
    
    # Deny access to other KV stores
    path "secret/*" {
      capabilities = ["deny"]
    }

Apply the policy::

    vault policy write odoo-policy odoo-policy.hcl
    vault token create -policy=odoo-policy -display-name="odoo-service"

Security Best Practices
========================

Token Management
----------------

**Service Token Requirements**
    * Use dedicated service tokens, not user tokens
    * Set appropriate TTL (Time To Live) for tokens
    * Implement token rotation procedures
    * Monitor token usage through Vault audit logs

**Token Storage**
    * Store tokens in secure environment variables
    * Never hardcode tokens in configuration files
    * Use orchestration secrets (Kubernetes secrets, Docker secrets)
    * Restrict access to token values

**Token Rotation**::

    # Create new token
    NEW_TOKEN=$(vault token create -policy=odoo-policy -ttl=30d -format=json | jq -r '.auth.client_token')
    
    # Update environment variable
    export VAULT_TOKEN=$NEW_TOKEN
    
    # Restart Odoo service
    systemctl restart odoo

Network Security
----------------

**TLS Configuration**
    * Always use HTTPS in production (``VAULT_SKIP_VERIFY=false``)
    * Use valid, trusted SSL certificates
    * Implement certificate pinning where possible
    * Monitor certificate expiration dates

**Network Isolation**::

    # Firewall rules - allow only Odoo server to Vault
    iptables -A OUTPUT -p tcp -s 10.0.1.10 -d 10.0.1.20 --dport 8200 -j ACCEPT
    iptables -A OUTPUT -p tcp --dport 8200 -j DROP

**VPN/Private Networks**
    * Use private networks for Vault communication
    * Implement VPN tunnels for remote access
    * Avoid exposing Vault to public internet

Environment Security
--------------------

**Environment Variables**::

    # Secure environment variable file
    # /etc/odoo/vault.env
    VAULT_ADDR=https://vault.internal.company.com:8200
    VAULT_TOKEN=hvs.CAESIJ...
    VAULT_SKIP_VERIFY=false
    
    # Set restrictive permissions
    chmod 600 /etc/odoo/vault.env
    chown odoo:odoo /etc/odoo/vault.env

**Docker Security**::

    # Use secrets instead of environment variables
    version: '3.8'
    services:
      odoo:
        secrets:
          - vault_token
          - vault_addr
        environment:
          - VAULT_TOKEN_FILE=/run/secrets/vault_token
          - VAULT_ADDR_FILE=/run/secrets/vault_addr
    
    secrets:
      vault_token:
        external: true
      vault_addr:
        external: true

Threat Model & Mitigations
==========================

Identified Threats
------------------

**T1: Token Compromise**
    * **Risk**: Unauthorized access to all secrets
    * **Mitigation**: Token rotation, audit logs, least privilege policies
    * **Detection**: Monitor unusual access patterns in Vault logs

**T2: Network Interception**
    * **Risk**: Secrets intercepted in transit  
    * **Mitigation**: TLS encryption, certificate validation
    * **Detection**: Network monitoring, certificate transparency logs

**T3: Database Compromise**
    * **Risk**: Access to secret references
    * **Mitigation**: UUID-only storage, external secret storage
    * **Impact**: Limited - only references exposed, not actual secrets

**T4: Vault Server Compromise**
    * **Risk**: Access to all stored secrets
    * **Mitigation**: Vault security hardening, encryption at rest
    * **Detection**: Vault audit logs, intrusion detection

**T5: Insider Threat**
    * **Risk**: Authorized user accessing unauthorized secrets
    * **Mitigation**: Role-based access, audit trails, least privilege
    * **Detection**: Access pattern analysis, regular access reviews

Security Monitoring
===================

Vault Audit Logs
-----------------

Enable comprehensive audit logging in Vault::

    # Enable file audit device
    vault audit enable file file_path=/var/log/vault/audit.log
    
    # Enable syslog audit device (additional)
    vault audit enable syslog tag="vault" facility="local0"

Monitor for:
    * Failed authentication attempts
    * Unusual access patterns
    * Token usage outside normal hours
    * Access to sensitive paths

Odoo Security Monitoring
------------------------

Monitor Odoo logs for:
    * Vault connection failures
    * Permission denied errors
    * Unusual API usage patterns
    * Failed secret operations

**Log Analysis Example**::

    # Monitor vault connector errors
    tail -f /var/log/odoo/odoo.log | grep "vault.connector"
    
    # Count failed vault operations per hour
    grep "vault.connector.*error" /var/log/odoo/odoo.log | \
      awk '{print $1" "$2}' | cut -c1-13 | uniq -c

Incident Response
=================

Token Compromise Response
------------------------

1. **Immediate Actions**
    * Revoke compromised token immediately
    * Generate new service token with fresh policy
    * Update environment variables
    * Restart Odoo services

2. **Investigation**
    * Review Vault audit logs for unauthorized access
    * Check Odoo logs for suspicious activity
    * Analyze network logs for unusual connections
    * Document timeline of events

3. **Recovery**
    * Rotate any secrets that may have been accessed
    * Update dependent systems with new credentials
    * Implement additional monitoring
    * Conduct security review

**Token Revocation**::

    # Revoke specific token
    vault token revoke <TOKEN_ID>
    
    # Revoke all tokens for accessor
    vault token revoke -accessor <ACCESSOR_ID>
    
    # Create new token
    vault token create -policy=odoo-policy -display-name="odoo-service-new"

Security Validation
===================

Regular Security Checks
-----------------------

**Monthly Checks**
    * Review user access to Vault User group
    * Validate token expiration dates
    * Check certificate validity
    * Review Vault audit logs

**Quarterly Checks**
    * Update Vault and Odoo to latest versions
    * Review and update Vault policies
    * Conduct access reviews
    * Test disaster recovery procedures

**Security Audit Checklist**
    * [ ] Only necessary users have Vault User group access
    * [ ] Service tokens have appropriate TTL settings
    * [ ] TLS certificates are valid and properly configured
    * [ ] Vault policies follow least privilege principle
    * [ ] Audit logging is enabled and monitored
    * [ ] Network access is properly restricted
    * [ ] Environment variables are securely stored
    * [ ] Regular token rotation is implemented

Compliance Considerations
=========================

The Vault Connector helps meet various compliance requirements:

**SOX (Sarbanes-Oxley)**
    * Segregation of duties through access controls
    * Audit trails for all secret access
    * Change management through Vault versioning

**PCI-DSS**
    * Secure storage of payment-related secrets
    * Network segmentation support
    * Regular security testing capabilities

**GDPR**
    * Data minimization through external storage
    * Right to erasure through secret deletion
    * Data protection by design and default

**HIPAA**
    * Administrative safeguards through access controls
    * Technical safeguards through encryption
    * Audit controls through comprehensive logging

Security is a shared responsibility between the Vault Connector, Vault server configuration, network infrastructure, and operational procedures. Regular security reviews and updates are essential for maintaining a strong security posture.