-- Dermé schema
-- Single-user, no auth

-- ─── Enums ────────────────────────────────────────────────────────────────────

CREATE TYPE skin_type_enum AS ENUM (
  'normal', 'dry', 'oily', 'combination', 'sensitive'
);

CREATE TYPE skin_concern_enum AS ENUM (
  'acne', 'hyperpigmentation', 'dryness', 'sensitivity',
  'redness', 'aging', 'texture', 'pores', 'dark_circles',
  'dehydration', 'brightening'
);

CREATE TYPE product_category_enum AS ENUM (
  'cleanser', 'toner', 'serum', 'moisturiser', 'spf',
  'eye_cream', 'exfoliant', 'mask', 'treatment', 'mist',
  'oil', 'lip', 'body', 'other'
);

CREATE TYPE product_status_enum AS ENUM (
  'active', 'finished', 'paused', 'destashed', 'sample'
);

CREATE TYPE reaction_type_enum AS ENUM (
  'redness', 'breakout', 'itching', 'burning',
  'stinging', 'peeling', 'dryness', 'purging'
);

CREATE TYPE severity_enum AS ENUM (
  'mild', 'moderate', 'severe'
);

CREATE TYPE wishlist_source_enum AS ENUM (
  'chatbot', 'manual'
);

-- ─── Tables ───────────────────────────────────────────────────────────────────

CREATE TABLE profile (
  id            INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1), -- enforces single row
  skin_type     skin_type_enum,
  concerns      skin_concern_enum[],
  notes         TEXT,
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name             TEXT NOT NULL, -- from incidecoder link
  brand            TEXT, -- from incidecoder link
  category         product_category_enum,
  rating           SMALLINT CHECK (rating BETWEEN 1 AND 5),
  status           product_status_enum NOT NULL DEFAULT 'active',
  had_reaction     BOOLEAN NOT NULL DEFAULT FALSE,
  ingredients_text TEXT, -- from incidecoder link
  notes            TEXT,
  purchase_date    DATE,
  opened_date      DATE,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW(),
  purchase_times   INTEGER DEFAULT 0
);

CREATE TABLE ingredients (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL UNIQUE, -- lowercase, normalised
  is_flagged   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE product_ingredients (
  product_id    UUID REFERENCES products(id) ON DELETE CASCADE,
  ingredient_id UUID REFERENCES ingredients(id) ON DELETE CASCADE,
  rank          INTEGER, -- order on label (1 = first listed)
  PRIMARY KEY (product_id, ingredient_id)
);

CREATE TABLE reactions (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ingredient_id     UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
  reaction_type     reaction_type_enum NOT NULL,
  severity          severity_enum NOT NULL,
  source_product_id UUID REFERENCES products(id) ON DELETE SET NULL,
  notes             TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE wishlist (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  brand      TEXT,
  category   product_category_enum,
  source     wishlist_source_enum NOT NULL DEFAULT 'manual',
  notes      TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Indexes ──────────────────────────────────────────────────────────────────

-- Culprit Finder: find all products containing a specific ingredient
CREATE INDEX idx_product_ingredients_ingredient ON product_ingredients(ingredient_id);

-- Culprit Finder: filter only products where had_reaction = true
CREATE INDEX idx_products_had_reaction ON products(had_reaction) WHERE had_reaction = TRUE;

-- Fast lookup of flagged ingredients (used when adding a new product)
CREATE INDEX idx_ingredients_flagged ON ingredients(is_flagged) WHERE is_flagged = TRUE;
