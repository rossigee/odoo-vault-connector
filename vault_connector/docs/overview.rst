========
Overview
========

The HashiCorp Vault Connector is a foundational security module for Odoo that provides a robust, secure interface for storing and retrieving sensitive data using HashiCorp Vault or OpenBao.

Architecture
============

The module follows a secure-by-design architecture:

External Storage
----------------
* All sensitive data is stored in HashiCorp Vault, never in the Odoo database
* Only UUID tokens are maintained in Odoo to reference vault secrets
* No plain text secrets are ever logged or displayed

Abstract Model Design
---------------------
* Uses Odoo's AbstractModel pattern for the connector
* No database tables created for storing secrets
* All operations are transient and secure

Token-Based Security
--------------------
* UUID validation ensures only properly formatted secret identifiers
* Vault token authentication for all operations
* Configurable TLS verification for production security

Use Cases
=========

Configuration Management
------------------------
* Store database connection strings securely
* Manage API keys and service tokens
* Protect SSL/TLS certificate private keys
* Secure third-party service credentials

Compliance & Governance
------------------------
* Meet security audit requirements
* Implement proper secret rotation policies
* Maintain complete audit trails through Vault
* Support various compliance frameworks (SOX, PCI-DSS, etc.)

Development & Operations
------------------------
* Separate secrets from application code
* Enable secure CI/CD pipeline configurations
* Support multiple deployment environments
* Facilitate secure secret sharing between teams

Integration Foundation
----------------------
* Serve as security foundation for other Odoo modules
* Enable secure cryptocurrency and payment processing
* Support custom security-focused modules
* Provide consistent secret management across applications

Security Benefits
=================

Data Protection
---------------
* **Zero Database Exposure**: Secrets never stored in Odoo database
* **Encryption in Transit**: All communications over HTTPS/TLS
* **Encryption at Rest**: Vault handles secure storage encryption
* **Access Control**: Fine-grained permissions through Vault policies

Audit & Compliance
-------------------
* **Complete Audit Trail**: All secret access logged in Vault
* **Access Monitoring**: Real-time visibility into secret usage
* **Policy Enforcement**: Vault's native policy system integration
* **Compliance Support**: Meets enterprise security requirements

Operational Security
--------------------
* **Token Lifecycle Management**: Proper token rotation and expiration
* **Network Isolation**: Supports private network deployments
* **High Availability**: Compatible with Vault cluster configurations
* **Disaster Recovery**: Leverages Vault's backup and recovery features

Technical Architecture
======================

Component Overview
------------------
* **VaultConnector Model**: Core AbstractModel providing the API
* **Environment Configuration**: Secure configuration via environment variables
* **Error Handling**: Comprehensive error categorization and user feedback
* **Status Monitoring**: Real-time vault connectivity and seal status checks

Integration Pattern
-------------------
Other modules depend on vault_connector and use its simple API::

    # Store a secret
    self.env['vault.connector'].set_secret(secret_id, secret_data)
    
    # Retrieve a secret
    secret_data = self.env['vault.connector'].get_secret(secret_id)
    
    # Check vault status
    status = self.env['vault.connector'].check_vault_status()

This pattern ensures consistent, secure secret management across all dependent modules.