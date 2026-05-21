import api from './api';
import type { Simulation, SimulationCreate } from '../types';

export const simulationService = {
  // Get all simulations for the current user
  getSimulations: async (params?: {
    simulation_type?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ simulations: Simulation[]; total: number }> => {
    const response = await api.get<{ simulations: Simulation[]; total: number }>('/simulations', { params });
    return response.data;
  },

  // Get a specific simulation by ID
  getSimulation: async (simulationId: string): Promise<Simulation> => {
    const response = await api.get<Simulation>(`/simulations/${simulationId}`);
    return response.data;
  },

  // Create and run a new simulation
  createSimulation: async (simulationData: SimulationCreate): Promise<Simulation> => {
    const response = await api.post<Simulation>('/simulations', simulationData);
    return response.data;
  },

  // Re-run an existing simulation
  rerunSimulation: async (simulationId: string): Promise<Simulation> => {
    const response = await api.post<Simulation>(`/simulations/${simulationId}/rerun`);
    return response.data;
  },

  // Delete a simulation
  deleteSimulation: async (simulationId: string): Promise<void> => {
    await api.delete(`/simulations/${simulationId}`);
  },

  // Get simulation types
  getSimulationTypes: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/simulations/types');
    return response.data;
  },

  // Compare multiple simulations
  compareSimulations: async (simulationIds: string[]): Promise<any> => {
    const response = await api.post('/simulations/compare', { simulation_ids: simulationIds });
    return response.data;
  },

  // Export simulation results
  exportSimulation: async (simulationId: string, format: 'pdf' | 'csv' | 'json'): Promise<Blob> => {
    const response = await api.get(`/simulations/${simulationId}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },
};

// Made with Bob
