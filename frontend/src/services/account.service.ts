import api from './api';
import type { Account, AccountCreate } from '../types';

export const accountService = {
  // Get all accounts for the current user
  getAccounts: async (params?: { is_active?: boolean }): Promise<Account[]> => {
    const response = await api.get<Account[]>('/accounts', { params });
    return response.data;
  },

  // Get a specific account by ID
  getAccount: async (accountId: string): Promise<Account> => {
    const response = await api.get<Account>(`/accounts/${accountId}`);
    return response.data;
  },

  // Create a new account
  createAccount: async (accountData: AccountCreate): Promise<Account> => {
    const response = await api.post<Account>('/accounts', accountData);
    return response.data;
  },

  // Update an existing account
  updateAccount: async (accountId: string, accountData: Partial<AccountCreate>): Promise<Account> => {
    const response = await api.put<Account>(`/accounts/${accountId}`, accountData);
    return response.data;
  },

  // Delete an account
  deleteAccount: async (accountId: string): Promise<void> => {
    await api.delete(`/accounts/${accountId}`);
  },

  // Get account balance
  getAccountBalance: async (accountId: string): Promise<number> => {
    const response = await api.get<{ balance: number }>(`/accounts/${accountId}/balance`);
    return response.data.balance;
  },
};

// Made with Bob
