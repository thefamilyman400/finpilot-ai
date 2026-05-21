import api from './api';
import type { Document } from '../types';

export const documentService = {
  // Get all documents for the current user
  getDocuments: async (params?: {
    document_type?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<Document[]> => {
    const response = await api.get<Document[]>('/documents/', { params });
    return response.data;
  },

  // Get a specific document by ID
  getDocument: async (documentId: string): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${documentId}`);
    return response.data;
  },

  // Upload a new document
  uploadDocument: async (file: File, documentType: string = 'other'): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    const response = await api.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete a document
  deleteDocument: async (documentId: string): Promise<void> => {
    await api.delete(`/documents/${documentId}`);
  },

  // Download a document
  downloadDocument: async (documentId: string): Promise<Blob> => {
    const response = await api.get(`/documents/${documentId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Process/re-process a document (OCR)
  processDocument: async (documentId: string): Promise<Document> => {
    const response = await api.post<Document>(`/documents/${documentId}/process`);
    return response.data;
  },

  // Get extracted text from document
  getExtractedText: async (documentId: string): Promise<{ text: string }> => {
    const response = await api.get<{ text: string }>(`/documents/${documentId}/text`);
    return response.data;
  },

  // Parse document and import data (bank statements, etc.)
  parseDocument: async (file: File): Promise<{
    file_name: string;
    detected_bank: string | null;
    detected_account_type: string | null;
    account_number: string | null;
    transactions_found: number;
    accounts_created: number;
    transactions_created: number;
    errors: string[];
    warnings: string[];
  }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/parse-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Made with Bob
