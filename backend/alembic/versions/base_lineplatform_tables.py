from alembic import op

revision = "0001_baseline_platform"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS redmine_users (
            id TEXT PRIMARY KEY,
            redmine_user_id INTEGER UNIQUE NOT NULL,
            email TEXT NOT NULL,
            full_name TEXT NOT NULL,
            platform_role TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS entitlements (
            user_id TEXT PRIMARY KEY REFERENCES redmine_users(id) ON DELETE CASCADE,
            enabled BOOLEAN NOT NULL DEFAULT FALSE,
            enabled_by_admin_id TEXT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS thread_owners (
            thread_id TEXT PRIMARY KEY,
            owner_user_id TEXT NOT NULL REFERENCES redmine_users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_redmine_users_redmine_user_id ON redmine_users(redmine_user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_thread_owners_owner_user_id ON thread_owners(owner_user_id);")

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS thread_owners;")
    op.execute("DROP TABLE IF EXISTS entitlements;")
    op.execute("DROP TABLE IF EXISTS redmine_users;")
