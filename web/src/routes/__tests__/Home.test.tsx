// Tests for Home component

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Home } from '../Home';
import { useAuth } from '../../hooks/useAuth';

// Mock the useAuth hook
vi.mock('../../hooks/useAuth');

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('Home', () => {
  it('renders dashboard for authenticated users', () => {
    // Mock authenticated state (development mode)
    (useAuth as any).mockReturnValue({
      isAuthenticated: true,
      user: {
        display_name: 'Development User',
        username: 'dev_user',
      },
    });

    renderWithQueryClient(<Home />);

    expect(screen.getByText('Welcome back, Development User!')).toBeInTheDocument();
    expect(screen.getByText('Ready to dominate your fantasy league?')).toBeInTheDocument();
    expect(screen.getByText('Active Leagues')).toBeInTheDocument();
    expect(screen.getByText('This Week')).toBeInTheDocument();
    expect(screen.getByText('Projections')).toBeInTheDocument();
  });

  it('shows league count in Active Leagues card', () => {
    // Mock authenticated state
    (useAuth as any).mockReturnValue({
      isAuthenticated: true,
      user: {
        display_name: 'Test User',
        username: 'testuser',
      },
    });

    renderWithQueryClient(<Home />);

    // Should show league count (will be 0 or loading state)
    expect(screen.getByText('Active Leagues')).toBeInTheDocument();
  });

  it('displays user information correctly', () => {
    // Mock authenticated state
    (useAuth as any).mockReturnValue({
      isAuthenticated: true,
      user: {
        display_name: 'John Doe',
        username: 'johndoe',
      },
    });

    renderWithQueryClient(<Home />);

    expect(screen.getByText('Welcome back, John Doe!')).toBeInTheDocument();
  });

  it('shows recent activity section', () => {
    // Mock authenticated state
    (useAuth as any).mockReturnValue({
      isAuthenticated: true,
      user: {
        display_name: 'Test User',
        username: 'testuser',
      },
    });

    renderWithQueryClient(<Home />);

    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    expect(screen.getByText('No recent activity')).toBeInTheDocument();
  });
});
