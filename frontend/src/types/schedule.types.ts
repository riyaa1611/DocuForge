import { DataSource } from './report.types';

export interface Schedule {
  id: string;
  user_id: string;
  template_id: string;
  template_name?: string;
  name: string;
  cron_expression: string;
  params: Record<string, unknown>;
  data_source: DataSource;
  is_active: boolean;
  next_run: string;
  last_run: string | null;
  created_at: string;
}

export interface ScheduleCreateRequest {
  template_id: string;
  name?: string;
  cron_expression: string;
  data_source: DataSource;
  params?: Record<string, unknown>;
}

export interface ScheduleUpdateRequest {
  name?: string;
  cron_expression?: string;
  params?: Record<string, unknown>;
  data_source?: DataSource;
  is_active?: boolean;
}

export interface SchedulesListResponse {
  items: Schedule[];
  total: number;
}
