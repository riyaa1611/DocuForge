import { api } from './api';
import type { Template, TemplatesListResponse } from '@/types';

export const templatesService = {
  getTemplates: async (): Promise<TemplatesListResponse> => {
    const response = await api.get<TemplatesListResponse>('/templates');
    return response;
  },

  getTemplate: async (id: string): Promise<Template> => {
    const response = await api.get<Template>(`/templates/${id}`);
    return response;
  },
};
