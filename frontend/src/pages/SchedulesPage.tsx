import React, { useState } from 'react';
import { Plus, Calendar, Trash2, Pause, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { EmptyState } from '@/components/common/EmptyState';
import { ConfirmDialog } from '@/components/common/ConfirmDialog';
import { ScheduleCreatorModal } from '@/components/schedules/ScheduleCreatorModal';
import { formatDateTime, formatCronExpression } from '@/utils/formatters';
import { toast } from 'sonner';
import type { Schedule } from '@/types';

// Mock data for demo
const mockSchedules: Schedule[] = [
  {
    id: '1',
    user_id: '1',
    template_id: '1',
    name: 'Monthly Sales Report Schedule',
    template_name: 'Monthly Sales Report',
    cron_expression: '0 9 1 * *',
    params: { region: 'All' },
    data_source: { type: 'sql', config: {} },
    is_active: true,
    next_run: new Date(Date.now() + 86400000 * 5).toISOString(),
    last_run: new Date(Date.now() - 86400000 * 25).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 60).toISOString(),
  },
  {
    id: '2',
    user_id: '1',
    template_id: '2',
    name: 'Weekly Analytics Schedule',
    template_name: 'Weekly Analytics',
    cron_expression: '0 8 * * 1',
    params: {},
    data_source: { type: 'api', config: {} },
    is_active: true,
    next_run: new Date(Date.now() + 86400000 * 2).toISOString(),
    last_run: new Date(Date.now() - 86400000 * 5).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 30).toISOString(),
  },
  {
    id: '3',
    user_id: '1',
    template_id: '3',
    name: 'Daily Inventory Schedule',
    template_name: 'Daily Inventory Check',
    cron_expression: '0 6 * * *',
    params: {},
    data_source: { type: 'csv', config: {} },
    is_active: false,
    next_run: new Date(Date.now() + 86400000).toISOString(),
    last_run: new Date(Date.now() - 86400000 * 10).toISOString(),
    created_at: new Date(Date.now() - 86400000 * 45).toISOString(),
  },
];

const SchedulesPage: React.FC = () => {
  const [schedules, setSchedules] = useState(mockSchedules);
  const [scheduleToDelete, setScheduleToDelete] = useState<Schedule | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleToggleActive = (schedule: Schedule) => {
    setSchedules((prev) =>
      prev.map((s) =>
        s.id === schedule.id ? { ...s, is_active: !s.is_active } : s
      )
    );
    toast.success(
      schedule.is_active ? 'Schedule paused' : 'Schedule activated'
    );
  };

  const handleDelete = () => {
    if (scheduleToDelete) {
      setSchedules((prev) => prev.filter((s) => s.id !== scheduleToDelete.id));
      toast.success('Schedule deleted');
      setScheduleToDelete(null);
    }
  };

  const handleScheduleCreated = (newSchedule: Schedule) => {
    setSchedules((prev) => [newSchedule, ...prev]);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Schedules</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage your automated report generation schedules
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Schedule
        </Button>
      </div>

      {/* Schedules List */}
      {schedules.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="No schedules yet"
          description="Create your first schedule to automate report generation"
          action={
            <Button onClick={() => setIsCreateModalOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Schedule
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          {schedules.map((schedule) => (
            <Card key={schedule.id} className="p-4">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent">
                    <Calendar className="h-5 w-5 text-accent-foreground" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-foreground">
                        {schedule.template_name}
                      </h3>
                      {!schedule.is_active && (
                        <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                          Paused
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {formatCronExpression(schedule.cron_expression)}
                    </p>
                    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                      <span>
                        Next run: {formatDateTime(schedule.next_run)}
                      </span>
                      {schedule.last_run && (
                        <span>
                          Last run: {formatDateTime(schedule.last_run)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    {schedule.is_active ? (
                      <Pause className="h-4 w-4 text-muted-foreground" />
                    ) : (
                      <Play className="h-4 w-4 text-muted-foreground" />
                    )}
                    <Switch
                      checked={schedule.is_active}
                      onCheckedChange={() => handleToggleActive(schedule)}
                    />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive"
                    onClick={() => setScheduleToDelete(schedule)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={!!scheduleToDelete}
        onOpenChange={(open) => !open && setScheduleToDelete(null)}
        title="Delete Schedule"
        description={`Are you sure you want to delete the schedule for "${scheduleToDelete?.template_name}"? This action cannot be undone.`}
        confirmLabel="Delete"
        onConfirm={handleDelete}
        variant="destructive"
      />

      {/* Create Schedule Modal */}
      <ScheduleCreatorModal
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onScheduleCreated={handleScheduleCreated}
      />
    </div>
  );
};

export default SchedulesPage;
