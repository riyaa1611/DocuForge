import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportsService } from '@/services/reports.service';
import type { ReportsFilters, ReportCreateRequest } from '@/types';
import { POLL_INTERVAL } from '@/utils/constants';

export const useReports = (filters?: ReportsFilters) => {
  return useQuery({
    queryKey: ['reports', filters],
    queryFn: () => reportsService.getReports(filters),
    staleTime: 30000,
  });
};

export const useReport = (id: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ['report', id],
    queryFn: () => reportsService.getReport(id),
    enabled: options?.enabled ?? true,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'pending' || status === 'processing' ? POLL_INTERVAL : false;
    },
  });
};

export const useGenerateReport = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ReportCreateRequest) => reportsService.generateReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
};

export const useDownloadReport = () => {
  return useMutation({
    mutationFn: ({ id, filename }: { id: string; filename?: string }) => 
      reportsService.downloadReport(id, filename),
  });
};

export const useDeleteReport = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => reportsService.deleteReport(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
};
