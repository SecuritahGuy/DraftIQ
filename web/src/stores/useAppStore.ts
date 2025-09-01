// Zustand store for app state management

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  // Theme
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
  
  // Selected league/team
  selectedLeagueKey: string | null;
  selectedTeamKey: string | null;
  setSelectedLeague: (leagueKey: string | null) => void;
  setSelectedTeam: (teamKey: string | null) => void;
  
  // UI preferences
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Table preferences
  tableDensity: 'compact' | 'normal' | 'comfortable';
  setTableDensity: (density: 'compact' | 'normal' | 'comfortable') => void;
  
  // Current week
  currentWeek: number;
  setCurrentWeek: (week: number) => void;
  
  // Loading states
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
  
  // Error state
  error: string | null;
  setError: (error: string | null) => void;
  
  // Notifications
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: number;
  }>;
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Theme
      theme: 'light',
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
      
      // Selected league/team
      selectedLeagueKey: null,
      selectedTeamKey: null,
      setSelectedLeague: (leagueKey) => set({ selectedLeagueKey: leagueKey }),
      setSelectedTeam: (teamKey) => set({ selectedTeamKey: teamKey }),
      
      // UI preferences
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      
      // Table preferences
      tableDensity: 'normal',
      setTableDensity: (density) => set({ tableDensity: density }),
      
      // Current week
      currentWeek: 1,
      setCurrentWeek: (week) => set({ currentWeek: week }),
      
      // Loading states
      isLoading: false,
      setLoading: (loading) => set({ isLoading: loading }),
      
      // Error state
      error: null,
      setError: (error) => set({ error }),
      
      // Notifications
      notifications: [],
      addNotification: (notification) => set((state) => ({
        notifications: [
          ...state.notifications,
          {
            ...notification,
            id: Math.random().toString(36).substr(2, 9),
            timestamp: Date.now(),
          },
        ],
      })),
      removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter(n => n.id !== id),
      })),
      clearNotifications: () => set({ notifications: [] }),
    }),
    {
      name: 'draftiq-app-store',
      partialize: (state) => ({
        theme: state.theme,
        selectedLeagueKey: state.selectedLeagueKey,
        selectedTeamKey: state.selectedTeamKey,
        sidebarCollapsed: state.sidebarCollapsed,
        tableDensity: state.tableDensity,
        currentWeek: state.currentWeek,
      }),
    }
  )
);
