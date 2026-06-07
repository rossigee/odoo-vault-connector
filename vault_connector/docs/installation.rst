============
Installation
============

This document covers the installation and initial setup of the HashiCorp Vault Connector module.

Prerequisites
=============

System Requirements
-------------------
* **Odoo**: Version 16.0 or later
* **Python**: requests library (automatically installed)
* **HashiCorp Vault**: Version 1.0+ or OpenBao instance
* **Network**: HTTPS connectivity between Odoo server and Vault

Vault Requirements
------------------
* **KV Secrets Engine**: Version 2 KV store must be enabled
* **Authentication**: Valid Vault token with appropriate permissions
* **Network Access**: Vault server must be reachable from Odoo server
* **TLS Configuration**: Proper SSL/TLS certificates (recommended for production)

Installation Steps
==================

1. Module Installation
----------------------

Download or clone the module to your Odoo addons directory::

    git clone https://github.com/rossigee/odoo-vault-connector.git
    cp -r odoo-vault-connector/vault_connector /path/to/odoo/addons/

Or place the ``vault_connector`` folder directly in your addons path.

2. Install Python Dependencies
------------------------------

The module requires the ``requests`` library. This is typically included with Odoo, but if needed::

    pip install requests

3. Update Module List
---------------------

In Odoo:

1. Go to **Apps** menu
2. Click **Update Apps List**
3. Search for "HashiCorp Vault Connector"
4. Click **Install**

4. Verify Installation
----------------------

Check that the module is properly installed:

1. Go to **Apps** menu
2. Search for "vault_connector"
3. Verify status shows as "Installed"

Initial Configuration
=====================

The module requires several environment variables to be configured before use. See the :doc:`configuration` section for detailed setup instructions.

User Permissions
================

After installation, users must be assigned to the "Vault User" group to access vault functionality:

1. Go to **Settings** → **Users & Companies** → **Users**
2. Select the user who needs vault access
3. In the **Access Rights** tab, add the user to the "Vault User" group

Docker Installation
===================

For development and testing, a Docker Compose setup is provided:

1. Clone the repository
2. Run the test environment::

    docker-compose up -d
    docker-compose exec odoo-test /usr/local/bin/run-tests.sh

This will set up a complete test environment with PostgreSQL and Odoo.

Troubleshooting Installation
============================

Common Issues
-------------

**Module Not Found**
    Ensure the vault_connector folder is in the correct addons directory and Odoo has been restarted.

**Permission Errors**
    Check that the Odoo user has read permissions on all module files.

**Python Dependencies**
    If requests library is missing, install it in the same Python environment as Odoo.

**Database Errors**
    Ensure PostgreSQL is running and accessible with the configured credentials.

Post-Installation
=================

After successful installation:

1. Configure environment variables (see :doc:`configuration`)
2. Set up Vault server connection
3. Assign user permissions
4. Test the connection using the status check method

The module is now ready for use by other modules or direct API calls.