import api from '../utils/api';

export const cameraService = {
  getAll: async () => {
    const response = await api.get('/cameras');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/cameras/${id}`);
    return response.data;
  },

  create: async (cameraData) => {
    const response = await api.post('/cameras', cameraData);
    return response.data;
  },

  update: async (id, cameraData) => {
    const response = await api.put(`/cameras/${id}`, cameraData);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/cameras/${id}`);
    return response.data;
  },
};

