========================
Vault Connector for Odoo
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   installation
   configuration
   usage
   security
   api_reference
   troubleshooting
   changelog

Overview
========

The Vault Connector provides a secure integration between Odoo and Vault (HashiCorp Vault or OpenBao) for storing and retrieving sensitive data like private keys, API tokens, certificates, and other secrets.

Key Features
============

* **Secure Secret Storage**: All sensitive data stored in Vault, not Odoo database
* **Token-based Authentication**: Secure authentication using Vault tokens
* **Real-time Status Monitoring**: Connection status and seal status checking
* **UUID Token System**: Only unique identifiers stored in Odoo
* **Comprehensive Error Handling**: User-friendly error messages and categorization
* **Multi-tenant Support**: Automatic KV store naming based on database
* **Production Ready**: Designed for enterprise Odoo deployments

Quick Start
===========

1. Install the module
2. Configure environment variables
3. Assign users to the "Vault User" group
4. Start using the API in your modules

For detailed instructions, see the :doc:`installation` and :doc:`configuration` sections.

Requirements
============

* **Odoo**: 16.0 or later
* **Python**: requests library
* **Vault Server**: HashiCorp Vault v1.0+ or OpenBao
* **Network**: HTTPS connectivity between Odoo and Vault

License
=======

This module is licensed under AGPL-3.0 or later.

Support
=======

For issues and feature requests, please use the GitHub repository issue tracker.