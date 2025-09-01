// Tests for Layout component

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Layout } from '../Layout';
import { useAppStore } from '../../stores/useAppStore';

// Mock the useAppStore hook
vi.mock('../../stores/useAppStore', () => ({
  useAppStore: vi.fn(() => ({
    theme: 'light',
    sidebarCollapsed: false,
    setSidebarCollapsed: vi.fn(),
    setTheme: vi.fn(),
    toggleTheme: vi.fn(),
    selectedLeagueKey: null,
    selectedTeamKey: null,
    setSelectedLeague: vi.fn(),
    setSelectedTeam: vi.fn(),
    tableDensity: 'normal',
    setTableDensity: vi.fn(),
    currentWeek: 1,
    setCurrentWeek: vi.fn(),
    isLoading: false,
    setLoading: vi.fn(),
    error: null,
    setError: vi.fn(),
    notifications: [],
    addNotification: vi.fn(),
    removeNotification: vi.fn(),
    clearNotifications: vi.fn(),
  })),
}));

describe('Layout', () => {
  it('renders the layout with sidebar and main content', () => {
    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );

    expect(screen.getByText('DraftIQ')).toBeInTheDocument();
    expect(screen.getByText('Fantasy Football Analytics')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Leagues')).toBeInTheDocument();
    expect(screen.getByText('Lineup')).toBeInTheDocument();
    expect(screen.getByText('Waivers')).toBeInTheDocument();
    expect(screen.getByText('Trades')).toBeInTheDocument();
  });

  it('renders children when provided', () => {
    const testContent = <div data-testid="test-content">Test Content</div>;
    
    render(
      <BrowserRouter>
        <Layout>{testContent}</Layout>
      </BrowserRouter>
    );

    expect(screen.getByTestId('test-content')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('applies dark theme class when theme is dark', () => {
    const mockUseAppStore = vi.mocked(useAppStore);
    mockUseAppStore.mockReturnValue({
      theme: 'dark',
      sidebarCollapsed: false,
      setSidebarCollapsed: vi.fn(),
      setTheme: vi.fn(),
      toggleTheme: vi.fn(),
      selectedLeagueKey: null,
      selectedTeamKey: null,
      setSelectedLeague: vi.fn(),
      setSelectedTeam: vi.fn(),
      tableDensity: 'normal',
      setTableDensity: vi.fn(),
      currentWeek: 1,
      setCurrentWeek: vi.fn(),
      isLoading: false,
      setLoading: vi.fn(),
      error: null,
      setError: vi.fn(),
      notifications: [],
      addNotification: vi.fn(),
      removeNotification: vi.fn(),
      clearNotifications: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );

    // Check that the root div has the dark class
    const rootElement = document.querySelector('.min-h-screen');
    expect(rootElement).toHaveClass('dark');
  });

  it('collapses sidebar when sidebarCollapsed is true', () => {
    const mockUseAppStore = vi.mocked(useAppStore);
    mockUseAppStore.mockReturnValue({
      theme: 'light',
      sidebarCollapsed: true,
      setSidebarCollapsed: vi.fn(),
      setTheme: vi.fn(),
      toggleTheme: vi.fn(),
      selectedLeagueKey: null,
      selectedTeamKey: null,
      setSelectedLeague: vi.fn(),
      setSelectedTeam: vi.fn(),
      tableDensity: 'normal',
      setTableDensity: vi.fn(),
      currentWeek: 1,
      setCurrentWeek: vi.fn(),
      isLoading: false,
      setLoading: vi.fn(),
      error: null,
      setError: vi.fn(),
      notifications: [],
      addNotification: vi.fn(),
      removeNotification: vi.fn(),
      clearNotifications: vi.fn(),
    });

    render(
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    );

    // When collapsed, the sidebar should have w-16 class instead of w-64
    const sidebar = document.querySelector('.w-16');
    expect(sidebar).toBeInTheDocument();
    expect(sidebar).toHaveClass('w-16');
  });
});
