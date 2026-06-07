=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[16.0.1.0.1] - 2025-07-01
==========================

Added
-----

Core Functionality
~~~~~~~~~~~~~~~~~~~
* Initial release of Vault Connector for Odoo 16
* Secure connection interface to Vault servers (HashiCorp Vault and OpenBao)
* Real-time vault seal status and accessibility checks
* Secret storage and retrieval from Vault KV stores
* UUID validation for secret identifiers to prevent injection attacks
* Abstract model design ensuring no sensitive data stored in Odoo database

API Methods
~~~~~~~~~~~
* ``check_vault_status()`` - Verify vault connectivity and seal status
* ``get_secret(secret_id)`` - Retrieve secrets from Vault with validation
* ``set_secret(secret_id, data)`` - Store secrets in Vault securely
* ``_get_kv_store_name()`` - Get KV store name with multi-tenant support

Configuration & Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Environment variable configuration support:

  * ``VAULT_ADDR`` - Vault server URL (required)
  * ``VAULT_TOKEN`` - Authentication token (required)  
  * ``VAULT_SKIP_VERIFY`` - Skip TLS verification (optional, dev only)
  * ``VAULT_KV_STORE`` - Custom KV store name (optional)

* Multi-tenant KV store naming based on database name
* Automatic fallback to ``odoo-{database_name}`` pattern

Security Features
~~~~~~~~~~~~~~~~~
* Dedicated ``group_vault_user`` security group for access control
* Token-based authentication with Vault
* TLS certificate verification enabled by default
* Comprehensive error handling without exposing sensitive information
* No caching or logging of secret values
* Input validation and sanitization

Error Handling
~~~~~~~~~~~~~~
* Comprehensive error categorization with user-friendly messages
* Specific error handling for common scenarios:

  * Connection timeouts and network issues
  * Authentication failures and token expiration
  * Vault seal status detection
  * Secret not found conditions
  * Permission denied scenarios

* Graceful degradation with informative error messages

Testing & Quality
~~~~~~~~~~~~~~~~~
* Comprehensive test suite with 19+ test methods
* Full mocking of external dependencies for reliable testing
* Error condition testing and edge case coverage
* Docker-based test environment with PostgreSQL
* Automated test execution script

Documentation
~~~~~~~~~~~~~
* Complete RST documentation suite:

  * Installation and configuration guides
  * API reference with examples
  * Security best practices
  * Troubleshooting guide
  * Usage patterns and integration examples

* Comprehensive README with quick start guide
* Security warnings and production deployment notes

Dependencies
~~~~~~~~~~~~
* Python ``requests`` library for HTTP operations
* Compatible with HashiCorp Vault v1.0+ and OpenBao
* Requires Odoo 16.0 or later
* No additional database requirements (AbstractModel)

Security
--------

Access Control
~~~~~~~~~~~~~~
* Restricted access through dedicated Odoo security group
* Server-side access control via Vault policies
* Principle of least privilege enforcement
* No unauthorized access to vault functionality

Data Protection
~~~~~~~~~~~~~~~
* All sensitive data stored externally in Vault
* Only UUID references maintained in Odoo database
* No plain text secrets in logs, displays, or error messages
* Encryption in transit via HTTPS/TLS
* Certificate validation for production security

Authentication
~~~~~~~~~~~~~~
* Vault token-based authentication
* Token validation before all operations
* Support for token rotation and lifecycle management
* Authentication failure detection and reporting

Technical Details
-----------------

Architecture
~~~~~~~~~~~~
* AbstractModel implementation (no database tables)
* Stateless operation design
* External secret storage pattern
* Clean separation of concerns

Performance
~~~~~~~~~~~
* Minimal memory footprint (no caching)
* Efficient HTTP client usage
* 5-second default timeout for operations
* Connection reuse through requests library

Integration
~~~~~~~~~~~
* Simple dependency declaration in ``__manifest__.py``
* Clean API for other modules to consume
* Consistent error handling patterns
* Extensible design for future enhancements

Compatibility
~~~~~~~~~~~~~
* Odoo 16.0+ compatibility
* HashiCorp Vault 1.0+ support
* OpenBao compatibility
* Cross-platform support (Linux, Docker, Kubernetes)

Known Issues
------------

* None reported for initial release

Upgrade Notes
-------------

* This is the initial release - no upgrade procedures needed
* For future upgrades, follow standard Odoo module upgrade procedures
* Backup vault configurations and secret references before upgrades

Migration Guide
---------------

* No migration needed for initial installation
* For organizations moving from other secret management solutions:

  1. Install and configure Vault Connector
  2. Migrate secrets to Vault using the API
  3. Update dependent modules to use vault connector
  4. Remove old secret storage mechanisms

Future Roadmap
--------------

Planned features for future releases:

* Secret versioning and rollback support
* Bulk secret operations
* Advanced monitoring and metrics
* Integration with Vault dynamic secrets
* Support for additional authentication methods
* Enhanced audit logging integration

Breaking Changes
----------------

* None for initial release

Deprecations
------------

* None for initial release

Contributors
------------

* Ross Golder - Initial development and documentation

License
-------

This module is licensed under AGPL-3.0 or later.