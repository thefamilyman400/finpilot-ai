import api from './api';
import type { Transaction, TransactionCreate } from '../types';

export const transactionService = {
  // Get all transactions for the current user
  getTransactions: async (params?: {
    account_id?: string;
    category?: string;
    transaction_type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ transactions: Transaction[]; total: number }> => {
    // Filter out empty string values
    const cleanParams = Object.entries(params || {}).reduce((acc, [key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        acc[key] = value;
      }
      return acc;
    }, {} as Record<string, any>);
    
    const response = await api.get<{ transactions: Transaction[]; total: number }>('/transactions', { params: cleanParams });
    return response.data;
  },

  // Get a specific transaction by ID
  getTransaction: async (transactionId: string): Promise<Transaction> => {
    const response = await api.get<Transaction>(`/transactions/${transactionId}`);
    return response.data;
  },

  // Create a new transaction
  createTransaction: async (transactionData: TransactionCreate): Promise<Transaction> => {
    const response = await api.post<Transaction>('/transactions', transactionData);
    return response.data;
  },

  // Update an existing transaction
  updateTransaction: async (transactionId: string, transactionData: Partial<TransactionCreate>): Promise<Transaction> => {
    const response = await api.put<Transaction>(`/transactions/${transactionId}`, transactionData);
    return response.data;
  },

  // Delete a transaction
  deleteTransaction: async (transactionId: string): Promise<void> => {
    await api.delete(`/transactions/${transactionId}`);
  },

  // Get transaction categories
  getCategories: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/transactions/categories');
    return response.data;
  },

  // Get transaction summary/analytics
  getSummary: async (params?: {
    start_date?: string;
    end_date?: string;
    account_id?: string;
  }): Promise<any> => {
    const response = await api.get('/transactions/summary', { params });
    return response.data;
  },
};

// Made with Bob
