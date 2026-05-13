CREATE TABLE IF NOT EXISTS business_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name   TEXT NOT NULL,
    business_type   TEXT NOT NULL,
    location        TEXT NOT NULL,
    monthly_revenue NUMERIC(15, 2),
    monthly_profit  NUMERIC(15, 2),
    main_products   TEXT,
    main_problem    TEXT NOT NULL,
    target_goal     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_business_profiles_user_id ON business_profiles(user_id);
