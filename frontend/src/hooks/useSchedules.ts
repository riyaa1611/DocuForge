import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { schedulesService } from '@/services/schedules.service';
import type { ScheduleCreateRequest, ScheduleUpdateRequest } from '@/types';

export const useSchedules = () => {
  return useQuery({
    queryKey: ['schedules'],
    queryFn: () => schedulesService.getSchedules(),
    staleTime: 30000,
  });
};

export const useSchedule = (id: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: ['schedule', id],
    queryFn: () => schedulesService.getSchedule(id),
    enabled: options?.enabled ?? !!id,
  });
};

export const useCreateSchedule = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ScheduleCreateRequest) => schedulesService.createSchedule(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
    },
  });
};

export const useUpdateSchedule = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ScheduleUpdateRequest }) => 
      schedulesService.updateSchedule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
    },
  });
};

export const useDeleteSchedule = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => schedulesService.deleteSchedule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
    },
  });
};

export const useToggleScheduleActive = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) => 
      schedulesService.toggleActive(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] });
    },
  });
};
