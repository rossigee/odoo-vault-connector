# Copyright 2025 Ross Golder
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Vault Connector",
    "version": "16.0.1.0.1",
    "category": "Tools",
    "author": "Ross Golder",
    "website": "https://github.com/rossigee/odoo-vault-connector",
    "summary": "Secure connection to Vault for secret storage",
    "description": """
        This module provides a secure connection interface to Vault 
        (HashiCorp Vault or OpenBao) for storing and retrieving sensitive 
        data like private keys, tokens, and other secrets. It can be used 
        as a dependency by other modules that need secure secret storage.
        
        Features:
        - Vault connectivity and status checking
        - Secure secret storage and retrieval
        - Environment variable configuration
        - Error handling and categorization
        - KV store path configuration
    """,
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "data": [
        "security/vault_connector_security.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,  # This is a utility module, not a standalone app
}
