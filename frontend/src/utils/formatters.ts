import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';

export const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return '—';
  const date = parseISO(dateString);
  if (!isValid(date)) return '—';
  return format(date, 'MMM d, yyyy');
};

export const formatDateTime = (dateString: string | null | undefined): string => {
  if (!dateString) return '—';
  const date = parseISO(dateString);
  if (!isValid(date)) return '—';
  return format(date, 'MMM d, yyyy, h:mm a');
};

export const formatRelativeTime = (dateString: string | null | undefined): string => {
  if (!dateString) return '—';
  const date = parseISO(dateString);
  if (!isValid(date)) return '—';
  return formatDistanceToNow(date, { addSuffix: true });
};

export const formatFileSize = (bytes: number | null | undefined): string => {
  if (bytes === null || bytes === undefined) return '—';
  if (bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const size = bytes / Math.pow(k, i);
  
  return `${size.toFixed(i > 0 ? 1 : 0)} ${units[i]}`;
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};

export const formatCronExpression = (cron: string): string => {
  const parts = cron.split(' ');
  if (parts.length !== 5) return cron;
  
  const [minute, hour, dayOfMonth, month, dayOfWeek] = parts;
  
  // Simple human-readable conversion for common patterns
  if (minute === '0' && hour === '*' && dayOfMonth === '*' && month === '*' && dayOfWeek === '*') {
    return 'Every hour';
  }
  if (minute === '0' && hour === '0' && dayOfMonth === '*' && month === '*' && dayOfWeek === '*') {
    return 'Daily at midnight';
  }
  if (minute === '0' && dayOfMonth === '*' && month === '*' && dayOfWeek === '*') {
    return `Daily at ${hour}:00`;
  }
  if (minute === '0' && hour === '0' && dayOfMonth === '1' && month === '*' && dayOfWeek === '*') {
    return 'Monthly on the 1st';
  }
  
  return cron;
};
