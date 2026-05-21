// User types
export interface UserPreferences {
  default_currency?: string;
  theme?: string;
  notifications_enabled?: boolean;
  language?: string;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  phone_number?: string;
  preferences?: UserPreferences;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface UserUpdate {
  full_name?: string;
  phone_number?: string;
  email?: string;
  preferences?: UserPreferences;
}

export interface PasswordChange {
  current_password: string;
  new_password: string;
}

// Account types
export interface Account {
  id: string;
  user_id: string;
  account_type: string;
  institution_name: string;
  account_name?: string;
  account_number_last4?: string;
  balance: number;
  currency: string;
  is_active: boolean;
  connection_status: string;
  last_synced?: string;
  created_at: string;
  updated_at: string;
  
  // Loan-specific fields
  loan_principal?: number;
  loan_outstanding?: number;
  interest_rate?: number;
  emi_amount?: number;
  loan_tenure_months?: number;
  remaining_tenure_months?: number;
  loan_start_date?: string;
  total_interest_paid?: number;
  total_principal_paid?: number;
}

export interface AccountCreate {
  account_type: string;
  institution_name: string;
  account_name?: string;
  account_number_last4?: string;
  balance?: number;
  currency: string;
  
  // Loan-specific fields
  loan_principal?: number;
  loan_outstanding?: number;
  interest_rate?: number;
  emi_amount?: number;
  loan_tenure_months?: number;
  remaining_tenure_months?: number;
  loan_start_date?: string;
  total_interest_paid?: number;
  total_principal_paid?: number;
}

// Transaction types
export interface Transaction {
  id: string;
  account_id: string;
  transaction_type: string;
  amount: number;
  description: string;
  category: string;
  transaction_date: string;
  merchant_name?: string;
  is_recurring?: boolean;
  tags?: string[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account_id: string;
  transaction_type: string;
  amount: number;
  description: string;
  transaction_date: string;
  category?: string;
  merchant_name?: string;
  is_recurring?: boolean;
  tags?: string[];
  notes?: string;
}

// Document types
export interface Document {
  id: string;
  user_id: string;
  filename: string;
  file_path: string;
  file_type: string;
  file_size: number;
  document_type: string;
  status: string;
  created_at: string;
  updated_at: string;
  extracted_text?: string;
  extracted_data?: any;
  ai_analysis?: any;
  confidence_score?: number;
  page_count?: number;
  language?: string;
  tags?: string[];
  is_sensitive?: boolean;
  processed_at?: string;
  expires_at?: string;
}

// Recommendation types
export interface Recommendation {
  id: string;
  user_id: string;
  recommendation_type: string;
  title: string;
  description: string;
  priority: string;
  status: string;
  created_at: string;
  updated_at: string;
}

// Simulation types
export interface Simulation {
  id: string;
  user_id: string;
  simulation_type: string;
  parameters: Record<string, any>;
  results: Record<string, any>;
  created_at: string;
}

export interface SimulationCreate {
  simulation_type: string;
  parameters: Record<string, any>;
}

// Workflow types
export interface Workflow {
  id: string;
  user_id: string;
  workflow_type: string;
  status: string;
  steps: Record<string, any>;
  current_step: number;
  created_at: string;
  updated_at: string;
}

// Conversation types
export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// API Error types
export interface ApiError {
  detail: string;
}

// Pagination types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Made with Bob
