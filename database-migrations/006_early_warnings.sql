CREATE TABLE IF NOT EXISTS early_warning_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  business_category TEXT,
  rule_type TEXT NOT NULL,
  threshold_config JSONB NOT NULL DEFAULT '{}',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS early_warning_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
  business_id UUID REFERENCES businesses(id) ON DELETE SET NULL,
  rule_id UUID REFERENCES early_warning_rules(id) ON DELETE SET NULL,
  severity TEXT NOT NULL DEFAULT 'info',
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  evidence JSONB,
  status TEXT NOT NULL DEFAULT 'draft',
  scheduled_send_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_early_warning_rules_updated_at ON early_warning_rules;
CREATE TRIGGER trg_early_warning_rules_updated_at
BEFORE UPDATE ON early_warning_rules
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
