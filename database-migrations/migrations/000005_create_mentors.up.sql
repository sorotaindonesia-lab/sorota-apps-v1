CREATE TABLE IF NOT EXISTS mentors (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT NOT NULL,
    expertise           TEXT NOT NULL,
    description         TEXT NOT NULL,
    business_background TEXT,
    booking_url         TEXT NOT NULL,
    image_url           TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
