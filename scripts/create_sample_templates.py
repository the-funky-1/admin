#!/usr/bin/env python3
"""
Create sample email templates for testing and demonstration.

Populates the database with common templates for Liberty Gold Silver use cases.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from m365_admin_mcp.tools.email_templates import EmailTemplateTools


async def create_templates() -> None:
    """Create sample email templates."""
    print("=" * 60)
    print("M365 Admin MCP Server - Creating Sample Templates")
    print("=" * 60)
    print()

    templates = [
        {
            "template_name": "wiring_instructions",
            "subject": "Wiring Instructions for Your {{ metal_type }} Purchase",
            "body_html": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #1a5490;">Wiring Instructions</h2>

    <p>Dear {{ customer_name }},</p>

    <p>Thank you for your {{ metal_type }} purchase with Liberty Gold & Silver. Below are the wiring instructions for your order:</p>

    <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #1a5490; margin: 20px 0;">
        <strong>Bank Information:</strong><br>
        Bank Name: {{ bank_name }}<br>
        Account Name: Liberty Gold & Silver<br>
        Account Number: {{ account_number }}<br>
        Routing Number: {{ routing_number }}<br>
        Wire Amount: ${{ amount }}
    </div>

    <p><strong>Important:</strong> Please include your order number <strong>{{ order_number }}</strong> in the wire memo/reference field.</p>

    <p>Once we receive your wire transfer, we will process your order immediately. If you have any questions, please don't hesitate to contact us.</p>

    <p>Best regards,<br>
    Liberty Gold & Silver Team</p>

    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <p style="font-size: 0.9em; color: #666;">
        <em>This communication is for informational purposes only and does not constitute investment advice.
        Please consult with your financial advisor before making investment decisions.</em>
    </p>
</body>
</html>
""",
            "category": "wiring",
            "variables": [
                "customer_name",
                "metal_type",
                "bank_name",
                "account_number",
                "routing_number",
                "amount",
                "order_number",
            ],
            "description": "Wiring instructions for precious metals purchases",
        },
        {
            "template_name": "order_confirmation",
            "subject": "Order Confirmation - {{ order_number }}",
            "body_html": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #1a5490;">Order Confirmation</h2>

    <p>Dear {{ customer_name }},</p>

    <p>Thank you for your order! We have received your purchase and are processing it now.</p>

    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <strong>Order Details:</strong><br>
        Order Number: {{ order_number }}<br>
        Date: {{ order_date }}<br>
        Product: {{ product_description }}<br>
        Quantity: {{ quantity }}<br>
        Total: ${{ total_amount }}
    </div>

    <p>Your order will ship within {{ shipping_days }} business days. You will receive a tracking number once your order ships.</p>

    <p>Thank you for choosing Liberty Gold & Silver for your precious metals investment needs.</p>

    <p>Best regards,<br>
    Liberty Gold & Silver Team</p>

    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <p style="font-size: 0.9em; color: #666;">
        <em>This communication is for informational purposes only. Past performance does not guarantee future results.</em>
    </p>
</body>
</html>
""",
            "category": "customer_service",
            "variables": [
                "customer_name",
                "order_number",
                "order_date",
                "product_description",
                "quantity",
                "total_amount",
                "shipping_days",
            ],
            "description": "Order confirmation for customer purchases",
        },
        {
            "template_name": "price_alert",
            "subject": "Price Alert: {{ metal_type }} Reaches {{ price_level }}",
            "body_html": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #1a5490;">Price Alert Notification</h2>

    <p>Dear {{ customer_name }},</p>

    <p>This is an automated alert to notify you that {{ metal_type }} has reached your target price level.</p>

    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
        <strong>Current Market Prices:</strong><br>
        {{ metal_type }}: ${{ current_price }} per {{ unit }}<br>
        Change: {{ price_change }}%<br>
        Last Updated: {{ timestamp }}
    </div>

    <p>This may be an opportune time to consider your precious metals investment strategy. Our team is available to discuss your options and answer any questions you may have.</p>

    <p>Contact us at {{ contact_phone }} or reply to this email to speak with one of our precious metals specialists.</p>

    <p>Best regards,<br>
    Liberty Gold & Silver Team</p>

    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <p style="font-size: 0.9em; color: #666;">
        <em>Precious metals prices are subject to market fluctuations. This alert is for informational purposes only
        and does not constitute investment advice. Please consult your financial advisor before making investment decisions.</em>
    </p>
</body>
</html>
""",
            "category": "customer_service",
            "variables": [
                "customer_name",
                "metal_type",
                "price_level",
                "current_price",
                "unit",
                "price_change",
                "timestamp",
                "contact_phone",
            ],
            "description": "Price alert notification for customers monitoring precious metals prices",
        },
        {
            "template_name": "ira_information",
            "subject": "Information About Precious Metals IRA",
            "body_html": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #1a5490;">Precious Metals IRA Information</h2>

    <p>Dear {{ customer_name }},</p>

    <p>Thank you for your interest in a Precious Metals IRA with Liberty Gold & Silver. A self-directed IRA
    allows you to diversify your retirement portfolio with physical gold, silver, platinum, and palladium.</p>

    <h3 style="color: #1a5490;">Key Benefits:</h3>
    <ul>
        <li>Tax-advantaged retirement savings</li>
        <li>Portfolio diversification beyond traditional stocks and bonds</li>
        <li>Protection against inflation and currency devaluation</li>
        <li>Physical ownership of precious metals in secure storage</li>
    </ul>

    <h3 style="color: #1a5490;">Next Steps:</h3>
    <ol>
        <li>Review the attached IRA information guide</li>
        <li>Schedule a consultation with our IRA specialists</li>
        <li>Complete the IRA account setup process</li>
        <li>Fund your account and select your metals</li>
    </ol>

    <p>Our IRA specialists are available to answer any questions you may have about the process,
    eligible metals, storage options, and tax implications.</p>

    <p>To schedule a consultation, reply to this email or call us at {{ contact_phone }}.</p>

    <p>Best regards,<br>
    Liberty Gold & Silver IRA Team</p>

    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
    <p style="font-size: 0.9em; color: #666;">
        <em>This communication is for educational purposes only and does not constitute tax, legal, or investment advice.
        Please consult with qualified professionals regarding your specific situation. IRA regulations and tax implications
        vary based on individual circumstances.</em>
    </p>
</body>
</html>
""",
            "category": "customer_service",
            "variables": ["customer_name", "contact_phone"],
            "description": "Educational information about precious metals IRAs",
        },
        {
            "template_name": "team_notification",
            "subject": "New {{ notification_type }}: {{ subject_line }}",
            "body_html": """
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #1a5490;">{{ notification_type }}</h2>

    <p>Team,</p>

    <p>{{ message_body }}</p>

    <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <strong>Details:</strong><br>
        {{ details }}
    </div>

    {% if action_required %}
    <p style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107;">
        <strong>Action Required:</strong> {{ action_required }}
    </p>
    {% endif %}

    <p>Please review and take appropriate action as needed.</p>

    <p>Thanks,<br>
    {{ sender_name }}</p>
</body>
</html>
""",
            "category": "internal",
            "variables": [
                "notification_type",
                "subject_line",
                "message_body",
                "details",
                "action_required",
                "sender_name",
            ],
            "description": "Internal team notifications and updates",
        },
    ]

    created_count = 0
    failed_count = 0

    for template_data in templates:
        try:
            print(f"Creating template: {template_data['template_name']}...", end=" ")
            result = await EmailTemplateTools.create_template(**template_data)
            print(f"✅ Created (ID: {result['template_id']})")
            created_count += 1
        except Exception as e:
            print(f"❌ Failed: {e}")
            failed_count += 1

    print()
    print("=" * 60)
    print(f"✅ Successfully created {created_count} template(s)")
    if failed_count > 0:
        print(f"❌ Failed to create {failed_count} template(s)")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. List templates: Use list_templates tool in Claude Code")
    print("2. Test sending: Use send_from_template tool with sample data")
    print("3. View template: Use get_template tool with template name or ID")


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(create_templates())
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
