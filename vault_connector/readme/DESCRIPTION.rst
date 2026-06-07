=====================================
HashiCorp Vault Connector for Odoo
=====================================

A secure integration module that provides a robust connection interface between Odoo and HashiCorp Vault for storing and retrieving sensitive data like private keys, API tokens, certificates, and other secrets.

🚀 **Key Features**
===================

Secure Secret Storage
---------------------
* **Vault Integration**: Direct connection to HashiCorp Vault or OpenBao instances
* **KV Store Support**: Uses Vault's Key-Value secrets engine for data storage
* **Token-based Authentication**: Secure authentication using Vault tokens
* **Status Monitoring**: Real-time Vault connection status checking

Data Protection
---------------
* **No Plain Text Storage**: Secrets never stored in Odoo database
* **UUID Token System**: Only unique identifiers stored in Odoo
* **External Security**: Leverages Vault's enterprise-grade security features
* **Audit Trails**: All secret access logged through Vault's audit system

Developer-Friendly API
----------------------
* **Simple Interface**: Easy-to-use methods for storing and retrieving secrets
* **Error Handling**: Comprehensive error categorization and handling
* **Configuration Management**: Environment variable-based configuration
* **Extensible Design**: Clean API for other modules to build upon

Enterprise Integration
----------------------
* **Production Ready**: Designed for enterprise Odoo deployments
* **Scalable Architecture**: Supports high-availability Vault clusters
* **Compliance Support**: Helps meet security and audit requirements
* **Dependency Module**: Serves as foundation for other secure modules

🔒 **Security & Architecture**
===============================

Connection Security
-------------------
* **HTTPS Only**: All communications encrypted in transit
* **Token Authentication**: Secure token-based access to Vault
* **Network Isolation**: Supports private network configurations
* **Certificate Validation**: Full TLS certificate verification

Data Architecture
-----------------
* **External Storage**: All sensitive data stored outside Odoo
* **Token References**: Only UUID tokens maintained in database
* **Path Organization**: Configurable Vault paths for data organization
* **Atomic Operations**: Consistent data operations with proper error handling

Access Control
--------------
* **Vault Policies**: Leverages Vault's native policy system
* **Principle of Least Privilege**: Minimal required permissions
* **Audit Logging**: Complete audit trail through Vault
* **Token Management**: Proper token lifecycle management

🏢 **Business Use Cases**
==========================

Secure Configuration Management
-------------------------------
* Store API keys and tokens securely
* Manage database connection strings
* Protect certificate private keys
* Secure third-party service credentials

Compliance & Governance
------------------------
* Meet security audit requirements
* Implement proper secret rotation
* Maintain audit trails for access
* Support compliance frameworks

Development & Operations
------------------------
* Separate secrets from code
* Enable secure CI/CD pipelines
* Support multiple environments
* Facilitate secret sharing between teams

Integration Foundation
----------------------
* Serve as security layer for other modules
* Enable cryptocurrency operations
* Support secure payment processing
* Foundation for custom security modules

📋 **Requirements**
===================

Technical Prerequisites
-----------------------
* **Odoo 16.0+**: Compatible with Odoo 16 and later versions
* **Python Libraries**: `requests` package for HTTP operations
* **HashiCorp Vault**: External Vault or OpenBao instance (v1.0+)
* **Network Access**: HTTPS connectivity between Odoo and Vault

Vault Configuration
-------------------
* **KV Secrets Engine**: Version 2 KV store enabled
* **Authentication**: Valid Vault token with appropriate permissions
* **Network Accessibility**: Vault reachable from Odoo server
* **TLS Configuration**: Proper SSL/TLS certificates configured

User Knowledge
--------------
* **Vault Basics**: Understanding of Vault concepts and operation
* **Secret Management**: Knowledge of secure secret handling practices
* **Network Security**: Understanding of secure network configurations
* **Odoo Administration**: Familiarity with Odoo module installation

⚠️ **Security Warnings**
=========================

Production Deployment
---------------------
**SECURITY CRITICAL**: This module handles sensitive data. Ensure proper security measures are in place before production use.

Vault Security
--------------
* **Secure Vault Instance**: Use properly configured, secured Vault installation
* **Token Management**: Regularly rotate tokens and follow Vault best practices
* **Network Security**: Use HTTPS and secure network connections only
* **Access Monitoring**: Monitor Vault access logs for suspicious activity

Configuration Security
-----------------------
* **Environment Variables**: Store Vault credentials in secure environment variables
* **No Hardcoding**: Never hardcode tokens or URLs in configuration files
* **Least Privilege**: Use minimal required permissions for Vault tokens
* **Regular Updates**: Keep Vault and this module updated with security patches

🎯 **Getting Started**
======================

See the CONFIGURE.rst file for detailed installation and setup instructions.
See the USAGE.rst file for API usage examples and integration patterns.

This module serves as a foundation for other modules requiring secure secret storage and provides a clean API for developers to build secure applications.

📞 **Support & Contributing**
=============================

This module is actively developed and maintained. See CONTRIBUTORS.rst for contributor information and guidelines.

For issues, feature requests, or contributions, please follow standard Odoo Community Association practices.