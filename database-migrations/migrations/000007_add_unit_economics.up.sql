ALTER TABLE business_profiles
    ADD COLUMN IF NOT EXISTS selling_price_per_unit NUMERIC(12, 2),
    ADD COLUMN IF NOT EXISTS cost_per_unit          NUMERIC(12, 2);
