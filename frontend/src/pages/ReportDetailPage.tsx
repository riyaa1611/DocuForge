import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Trash2, RefreshCw, FileStack, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ReportStatusBadge } from '@/components/reports/ReportStatusBadge';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { formatDateTime, formatFileSize, formatRelativeTime } from '@/utils/formatters';
import { DATA_SOURCE_LABELS } from '@/utils/constants';
import { toast } from 'sonner';
import type { Report } from '@/types';

// Mock data for demo
const mockReport: Report = {
  id: '1',
  user_id: '1',
  template_id: '1',
  template_name: 'Monthly Sales Report',
  status: 'completed',
  file_path: '/reports/1.pdf',
  file_size: 2456789,
  params: {
    start_date: '2025-01-01',
    end_date: '2025-01-31',
    region: 'North',
  },
  data_source: {
    type: 'sql',
    config: {
      query: 'SELECT * FROM sales WHERE date >= \'2025-01-01\' AND date <= \'2025-01-31\'',
    },
  },
  error_message: null,
  created_at: new Date(Date.now() - 3600000).toISOString(),
  completed_at: new Date().toISOString(),
};

const ReportDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isDeleteOpen, setIsDeleteOpen] = React.useState(false);

  // In real app, use useReport(id) hook with polling
  const report = mockReport;
  const isPolling = report.status === 'pending' || report.status === 'processing';

  const handleDownload = () => {
    toast.success('Downloading report...');
  };

  const handleDelete = () => {
    toast.success('Report deleted');
    navigate('/reports');
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6 animate-fade-in">
      {/* Back Button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate('/reports')}
        className="-ml-2"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Reports
      </Button>

      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-accent">
            <FileStack className="h-7 w-7 text-accent-foreground" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-semibold text-foreground">
                {report.template_name}
              </h1>
              <ReportStatusBadge status={report.status} />
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Report ID: {id}
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          {report.status === 'completed' && (
            <Button onClick={handleDownload}>
              <Download className="mr-2 h-4 w-4" />
              Download PDF
            </Button>
          )}
          <Button
            variant="outline"
            className="text-destructive hover:text-destructive"
            onClick={() => setIsDeleteOpen(true)}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      {/* Status Card for Processing */}
      {isPolling && (
        <Card className="flex items-center gap-4 border-status-processing-bg bg-status-processing-bg/30 p-4">
          <RefreshCw className="h-5 w-5 animate-spin text-status-processing" />
          <div>
            <p className="font-medium text-foreground">
              {report.status === 'pending' ? 'Waiting in queue...' : 'Generating report...'}
            </p>
            <p className="text-sm text-muted-foreground">
              This page will update automatically when the report is ready
            </p>
          </div>
        </Card>
      )}

      {/* Error Card */}
      {report.status === 'failed' && report.error_message && (
        <Card className="flex items-start gap-4 border-destructive/30 bg-destructive/5 p-4">
          <AlertCircle className="h-5 w-5 shrink-0 text-destructive" />
          <div>
            <p className="font-medium text-destructive">Report generation failed</p>
            <p className="mt-1 text-sm text-muted-foreground">{report.error_message}</p>
          </div>
        </Card>
      )}

      {/* Details */}
      <Card className="divide-y">
        <div className="p-4">
          <h2 className="text-sm font-medium text-muted-foreground">Details</h2>
        </div>
        
        <div className="grid gap-4 p-4 sm:grid-cols-2">
          <div>
            <p className="text-sm text-muted-foreground">Created</p>
            <p className="mt-1 font-medium text-foreground">
              {formatDateTime(report.created_at)}
            </p>
            <p className="text-xs text-muted-foreground">
              {formatRelativeTime(report.created_at)}
            </p>
          </div>
          
          {report.completed_at && (
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="mt-1 font-medium text-foreground">
                {formatDateTime(report.completed_at)}
              </p>
            </div>
          )}

          <div>
            <p className="text-sm text-muted-foreground">Data Source</p>
            <p className="mt-1 font-medium text-foreground">
              {DATA_SOURCE_LABELS[report.data_source.type]}
            </p>
          </div>

          {report.file_size && (
            <div>
              <p className="text-sm text-muted-foreground">File Size</p>
              <p className="mt-1 font-medium text-foreground">
                {formatFileSize(report.file_size)}
              </p>
            </div>
          )}
        </div>

        {/* Parameters */}
        {Object.keys(report.params).length > 0 && (
          <>
            <div className="p-4">
              <h2 className="text-sm font-medium text-muted-foreground">Parameters</h2>
            </div>
            <div className="p-4">
              <div className="rounded-lg bg-muted p-4 font-mono text-sm">
                <pre className="overflow-x-auto">
                  {JSON.stringify(report.params, null, 2)}
                </pre>
              </div>
            </div>
          </>
        )}
      </Card>

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={isDeleteOpen}
        onOpenChange={setIsDeleteOpen}
        title="Delete Report"
        description="Are you sure you want to delete this report? This action cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        variant="destructive"
      />
    </div>
  );
};

export default ReportDetailPage;
