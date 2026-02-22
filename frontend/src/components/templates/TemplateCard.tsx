import React from 'react';
import { Layers, FileText, BarChart3, PieChart, Table } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { Template } from '@/types';

interface TemplateCardProps {
  template: Template;
  isSelected?: boolean;
  onClick?: (template: Template) => void;
}

const categoryIcons: Record<string, React.ElementType> = {
  financial: BarChart3,
  analytics: PieChart,
  data: Table,
  document: FileText,
  default: Layers,
};

export const TemplateCard: React.FC<TemplateCardProps> = ({
  template,
  isSelected,
  onClick,
}) => {
  const Icon = categoryIcons[template.category.toLowerCase()] || categoryIcons.default;

  return (
    <Card
      className={cn(
        'cursor-pointer p-4 transition-all hover:shadow-md',
        isSelected && 'ring-2 ring-primary ring-offset-2'
      )}
      onClick={() => onClick?.(template)}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-accent">
          <Icon className="h-6 w-6 text-accent-foreground" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-medium text-foreground">{template.name}</h3>
          <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
            {template.description}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <span className="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
              {template.category}
            </span>
            <span className="text-xs text-muted-foreground">
              {template.schema.length} parameters
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};
