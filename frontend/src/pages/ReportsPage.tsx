import React, { useState, useMemo } from 'react';
import { Plus, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ReportCard } from '@/components/reports/ReportCard';
import { ReportCardSkeleton } from '@/components/common/Skeletons';
import { EmptyState } from '@/components/common/EmptyState';
import { ReportGeneratorModal } from '@/components/reports/ReportGeneratorModal';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { toast } from 'sonner';
import { useDebounce } from '@/hooks/useDebounce';
import type { Report, ReportStatus } from '@/types';
import { FileStack } from 'lucide-react';

// Mock data for demo
const mockReports: Report[] = [
  {
    id: '1',
    user_id: '1',
    template_id: '1',
    template_name: 'Monthly Sales Report',
    status: 'completed',
    file_path: '/reports/1.pdf',
    file_size: 2456789,
    params: {},
    data_source: { type: 'sql', config: {} },
    error_message: null,
    created_at: new Date(Date.now() - 3600000).toISOString(),
    completed_at: new Date().toISOString(),
  },
  {
    id: '2',
    user_id: '1',
    template_id: '2',
    template_name: 'Customer Analytics Dashboard',
    status: 'processing',
    file_path: null,
    file_size: null,
    params: {},
    data_source: { type: 'api', config: {} },
    error_message: null,
    created_at: new Date(Date.now() - 1800000).toISOString(),
    completed_at: null,
  },
  {
    id: '3',
    user_id: '1',
    template_id: '3',
    template_name: 'Inventory Status Report',
    status: 'pending',
    file_path: null,
    file_size: null,
    params: {},
    data_source: { type: 'csv', config: {} },
    error_message: null,
    created_at: new Date(Date.now() - 900000).toISOString(),
    completed_at: null,
  },
  {
    id: '4',
    user_id: '1',
    template_id: '1',
    template_name: 'Weekly Performance',
    status: 'failed',
    file_path: null,
    file_size: null,
    params: {},
    data_source: { type: 'sql', config: {} },
    error_message: 'Connection timeout: Could not reach database server',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    completed_at: null,
  },
  {
    id: '5',
    user_id: '1',
    template_id: '2',
    template_name: 'Q4 Financial Summary',
    status: 'completed',
    file_path: '/reports/5.pdf',
    file_size: 5678901,
    params: {},
    data_source: { type: 'api', config: {} },
    error_message: null,
    created_at: new Date(Date.now() - 172800000).toISOString(),
    completed_at: new Date(Date.now() - 172000000).toISOString(),
  },
];

const ReportsPage: React.FC = () => {
  const [isLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ReportStatus | 'all'>('all');
  const [isGeneratorOpen, setIsGeneratorOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<Report | null>(null);

  const debouncedSearch = useDebounce(searchQuery, 300);

  const filteredReports = useMemo(() => {
    return mockReports.filter((report) => {
      const matchesSearch = !debouncedSearch || 
        report.template_name?.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        report.id.includes(debouncedSearch);
      
      const matchesStatus = statusFilter === 'all' || report.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });
  }, [debouncedSearch, statusFilter]);

  const handleDownload = (report: Report) => {
    toast.success(`Downloading ${report.template_name}...`);
    // In real app: call reportsService.downloadReport
  };

  const handleDelete = (report: Report) => {
    setReportToDelete(report);
  };

  const confirmDelete = () => {
    if (reportToDelete) {
      toast.success(`Report deleted successfully`);
      setReportToDelete(null);
      // In real app: call deleteReport mutation
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Reports</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            View and manage your generated reports
          </p>
        </div>
        <Button onClick={() => setIsGeneratorOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Generate Report
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search reports..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select
          value={statusFilter}
          onValueChange={(value) => setStatusFilter(value as ReportStatus | 'all')}
        >
          <SelectTrigger className="w-full sm:w-40">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent className="bg-popover">
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Reports List */}
      <div className="space-y-3">
        {isLoading ? (
          <>
            <ReportCardSkeleton />
            <ReportCardSkeleton />
            <ReportCardSkeleton />
          </>
        ) : filteredReports.length === 0 ? (
          <EmptyState
            icon={FileStack}
            title="No reports found"
            description={
              searchQuery || statusFilter !== 'all'
                ? 'Try adjusting your filters'
                : 'Generate your first report to get started'
            }
            action={
              !searchQuery && statusFilter === 'all' && (
                <Button onClick={() => setIsGeneratorOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Generate Report
                </Button>
              )
            }
          />
        ) : (
          filteredReports.map((report) => (
            <ReportCard
              key={report.id}
              report={report}
              onDownload={handleDownload}
              onDelete={handleDelete}
            />
          ))
        )}
      </div>

      {/* Report Generator Modal */}
      <ReportGeneratorModal
        open={isGeneratorOpen}
        onOpenChange={setIsGeneratorOpen}
      />

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={!!reportToDelete}
        onOpenChange={(open) => !open && setReportToDelete(null)}
        title="Delete Report"
        description={`Are you sure you want to delete "${reportToDelete?.template_name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        onConfirm={confirmDelete}
        variant="destructive"
      />
    </div>
  );
};

export default ReportsPage;
