import React, { useState } from 'react';
import { Loader2, Database, Globe, FileSpreadsheet, AlertCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { useTemplates } from '@/hooks/useTemplates';
import { useGenerateReport } from '@/hooks/useReports';
import { fastapiService, isBackendConfigured, getApiUrl } from '@/services/fastapi.service';
import type { DataSourceType, DataSource } from '@/types';

interface ReportGeneratorModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const dataSourceOptions: { type: DataSourceType; label: string; icon: React.ElementType; description: string }[] = [
  { type: 'sql', label: 'SQL Database', icon: Database, description: 'Connect to a database' },
  { type: 'api', label: 'REST API', icon: Globe, description: 'Fetch from an API endpoint' },
  { type: 'csv', label: 'CSV File', icon: FileSpreadsheet, description: 'Upload a CSV file' },
];

export const ReportGeneratorModal: React.FC<ReportGeneratorModalProps> = ({
  open,
  onOpenChange,
}) => {
  const [step, setStep] = useState(1);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [dataSourceType, setDataSourceType] = useState<DataSourceType | null>(null);

  // SQL config
  const [connectionString, setConnectionString] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');

  // API config
  const [apiUrl, setApiUrl] = useState('');
  const [apiMethod, setApiMethod] = useState<'GET' | 'POST'>('GET');

  // CSV config
  const [csvContent, setCsvContent] = useState<string | null>(null);
  const [csvFileName, setCsvFileName] = useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Hooks
  const { data: templatesData, isLoading: templatesLoading } = useTemplates();
  const generateReport = useGenerateReport();

  const templates = templatesData?.items || [];

  const handleClose = () => {
    onOpenChange(false);
    // Reset form after animation
    setTimeout(() => {
      setStep(1);
      setSelectedTemplate('');
      setDataSourceType(null);
      setConnectionString('');
      setSqlQuery('');
      setConnectionString('');
      setSqlQuery('');
      setApiUrl('');
      setApiMethod('GET');
      setCsvContent(null);
      setCsvFileName(null);
    }, 200);
  };

  const buildDataSource = (): DataSource => {
    if (dataSourceType === 'sql') {
      return {
        type: 'sql',
        config: {
          connection_string: connectionString,
          query: sqlQuery,
        },
      };
    }
    if (dataSourceType === 'api') {
      return {
        type: 'api',
        config: {
          url: apiUrl,
          method: apiMethod,
        },
      };
    }
    return {
      type: 'csv',
      config: {
        content: csvContent || undefined,
        file_name: csvFileName || undefined,
      },
    };
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      toast.error('Please select a valid CSV file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setCsvContent(content);
      setCsvFileName(file.name);
      toast.success(`Loaded ${file.name}`);
    };
    reader.onerror = () => {
      toast.error('Failed to read file');
    };
    reader.readAsText(file);
  };

  const handleSubmit = async () => {
    try {
      const dataSource = buildDataSource();

      // Create report in Supabase
      const result = await generateReport.mutateAsync({
        template_id: selectedTemplate,
        data_source: dataSource,
        params: {},
      });

      // Try to trigger FastAPI backend for PDF generation (if configured)
      if (isBackendConfigured()) {
        try {
          await fastapiService.triggerGeneration(result.report_id, {
            template_id: selectedTemplate,
            data_source: dataSource,
            params: {},
          });
          toast.success('Report generation started!');
        } catch (backendError) {
          console.warn('FastAPI backend not reachable, report created in database only:', backendError);
          toast.success('Report created! (Backend processing pending)');
        }
      } else {
        toast.success('Report created! Configure VITE_API_URL to enable PDF generation.');
      }

      handleClose();
    } catch (error) {
      console.error('Failed to generate report:', error);
      toast.error('Failed to generate report');
    }
  };

  const canProceed = () => {
    if (step === 1) return !!selectedTemplate;
    if (step === 2) return !!dataSourceType;
    if (step === 3) {
      if (dataSourceType === 'sql') return connectionString && sqlQuery;
      if (dataSourceType === 'api') return apiUrl;
      if (dataSourceType === 'api') return apiUrl;
      if (dataSourceType === 'csv') return !!csvContent;
    }
    return false;
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg bg-card">
        <DialogHeader>
          <DialogTitle>Generate New Report</DialogTitle>
          <DialogDescription>
            {step === 1 && 'Select a template for your report'}
            {step === 2 && 'Choose how to connect your data'}
            {step === 3 && 'Configure your data source'}
          </DialogDescription>
        </DialogHeader>

        {/* Step Indicator */}
        <div className="flex items-center gap-2 px-1">
          {[1, 2, 3].map((s) => (
            <React.Fragment key={s}>
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-colors',
                  step >= s
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                )}
              >
                {s}
              </div>
              {s < 3 && (
                <div
                  className={cn(
                    'h-0.5 flex-1 transition-colors',
                    step > s ? 'bg-primary' : 'bg-muted'
                  )}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Step 1: Template Selection */}
        {step === 1 && (
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {templatesLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : templates.length === 0 ? (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  No templates available. Add templates to your database first.
                </AlertDescription>
              </Alert>
            ) : (
              templates.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  onClick={() => setSelectedTemplate(template.id)}
                  className={cn(
                    'w-full rounded-lg border p-4 text-left transition-all hover:border-primary/50',
                    selectedTemplate === template.id
                      ? 'border-primary bg-accent'
                      : 'border-border bg-card'
                  )}
                >
                  <p className="font-medium text-foreground">{template.name}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{template.description}</p>
                  <span className="mt-2 inline-block rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
                    {template.category}
                  </span>
                </button>
              ))
            )}
          </div>
        )}

        {/* Step 2: Data Source Type */}
        {step === 2 && (
          <div className="grid gap-3">
            {dataSourceOptions.map(({ type, label, icon: Icon, description }) => (
              <button
                key={type}
                type="button"
                onClick={() => setDataSourceType(type)}
                className={cn(
                  'flex items-center gap-4 rounded-lg border p-4 text-left transition-all hover:border-primary/50',
                  dataSourceType === type
                    ? 'border-primary bg-accent'
                    : 'border-border bg-card'
                )}
              >
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-secondary">
                  <Icon className="h-5 w-5 text-secondary-foreground" />
                </div>
                <div>
                  <p className="font-medium text-foreground">{label}</p>
                  <p className="text-sm text-muted-foreground">{description}</p>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Step 3: Data Source Configuration */}
        {step === 3 && (
          <div className="space-y-4">
            {dataSourceType === 'sql' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="connection">Connection String</Label>
                  <Input
                    id="connection"
                    placeholder="postgresql://user:password@host:5432/db"
                    value={connectionString}
                    onChange={(e) => setConnectionString(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="query">SQL Query</Label>
                  <Textarea
                    id="query"
                    placeholder="SELECT * FROM sales WHERE date >= '2025-01-01'"
                    value={sqlQuery}
                    onChange={(e) => setSqlQuery(e.target.value)}
                    rows={4}
                  />
                </div>
              </>
            )}

            {dataSourceType === 'api' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="url">API URL</Label>
                  <Input
                    id="url"
                    placeholder="https://api.example.com/data"
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="method">HTTP Method</Label>
                  <Select value={apiMethod} onValueChange={(v) => setApiMethod(v as 'GET' | 'POST')}>
                    <SelectTrigger id="method">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-popover">
                      <SelectItem value="GET">GET</SelectItem>
                      <SelectItem value="POST">POST</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}

            {dataSourceType === 'csv' && (
              <div className="rounded-lg border-2 border-dashed p-8 text-center">
                <FileSpreadsheet className="mx-auto h-10 w-10 text-muted-foreground" />
                <p className="mt-2 text-sm font-medium text-foreground">
                  {csvFileName ? `Selected: ${csvFileName}` : 'Drag and drop your CSV file'}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {csvFileName ? 'Click to change file' : 'Or click to browse'}
                </p>
                <input
                  type="file"
                  accept=".csv"
                  className="hidden"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                />
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-4"
                  onClick={() => fileInputRef.current?.click()}
                >
                  {csvFileName ? 'Change File' : 'Browse Files'}
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-between pt-2">
          <Button
            variant="ghost"
            onClick={step === 1 ? handleClose : () => setStep((s) => s - 1)}
          >
            {step === 1 ? 'Cancel' : 'Back'}
          </Button>
          <Button
            onClick={step === 3 ? handleSubmit : () => setStep((s) => s + 1)}
            disabled={!canProceed() || generateReport.isPending}
          >
            {generateReport.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : step === 3 ? (
              'Generate Report'
            ) : (
              'Continue'
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
