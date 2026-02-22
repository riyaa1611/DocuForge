import React from 'react';
import { FileStack, Download, Trash2, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ReportStatusBadge } from './ReportStatusBadge';
import { formatDateTime, formatFileSize } from '@/utils/formatters';
import { DATA_SOURCE_LABELS } from '@/utils/constants';
import type { Report } from '@/types';

interface ReportCardProps {
  report: Report;
  onDownload: (report: Report) => void;
  onDelete: (report: Report) => void;
}

export const ReportCard: React.FC<ReportCardProps> = ({
  report,
  onDownload,
  onDelete,
}) => {
  const navigate = useNavigate();

  return (
    <Card className="flex flex-col gap-4 p-4 transition-shadow hover:shadow-md sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent">
          <FileStack className="h-5 w-5 text-accent-foreground" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <h3 className="truncate text-sm font-medium text-foreground">
              {report.template_name || `Report ${report.id.slice(0, 8)}`}
            </h3>
            <ReportStatusBadge status={report.status} />
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
            <span>{formatDateTime(report.created_at)}</span>
            <span>{DATA_SOURCE_LABELS[report.data_source.type]}</span>
            {report.file_size && <span>{formatFileSize(report.file_size)}</span>}
          </div>
          {report.error_message && (
            <p className="mt-2 text-xs text-destructive">{report.error_message}</p>
          )}
        </div>
      </div>

      <div className="flex shrink-0 gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/reports/${report.id}`)}
        >
          <Eye className="mr-1.5 h-4 w-4" />
          View
        </Button>
        {report.status === 'completed' && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDownload(report)}
          >
            <Download className="mr-1.5 h-4 w-4" />
            Download
          </Button>
        )}
        <Button
          variant="ghost"
          size="sm"
          className="text-destructive hover:text-destructive"
          onClick={() => onDelete(report)}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </Card>
  );
};
