#!/usr/bin/env python3
"""
Database initialization script.

Creates the SQLite database with required tables for the M365 Admin MCP Server.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from m365_admin_mcp.config import get_settings


def create_tables(conn: sqlite3.Connection) -> None:
    """Create database tables."""

    # Email Templates table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_templates (
            template_id TEXT PRIMARY KEY,
            template_name TEXT NOT NULL UNIQUE,
            subject TEXT NOT NULL,
            body_html TEXT NOT NULL,
            body_text TEXT,
            category TEXT NOT NULL,
            variables TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            version INTEGER DEFAULT 1
        )
    """)

    # Template Usage Logs table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS template_usage (
            usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id TEXT NOT NULL,
            sent_by TEXT NOT NULL,
            sent_to TEXT NOT NULL,
            variables_used TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_id TEXT,
            FOREIGN KEY (template_id) REFERENCES email_templates(template_id)
        )
    """)

    # Audit Logs table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            user_email TEXT,
            target_resource TEXT,
            details TEXT,
            status TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Configuration Settings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_template_category
        ON email_templates(category)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_template_usage_template
        ON template_usage(template_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_timestamp
        ON audit_logs(timestamp)
    """)

    conn.commit()


def insert_sample_data(conn: sqlite3.Connection) -> None:
    """Insert sample configuration data."""

    # Insert server info
    conn.execute("""
        INSERT OR REPLACE INTO config (key, value)
        VALUES ('server_version', '1.0.0')
    """)

    conn.execute("""
        INSERT OR REPLACE INTO config (key, value)
        VALUES ('db_initialized', datetime('now'))
    """)

    conn.commit()


def main() -> None:
    """Main initialization function."""
    print("M365 Admin MCP Server - Database Initialization")
    print("=" * 50)

    # Get settings
    try:
        settings = get_settings()
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        print("   Make sure .env file is configured correctly")
        sys.exit(1)

    db_path = settings.database_path

    # Ensure database directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nDatabase path: {db_path}")

    # Check if database already exists
    if db_path.exists():
        response = input("\n⚠️  Database already exists. Recreate? (y/N): ")
        if not response.lower().startswith('y'):
            print("Aborted.")
            sys.exit(0)
        db_path.unlink()
        print("Existing database deleted.")

    # Create database and tables
    print("\nCreating database...")
    try:
        conn = sqlite3.connect(db_path)

        print("Creating tables...")
        create_tables(conn)

        print("Inserting sample data...")
        insert_sample_data(conn)

        conn.close()

        print("\n✅ Database initialized successfully!")
        print(f"   Location: {db_path}")
        print("\nNext steps:")
        print("1. Configure Azure AD credentials in .env")
        print("2. Test connection: python -m m365_admin_mcp.server")

    except Exception as e:
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
