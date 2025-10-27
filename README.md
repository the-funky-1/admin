# M365 Admin MCP Server

Microsoft 365 administration and provisioning platform for Liberty Gold Silver. This MCP server provides comprehensive M365 administration capabilities through Claude Code CLI.

## Features

- **User Management**: Create and configure M365 user accounts
- **Email Templates**: Create, store, and send professional email templates
- **Teams Provisioning**: Provision Microsoft Teams with full configuration
- **Service Configuration**: Configure tracking, add-ins, and M365 features
- **Security**: Certificate-based auth, encrypted storage, audit logging

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Azure AD tenant with admin access
- Microsoft 365 subscription

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/libertygoldsilver/m365-admin-mcp.git
   cd m365-admin-mcp
   ```

2. **Create virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure AD credentials
   ```

### Azure AD Setup

1. **Register Application** in Azure Portal:
   - Navigate to Azure Active Directory → App registrations
   - Click "New registration"
   - Name: "M365 Admin MCP Server"
   - Supported account types: "Single tenant"
   - Register

2. **Configure Permissions**:
   - Go to "API permissions"
   - Add these Microsoft Graph Application permissions:
     - User.ReadWrite.All
     - Mail.ReadWrite, Mail.Send
     - MailboxSettings.ReadWrite
     - Organization.ReadWrite.All
     - Group.ReadWrite.All
     - Team.Create, TeamSettings.ReadWrite.All
     - Sites.ReadWrite.All
     - Directory.ReadWrite.All
     - Application.ReadWrite.All
     - AuditLog.Read.All
   - Click "Grant admin consent"

3. **Create Client Secret** (Development):
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: "Dev Secret"
   - Expires: 6 months (or as needed)
   - Copy the secret value to .env

4. **Upload Certificate** (Production - Recommended):
   ```bash
   # Generate certificate
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout cert.key -out cert.pem

   # Upload cert.pem to Azure AD → Certificates & secrets
   # Keep cert.key secure
   ```

### Running the Server

```bash
# Development mode
python -m m365_admin_mcp.server

# Or use the installed command
m365-admin-mcp
```

### Claude Code Integration

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "m365-admin": {
      "command": "python",
      "args": ["-m", "m365_admin_mcp.server"],
      "env": {
        "AZURE_TENANT_ID": "your-tenant-id",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

## Usage Examples

### Create a User

```python
# In Claude Code:
"Create a new user john.doe@libertygoldsilver.com with Business Standard license"
```

### Create Email Template

```python
# In Claude Code:
"Create an email template for wiring instructions"
```

### Send from Template

```python
# In Claude Code:
"Send wiring instructions to customer@example.com using the wiring template"
```

### Create Teams Group

```python
# In Claude Code:
"Create a Sales Team with channels for Leads and Deals"
```

## Project Structure

```
m365-admin-mcp/
├── src/m365_admin_mcp/
│   ├── server.py              # Main MCP server
│   ├── config.py              # Configuration management
│   ├── auth/
│   │   └── graph_auth.py      # Azure AD authentication
│   ├── tools/                 # MCP tool implementations
│   ├── resources/             # MCP resource implementations
│   ├── services/              # Business logic
│   ├── storage/               # Database layer
│   └── utils/                 # Utilities
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
└── docs/                      # Documentation
```

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_auth.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Database Initialization

```bash
python scripts/init_database.py
```

## Security

- **Certificate-based authentication** recommended for production
- **Database encryption** with 256-bit AES (optional, requires pysqlcipher3)
- **Audit logging** for all operations
- **Input validation** on all MCP tools
- **HTML sanitization** for email templates

See [docs/security.md](docs/security.md) for detailed security guidelines.

## Documentation

- [Setup Guide](docs/setup.md)
- [API Reference](docs/api_reference.md)
- [Security Guidelines](docs/security.md)
- [Usage Examples](docs/examples.md)

## Troubleshooting

### Authentication Errors

```
Error: Authorization_RequestDenied
Solution: Ensure admin consent is granted in Azure AD
```

### Permission Errors

```
Error: Insufficient privileges
Solution: Verify all required permissions are configured in Azure AD
```

### Database Errors

```
Error: Unable to open database
Solution: Check DATABASE_PATH in .env and ensure directory exists
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/libertygoldsilver/m365-admin-mcp/issues
- Email: admin@libertygoldsilver.com

## Changelog

### Version 1.0.0 (2025-10-26)
- Initial release
- User management tools
- Email template system
- Teams provisioning
- Service configuration
- Health check and monitoring
