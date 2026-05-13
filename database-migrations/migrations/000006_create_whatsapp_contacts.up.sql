CREATE TABLE IF NOT EXISTS whatsapp_contacts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number        TEXT NOT NULL UNIQUE,
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,
    business_profile_id UUID REFERENCES business_profiles(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
