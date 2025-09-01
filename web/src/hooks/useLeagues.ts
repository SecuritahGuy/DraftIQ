// League-related hooks

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/api';
import { queryKeys } from '../lib/queryClient';
import type { League, Team } from '../types/api';

export const useUserLeagues = () => {
  return useQuery({
    queryKey: queryKeys.yahoo.leagues,
    queryFn: () => apiClient.getUserLeagues(),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
};

export const useLeagueDetails = (leagueKey: string) => {
  return useQuery({
    queryKey: queryKeys.yahoo.league(leagueKey),
    queryFn: () => apiClient.getLeagueDetails(leagueKey),
    enabled: !!leagueKey,
    staleTime: 60 * 60 * 1000, // 1 hour
  });
};

export const useLeagueTeams = (leagueKey: string) => {
  return useQuery({
    queryKey: queryKeys.yahoo.leagueTeams(leagueKey),
    queryFn: () => apiClient.getLeagueTeams(leagueKey),
    enabled: !!leagueKey,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useTeamRoster = (teamKey: string, week?: number) => {
  return useQuery({
    queryKey: queryKeys.yahoo.teamRoster(teamKey, week),
    queryFn: () => apiClient.getTeamRoster(teamKey, week),
    enabled: !!teamKey,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useLeaguePlayers = (leagueKey: string) => {
  return useQuery({
    queryKey: queryKeys.yahoo.leaguePlayers(leagueKey),
    queryFn: () => apiClient.getLeaguePlayers(leagueKey),
    enabled: !!leagueKey,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

export const useDraftResults = (leagueKey: string) => {
  return useQuery({
    queryKey: queryKeys.yahoo.draftResults(leagueKey),
    queryFn: () => apiClient.getDraftResults(leagueKey),
    enabled: !!leagueKey,
    staleTime: 60 * 60 * 1000, // 1 hour (draft results don't change)
  });
};

export const usePlayerStats = (gsisId: string, season: number, week: number) => {
  return useQuery({
    queryKey: ['nfl', 'stats', gsisId, season, week],
    queryFn: () => apiClient.getWeeklyStats(gsisId, season, week),
    enabled: !!gsisId && !!season && !!week,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useSyncLeagueData = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (leagueKey: string) => apiClient.syncLeagueData(leagueKey),
    onSuccess: (data, leagueKey) => {
      if (data.success) {
        // Invalidate related queries
        queryClient.invalidateQueries({ queryKey: queryKeys.yahoo.league(leagueKey) });
        queryClient.invalidateQueries({ queryKey: queryKeys.yahoo.leagueTeams(leagueKey) });
        queryClient.invalidateQueries({ queryKey: queryKeys.yahoo.leaguePlayers(leagueKey) });
        queryClient.invalidateQueries({ queryKey: queryKeys.dataSync.league(leagueKey) });
      }
    },
    onError: (error) => {
      console.error('Failed to sync league data:', error);
    },
  });
};

export const useLeagues = () => {
  const { data: leaguesData, isLoading, error } = useUserLeagues();
  const syncLeagueData = useSyncLeagueData();
  
  // The API returns { leagues: [...], total_count: 1 } directly
  const leagues = leaguesData?.leagues || [];
  
  return {
    leagues,
    isLoading,
    error,
    syncLeagueData: syncLeagueData.mutate,
    isSyncing: syncLeagueData.isPending,
  };
};
