-- Create enum for report status
CREATE TYPE public.report_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Create templates table (shared across all users, read-only for regular users)
CREATE TABLE public.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    html_path VARCHAR(255) NOT NULL,
    thumbnail_url TEXT,
    category VARCHAR(100),
    schema JSONB,
    sample_output_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create reports table
CREATE TABLE public.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    template_id UUID REFERENCES public.templates(id) ON DELETE SET NULL,
    status report_status NOT NULL DEFAULT 'pending',
    file_path VARCHAR(500),
    file_size INTEGER,
    params JSONB,
    data_source JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create schedules table
CREATE TABLE public.schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    params JSONB,
    data_source JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true,
    next_run TIMESTAMP WITH TIME ZONE,
    last_run TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX idx_reports_user_id ON public.reports(user_id);
CREATE INDEX idx_reports_template_id ON public.reports(template_id);
CREATE INDEX idx_reports_status ON public.reports(status);
CREATE INDEX idx_reports_created_at ON public.reports(created_at DESC);
CREATE INDEX idx_schedules_user_id ON public.schedules(user_id);
CREATE INDEX idx_schedules_template_id ON public.schedules(template_id);
CREATE INDEX idx_schedules_is_active ON public.schedules(is_active);
CREATE INDEX idx_templates_name ON public.templates(name);

-- Enable RLS on all tables
ALTER TABLE public.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;

-- Templates policies (public read, no write for regular users)
CREATE POLICY "Templates are viewable by authenticated users" 
ON public.templates 
FOR SELECT 
TO authenticated
USING (true);

-- Reports policies (users can only access their own reports)
CREATE POLICY "Users can view their own reports" 
ON public.reports 
FOR SELECT 
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own reports" 
ON public.reports 
FOR INSERT 
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own reports" 
ON public.reports 
FOR UPDATE 
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own reports" 
ON public.reports 
FOR DELETE 
TO authenticated
USING (auth.uid() = user_id);

-- Schedules policies (users can only access their own schedules)
CREATE POLICY "Users can view their own schedules" 
ON public.schedules 
FOR SELECT 
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own schedules" 
ON public.schedules 
FOR INSERT 
TO authenticated
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own schedules" 
ON public.schedules 
FOR UPDATE 
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own schedules" 
ON public.schedules 
FOR DELETE 
TO authenticated
USING (auth.uid() = user_id);

-- Insert sample templates for testing
INSERT INTO public.templates (id, name, description, html_path, thumbnail_url, category, schema) VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Financial Report', 'Comprehensive financial analysis with charts and tables', 'templates/financial_report.html', null, 'Finance', '{"parameters": [{"name": "start_date", "type": "date", "label": "Start Date", "required": true}, {"name": "end_date", "type": "date", "label": "End Date", "required": true}]}'),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'Invoice Template', 'Professional invoice with itemized billing', 'templates/invoice.html', null, 'Billing', '{"parameters": [{"name": "customer_id", "type": "string", "label": "Customer ID", "required": true}, {"name": "invoice_date", "type": "date", "label": "Invoice Date", "required": true}]}'),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'Sales Summary', 'Monthly sales overview with performance metrics', 'templates/sales_summary.html', null, 'Sales', '{"parameters": [{"name": "month", "type": "select", "label": "Month", "required": true, "options": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}, {"name": "year", "type": "number", "label": "Year", "required": true}]}');