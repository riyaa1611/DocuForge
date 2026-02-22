import { useQuery } from '@tanstack/react-query';
import { templatesService } from '@/services/templates.service';

export const useTemplates = () => {
  return useQuery({
    queryKey: ['templates'],
    queryFn: () => templatesService.getTemplates(),
    staleTime: 60000, // Templates don't change often
  });
};

export const useTemplate = (id: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ['template', id],
    queryFn: () => templatesService.getTemplate(id),
    enabled: options?.enabled ?? !!id,
    staleTime: 60000,
  });
};
