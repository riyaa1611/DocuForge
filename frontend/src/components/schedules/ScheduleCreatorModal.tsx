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
import type { DataSourceType, DataSource, Schedule } from '@/types';

interface ScheduleCreatorModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onScheduleCreated: (schedule: Schedule) => void;
}

const dataSourceOptions: { type: DataSourceType; label: string; icon: React.ElementType; description: string }[] = [
    { type: 'sql', label: 'SQL Database', icon: Database, description: 'Connect to a database' },
    { type: 'api', label: 'REST API', icon: Globe, description: 'Fetch from an API endpoint' },
    { type: 'csv', label: 'CSV File', icon: FileSpreadsheet, description: 'Upload a CSV file' },
];

const cronPresets = [
    { label: 'Every hour', value: '0 * * * *' },
    { label: 'Daily at 9 AM', value: '0 9 * * *' },
    { label: 'Every Monday at 8 AM', value: '0 8 * * 1' },
    { label: 'First of each month', value: '0 9 1 * *' },
    { label: 'Custom', value: 'custom' },
];

export const ScheduleCreatorModal: React.FC<ScheduleCreatorModalProps> = ({
    open,
    onOpenChange,
    onScheduleCreated,
}) => {
    const [step, setStep] = useState(1);
    const [scheduleName, setScheduleName] = useState('');
    const [selectedTemplate, setSelectedTemplate] = useState<string>('');
    const [cronPreset, setCronPreset] = useState<string>('');
    const [customCron, setCustomCron] = useState('');
    const [dataSourceType, setDataSourceType] = useState<DataSourceType | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Hooks
    const { data: templatesData, isLoading: templatesLoading } = useTemplates();

    // Fallback templates when Supabase has no data
    const mockTemplates = [
        { id: 'template-1', name: 'Monthly Sales Report', description: 'Comprehensive monthly sales analysis with charts', category: 'Sales' },
        { id: 'template-2', name: 'Weekly Analytics Dashboard', description: 'Weekly KPI dashboard with performance metrics', category: 'Analytics' },
        { id: 'template-3', name: 'Financial Statement', description: 'Balance sheet and income statement report', category: 'Finance' },
        { id: 'template-4', name: 'Inventory Report', description: 'Stock levels and inventory movement analysis', category: 'Operations' },
    ];

    const templates = (templatesData?.items && templatesData.items.length > 0)
        ? templatesData.items
        : mockTemplates;

    const handleClose = () => {
        onOpenChange(false);
        setTimeout(() => {
            setStep(1);
            setScheduleName('');
            setSelectedTemplate('');
            setCronPreset('');
            setCustomCron('');
            setDataSourceType(null);
        }, 200);
    };

    const getCronExpression = () => {
        return cronPreset === 'custom' ? customCron : cronPreset;
    };

    const handleSubmit = async () => {
        setIsSubmitting(true);
        try {
            // Create a new schedule (mock for now - will integrate with backend)
            const selectedTemplateName = templates.find(t => t.id === selectedTemplate)?.name || 'Untitled';

            const newSchedule: Schedule = {
                id: `schedule-${Date.now()}`,
                user_id: '1',
                template_id: selectedTemplate,
                name: scheduleName || `${selectedTemplateName} Schedule`,
                template_name: selectedTemplateName,
                cron_expression: getCronExpression(),
                params: {},
                data_source: {
                    type: dataSourceType || 'sql',
                    config: {},
                },
                is_active: true,
                next_run: new Date(Date.now() + 86400000).toISOString(),
                last_run: null,
                created_at: new Date().toISOString(),
            };

            onScheduleCreated(newSchedule);
            toast.success('Schedule created successfully!');
            handleClose();
        } catch (error) {
            console.error('Failed to create schedule:', error);
            toast.error('Failed to create schedule');
        } finally {
            setIsSubmitting(false);
        }
    };

    const canProceed = () => {
        if (step === 1) return !!selectedTemplate;
        if (step === 2) return cronPreset && (cronPreset !== 'custom' || customCron);
        if (step === 3) return !!dataSourceType;
        return false;
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="max-w-lg bg-card">
                <DialogHeader>
                    <DialogTitle>Create New Schedule</DialogTitle>
                    <DialogDescription>
                        {step === 1 && 'Select a template for your scheduled report'}
                        {step === 2 && 'Set up the schedule frequency'}
                        {step === 3 && 'Choose how to connect your data'}
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
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="schedule-name">Schedule Name (optional)</Label>
                            <Input
                                id="schedule-name"
                                placeholder="e.g., Weekly Sales Report"
                                value={scheduleName}
                                onChange={(e) => setScheduleName(e.target.value)}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label>Template</Label>
                            <div className="space-y-2 max-h-48 overflow-y-auto">
                                {templatesLoading ? (
                                    <div className="flex items-center justify-center py-8">
                                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                                    </div>
                                ) : templates.length === 0 ? (
                                    <Alert>
                                        <AlertCircle className="h-4 w-4" />
                                        <AlertDescription>
                                            No templates available. Add templates first.
                                        </AlertDescription>
                                    </Alert>
                                ) : (
                                    templates.map((template) => (
                                        <button
                                            key={template.id}
                                            type="button"
                                            onClick={() => setSelectedTemplate(template.id)}
                                            className={cn(
                                                'w-full rounded-lg border p-3 text-left transition-all hover:border-primary/50',
                                                selectedTemplate === template.id
                                                    ? 'border-primary bg-accent'
                                                    : 'border-border bg-card'
                                            )}
                                        >
                                            <p className="font-medium text-foreground">{template.name}</p>
                                            <p className="mt-0.5 text-sm text-muted-foreground line-clamp-1">{template.description}</p>
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Step 2: Schedule Frequency */}
                {step === 2 && (
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label>Frequency</Label>
                            <Select value={cronPreset} onValueChange={setCronPreset}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select frequency" />
                                </SelectTrigger>
                                <SelectContent className="bg-popover">
                                    {cronPresets.map((preset) => (
                                        <SelectItem key={preset.value} value={preset.value}>
                                            {preset.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {cronPreset === 'custom' && (
                            <div className="space-y-2">
                                <Label htmlFor="custom-cron">Cron Expression</Label>
                                <Input
                                    id="custom-cron"
                                    placeholder="0 9 * * 1"
                                    value={customCron}
                                    onChange={(e) => setCustomCron(e.target.value)}
                                />
                                <p className="text-xs text-muted-foreground">
                                    Format: minute hour day month weekday
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* Step 3: Data Source Type */}
                {step === 3 && (
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
                        disabled={!canProceed() || isSubmitting}
                    >
                        {isSubmitting ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Creating...
                            </>
                        ) : step === 3 ? (
                            'Create Schedule'
                        ) : (
                            'Continue'
                        )}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
};
