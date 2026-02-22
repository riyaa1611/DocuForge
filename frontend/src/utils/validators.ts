import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().trim().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export const registerSchema = z.object({
  name: z.string().trim().min(2, 'Name must be at least 2 characters').max(100, 'Name is too long'),
  email: z.string().trim().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

export const sqlDataSourceSchema = z.object({
  connection_string: z.string().min(1, 'Connection string is required'),
  query: z.string().min(1, 'SQL query is required'),
});

export const apiDataSourceSchema = z.object({
  url: z.string().url('Please enter a valid URL'),
  method: z.enum(['GET', 'POST', 'PUT', 'DELETE']),
  headers: z.record(z.string()).optional(),
  body: z.string().optional(),
});

export const csvDataSourceSchema = z.object({
  file_name: z.string().min(1, 'Please upload a CSV file'),
});

export const reportGenerateSchema = z.object({
  template_id: z.string().uuid('Please select a template'),
  data_source_type: z.enum(['sql', 'api', 'csv']),
  sql_config: sqlDataSourceSchema.optional(),
  api_config: apiDataSourceSchema.optional(),
  csv_config: csvDataSourceSchema.optional(),
}).refine((data) => {
  if (data.data_source_type === 'sql') {
    return !!data.sql_config;
  }
  if (data.data_source_type === 'api') {
    return !!data.api_config;
  }
  if (data.data_source_type === 'csv') {
    return !!data.csv_config;
  }
  return true;
}, {
  message: 'Please configure the data source',
});

export const scheduleSchema = z.object({
  template_id: z.string().uuid('Please select a template'),
  cron_expression: z.string().min(1, 'Cron expression is required'),
  data_source_type: z.enum(['sql', 'api', 'csv']),
  is_active: z.boolean().default(true),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ReportGenerateFormData = z.infer<typeof reportGenerateSchema>;
export type ScheduleFormData = z.infer<typeof scheduleSchema>;
