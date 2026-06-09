-- UC5 Banking/Insurance Portal - Database Migration Script
-- Creates all new tables for MCP, products, escalations, and tickets
-- Run this after existing FinPilot tables are created

-- ============================================================================
-- PRODUCTS AND POLICY DOCUMENTS
-- ============================================================================

-- Products table (banking and insurance products)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_type VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    features JSONB,
    eligibility_criteria JSONB,
    terms_and_conditions TEXT,
    interest_rate DECIMAL(5,2),
    min_amount DECIMAL(15,2),
    max_amount DECIMAL(15,2),
    fees JSONB,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    display_order INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_products_type ON products(product_type);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_products_code ON products(product_code);

-- Product documents table
CREATE TABLE IF NOT EXISTS product_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    vector_id VARCHAR(255),
    content_hash VARCHAR(64),
    file_size INTEGER,
    mime_type VARCHAR(100),
    is_indexed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_product_documents_product ON product_documents(product_id);
CREATE INDEX idx_product_documents_type ON product_documents(document_type);
CREATE INDEX idx_product_documents_indexed ON product_documents(is_indexed);

-- Policy documents table (general policies, not product-specific)
CREATE TABLE IF NOT EXISTS policy_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    file_path VARCHAR(500),
    vector_id VARCHAR(255),
    content_hash VARCHAR(64),
    file_size INTEGER,
    mime_type VARCHAR(100),
    is_indexed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    version VARCHAR(20),
    effective_date TIMESTAMP,
    expiry_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_policy_documents_type ON policy_documents(document_type);
CREATE INDEX idx_policy_documents_active ON policy_documents(is_active);
CREATE INDEX idx_policy_documents_indexed ON policy_documents(is_indexed);

-- ============================================================================
-- INTENT DETECTION AND COMPLIANCE
-- ============================================================================

-- Intent logs table (tracks all intent classifications)
CREATE TABLE IF NOT EXISTS intent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_message TEXT NOT NULL,
    detected_intent VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    was_blocked BOOLEAN DEFAULT FALSE,
    reason TEXT,
    entities JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_intent_logs_conversation ON intent_logs(conversation_id);
CREATE INDEX idx_intent_logs_intent ON intent_logs(detected_intent);
CREATE INDEX idx_intent_logs_blocked ON intent_logs(was_blocked);
CREATE INDEX idx_intent_logs_created ON intent_logs(created_at);

-- Compliance violations table (tracks policy violations)
CREATE TABLE IF NOT EXISTS compliance_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    violation_type VARCHAR(100) NOT NULL,
    ai_response TEXT NOT NULL,
    corrected_response TEXT,
    severity VARCHAR(20) DEFAULT 'medium',
    violations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_compliance_violations_conversation ON compliance_violations(conversation_id);
CREATE INDEX idx_compliance_violations_type ON compliance_violations(violation_type);
CREATE INDEX idx_compliance_violations_severity ON compliance_violations(severity);
CREATE INDEX idx_compliance_violations_created ON compliance_violations(created_at);

-- ============================================================================
-- ESCALATIONS (HUMAN-IN-THE-LOOP)
-- ============================================================================

-- Create enum types for escalations
DO $$ BEGIN
    CREATE TYPE escalation_priority AS ENUM ('low', 'medium', 'high', 'urgent');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE escalation_status AS ENUM ('pending', 'in_review', 'resolved', 'closed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Escalations table
CREATE TABLE IF NOT EXISTS escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    reason VARCHAR(255) NOT NULL,
    priority escalation_priority DEFAULT 'medium' NOT NULL,
    status escalation_status DEFAULT 'pending' NOT NULL,
    assigned_to UUID REFERENCES users(id),
    resolution_notes TEXT,
    resolution_action VARCHAR(100),
    escalation_context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    assigned_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_escalations_conversation ON escalations(conversation_id);
CREATE INDEX idx_escalations_status ON escalations(status);
CREATE INDEX idx_escalations_priority ON escalations(priority);
CREATE INDEX idx_escalations_assigned ON escalations(assigned_to);
CREATE INDEX idx_escalations_created ON escalations(created_at);

-- ============================================================================
-- SUPPORT TICKETS
-- ============================================================================

-- Create enum types for tickets
DO $$ BEGIN
    CREATE TYPE ticket_priority AS ENUM ('low', 'medium', 'high', 'urgent');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Support tickets table
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    conversation_id UUID REFERENCES conversations(id),
    issue_type VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority ticket_priority DEFAULT 'medium' NOT NULL,
    status ticket_status DEFAULT 'open' NOT NULL,
    assigned_to UUID REFERENCES users(id),
    department VARCHAR(100),
    resolution TEXT,
    resolution_time_minutes INTEGER,
    ticket_metadata JSONB,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    assigned_at TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE INDEX idx_support_tickets_number ON support_tickets(ticket_number);
CREATE INDEX idx_support_tickets_user ON support_tickets(user_id);
CREATE INDEX idx_support_tickets_conversation ON support_tickets(conversation_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_support_tickets_priority ON support_tickets(priority);
CREATE INDEX idx_support_tickets_assigned ON support_tickets(assigned_to);
CREATE INDEX idx_support_tickets_issue_type ON support_tickets(issue_type);
CREATE INDEX idx_support_tickets_created ON support_tickets(created_at);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_documents_updated_at BEFORE UPDATE ON product_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policy_documents_updated_at BEFORE UPDATE ON policy_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE DATA (OPTIONAL - FOR TESTING)
-- ============================================================================

-- Insert sample products
INSERT INTO products (product_code, product_type, product_name, description, interest_rate, min_amount, max_amount, features, eligibility_criteria, is_active)
VALUES 
    ('SAV-001', 'savings', 'Premium Savings Account', 'High-interest savings account with no minimum balance', 4.50, 0, NULL, 
     '["No minimum balance", "Free ATM withdrawals", "Online banking", "Mobile app access"]'::jsonb,
     '["Age 18+", "Valid ID", "Proof of address"]'::jsonb, true),
    
    ('LOAN-001', 'loan', 'Personal Loan', 'Flexible personal loan with competitive rates', 8.99, 5000, 500000,
     '["Flexible tenure", "Quick approval", "No collateral", "Prepayment allowed"]'::jsonb,
     '["Age 21-60", "Minimum income $30,000/year", "Good credit score", "Employment proof"]'::jsonb, true),
    
    ('INS-001', 'insurance', 'Term Life Insurance', 'Comprehensive term life insurance coverage', NULL, 100000, 10000000,
     '["Tax benefits", "Flexible premium payment", "Accidental death benefit", "Critical illness rider"]'::jsonb,
     '["Age 18-65", "Medical examination", "No pre-existing conditions"]'::jsonb, true)
ON CONFLICT (product_code) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify table creation
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
    AND table_name IN (
        'products', 'product_documents', 'policy_documents',
        'intent_logs', 'compliance_violations',
        'escalations', 'support_tickets'
    )
ORDER BY table_name;

-- Made with Bob - Compliance-First AI Assistant