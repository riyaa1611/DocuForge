// Seed script to add basic templates to Supabase
// Run with: npx tsx scripts/seed-templates.ts

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = "https://taxcrahpdoapuvfmvhcr.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRheGNyYWhwZG9hcHV2Zm12aGNyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NTU1NzEsImV4cCI6MjA4NTUzMTU3MX0.kbfVuOmtOlV3yb6IbR0OMw6sN6_kZw2-Lp9GsQfkiJ4";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const templates = [
    {
        name: 'Monthly Sales Report',
        description: 'A comprehensive monthly sales report with charts, tables, and key performance indicators.',
        category: 'Sales',
        html_path: 'templates/monthly-sales.html',
        schema: {
            parameters: [
                { name: 'month', type: 'select', label: 'Month', required: true, options: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] },
                { name: 'year', type: 'number', label: 'Year', required: true, default_value: new Date().getFullYear() },
                { name: 'include_charts', type: 'boolean', label: 'Include Charts', required: false, default_value: true },
            ]
        }
    },
    {
        name: 'Invoice',
        description: 'Professional invoice template for billing clients with itemized services and payment details.',
        category: 'Finance',
        html_path: 'templates/invoice.html',
        schema: {
            parameters: [
                { name: 'client_name', type: 'string', label: 'Client Name', required: true },
                { name: 'invoice_number', type: 'string', label: 'Invoice Number', required: true },
                { name: 'due_date', type: 'date', label: 'Due Date', required: true },
                { name: 'currency', type: 'select', label: 'Currency', required: true, options: ['USD', 'EUR', 'GBP', 'INR'], default_value: 'USD' },
            ]
        }
    },
    {
        name: 'Employee Performance Report',
        description: 'Quarterly employee performance evaluation report with metrics and feedback sections.',
        category: 'HR',
        html_path: 'templates/employee-performance.html',
        schema: {
            parameters: [
                { name: 'employee_name', type: 'string', label: 'Employee Name', required: true },
                { name: 'department', type: 'string', label: 'Department', required: true },
                { name: 'quarter', type: 'select', label: 'Quarter', required: true, options: ['Q1', 'Q2', 'Q3', 'Q4'] },
                { name: 'year', type: 'number', label: 'Year', required: true, default_value: new Date().getFullYear() },
            ]
        }
    }
];

async function seedTemplates() {
    console.log('🚀 Seeding templates...\n');

    for (const template of templates) {
        const { data, error } = await supabase
            .from('templates')
            .insert(template)
            .select()
            .single();

        if (error) {
            console.error(`❌ Failed to insert "${template.name}":`, error.message);
        } else {
            console.log(`✅ Inserted: ${data.name} (ID: ${data.id})`);
        }
    }

    console.log('\n🎉 Seeding complete!');
}

seedTemplates();
