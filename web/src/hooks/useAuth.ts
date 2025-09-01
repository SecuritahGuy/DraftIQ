// Authentication hooks

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api';
import { queryKeys } from '../lib/queryClient';
import { useAppStore } from '../stores/useAppStore';
import type { AuthStatus, OAuthStartResponse, OAuthCallbackResponse } from '../types/api';

export const useAuthStatus = () => {
  return useQuery({
    queryKey: queryKeys.auth.status,
    queryFn: () => apiClient.getAuthStatus(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useStartYahooOAuth = () => {
  const queryClient = useQueryClient();
  const addNotification = useAppStore((state) => state.addNotification);
  
  return useMutation({
    mutationFn: () => apiClient.startYahooOAuth(),
    onSuccess: (data: OAuthStartResponse) => {
      console.log('OAuth response:', data);
      if (data.authorization_url) {
        console.log('Redirecting to Yahoo OAuth:', data.authorization_url);
        // Redirect directly to Yahoo OAuth in the same window
        window.location.href = data.authorization_url;
      } else {
        console.error('No authorization_url in response:', data);
      }
    },
    onError: (error) => {
      console.error('Failed to start Yahoo OAuth:', error);
    },
  });
};

export const useYahooOAuthCallback = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ code, state }: { code: string; state: string }) => 
      apiClient.yahooOAuthCallback(code, state),
    onSuccess: (data: OAuthCallbackResponse) => {
      if (data.success) {
        // Invalidate auth status to refetch
        queryClient.invalidateQueries({ queryKey: queryKeys.auth.status });
      }
    },
    onError: (error) => {
      console.error('OAuth callback failed:', error);
    },
  });
};

export const useAuth = () => {
  const { data: authStatus, isLoading, error } = useAuthStatus();
  const startOAuth = useStartYahooOAuth();
  const oauthCallback = useYahooOAuthCallback();
  
  const isAuthenticated = authStatus?.success && authStatus?.data?.authenticated;
  const user = authStatus?.data?.user;
  const yahooToken = authStatus?.data?.yahoo_token;
  
  return {
    isAuthenticated,
    user,
    yahooToken,
    isLoading,
    error,
    startOAuth: startOAuth.mutate,
    isStartingOAuth: startOAuth.isPending,
    oauthCallback: oauthCallback.mutate,
    isOAuthCallbackPending: oauthCallback.isPending,
  };
};
