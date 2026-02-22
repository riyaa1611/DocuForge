import { create } from 'zustand';
import { supabase } from '@/integrations/supabase/client';
import type { User as SupabaseUser } from '@supabase/supabase-js';

interface Profile {
  id: string;
  user_id: string;
  display_name: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

interface AuthUser {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthStore extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: AuthUser | null) => void;
  initialize: () => Promise<void>;
}

const mapSupabaseUser = async (supabaseUser: SupabaseUser | null): Promise<AuthUser | null> => {
  if (!supabaseUser) return null;

  // Try to get profile for display name
  const { data: profile } = await supabase
    .from('profiles')
    .select('display_name')
    .eq('user_id', supabaseUser.id)
    .single();

  return {
    id: supabaseUser.id,
    email: supabaseUser.email || '',
    name: profile?.display_name || supabaseUser.email || 'User',
  };
};

export const useAuthStore = create<AuthStore>()((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  initialize: async () => {
    try {
      // Set up auth state listener FIRST
      supabase.auth.onAuthStateChange(async (event, session) => {
        if (session?.user) {
          const user = await mapSupabaseUser(session.user);
          set({ user, isAuthenticated: true, isLoading: false });
        } else {
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      });

      // Then check for existing session
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        const user = await mapSupabaseUser(session.user);
        set({ user, isAuthenticated: true, isLoading: false });
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    console.log('Login attempt started for:', email);

    // Add timeout to detect hanging requests
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Login timeout - check your network connection')), 15000);
    });

    const loginPromise = supabase.auth.signInWithPassword({
      email,
      password,
    });

    const { data, error } = await Promise.race([loginPromise, timeoutPromise]) as Awaited<typeof loginPromise>;

    if (error) {
      console.error('Login error:', error);
      throw error;
    }

    console.log('Login successful');
    const user = await mapSupabaseUser(data.user);
    set({ user, isAuthenticated: true, isLoading: false });
  },

  register: async (name: string, email: string, password: string) => {
    console.log('Register attempt started for:', email);

    // Add timeout to detect hanging requests
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Registration timeout - check your network connection')), 15000);
    });

    const registerPromise = supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          display_name: name,
        },
        emailRedirectTo: window.location.origin,
      },
    });

    const { data, error } = await Promise.race([registerPromise, timeoutPromise]) as Awaited<typeof registerPromise>;

    if (error) {
      console.error('Registration error:', error);
      throw error;
    }

    console.log('Registration successful');
    const user = await mapSupabaseUser(data.user);
    set({ user, isAuthenticated: true, isLoading: false });
  },

  logout: async () => {
    await supabase.auth.signOut();
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  setUser: (user: AuthUser | null) => {
    set({ user, isAuthenticated: !!user });
  },
}));

// Convenience hook
export const useAuth = () => {
  const store = useAuthStore();
  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    login: store.login,
    register: store.register,
    logout: store.logout,
    initialize: store.initialize,
  };
};
