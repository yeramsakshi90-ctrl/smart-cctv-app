import api from '../utils/api';

export const videoService = {
  upload: async (file, cameraId) => {
    const formData = new FormData();
    formData.append('video', file);
    formData.append('camera_id', cameraId);

    const response = await api.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  process: async (cameraId) => {
    const response = await api.post(`/videos/process/${cameraId}`);
    return response.data;
  },
};

