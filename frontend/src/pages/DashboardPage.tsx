import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileStack, Calendar, CheckCircle, Clock, Plus, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { StatCard } from '@/components/dashboard/StatCard';
import { ReportStatusBadge } from '@/components/reports/ReportStatusBadge';
import { StatCardSkeleton } from '@/components/common/Skeletons';
import { EmptyState } from '@/components/common/EmptyState';
import { formatRelativeTime } from '@/utils/formatters';
import type { Report } from '@/types';

// Mock data for demo
const mockStats = {
  totalReports: 142,
  completedReports: 128,
  activeSchedules: 8,
  pendingReports: 3,
};

const mockRecentReports: Report[] = [
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
    template_name: 'Customer Analytics',
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
    template_name: 'Inventory Status',
    status: 'pending',
    file_path: null,
    file_size: null,
    params: {},
    data_source: { type: 'csv', config: {} },
    error_message: null,
    created_at: new Date(Date.now() - 900000).toISOString(),
    completed_at: null,
  },
];

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading] = React.useState(false);

  return (
    <div className="mx-auto max-w-7xl space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Overview of your report generation activity
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => navigate('/schedules')}>
            <Calendar className="mr-2 h-4 w-4" />
            New Schedule
          </Button>
          <Button onClick={() => navigate('/reports')}>
            <Plus className="mr-2 h-4 w-4" />
            Generate Report
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            <StatCard
              title="Total Reports"
              value={mockStats.totalReports}
              icon={FileStack}
              trend={{ value: 12, isPositive: true }}
            />
            <StatCard
              title="Completed"
              value={mockStats.completedReports}
              icon={CheckCircle}
            />
            <StatCard
              title="Active Schedules"
              value={mockStats.activeSchedules}
              icon={Calendar}
            />
            <StatCard
              title="Pending"
              value={mockStats.pendingReports}
              icon={Clock}
            />
          </>
        )}
      </div>

      {/* Recent Reports */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">Recent Reports</h2>
          <Button variant="ghost" size="sm" onClick={() => navigate('/reports')}>
            View all
            <ArrowRight className="ml-1.5 h-4 w-4" />
          </Button>
        </div>

        {mockRecentReports.length === 0 ? (
          <EmptyState
            icon={FileStack}
            title="No reports yet"
            description="Generate your first report to see it here"
            action={
              <Button onClick={() => navigate('/reports')}>
                <Plus className="mr-2 h-4 w-4" />
                Generate Report
              </Button>
            }
          />
        ) : (
          <Card className="divide-y">
            {mockRecentReports.map((report) => (
              <div
                key={report.id}
                className="flex items-center justify-between p-4 transition-colors hover:bg-muted/50"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent">
                    <FileStack className="h-5 w-5 text-accent-foreground" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">
                      {report.template_name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {formatRelativeTime(report.created_at)}
                    </p>
                  </div>
                </div>
                <ReportStatusBadge status={report.status} />
              </div>
            ))}
          </Card>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card
          className="cursor-pointer p-6 transition-shadow hover:shadow-md"
          onClick={() => navigate('/reports')}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <FileStack className="h-6 w-6 text-primary" />
          </div>
          <h3 className="mt-4 font-medium text-foreground">Generate Report</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Create a new PDF report from your data sources
          </p>
        </Card>

        <Card
          className="cursor-pointer p-6 transition-shadow hover:shadow-md"
          onClick={() => navigate('/schedules')}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Calendar className="h-6 w-6 text-primary" />
          </div>
          <h3 className="mt-4 font-medium text-foreground">Schedule Reports</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Set up automated recurring report generation
          </p>
        </Card>

        <Card
          className="cursor-pointer p-6 transition-shadow hover:shadow-md"
          onClick={() => navigate('/templates')}
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <CheckCircle className="h-6 w-6 text-primary" />
          </div>
          <h3 className="mt-4 font-medium text-foreground">Browse Templates</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Explore available report templates
          </p>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
