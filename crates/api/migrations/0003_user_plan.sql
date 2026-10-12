-- Migration 0003: subscription plan per user (trial / pro)
ALTER TABLE app_user
    ADD COLUMN plan TEXT NOT NULL DEFAULT 'trial' CHECK (plan IN ('trial', 'pro'));

-- Existing seeded administrator is treated as pro
UPDATE app_user SET plan = 'pro' WHERE username = 'admin';
