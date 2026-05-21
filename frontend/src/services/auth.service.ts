import api from './api';
import type { LoginRequest, LoginResponse, RegisterRequest, User } from '../types';

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse & { user: User }> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    // Store token
    localStorage.setItem('access_token', response.data.access_token);
    
    // Fetch user data
    const user = await authService.getCurrentUser();
    
    return { ...response.data, user };
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  },
};

// Made with Bob
