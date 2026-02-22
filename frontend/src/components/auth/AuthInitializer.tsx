import { useEffect } from 'react';
import { useAuthStore } from '@/hooks/useAuth';

export const AuthInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return <>{children}</>;
};
