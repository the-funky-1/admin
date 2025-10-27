#!/bin/bash
#
# Structure validation script - validates project structure without dependencies
#

echo "============================================================"
echo "M365 Admin MCP Server - Structure Validation"
echo "============================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
        return 0
    else
        echo -e "${RED}❌${NC} $1 - MISSING"
        ((ERRORS++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $1/"
        return 0
    else
        echo -e "${RED}❌${NC} $1/ - MISSING"
        ((ERRORS++))
        return 1
    fi
}

# Function to grep for pattern in file
check_pattern() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Found in $1: $3"
        return 0
    else
        echo -e "${RED}❌${NC} NOT found in $1: $3"
        ((ERRORS++))
        return 1
    fi
}

echo "1. Core Project Files"
echo "-------------------------------------------------------------"
check_file "pyproject.toml"
check_file "requirements.txt"
check_file ".env.example"
check_file ".gitignore"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "GETTING-STARTED.md"
echo ""

echo "2. Source Code Structure"
echo "-------------------------------------------------------------"
check_dir "src/m365_admin_mcp"
check_file "src/m365_admin_mcp/__init__.py"
check_file "src/m365_admin_mcp/server.py"
check_file "src/m365_admin_mcp/config.py"
check_dir "src/m365_admin_mcp/auth"
check_file "src/m365_admin_mcp/auth/graph_auth.py"
check_dir "src/m365_admin_mcp/tools"
check_file "src/m365_admin_mcp/tools/user_management.py"
check_dir "src/m365_admin_mcp/resources"
check_file "src/m365_admin_mcp/resources/health_resource.py"
check_dir "src/m365_admin_mcp/utils"
check_file "src/m365_admin_mcp/utils/validation.py"
check_file "src/m365_admin_mcp/utils/sanitization.py"
echo ""

echo "3. Test Suite"
echo "-------------------------------------------------------------"
check_dir "tests"
check_dir "tests/unit"
check_file "tests/unit/test_auth.py"
check_file "tests/unit/test_validation.py"
echo ""

echo "4. Scripts"
echo "-------------------------------------------------------------"
check_file "scripts/setup_azure_ad.sh"
check_file "scripts/init_database.py"
check_file "scripts/validate_tools.py"
echo ""

echo "5. Documentation"
echo "-------------------------------------------------------------"
check_dir "claudedocs"
check_file "claudedocs/M365-Admin-MCP-Specification.md"
check_file "claudedocs/Implementation-Summary.md"
echo ""

echo "6. User Management Tools Registration"
echo "-------------------------------------------------------------"
check_pattern "src/m365_admin_mcp/server.py" "create_user" "create_user tool"
check_pattern "src/m365_admin_mcp/server.py" "get_user" "get_user tool"
check_pattern "src/m365_admin_mcp/server.py" "list_users" "list_users tool"
check_pattern "src/m365_admin_mcp/server.py" "_tool_create_user" "create_user handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_get_user" "get_user handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_list_users" "list_users handler"
check_pattern "src/m365_admin_mcp/server.py" "UserManagementTools" "UserManagementTools import"
echo ""

echo "7. Email Template Tools Registration"
echo "-------------------------------------------------------------"
check_pattern "src/m365_admin_mcp/server.py" "create_template" "create_template tool"
check_pattern "src/m365_admin_mcp/server.py" "get_template" "get_template tool"
check_pattern "src/m365_admin_mcp/server.py" "list_templates" "list_templates tool"
check_pattern "src/m365_admin_mcp/server.py" "update_template" "update_template tool"
check_pattern "src/m365_admin_mcp/server.py" "delete_template" "delete_template tool"
check_pattern "src/m365_admin_mcp/server.py" "send_from_template" "send_from_template tool"
check_pattern "src/m365_admin_mcp/server.py" "_tool_create_template" "create_template handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_get_template" "get_template handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_list_templates" "list_templates handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_update_template" "update_template handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_delete_template" "delete_template handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_send_from_template" "send_from_template handler"
check_pattern "src/m365_admin_mcp/server.py" "EmailTemplateTools" "EmailTemplateTools import"
check_file "src/m365_admin_mcp/tools/email_templates.py"
echo ""

echo "8. Teams Provisioning Tools Registration"
echo "-------------------------------------------------------------"
check_pattern "src/m365_admin_mcp/server.py" "create_team" "create_team tool"
check_pattern "src/m365_admin_mcp/server.py" "list_teams" "list_teams tool"
check_pattern "src/m365_admin_mcp/server.py" "create_channel" "create_channel tool"
check_pattern "src/m365_admin_mcp/server.py" "list_channels" "list_channels tool"
check_pattern "src/m365_admin_mcp/server.py" "add_team_member" "add_team_member tool"
check_pattern "src/m365_admin_mcp/server.py" "list_team_members" "list_team_members tool"
check_pattern "src/m365_admin_mcp/server.py" "provision_team" "provision_team tool"
check_pattern "src/m365_admin_mcp/server.py" "_tool_create_team" "create_team handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_list_teams" "list_teams handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_create_channel" "create_channel handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_list_channels" "list_channels handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_add_team_member" "add_team_member handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_list_team_members" "list_team_members handler"
check_pattern "src/m365_admin_mcp/server.py" "_tool_provision_team" "provision_team handler"
check_pattern "src/m365_admin_mcp/server.py" "TeamsProvisioningTools" "TeamsProvisioningTools import"
check_file "src/m365_admin_mcp/tools/teams_provisioning.py"
echo ""

echo "9. Tool Schema Validation"
echo "-------------------------------------------------------------"
check_pattern "src/m365_admin_mcp/server.py" '"email"' "Email field in schemas"
check_pattern "src/m365_admin_mcp/server.py" '"displayName"' "DisplayName field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"password"' "Password field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"maxResults"' "MaxResults field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"templateName"' "TemplateName field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"bodyHtml"' "BodyHtml field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"category"' "Category field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"teamId"' "TeamId field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"userEmail"' "UserEmail field in schema"
check_pattern "src/m365_admin_mcp/server.py" '"channels"' "Channels field in schema"
echo ""

echo "10. Code Quality Checks"
echo "-------------------------------------------------------------"

# Count lines of code
if command -v wc &> /dev/null; then
    TOTAL_PY_LINES=$(find src -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
    echo -e "${GREEN}✅${NC} Python code: ${TOTAL_PY_LINES} lines"
fi

# Check for TODOs (warnings only)
TODO_COUNT=$(grep -r "TODO" src/ 2>/dev/null | wc -l)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️${NC}  Found $TODO_COUNT TODO comments"
    ((WARNINGS++))
else
    echo -e "${GREEN}✅${NC} No TODO comments"
fi

echo ""

echo "============================================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ VALIDATION PASSED${NC}"
    echo "   All files present and tools registered correctly"
    echo ""
    echo "Next steps:"
    echo "  1. Install dependencies: pip install -e '.[dev]'"
    echo "  2. Configure .env file"
    echo "  3. Run: python scripts/validate_tools.py"
    echo "  4. Start server: python -m m365_admin_mcp.server"
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo "   Errors: $ERRORS"
    echo "   Please fix the missing files/patterns above"
    exit 1
fi

if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
fi

echo "============================================================"
