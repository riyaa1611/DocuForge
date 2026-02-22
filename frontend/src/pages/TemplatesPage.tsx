import React from 'react';
import { Search, Layers } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { TemplateCard } from '@/components/templates/TemplateCard';
import { TemplateCardSkeleton } from '@/components/common/Skeletons';
import { EmptyState } from '@/components/common/EmptyState';
import { useDebounce } from '@/hooks/useDebounce';
import type { Template } from '@/types';

// Mock templates for demo
const mockTemplates: Template[] = [
  {
    id: '1',
    name: 'Monthly Sales Report',
    description: 'Comprehensive monthly sales analysis with revenue charts, top products, and regional breakdown. Includes year-over-year comparisons.',
    thumbnail_url: null,
    category: 'Financial',
    schema: [
      { name: 'start_date', type: 'date', label: 'Start Date', required: true },
      { name: 'end_date', type: 'date', label: 'End Date', required: true },
      { name: 'region', type: 'select', label: 'Region', required: false, options: ['North', 'South', 'East', 'West'] },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'Customer Analytics Dashboard',
    description: 'Detailed customer behavior analysis including engagement metrics, retention rates, and customer lifetime value calculations.',
    thumbnail_url: null,
    category: 'Analytics',
    schema: [
      { name: 'date_range', type: 'string', label: 'Date Range', required: true },
      { name: 'segment', type: 'select', label: 'Customer Segment', required: false, options: ['All', 'Premium', 'Standard', 'New'] },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: '3',
    name: 'Inventory Status Report',
    description: 'Current inventory levels, stock alerts, and reorder recommendations. Includes warehouse-level breakdown and turnover analysis.',
    thumbnail_url: null,
    category: 'Data',
    schema: [
      { name: 'warehouse', type: 'select', label: 'Warehouse', required: false, options: ['All', 'Main', 'Secondary'] },
      { name: 'include_zero', type: 'boolean', label: 'Include Zero Stock', required: false },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: '4',
    name: 'Financial Statement',
    description: 'Balance sheet, income statement, and cash flow analysis. Suitable for quarterly and annual reporting requirements.',
    thumbnail_url: null,
    category: 'Financial',
    schema: [
      { name: 'period', type: 'select', label: 'Period', required: true, options: ['Q1', 'Q2', 'Q3', 'Q4', 'Annual'] },
      { name: 'year', type: 'number', label: 'Year', required: true },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: '5',
    name: 'Employee Performance',
    description: 'Team and individual performance metrics including KPIs, goals achievement, and productivity trends.',
    thumbnail_url: null,
    category: 'Analytics',
    schema: [
      { name: 'department', type: 'select', label: 'Department', required: false, options: ['All', 'Sales', 'Engineering', 'Marketing'] },
      { name: 'period', type: 'date', label: 'Review Period', required: true },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: '6',
    name: 'Marketing Campaign Report',
    description: 'Campaign performance analysis with ROI calculations, conversion funnels, and channel attribution data.',
    thumbnail_url: null,
    category: 'Analytics',
    schema: [
      { name: 'campaign_id', type: 'string', label: 'Campaign ID', required: true },
      { name: 'include_ab', type: 'boolean', label: 'Include A/B Test Results', required: false },
    ],
    created_at: new Date().toISOString(),
  },
];

const TemplatesPage: React.FC = () => {
  const [isLoading] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all');

  const debouncedSearch = useDebounce(searchQuery, 300);

  const categories = React.useMemo(() => {
    const cats = new Set(mockTemplates.map((t) => t.category));
    return ['all', ...Array.from(cats)];
  }, []);

  const filteredTemplates = React.useMemo(() => {
    return mockTemplates.filter((template) => {
      const matchesSearch =
        !debouncedSearch ||
        template.name.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        template.description.toLowerCase().includes(debouncedSearch.toLowerCase());

      const matchesCategory =
        selectedCategory === 'all' || template.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [debouncedSearch, selectedCategory]);

  return (
    <div className="mx-auto max-w-5xl space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Templates</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Browse and select from available report templates
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`shrink-0 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                selectedCategory === cat
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
            >
              {cat === 'all' ? 'All' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Templates Grid */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <TemplateCardSkeleton />
          <TemplateCardSkeleton />
          <TemplateCardSkeleton />
          <TemplateCardSkeleton />
        </div>
      ) : filteredTemplates.length === 0 ? (
        <EmptyState
          icon={Layers}
          title="No templates found"
          description="Try adjusting your search or filters"
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {filteredTemplates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onClick={() => {
                // Could open a detail modal or navigate
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TemplatesPage;
