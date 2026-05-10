CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Optional later, when semantic search is enabled:
-- CREATE EXTENSION IF NOT EXISTS vector;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
