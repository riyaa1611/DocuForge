import React from 'react';
import { cn } from '@/lib/utils';
import type { ReportStatus } from '@/types';

interface ReportStatusBadgeProps {
  status: ReportStatus;
  className?: string;
}

const statusConfig: Record<ReportStatus, { label: string; className: string }> = {
  pending: {
    label: 'Pending',
    className: 'status-pending',
  },
  processing: {
    label: 'Processing',
    className: 'status-processing animate-status-pulse',
  },
  completed: {
    label: 'Completed',
    className: 'status-completed',
  },
  failed: {
    label: 'Failed',
    className: 'status-failed',
  },
};

export const ReportStatusBadge: React.FC<ReportStatusBadgeProps> = ({
  status,
  className,
}) => {
  const config = statusConfig[status];

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  );
};
