# Vault Connector for Odoo

A secure integration module that connects Odoo with Vault servers (HashiCorp Vault or OpenBao) for storing and retrieving sensitive data like API keys, passwords, certificates, and other secrets.

## 🔒 Key Features

- **Secure External Storage**: All secrets stored in Vault, never in Odoo database
- **Zero Database Exposure**: Only UUID references stored in Odoo
- **Real-time Status Monitoring**: Connection and seal status checking
- **Enterprise Security**: Token-based authentication with proper access controls
- **Multi-tenant Support**: Automatic KV store isolation per database
- **Production Ready**: Comprehensive error handling and security validations

## 🚀 Quick Start

### 1. Install the Module

Place the `vault_connector` folder in your Odoo addons directory and install through the Apps menu.

### 2. Configure Environment Variables

```bash
export VAULT_ADDR="https://your-vault-server:8200"
export VAULT_TOKEN="your-vault-token"
```

### 3. Assign User Permissions

Add users to the "Vault User" security group in Odoo.

### 4. Use in Your Modules

```python
# Add dependency in __manifest__.py
"depends": ["vault_connector"]

# Store a secret
secret_id = str(uuid.uuid4())
self.env['vault.connector'].set_secret(secret_id, {
    'api_key': 'secret-key-123',
    'password': 'secure-password'
})

# Retrieve a secret
secret_data = self.env['vault.connector'].get_secret(secret_id)
```

## 📋 Requirements

- **Odoo**: 16.0 or later
- **Vault Server**: HashiCorp Vault 1.0+ or OpenBao
- **Python**: `requests` library (included with Odoo)
- **Network**: HTTPS connectivity to Vault server

## 🛡️ Security

- **Access Control**: Dedicated security group restricts access
- **TLS Encryption**: All communications encrypted in transit
- **Input Validation**: UUID validation prevents injection attacks
- **No Caching**: Secrets never cached or logged
- **Audit Trail**: All access logged through Vault's audit system

## 📖 Documentation

Complete documentation is available in the `vault_connector/docs/` directory:

- **Installation Guide**: Setup and configuration instructions
- **API Reference**: Complete method documentation with examples
- **Security Guide**: Best practices and threat mitigation
- **Troubleshooting**: Common issues and solutions
- **Usage Examples**: Integration patterns and code samples

## 🧪 Testing

Run the test suite using Docker:

```bash
docker compose up -d
docker compose exec odoo-test /usr/local/bin/run-tests.sh
```

## 📄 License

This module is licensed under AGPL-3.0 or later.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the `docs/` folder for detailed guides
- **Security**: Follow responsible disclosure for security issues

---

**⚠️ Security Notice**: This module handles sensitive data. Always use HTTPS connections, rotate tokens regularly, and follow security best practices outlined in the documentation.
