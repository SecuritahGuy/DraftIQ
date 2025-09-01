// Tests for Leagues component

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { Leagues } from '../Leagues';
import { useLeagues } from '../../hooks/useLeagues';

// Mock the useLeagues hook
vi.mock('../../hooks/useLeagues');

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('Leagues', () => {
  it('renders loading state', () => {
    (useLeagues as any).mockReturnValue({
      leagues: [],
      isLoading: true,
      error: null,
      syncLeagueData: vi.fn(),
      isSyncing: false,
    });

    renderWithQueryClient(<Leagues />);

    expect(screen.getByText('Loading leagues...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    const mockError = new Error('Failed to load leagues');
    (useLeagues as any).mockReturnValue({
      leagues: [],
      isLoading: false,
      error: mockError,
      syncLeagueData: vi.fn(),
      isSyncing: false,
    });

    renderWithQueryClient(<Leagues />);

    expect(screen.getByText('Error Loading Leagues')).toBeInTheDocument();
    expect(screen.getByText('Failed to load leagues')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  it('renders empty state when no leagues', () => {
    (useLeagues as any).mockReturnValue({
      leagues: [],
      isLoading: false,
      error: null,
      syncLeagueData: vi.fn(),
      isSyncing: false,
    });

    renderWithQueryClient(<Leagues />);

    expect(screen.getByText('No Leagues Found')).toBeInTheDocument();
    expect(screen.getByText('Connect your Yahoo Fantasy Football account to see your leagues')).toBeInTheDocument();
    expect(screen.getByText('Go to Home')).toBeInTheDocument();
  });

  it('renders leagues list when leagues are available', () => {
    const mockLeagues = [
      {
        league_key: '414.l.123456',
        name: 'Test League 1',
        season: 2024,
        league_type: 'Standard',
        num_teams: 12,
        is_finished: false,
      },
      {
        league_key: '414.l.789012',
        name: 'Test League 2',
        season: 2024,
        league_type: 'PPR',
        num_teams: 10,
        is_finished: true,
      },
    ];

    (useLeagues as any).mockReturnValue({
      leagues: mockLeagues,
      isLoading: false,
      error: null,
      syncLeagueData: vi.fn(),
      isSyncing: false,
    });

    renderWithQueryClient(<Leagues />);

    expect(screen.getByText('Your Leagues')).toBeInTheDocument();
    expect(screen.getByText('Test League 1')).toBeInTheDocument();
    expect(screen.getByText('Test League 2')).toBeInTheDocument();
    expect(screen.getAllByText('Season 2024')).toHaveLength(2);
    expect(screen.getByText('12 teams')).toBeInTheDocument();
    expect(screen.getByText('10 teams')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('Finished')).toBeInTheDocument();
  });

  it('calls syncLeagueData when sync button is clicked', async () => {
    const mockSyncLeagueData = vi.fn();
    const mockLeagues = [
      {
        league_key: '414.l.123456',
        name: 'Test League',
        season: 2024,
        league_type: 'Standard',
        num_teams: 12,
        is_finished: false,
      },
    ];

    (useLeagues as any).mockReturnValue({
      leagues: mockLeagues,
      isLoading: false,
      error: null,
      syncLeagueData: mockSyncLeagueData,
      isSyncing: false,
    });

    renderWithQueryClient(<Leagues />);

    const syncButton = screen.getByText('Sync Data');
    syncButton.click();

    await waitFor(() => {
      expect(mockSyncLeagueData).toHaveBeenCalledWith('414.l.123456');
    });
  });

  it('shows syncing state when isSyncing is true', () => {
    const mockLeagues = [
      {
        league_key: '414.l.123456',
        name: 'Test League',
        season: 2024,
        league_type: 'Standard',
        num_teams: 12,
        is_finished: false,
      },
    ];

    (useLeagues as any).mockReturnValue({
      leagues: mockLeagues,
      isLoading: false,
      error: null,
      syncLeagueData: vi.fn(),
      isSyncing: true,
    });

    renderWithQueryClient(<Leagues />);

    expect(screen.getByText('Syncing...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Syncing...' })).toBeDisabled();
  });
});
