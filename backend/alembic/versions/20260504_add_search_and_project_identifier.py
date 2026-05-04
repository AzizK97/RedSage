"""Add project_identifier and full-text search support for messages and threads

Revision ID: 20260504_add_search
Revises: 
Create Date: 2026-05-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260504_add_search'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable pg_trgm extension (if not already enabled)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # Add project_identifier columns
    op.execute("ALTER TABLE IF EXISTS thread_owners ADD COLUMN IF NOT EXISTS project_identifier TEXT;")
    op.execute("ALTER TABLE IF EXISTS thread_messages ADD COLUMN IF NOT EXISTS project_identifier TEXT;")

    # Add tsvector column for message full-text search
    op.execute("ALTER TABLE IF EXISTS thread_messages ADD COLUMN IF NOT EXISTS search_tsv tsvector;")

    # Create GIN index for full-text search on messages
    op.execute("CREATE INDEX IF NOT EXISTS idx_thread_messages_search_tsv ON thread_messages USING GIN(search_tsv);")

    # Create trigram index on message content for fuzzy/partial matching
    op.execute("CREATE INDEX IF NOT EXISTS idx_thread_messages_content_trgm ON thread_messages USING GIN (content gin_trgm_ops);")

    # Create trigram index on thread_owners.title for fast title fuzzy search
    op.execute("CREATE INDEX IF NOT EXISTS idx_thread_owners_title_trgm ON thread_owners USING GIN (title gin_trgm_ops);")

    # Create trigger function to update search_tsv
    op.execute(r"""
    CREATE OR REPLACE FUNCTION thread_messages_search_trigger() RETURNS trigger AS $$
    begin
      new.search_tsv := to_tsvector('english', coalesce(new.content, ''));
      return new;
    end
    $$ LANGUAGE plpgsql;
    """)

    # Attach trigger (DROP if exists then CREATE — PostgreSQL has no CREATE TRIGGER IF NOT EXISTS)
    op.execute(r"""
    DROP TRIGGER IF EXISTS thread_messages_search_tsv_update ON thread_messages;
    CREATE TRIGGER thread_messages_search_tsv_update
    BEFORE INSERT OR UPDATE ON thread_messages
    FOR EACH ROW EXECUTE FUNCTION thread_messages_search_trigger();
    """)


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS thread_messages_search_tsv_update ON thread_messages;")
    op.execute("DROP FUNCTION IF EXISTS thread_messages_search_trigger();")
    op.execute("DROP INDEX IF EXISTS idx_thread_messages_content_trgm;")
    op.execute("DROP INDEX IF EXISTS idx_thread_messages_search_tsv;")
    op.execute("DROP INDEX IF EXISTS idx_thread_owners_title_trgm;")
    op.execute("ALTER TABLE IF EXISTS thread_messages DROP COLUMN IF EXISTS search_tsv;")
    op.execute("ALTER TABLE IF EXISTS thread_messages DROP COLUMN IF EXISTS project_identifier;")
    op.execute("ALTER TABLE IF EXISTS thread_owners DROP COLUMN IF EXISTS project_identifier;")
