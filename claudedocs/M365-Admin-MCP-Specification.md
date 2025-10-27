# Microsoft 365 Admin MCP Server - Complete Specification

**Project**: Liberty Gold Silver M365 Administration & Provisioning Platform
**Version**: 1.0.0
**Date**: 2025-10-26
**Status**: Design Complete - Ready for Implementation

---

## Executive Summary

This MCP server provides **comprehensive Microsoft 365 administration, resource provisioning, and service orchestration** capabilities for Liberty Gold Silver's tenant (< 10 users). It abstracts the complexity of Microsoft Graph API, Exchange Online, and Teams administration into simple, high-level operations accessible via Claude Code CLI.

**Core Value Proposition:**
- Provision resources (users, Teams, email templates)
- Configure M365 services and features
- Orchestrate multi-service operations
- Enable native tracking and monitoring features

---

## 1. Requirements Summary

### 1.1 Use Case
**Complete M365 configuration and provisioning automation** for Liberty Gold Silver:
- User account creation and configuration
- Email template creation and management
- Teams group provisioning
- Service connections and integrations
- Feature enablement (tracking, rules, policies)

### 1.2 Component Priority

**MVP (Must-have immediately):**
- ✅ User account creation/configuration
- ✅ Create and manage email templates
- ✅ Create Teams groups
- ✅ Configure Outlook native tracking
- ✅ Connect services (integrate apps/services)
- ✅ Enable and configure M365 features

**Important but can wait:**
- ⏳ Advanced automation workflows
- ⏳ Bulk operations
- ⏳ Complex service orchestrations

**Nice-to-have:**
- 📋 Monitoring/reporting dashboards
- 📋 Template versioning system
- 📋 Advanced integrations

### 1.3 Deployment Context
- **Tenant**: Single tenant (Liberty Gold Silver)
- **Users**: < 10 users
- **Permissions**: IT admin-level (high-trust environment)
- **Deployment**: Local development or internal network
- **Access**: Claude Code CLI only
- **Compliance**: Minimal (CAN-SPAM, financial data security)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Code CLI                        │
│                  (User Interface)                        │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
                     │
┌────────────────────▼────────────────────────────────────┐
│              M365 Admin MCP Server                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │         MCP Protocol Layer                       │   │
│  │  • Tools (operations)                            │   │
│  │  • Resources (data access)                       │   │
│  │  • Health check                                  │   │
│  └───────────────┬─────────────────────────────────┘   │
│                  │                                       │
│  ┌───────────────▼─────────────────────────────────┐   │
│  │      Orchestration Layer                         │   │
│  │  • Multi-service workflows                       │   │
│  │  • Dependency management                         │   │
│  │  • Transaction coordination                      │   │
│  │  • Error handling & rollback                     │   │
│  └───────────────┬─────────────────────────────────┘   │
│                  │                                       │
│  ┌───────────────▼─────────────────────────────────┐   │
│  │       Service Integration Layer                  │   │
│  │  ┌─────────────┬──────────────┬────────────┐   │   │
│  │  │ Graph API   │ Exchange     │ Templates  │   │   │
│  │  │ Client      │ PowerShell   │ Manager    │   │   │
│  │  └─────────────┴──────────────┴────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Storage Layer                            │   │
│  │  • SQLite (templates, metadata, audit logs)     │   │
│  │  • Encrypted at rest                            │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────┬──────────────────┬────────────────────┘
               │                  │
               │                  │
     ┌─────────▼────────┐  ┌─────▼──────────┐
     │ Microsoft Graph  │  │ Exchange Online │
     │ API              │  │ PowerShell      │
     │ (REST)           │  │ (REST/PS)       │
     └──────────────────┘  └─────────────────┘
```

### 2.2 Technology Stack

**Core Components:**
- **Language**: Python 3.11+
- **MCP SDK**: `@modelcontextprotocol/sdk` (Python implementation)
- **Microsoft Graph**: `msgraph-sdk-python` (official SDK)
- **Authentication**: `azure-identity` (MSAL for Python)
- **Storage**: SQLite3 with encryption (`sqlcipher` or `pysqlcipher3`)
- **Exchange**: `exchangelib` or REST API calls

**Key Libraries:**
```python
msgraph-sdk-python>=1.0.0
azure-identity>=1.15.0
pysqlcipher3>=1.2.0
asyncio>=3.4.3
pydantic>=2.0.0  # Schema validation
jinja2>=3.1.0    # Template rendering
```

---

## 3. MCP Server Interface Design

### 3.1 Tools (Operations)

#### **User Management**

##### `create_user`
Create a new Microsoft 365 user account.

```python
{
  "name": "create_user",
  "description": "Create a new Microsoft 365 user account with mailbox",
  "inputSchema": {
    "type": "object",
    "properties": {
      "email": {"type": "string", "format": "email"},
      "displayName": {"type": "string"},
      "firstName": {"type": "string"},
      "lastName": {"type": "string"},
      "password": {"type": "string"},
      "license": {"type": "string", "enum": ["BusinessBasic", "BusinessStandard", "BusinessPremium"]},
      "department": {"type": "string", "optional": true}
    },
    "required": ["email", "displayName", "password", "license"]
  }
}
```

##### `configure_mailbox`
Configure mailbox settings (tracking, rules, automatic replies).

```python
{
  "name": "configure_mailbox",
  "description": "Configure mailbox settings including tracking, rules, and OOF",
  "inputSchema": {
    "type": "object",
    "properties": {
      "userEmail": {"type": "string", "format": "email"},
      "settings": {
        "type": "object",
        "properties": {
          "readReceipts": {"type": "boolean"},
          "deliveryReceipts": {"type": "boolean"},
          "automaticReplies": {"type": "object"},
          "forwardingRules": {"type": "array"}
        }
      }
    },
    "required": ["userEmail", "settings"]
  }
}
```

#### **Email Template Management**

##### `create_email_template`
Create and store a reusable email template.

```python
{
  "name": "create_email_template",
  "description": "Create a reusable email template with variables",
  "inputSchema": {
    "type": "object",
    "properties": {
      "templateName": {"type": "string"},
      "subject": {"type": "string"},
      "bodyHtml": {"type": "string"},
      "bodyText": {"type": "string"},
      "category": {"type": "string", "enum": ["wiring", "customer_communication", "marketing"]},
      "variables": {"type": "array", "items": {"type": "string"}},
      "description": {"type": "string"}
    },
    "required": ["templateName", "subject", "bodyHtml", "category"]
  }
}
```

##### `list_email_templates`
List all stored email templates.

```python
{
  "name": "list_email_templates",
  "description": "List all available email templates",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": {"type": "string", "optional": true},
      "searchQuery": {"type": "string", "optional": true}
    }
  }
}
```

##### `get_email_template`
Retrieve a specific email template.

```python
{
  "name": "get_email_template",
  "description": "Get details of a specific email template",
  "inputSchema": {
    "type": "object",
    "properties": {
      "templateId": {"type": "string"}
    },
    "required": ["templateId"]
  }
}
```

##### `send_from_template`
Send an email using a template with variable substitution.

```python
{
  "name": "send_from_template",
  "description": "Send email using a template with variable substitution",
  "inputSchema": {
    "type": "object",
    "properties": {
      "templateId": {"type": "string"},
      "to": {"type": "array", "items": {"type": "string", "format": "email"}},
      "variables": {"type": "object"},
      "from": {"type": "string", "format": "email", "optional": true},
      "cc": {"type": "array", "optional": true},
      "bcc": {"type": "array", "optional": true}
    },
    "required": ["templateId", "to", "variables"]
  }
}
```

#### **Teams & Groups Management**

##### `create_teams_group`
Create a Microsoft Teams group with configuration.

```python
{
  "name": "create_teams_group",
  "description": "Create a Microsoft Teams group with channels and settings",
  "inputSchema": {
    "type": "object",
    "properties": {
      "displayName": {"type": "string"},
      "description": {"type": "string"},
      "visibility": {"type": "string", "enum": ["Private", "Public"]},
      "owners": {"type": "array", "items": {"type": "string", "format": "email"}},
      "members": {"type": "array", "items": {"type": "string", "format": "email"}},
      "channels": {"type": "array", "items": {"type": "object"}},
      "enableGuestAccess": {"type": "boolean", "default": false}
    },
    "required": ["displayName", "owners"]
  }
}
```

#### **Service Configuration**

##### `configure_tracking`
Configure Microsoft 365 native tracking features.

```python
{
  "name": "configure_tracking",
  "description": "Configure native M365 tracking (read/delivery receipts, message tracking)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "scope": {"type": "string", "enum": ["user", "organization"]},
      "targetEmail": {"type": "string", "format": "email", "optional": true},
      "readReceipts": {"type": "boolean"},
      "deliveryReceipts": {"type": "boolean"},
      "messageTracking": {"type": "boolean"}
    },
    "required": ["scope"]
  }
}
```

##### `deploy_outlook_addin`
Deploy an Outlook add-in to the organization.

```python
{
  "name": "deploy_outlook_addin",
  "description": "Deploy an Outlook add-in to users",
  "inputSchema": {
    "type": "object",
    "properties": {
      "addinManifestUrl": {"type": "string", "format": "uri"},
      "deploymentScope": {"type": "string", "enum": ["organization", "specificUsers"]},
      "targetUsers": {"type": "array", "items": {"type": "string"}, "optional": true},
      "enabled": {"type": "boolean", "default": true}
    },
    "required": ["addinManifestUrl", "deploymentScope"]
  }
}
```

##### `connect_service`
Connect or integrate Microsoft 365 services.

```python
{
  "name": "connect_service",
  "description": "Connect and integrate M365 services (e.g., Teams with SharePoint)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "sourceService": {"type": "string"},
      "targetService": {"type": "string"},
      "connectionConfig": {"type": "object"}
    },
    "required": ["sourceService", "targetService"]
  }
}
```

##### `enable_feature`
Enable a Microsoft 365 feature.

```python
{
  "name": "enable_feature",
  "description": "Enable M365 features (audit logging, retention policies, etc.)",
  "inputSchema": {
    "type": "object",
    "properties": {
      "featureName": {"type": "string"},
      "scope": {"type": "string", "enum": ["user", "organization"]},
      "targetEmail": {"type": "string", "optional": true},
      "configuration": {"type": "object"}
    },
    "required": ["featureName", "scope"]
  }
}
```

#### **Monitoring & Diagnostics**

##### `get_message_tracking_logs`
Retrieve message tracking logs from Exchange.

```python
{
  "name": "get_message_tracking_logs",
  "description": "Get message tracking logs for delivered/read status",
  "inputSchema": {
    "type": "object",
    "properties": {
      "startDate": {"type": "string", "format": "date-time"},
      "endDate": {"type": "string", "format": "date-time"},
      "senderEmail": {"type": "string", "optional": true},
      "recipientEmail": {"type": "string", "optional": true},
      "messageId": {"type": "string", "optional": true}
    },
    "required": ["startDate", "endDate"]
  }
}
```

### 3.2 Resources (Data Access)

#### `m365://templates/{templateId}`
Access email template content and metadata.

```json
{
  "uri": "m365://templates/wiring-instructions-v1",
  "name": "Wiring Instructions Template",
  "description": "Template for sending wire transfer instructions to customers",
  "mimeType": "application/json"
}
```

**Response:**
```json
{
  "contents": [{
    "uri": "m365://templates/wiring-instructions-v1",
    "mimeType": "application/json",
    "text": "{\"templateId\": \"wiring-instructions-v1\", \"subject\": \"Wire Transfer Instructions\", ...}"
  }]
}
```

#### `m365://users/{userEmail}`
Access user account information.

```json
{
  "uri": "m365://users/john@libertygoldsilver.com",
  "name": "User: John Doe",
  "mimeType": "application/json"
}
```

#### `m365://teams/{teamId}`
Access Teams group configuration.

```json
{
  "uri": "m365://teams/team-sales-2024",
  "name": "Sales Team 2024",
  "mimeType": "application/json"
}
```

#### `m365://tracking-settings`
Access current tracking configuration.

```json
{
  "uri": "m365://tracking-settings",
  "name": "Organization Tracking Settings",
  "mimeType": "application/json"
}
```

#### `m365://health`
Server health and authentication status.

```json
{
  "uri": "m365://health",
  "name": "MCP Server Health Status",
  "mimeType": "application/json"
}
```

**Response:**
```json
{
  "contents": [{
    "uri": "m365://health",
    "mimeType": "application/json",
    "text": "{\"status\": \"healthy\", \"authenticated\": true, \"graphApiConnected\": true, \"lastCheck\": \"2025-10-26T10:30:00Z\"}"
  }]
}
```

---

## 4. Microsoft Graph API Integration

### 4.1 Required Permissions

**Application Permissions (Admin-consented):**

```
User.ReadWrite.All              - User account management
Mail.ReadWrite                  - Email template creation/management
Mail.Send                       - Send emails on behalf of users
MailboxSettings.ReadWrite       - Configure mailbox settings
Organization.ReadWrite.All      - Tenant-wide settings
Application.ReadWrite.All       - App configurations
Group.ReadWrite.All             - Microsoft 365 groups
Team.Create                     - Create Teams
TeamSettings.ReadWrite.All      - Configure Teams settings
Sites.ReadWrite.All             - SharePoint (for Teams integration)
Directory.ReadWrite.All         - Service connections and directory operations
AuditLog.Read.All               - Read audit logs
```

### 4.2 Authentication Flow

**Azure AD App Registration:**
1. Single-tenant application
2. Certificate-based authentication (recommended) or client secret
3. Admin consent granted once
4. Token caching with refresh

**Authentication Pattern:**
```python
from azure.identity import ClientSecretCredential, CertificateCredential
from msgraph import GraphServiceClient

# Certificate-based (production)
credential = CertificateCredential(
    tenant_id=config.tenant_id,
    client_id=config.client_id,
    certificate_path=config.cert_path
)

# Client secret (development)
credential = ClientSecretCredential(
    tenant_id=config.tenant_id,
    client_id=config.client_id,
    client_secret=config.client_secret
)

scopes = ['https://graph.microsoft.com/.default']
client = GraphServiceClient(credentials=credential, scopes=scopes)
```

### 4.3 Graph API Endpoint Mapping

| Operation | Graph API Endpoint | Method |
|-----------|-------------------|--------|
| Create User | `/users` | POST |
| Get User | `/users/{id}` | GET |
| Update Mailbox Settings | `/users/{id}/mailboxSettings` | PATCH |
| Send Mail | `/users/{id}/sendMail` | POST |
| Create Group | `/groups` | POST |
| Create Team | `/teams` | POST (with group ID) |
| Get Message Tracking | `/reports/getEmailActivityUserDetail` | GET |
| Deploy Add-in | `/admin/serviceAnnouncement/officeClientUpdate` | POST |

---

## 5. Storage Architecture

### 5.1 SQLite Database Schema

```sql
-- Email Templates
CREATE TABLE email_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    category TEXT NOT NULL,
    variables TEXT,  -- JSON array
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Template Usage Logs
CREATE TABLE template_usage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id TEXT NOT NULL,
    sent_by TEXT NOT NULL,
    sent_to TEXT NOT NULL,
    variables_used TEXT,  -- JSON object
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_id TEXT,
    FOREIGN KEY (template_id) REFERENCES email_templates(template_id)
);

-- Audit Logs
CREATE TABLE audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    user_email TEXT,
    target_resource TEXT,
    details TEXT,  -- JSON object
    status TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration Settings
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_template_category ON email_templates(category);
CREATE INDEX idx_template_usage_template ON template_usage(template_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
```

### 5.2 Encryption

**Database Encryption:**
- Use `sqlcipher` for encrypted SQLite
- 256-bit AES encryption
- Master key stored in secure location (environment variable or key vault)

```python
import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher

def get_encrypted_connection():
    conn = sqlcipher.connect('m365_admin.db')
    conn.execute(f"PRAGMA key = '{os.getenv('DB_ENCRYPTION_KEY')}'")
    conn.execute("PRAGMA cipher_compatibility = 4")
    return conn
```

---

## 6. Orchestration Patterns

### 6.1 Multi-Service Workflow Example

**Use Case: Create Complete Team Setup**

```python
async def create_complete_team(team_config):
    """
    Orchestrate multi-service team creation with rollback capability.
    """
    operations = []

    try:
        # Step 1: Create Microsoft 365 Group
        group = await create_m365_group(team_config)
        operations.append(('group', group.id))

        # Step 2: Wait for SharePoint site provisioning (automatic)
        await wait_for_sharepoint_site(group.id)
        operations.append(('site', group.id))

        # Step 3: Enable Teams for the group
        team = await enable_teams_for_group(group.id, team_config)
        operations.append(('team', team.id))

        # Step 4: Create channels
        for channel_config in team_config.channels:
            channel = await create_channel(team.id, channel_config)
            operations.append(('channel', channel.id))

        # Step 5: Add members
        for member_email in team_config.members:
            await add_team_member(team.id, member_email)
            operations.append(('member', member_email))

        # Step 6: Configure settings
        await configure_team_settings(team.id, team_config.settings)
        operations.append(('settings', team.id))

        return {
            'success': True,
            'team_id': team.id,
            'group_id': group.id,
            'operations': operations
        }

    except Exception as e:
        # Rollback in reverse order
        await rollback_operations(operations)
        raise
```

### 6.2 Dependency Management

**Dependency Graph:**
```
User Account Creation
    ├─→ Mailbox Provisioning (automatic)
    ├─→ License Assignment
    └─→ Mailbox Configuration

Teams Creation
    ├─→ M365 Group Creation (prerequisite)
    ├─→ SharePoint Site Provisioning (automatic)
    ├─→ Teams Enablement
    └─→ Channel Creation
```

### 6.3 Error Handling Strategy

**Error Categories:**
1. **Authentication Errors**: Token expired, invalid credentials
2. **Permission Errors**: Insufficient permissions for operation
3. **Resource Conflicts**: User already exists, team name taken
4. **Rate Limiting**: Graph API throttling
5. **Service Unavailable**: Temporary Graph API outages

**Handling Pattern:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, ServiceUnavailableError))
)
async def graph_api_call_with_retry(operation):
    try:
        return await operation()
    except GraphError as e:
        if e.code == 'Authorization_RequestDenied':
            raise PermissionError(f"Insufficient permissions: {e.message}")
        elif e.code == 'Request_ResourceNotFound':
            raise ResourceNotFoundError(f"Resource not found: {e.message}")
        elif e.code == 'ErrorInternalServerError':
            raise ServiceUnavailableError("Graph API temporarily unavailable")
        else:
            raise
```

---

## 7. Security Analysis

### 7.1 Threat Model

**High-Risk Areas:**

1. **Admin Permission Abuse**
   - **Risk**: User.ReadWrite.All allows creating/deleting any user
   - **Mitigation**:
     - Restrict MCP server access to authorized machines only
     - Implement operation confirmation for destructive actions
     - Audit all operations with timestamps and actors

2. **Credential Theft**
   - **Risk**: Stolen credentials = full tenant access
   - **Mitigation**:
     - Use certificate-based authentication
     - Store certificates in Azure Key Vault
     - Never log tokens or credentials
     - Implement token rotation

3. **Template Injection**
   - **Risk**: Malicious content in email templates
   - **Mitigation**:
     - Sanitize HTML input (use bleach library)
     - Validate email addresses and domains
     - Content Security Policy for HTML templates
     - Template approval workflow (optional)

4. **Data Exfiltration**
   - **Risk**: Sensitive template data (wiring instructions) exposed
   - **Mitigation**:
     - Encrypt database at rest
     - TLS for all API communication
     - Access logging for all template operations
     - Regular security audits

5. **Rate Limiting Bypass**
   - **Risk**: Accidental or malicious bulk operations
   - **Mitigation**:
     - Implement client-side rate limiting
     - Exponential backoff for Graph API calls
     - Operation confirmation for bulk actions

### 7.2 Security Controls

**Authentication & Authorization:**
- ✅ Azure AD application with certificate authentication
- ✅ Single-tenant application (no multi-tenant risks)
- ✅ Admin-consented permissions (one-time consent)
- ✅ Token caching with secure storage
- ✅ Automatic token refresh

**Data Protection:**
- ✅ SQLite database encrypted with 256-bit AES
- ✅ Sensitive data (wiring instructions) in encrypted storage
- ✅ TLS 1.3 for all API communication
- ✅ No credential logging or storage in plaintext

**Access Control:**
- ✅ MCP server accessible only from authorized machines
- ✅ Audit logging for all operations
- ✅ Operation-level access control (future enhancement)

**Input Validation:**
- ✅ Pydantic schemas for all inputs
- ✅ HTML sanitization (bleach library)
- ✅ Email address validation (RFC 5322)
- ✅ SQL injection prevention (parameterized queries)

**Monitoring & Logging:**
- ✅ All operations logged to audit table
- ✅ Failed authentication attempts logged
- ✅ Rate limiting violations logged
- ✅ Health check endpoint for monitoring

### 7.3 Compliance

**CAN-SPAM Compliance:**
- Include unsubscribe mechanism in marketing templates
- Physical address in email footer
- Accurate "From" and "Subject" lines
- Honor opt-out requests within 10 business days

**Financial Data Security:**
- Encrypt wiring instruction templates
- Access logging for template retrieval
- Secure transmission (TLS 1.3)
- Regular security audits

---

## 8. Implementation Plan

### 8.1 Development Phases

**Phase 1: Foundation (Week 1-2)**
- [ ] Azure AD app registration and configuration
- [ ] Basic MCP server structure (server.py)
- [ ] Authentication implementation (azure-identity)
- [ ] Health check endpoint
- [ ] User management tools (create_user, configure_mailbox)
- [ ] Basic error handling

**Deliverables:**
- Functional MCP server with user management
- Authenticated Graph API connection
- Health check validation

---

**Phase 2: Email Templates (Week 2-3)**
- [ ] SQLite database setup with encryption
- [ ] Template CRUD operations
- [ ] Template rendering with Jinja2
- [ ] Send from template functionality
- [ ] Template storage and retrieval
- [ ] Audit logging

**Deliverables:**
- Complete email template system
- Template usage tracking
- Send functionality with variable substitution

---

**Phase 3: Teams Provisioning (Week 3-4)**
- [ ] Teams/Groups creation tools
- [ ] SharePoint site handling
- [ ] Channel creation and configuration
- [ ] Member management
- [ ] Orchestration patterns for multi-step operations
- [ ] Rollback capability

**Deliverables:**
- Complete Teams provisioning system
- Multi-service orchestration
- Error handling and rollback

---

**Phase 4: Advanced Configuration (Week 4-5)**
- [ ] Tracking configuration (read/delivery receipts)
- [ ] Message tracking log retrieval
- [ ] Outlook add-in deployment
- [ ] Service connection tools
- [ ] Feature enablement tools
- [ ] Exchange Online PowerShell integration (if needed)

**Deliverables:**
- Complete configuration management
- Tracking capabilities
- Add-in deployment

---

**Phase 5: Polish & Production (Week 5-6)**
- [ ] Comprehensive error handling
- [ ] Rate limiting implementation
- [ ] Security hardening
- [ ] Documentation (API docs, setup guide)
- [ ] Integration testing
- [ ] Performance optimization

**Deliverables:**
- Production-ready MCP server
- Complete documentation
- Test coverage > 80%

---

### 8.2 Project Structure

```
m365-admin-mcp/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── server.py              # Main MCP server entry point
│   ├── config.py              # Configuration management
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   └── graph_auth.py      # Azure AD authentication
│   │
│   ├── tools/                 # MCP tools implementation
│   │   ├── __init__.py
│   │   ├── user_management.py
│   │   ├── email_templates.py
│   │   ├── teams_management.py
│   │   ├── configuration.py
│   │   └── monitoring.py
│   │
│   ├── resources/             # MCP resources implementation
│   │   ├── __init__.py
│   │   ├── template_resource.py
│   │   ├── user_resource.py
│   │   └── health_resource.py
│   │
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── graph_service.py   # Graph API wrapper
│   │   ├── template_service.py
│   │   ├── teams_service.py
│   │   └── orchestration.py   # Multi-service workflows
│   │
│   ├── storage/               # Data persistence
│   │   ├── __init__.py
│   │   ├── database.py        # SQLite connection
│   │   ├── template_repo.py
│   │   └── audit_repo.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validation.py      # Input validation
│       ├── sanitization.py    # HTML sanitization
│       └── retry.py           # Retry logic
│
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_resources.py
│   ├── test_services.py
│   └── integration/
│       └── test_graph_api.py
│
├── data/
│   ├── m365_admin.db          # SQLite database (encrypted)
│   └── .gitkeep
│
├── docs/
│   ├── setup.md               # Setup instructions
│   ├── api_reference.md       # Tool/resource documentation
│   ├── security.md            # Security guidelines
│   └── examples.md            # Usage examples
│
└── scripts/
    ├── setup_azure_ad.sh      # Azure AD app registration script
    └── init_database.py       # Database initialization
```

### 8.3 Configuration Management

**Environment Variables:**
```bash
# Azure AD Configuration
AZURE_TENANT_ID=00000000-0000-0000-0000-000000000000
AZURE_CLIENT_ID=11111111-1111-1111-1111-111111111111
AZURE_CLIENT_SECRET=secret_for_dev_only
AZURE_CERTIFICATE_PATH=/path/to/cert.pem  # Production

# Database Configuration
DB_ENCRYPTION_KEY=your-256-bit-encryption-key
DATABASE_PATH=./data/m365_admin.db

# MCP Server Configuration
MCP_SERVER_NAME=m365-admin
MCP_SERVER_VERSION=1.0.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/m365_admin.log

# Security
ENABLE_OPERATION_CONFIRMATION=true
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60
```

---

## 9. Testing Strategy

### 9.1 Test Coverage Requirements

**Unit Tests (Target: 80% coverage):**
- Authentication flows
- Tool input validation
- Template rendering
- Database operations
- Sanitization functions

**Integration Tests:**
- Graph API calls (mocked)
- Database persistence
- End-to-end tool execution
- Orchestration workflows

**Security Tests:**
- SQL injection attempts
- XSS injection in templates
- Authentication bypass attempts
- Rate limiting validation

**Manual Tests:**
- Full user provisioning workflow
- Email template creation and sending
- Teams creation with channels
- Tracking configuration

### 9.2 Test Data

**Mock Users:**
```json
{
  "testUser1": "test.user1@libertygoldsilver.com",
  "testUser2": "test.user2@libertygoldsilver.com"
}
```

**Mock Templates:**
- Wiring instructions template
- Customer communication template
- Marketing email template

### 9.3 Integration Testing

**Prerequisites:**
- Test Microsoft 365 tenant (or sandbox environment)
- Test Azure AD app registration
- Test user accounts

**Test Scenarios:**
1. Create user → Configure mailbox → Send test email
2. Create template → Send from template → Verify delivery
3. Create Teams group → Add channels → Add members
4. Configure tracking → Send email → Verify tracking logs
5. Deploy Outlook add-in → Verify deployment

---

## 10. Operations & Maintenance

### 10.1 Monitoring

**Health Checks:**
- Graph API connectivity
- Database connection
- Authentication status
- Token expiration

**Metrics to Track:**
- API call success rate
- Average response time
- Error rate by operation
- Template usage statistics

### 10.2 Backup & Recovery

**Database Backup:**
- Daily encrypted backups
- Retention: 30 days
- Backup location: Secure storage

**Disaster Recovery:**
- Database restore procedure
- Azure AD app re-registration steps
- Configuration restoration

### 10.3 Upgrades & Maintenance

**Dependency Updates:**
- Monthly security updates
- Quarterly feature updates
- Graph API version monitoring

**Breaking Changes:**
- Monitor Microsoft Graph API changelog
- Test in sandbox before production
- Version compatibility matrix

---

## 11. Documentation Requirements

### 11.1 User Documentation

**Setup Guide:**
1. Azure AD app registration
2. Permission configuration
3. MCP server installation
4. Configuration file setup
5. Claude Code integration

**Usage Examples:**
- Creating users
- Managing email templates
- Provisioning Teams
- Configuring tracking

### 11.2 Developer Documentation

**API Reference:**
- All tools with schemas
- All resources with examples
- Error codes and handling
- Authentication flows

**Architecture Documentation:**
- System diagrams
- Data flow diagrams
- Security architecture
- Orchestration patterns

---

## 12. Success Metrics

### 12.1 Functional Metrics

- ✅ All MVP tools implemented and tested
- ✅ > 80% test coverage
- ✅ < 2 second average response time
- ✅ > 99% API call success rate
- ✅ Zero security vulnerabilities (high/critical)

### 12.2 Business Metrics

- ✅ Reduces M365 admin tasks by 70%
- ✅ Email template usage > 10 sends/week
- ✅ Zero manual user provisioning errors
- ✅ Teams provisioning time < 5 minutes

---

## 13. Next Steps

### Immediate Actions

1. **Azure AD Setup** (Day 1)
   - Register Azure AD application
   - Configure permissions
   - Generate certificates (production)
   - Obtain admin consent

2. **Development Environment** (Day 1-2)
   - Set up Python virtual environment
   - Install dependencies
   - Configure VS Code / IDE
   - Initialize Git repository

3. **Foundation Implementation** (Week 1)
   - Implement authentication layer
   - Create basic MCP server structure
   - Implement health check
   - Test Graph API connectivity

4. **Iterative Development** (Weeks 2-6)
   - Follow phased implementation plan
   - Test each phase before proceeding
   - Document as you build
   - Regular security reviews

---

## Appendix A: Graph API Reference

### User Management
- **Create User**: `POST /users`
- **Get User**: `GET /users/{id}`
- **Update User**: `PATCH /users/{id}`
- **Delete User**: `DELETE /users/{id}`

### Mailbox Operations
- **Get Mailbox Settings**: `GET /users/{id}/mailboxSettings`
- **Update Mailbox Settings**: `PATCH /users/{id}/mailboxSettings`
- **Send Mail**: `POST /users/{id}/sendMail`

### Teams & Groups
- **Create Group**: `POST /groups`
- **Create Team**: `POST /teams`
- **Add Member**: `POST /groups/{id}/members/$ref`
- **Create Channel**: `POST /teams/{id}/channels`

### Message Tracking
- **Get Email Activity**: `GET /reports/getEmailActivityUserDetail`
- **Get Mail Tips**: `POST /users/{id}/getMailTips`

---

## Appendix B: Error Codes

| Code | Description | Action |
|------|-------------|--------|
| AUTH_001 | Authentication failed | Check credentials |
| AUTH_002 | Token expired | Refresh token |
| PERM_001 | Insufficient permissions | Verify app permissions |
| USER_001 | User already exists | Use different email |
| TEAM_001 | Team name taken | Choose different name |
| TMPL_001 | Template not found | Verify template ID |
| RATE_001 | Rate limit exceeded | Retry after delay |
| GRAPH_001 | Graph API error | Check Graph status |

---

## Appendix C: Security Checklist

- [ ] Certificate-based authentication configured
- [ ] Database encrypted with strong key
- [ ] All Graph API calls use HTTPS
- [ ] Input validation on all tools
- [ ] HTML sanitization for templates
- [ ] Audit logging enabled
- [ ] Rate limiting implemented
- [ ] No credentials in logs
- [ ] Secure credential storage
- [ ] Regular security updates

---

**End of Specification**

*This document is a living specification and will be updated as the project evolves.*
