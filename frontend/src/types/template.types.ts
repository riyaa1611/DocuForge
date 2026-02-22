export interface TemplateParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'select';
  label: string;
  required: boolean;
  default_value?: unknown;
  options?: string[]; // For select type
  description?: string;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string | null;
  category: string;
  schema: TemplateParameter[];
  sample_output_url?: string;
  created_at: string;
}

export interface TemplatesListResponse {
  items: Template[];
  total: number;
}
