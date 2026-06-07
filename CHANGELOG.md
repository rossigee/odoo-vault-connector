# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [16.0.1.0.1] - 2025-07-01

### Added
- Initial release of HashiCorp Vault Connector for Odoo 16
- Secure connection interface to HashiCorp Vault servers
- Real-time vault seal status and accessibility checks
- Secret storage and retrieval from Vault KV stores
- Comprehensive error handling with user-friendly messages
- Environment variable configuration support
- Multi-tenant KV store naming based on database
- UUID validation for secret identifiers
- Abstract model design for security (no database storage)
- Comprehensive test suite with mocking
- Complete documentation set (README, CONFIGURE, USAGE, DESCRIPTION)

### Security
- TLS certificate verification by default
- Token-based authentication with Vault
- No sensitive data stored in Odoo database
- Proper error handling without exposing secrets
- Security permissions configured for all users

### Dependencies
- Python `requests` library for HTTP operations
- Compatible with HashiCorp Vault v1.0+ and OpenBao
- Requires Odoo 16.0 or later

### Configuration
- `VAULT_ADDR`: Vault server URL (required)
- `VAULT_TOKEN`: Authentication token (required)
- `VAULT_SKIP_VERIFY`: Skip TLS verification (optional, dev only)
- `VAULT_KV_STORE`: Custom KV store name (optional)