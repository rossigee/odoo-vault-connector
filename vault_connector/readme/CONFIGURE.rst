=========================================
Vault Connector Configuration Guide
=========================================

This guide covers installation, configuration, and setup of the HashiCorp Vault Connector module for Odoo.

📋 **Prerequisites**
====================

System Requirements
-------------------
* **Odoo 16.0 or later**: Compatible with Odoo 16+
* **Python 3.8+**: Required for requests library support
* **External Vault**: HashiCorp Vault or OpenBao instance (v1.0+)
* **Network Access**: HTTPS connectivity between Odoo and Vault

Required Knowledge
------------------
* **Odoo Administration**: Module installation and configuration
* **Vault Administration**: Basic Vault setup and token management
* **Secret Management**: Understanding of secure secret storage practices
* **Network Security**: Knowledge of secure network configurations

🚀 **Installation**
===================

Step 1: Install Python Dependencies
------------------------------------

The module requires the `requests` Python library for HTTP operations.

**On Ubuntu/Debian**::

    sudo apt update
    sudo apt install python3-pip
    pip3 install requests

**On CentOS/RHEL**::

    sudo yum install python3-pip
    pip3 install requests

**Using Conda**::

    conda install -c conda-forge requests

**Using Poetry (if used in your Odoo deployment)**::

    poetry add requests

Step 2: Install Odoo Module
----------------------------

**Method 1: Manual Installation**

1. Copy the module to your Odoo addons directory::

    cp -r vault_connector /path/to/odoo/addons/

2. Restart Odoo server
3. Update the apps list in Odoo
4. Install the "HashiCorp Vault Connector" module

**Method 2: Git Clone**

1. Clone into addons directory::

    cd /path/to/odoo/addons/
    git clone <repository-url> vault_connector

2. Follow steps 2-4 from Method 1

Step 3: Verify Installation
----------------------------

1. Log into Odoo as administrator
2. Go to **Apps** → **Update Apps List**
3. Search for "HashiCorp Vault Connector"
4. Click **Install**
5. Verify no error messages during installation

🔐 **Vault Setup**
==================

The module requires an external Vault instance for secure secret storage. This section covers basic setup.

HashiCorp Vault Installation
-----------------------------

**Using Docker (Recommended for Testing)**::

    # Run Vault in development mode (DO NOT USE IN PRODUCTION)
    docker run --cap-add=IPC_LOCK -d --name=vault-dev -p 8200:8200 vault:latest

    # Get the root token
    docker logs vault-dev

**Production Installation on Ubuntu/Debian**::

    # Add HashiCorp GPG key
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -

    # Add repository
    sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"

    # Install Vault
    sudo apt update && sudo apt install vault

**Production Installation on CentOS/RHEL**::

    # Add repository
    sudo yum install -y yum-utils
    sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo

    # Install Vault
    sudo yum -y install vault

OpenBao Alternative
-------------------

OpenBao is an open-source Vault fork that's fully compatible::

    # Download and install OpenBao
    wget https://github.com/openbao/openbao/releases/download/v1.0.0/bao_1.0.0_linux_amd64.zip
    unzip bao_1.0.0_linux_amd64.zip
    sudo mv bao /usr/local/bin/

Vault Configuration
-------------------

**Basic Production Configuration** (`/etc/vault.d/vault.hcl`)::

    ui = true
    
    storage "file" {
      path = "/opt/vault/data"
    }
    
    listener "tcp" {
      address     = "0.0.0.0:8200"
      tls_cert_file = "/path/to/cert.pem"
      tls_key_file  = "/path/to/key.pem"
    }

**Initialize Vault**::

    # Start Vault
    sudo systemctl start vault
    
    # Initialize (save these keys securely!)
    vault operator init
    
    # Unseal Vault (use 3 of the 5 unseal keys)
    vault operator unseal <key1>
    vault operator unseal <key2>
    vault operator unseal <key3>

**Create Odoo Policy**::

    # Login with root token
    vault auth <root-token>
    
    # Create policy for Odoo
    vault policy write odoo-connector - <<EOF
    path "secret/*" {
      capabilities = ["create", "read", "update", "delete", "list"]
    }
    EOF
    
    # Create token for Odoo
    vault token create -policy=odoo-connector -ttl=8760h

🔧 **Odoo Configuration**
=========================

Environment Variables
---------------------

Set these environment variables for your Odoo instance:

**Option 1: Environment File** (`.env` or in Docker)::

    VAULT_ADDR=https://your-vault-server.com:8200
    VAULT_TOKEN=hvs.XXXXXXXXXXXXXXXXXXXX

**Option 2: System Environment**::

    export VAULT_ADDR=https://your-vault-server.com:8200
    export VAULT_TOKEN=hvs.XXXXXXXXXXXXXXXXXXXX

**Option 3: Docker Compose**::

    version: '3'
    services:
      odoo:
        image: odoo:16
        environment:
          - VAULT_ADDR=https://your-vault-server.com:8200
          - VAULT_TOKEN=hvs.XXXXXXXXXXXXXXXXXXXX

**Option 4: Kubernetes**::

    apiVersion: v1
    kind: Secret
    metadata:
      name: odoo-vault-config
    type: Opaque
    data:
      VAULT_ADDR: <base64-encoded-url>
      VAULT_TOKEN: <base64-encoded-token>

Testing Vault Connection
-------------------------

1. Restart Odoo after setting environment variables
2. Test connection using Python console or Odoo shell::

    # Test connection
    from odoo.addons.vault_connector.models.vault_connector import VaultConnector
    vault = VaultConnector()
    status = vault.check_status()
    print(f"Vault status: {status}")

3. Check Odoo logs for any Vault connection errors

👥 **User Management**
======================

The Vault Connector module is a utility module that doesn't provide specific user interfaces but enables other modules to securely store and retrieve secrets.

Access Control
--------------

**Technical Module**: This module operates at the technical level and doesn't define specific user groups. Access control is managed by:

* **Vault Token Permissions**: Controlled by Vault policies
* **Environment Variables**: Secured at system level
* **Module Dependencies**: Other modules handle user access to Vault functionality

Developer Access
----------------

**For developers building on this module**:

1. Import the VaultConnector class in your module
2. Use environment variables for Vault configuration
3. Implement appropriate user permissions in your module
4. Follow security best practices for secret handling

**Example Integration**::

    from odoo.addons.vault_connector.models.vault_connector import VaultConnector
    
    class MySecureModel(models.Model):
        _name = 'my.secure.model'
        
        def store_secret(self, secret_data):
            vault = VaultConnector()
            token = vault.store_secret(secret_data)
            # Store only the token in your model
            self.vault_token = token

🔒 **Security Configuration**
=============================

Vault Security Hardening
-------------------------

**Production Vault Security**:

1. **Use TLS**: Always use HTTPS for Vault communication
2. **Network Segmentation**: Isolate Vault on secure network
3. **Regular Backups**: Backup Vault data and unseal keys
4. **Monitor Access**: Enable Vault audit logging
5. **Rotate Tokens**: Regularly rotate Odoo's Vault token

**Vault Audit Logging**::

    vault audit enable file file_path=/vault/logs/audit.log

**Token Rotation**::

    # Create new token
    vault token create -policy=odoo-bitcoin -ttl=8760h
    
    # Update Odoo environment variables
    # Restart Odoo
    
    # Revoke old token
    vault token revoke <old-token>

Network Security
----------------

**Firewall Rules**:

* Only allow Odoo server IP to connect to Vault
* Use VPN or private networks when possible
* Block public access to Vault unless necessary

**TLS Configuration**:

* Use valid SSL certificates
* Implement certificate pinning if possible
* Monitor certificate expiration

Odoo Security Settings
----------------------

**Database Security**:

* Enable database encryption at rest
* Use strong database passwords
* Regular database backups
* Monitor database access logs

**Session Security**:

* Short session timeouts for Bitcoin users
* Two-factor authentication where possible
* Regular password changes
* Monitor user login patterns

🧪 **Testing Configuration**
=============================

Vault Connectivity Test
-----------------------

**Manual Test**::

    # Test Vault connection
    curl -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/sys/health

**Odoo Test**:

1. Open Odoo shell or Python console
2. Test the connector::

    from odoo.addons.vault_connector.models.vault_connector import VaultConnector
    vault = VaultConnector()
    
    # Test connection
    status = vault.check_status()
    print(f"Connection status: {status}")
    
    # Test secret storage
    test_data = {"test": "secret_value"}
    token = vault.store_secret(test_data)
    print(f"Stored secret with token: {token}")
    
    # Test secret retrieval
    retrieved = vault.get_secret(token)
    print(f"Retrieved secret: {retrieved}")

3. Check Vault for stored data::

    vault kv get secret/<token-uuid>

**Connection Troubleshooting**:

* Verify environment variables are set
* Check network connectivity to Vault
* Verify Vault token has proper permissions
* Check Odoo logs for connection errors

Module Functionality Test
--------------------------

**Basic Integration Test**:

1. **Store Secret**: Use VaultConnector to store test data
2. **Retrieve Secret**: Verify data can be retrieved using token
3. **Error Handling**: Test with invalid tokens and network issues
4. **Performance**: Test multiple concurrent operations

**Expected Results**:

* Secrets stored securely in Vault
* Only tokens stored in Odoo
* Proper error handling for connection issues
* No sensitive data in Odoo logs or database

📊 **Monitoring & Maintenance**
===============================

Log Monitoring
--------------

**Odoo Logs to Monitor**:

* Vault connector operations
* Vault connection attempts
* Secret storage/retrieval operations
* Authentication failures

**Vault Logs to Monitor**:

* Odoo authentication attempts
* Secret storage/retrieval operations
* Failed authentication attempts
* Token usage patterns

Regular Maintenance
-------------------

**Weekly Tasks**:

* Review Vault access logs
* Check system connectivity
* Verify backup procedures
* Monitor user activity

**Monthly Tasks**:

* Rotate Vault tokens
* Review user permissions
* Update security patches
* Test disaster recovery

**Quarterly Tasks**:

* Full security audit
* Review backup restoration
* Update documentation
* Training for new users

🚨 **Troubleshooting**
======================

Common Configuration Issues
---------------------------

**Vault Connection Failed**:

* **Symptoms**: "Vault not accessible" errors, empty private key data
* **Solutions**: 
  * Check VAULT_ADDR and VAULT_TOKEN environment variables
  * Verify network connectivity to Vault server
  * Check Vault server status and unseal state
  * Verify token has proper permissions

**Module Not Available**:

* **Symptoms**: Vault connector not available for import
* **Solutions**:
  * Verify module installation completed successfully
  * Check module is in correct addons path
  * Restart Odoo server after installation
  * Check Odoo logs for import errors

**Module Installation Fails**:

* **Symptoms**: Error during module installation
* **Solutions**:
  * Install required Python dependencies (requests)
  * Check Odoo version compatibility
  * Verify addons path configuration
  * Review installation logs

**Secret Storage/Retrieval Errors**:

* **Symptoms**: Errors when storing or retrieving secrets
* **Solutions**:
  * Check Vault token permissions
  * Verify KV store is properly configured
  * Check network connectivity to Vault
  * Review Vault and Odoo error logs

Performance Issues
------------------

**Slow Secret Operations**:

* **Cause**: Network latency to Vault
* **Solutions**: Move Vault closer to Odoo, optimize network

**Connection Timeouts**:

* **Cause**: Network issues or Vault overload
* **Solutions**: Increase timeout values, check Vault performance

Getting Support
---------------

**Before Requesting Support**:

1. Check all configuration steps
2. Review logs for specific error messages
3. Test Vault connectivity independently
4. Verify environment variables are set correctly
5. Test with minimal example code

**Information to Provide**:

* Odoo version and installation method
* Vault version and configuration
* Environment variable settings (without tokens!)
* Relevant log excerpts
* Steps to reproduce issues
* Expected vs actual behavior

**Support Channels**:

* Module documentation and README files
* Odoo Community Association forums
* HashiCorp Vault community
* Professional Odoo support services