-- ENUM types
CREATE TYPE billing_cycle_type AS ENUM ('monthly', 'quarterly', 'yearly');
CREATE TYPE subscription_status AS ENUM ('active', 'past_due', 'cancelled', 'expired');
CREATE TYPE transaction_type AS ENUM ('payment', 'refund', 'chargeback');
CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'cancelled');
CREATE TYPE invoice_status AS ENUM ('draft', 'open', 'paid', 'void', 'uncollectible');
CREATE TYPE payment_method_type AS ENUM ('card', 'bank_account', 'wallet');
CREATE TYPE plan_status AS ENUM ('active', 'inactive');

-- Subscription Plans
CREATE TABLE subscription_plans (
                                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                                    name VARCHAR NOT NULL,
                                    description TEXT,
                                    price DECIMAL(10,2) NOT NULL,
                                    currency VARCHAR(3) NOT NULL,
                                    billing_cycle billing_cycle_type,
                                    trial_days INTEGER DEFAULT 0,
                                    status plan_status DEFAULT 'active',
                                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- User Subscriptions
CREATE TABLE subscriptions (
                               id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                               user_id UUID REFERENCES users(id),
                               plan_id UUID REFERENCES subscription_plans(id),
                               status subscription_status DEFAULT 'active',
                               current_period_start TIMESTAMPTZ,
                               current_period_end TIMESTAMPTZ,
                               cancelled_at TIMESTAMPTZ,
                               created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Payment Methods
CREATE TABLE payment_methods (
                                 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                                 type payment_method_type NOT NULL,
                                 provider VARCHAR,
                                 provider_id VARCHAR,
                                 last4 VARCHAR(4),
                                 expiry_month INTEGER,
                                 expiry_year INTEGER,
                                 created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Transactions
CREATE TABLE transactions (
                              id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                              user_id UUID REFERENCES users(id),
                              subscription_id UUID REFERENCES subscriptions(id),
                              payment_method_id UUID REFERENCES payment_methods(id),
                              amount DECIMAL(10,2) NOT NULL,
                              currency VARCHAR(3) NOT NULL,
                              type transaction_type NOT NULL,
                              status transaction_status NOT NULL DEFAULT 'pending',
                              gateway VARCHAR,
                              gateway_transaction_id VARCHAR,
                              failure_reason TEXT,
                              processed_at TIMESTAMPTZ,
                              created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Invoices
CREATE TABLE invoices (
                          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                          subscription_id UUID REFERENCES subscriptions(id),
                          invoice_number VARCHAR UNIQUE NOT NULL,
                          amount_subtotal DECIMAL(10,2),
                          tax_amount DECIMAL(10,2),
                          amount_total DECIMAL(10,2),
                          currency VARCHAR(3),
                          status invoice_status DEFAULT 'draft',
                          due_date DATE,
                          paid_at TIMESTAMPTZ,
                          created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Dùng gen_random_uuid() từ extension pgcrypto --
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

