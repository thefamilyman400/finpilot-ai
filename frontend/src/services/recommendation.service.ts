import api from './api';
import type { GenerateRecommendationsResponse, Recommendation, RecommendationSummary } from '../types';

export interface RecommendationFilters {
  status?: string;
  type?: string;
  skip?: number;
  limit?: number;
}

export interface GenerateRecommendationsPayload {
  focus_areas?: string[];
  max_recommendations?: number;
  include_context?: boolean;
}

const cleanParams = (params: RecommendationFilters = {}) => {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== '')
  );
};

export const recommendationService = {
  async getRecommendations(params: RecommendationFilters = {}) {
    const response = await api.get<Recommendation[]>('/recommendations', {
      params: cleanParams(params),
    });
    return response.data;
  },

  async getSummary() {
    const response = await api.get<RecommendationSummary>('/recommendations/summary');
    return response.data;
  },

  async generateRecommendations(payload: GenerateRecommendationsPayload = {}) {
    const response = await api.post<GenerateRecommendationsResponse>('/recommendations/generate', {
      max_recommendations: payload.max_recommendations ?? 5,
      focus_areas: payload.focus_areas?.length ? payload.focus_areas : undefined,
      include_context: payload.include_context ?? false,
    });
    return response.data;
  },

  async acceptRecommendation(recommendationId: string) {
    const response = await api.post<Recommendation>(`/recommendations/${recommendationId}/accept`, {});
    return response.data;
  },

  async rejectRecommendation(recommendationId: string) {
    const response = await api.post<Recommendation>(`/recommendations/${recommendationId}/reject`, {});
    return response.data;
  },

  async completeRecommendation(recommendationId: string) {
    const response = await api.post<Recommendation>(`/recommendations/${recommendationId}/complete`, {});
    return response.data;
  },

  async deleteRecommendation(recommendationId: string) {
    await api.delete(`/recommendations/${recommendationId}`);
  },
};

// Made with Bob
