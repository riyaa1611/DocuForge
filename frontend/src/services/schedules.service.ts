import { api } from './api';
import type { 
  Schedule, 
  ScheduleCreateRequest, 
  ScheduleUpdateRequest,
  SchedulesListResponse
} from '@/types';

export interface ScheduleFilters {
  is_active?: boolean;
  template_id?: string;
  limit?: number;
  offset?: number;
}

export const schedulesService = {
  /**
   * Get a paginated list of schedules with optional filters
   */
  getSchedules: async (filters?: ScheduleFilters): Promise<SchedulesListResponse> => {
    const response = await api.get<SchedulesListResponse>('/schedules', { params: filters as Record<string, string | number> });
    return response;
  },

  /**
   * Get a specific schedule by ID
   */
  getSchedule: async (id: string): Promise<Schedule> => {
    const response = await api.get<Schedule>(`/schedules/${id}`);
    return response;
  },

  /**
   * Create a new schedule
   */
  createSchedule: async (request: ScheduleCreateRequest): Promise<Schedule> => {
    const response = await api.post<Schedule>('/schedules', request);
    return response;
  },

  /**
   * Update an existing schedule
   */
  updateSchedule: async (id: string, request: ScheduleUpdateRequest): Promise<Schedule> => {
    const response = await api.put<Schedule>(`/schedules/${id}`, request);
    return response;
  },

  /**
   * Delete a schedule
   */
  deleteSchedule: async (id: string): Promise<void> => {
    await api.delete(`/schedules/${id}`);
  },

  /**
   * Toggle schedule active status
   */
  toggleActive: async (id: string, isActive: boolean): Promise<Schedule> => {
    return schedulesService.updateSchedule(id, { is_active: isActive });
  },
};
