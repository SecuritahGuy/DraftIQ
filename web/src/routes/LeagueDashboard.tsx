// League Dashboard component

import React from 'react';
import { useParams } from 'react-router-dom';
import { useUserLeagues, useLeagueTeams, useLeaguePlayers, usePlayerStats } from '../hooks/useLeagues';

export const LeagueDashboard: React.FC = () => {
  const { leagueKey } = useParams<{ leagueKey: string }>();
  
  const { data: leaguesData, isLoading: leaguesLoading, error: leaguesError } = useUserLeagues();
  const { data: teamsData, isLoading: teamsLoading, error: teamsError } = useLeagueTeams(leagueKey!);
  const { data: playersData, isLoading: playersLoading, error: playersError } = useLeaguePlayers(leagueKey!);
  
  const isLoading = leaguesLoading || teamsLoading || playersLoading;
  const error = leaguesError || teamsError || playersError;
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading league details...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Error Loading League
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {error?.message || 'Failed to load league details'}
          </p>
          <button
            onClick={() => window.location.href = '/leagues'}
            className="btn-primary"
          >
            Back to Leagues
          </button>
        </div>
      </div>
    );
  }
  
  // Find the specific league from the leagues list
  const league = leaguesData?.leagues?.find((l: any) => l.league_key === leagueKey);
  const teams = teamsData?.teams || [];
  const players = playersData?.players || [];
  

  
  if (!league) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            League Not Found
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            The requested league could not be found.
          </p>
          <button
            onClick={() => window.location.href = '/leagues'}
            className="btn-primary"
          >
            Back to Leagues
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              {league.name}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Season {league.season} • {league.num_teams} teams
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => window.location.href = '/leagues'}
              className="btn-secondary"
            >
              Back to Leagues
            </button>
            <button
              onClick={() => window.location.href = `/lineup`}
              className="btn-primary"
            >
              Set Lineup
            </button>
          </div>
        </div>
      </div>
      
      {/* League Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Total Teams
          </h3>
          <p className="text-3xl font-bold text-primary-600">{league.num_teams}</p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            League Type
          </h3>
          <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
            {league.league_type}
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Status
          </h3>
          <p className={`text-lg font-semibold ${league.is_finished ? 'text-red-600' : 'text-green-600'}`}>
            {league.is_finished ? 'Finished' : 'Active'}
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Total Players
          </h3>
          <p className="text-3xl font-bold text-blue-600">{players.length}</p>
        </div>
      </div>
      
      {/* Standings Table */}
      <div className="card mb-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Standings
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Team
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Manager
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Record
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Win %
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              {teams.length > 0 ? teams.map((team: any, index: number) => {
                  const winPercentage = team.wins + team.losses + team.ties > 0 
                    ? ((team.wins + (team.ties * 0.5)) / (team.wins + team.losses + team.ties) * 100).toFixed(1)
                    : '0.0';
                  
                  return (
                    <tr key={team.team_key} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                        {team.rank || index + 1}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {team.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {team.manager || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {team.wins}-{team.losses}{team.ties > 0 ? `-${team.ties}` : ''}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {winPercentage}%
                      </td>
                    </tr>
                  );
                }) : (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                      No teams found
                    </td>
                                  </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Top Performers */}
      <div className="card mb-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Top Performers (Based on 2024 Stats)
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Using 2024 season data for 2025 league projections
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <TopPerformerCard 
            playerName="Patrick Mahomes" 
            position="QB" 
            team="KC" 
            gsisId="00-0033873" 
            season={2024} 
            week={1} 
          />
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <p>More players coming soon...</p>
              <p className="text-sm">Real NFL stats will be displayed here</p>
            </div>
          </div>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <p>More players coming soon...</p>
              <p className="text-sm">Real NFL stats will be displayed here</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Lineup Management
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Set your optimal lineup for the current week
          </p>
          <button
            onClick={() => window.location.href = '/lineup'}
            className="btn-primary w-full"
          >
            Set Lineup
          </button>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Waiver Wire
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Find the best available players to add
          </p>
          <button
            onClick={() => window.location.href = '/waivers'}
            className="btn-primary w-full"
          >
            Browse Waivers
          </button>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Trade Analyzer
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Analyze potential trades with other teams
          </p>
          <button
            onClick={() => window.location.href = '/trades'}
            className="btn-primary w-full"
          >
            Analyze Trades
          </button>
        </div>
      </div>
    </div>
  );
};

// Top Performer Card Component
interface TopPerformerCardProps {
  playerName: string;
  position: string;
  team: string;
  gsisId: string;
  season: number;
  week: number;
}

const TopPerformerCard: React.FC<TopPerformerCardProps> = ({ 
  playerName, 
  position, 
  team, 
  gsisId, 
  season, 
  week 
}) => {
  const { data: statsData, isLoading, error } = usePlayerStats(gsisId, season, week);
  
  if (isLoading) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-2/3"></div>
        </div>
      </div>
    );
  }
  
  if (error || !statsData?.stats) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <p>Stats unavailable</p>
          <p className="text-sm">{playerName}</p>
        </div>
      </div>
    );
  }
  
  const stats = statsData.stats;
  const fantasyPoints = stats.fantasy_points || 0;
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h4 className="font-semibold text-gray-900 dark:text-white">{playerName}</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">{position} • {team}</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-primary-600">{fantasyPoints.toFixed(1)}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">Fantasy Points</div>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-sm">
        {position === 'QB' && (
          <>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Pass Yds:</span>
              <span className="font-medium text-gray-900 dark:text-white">{stats.passing_yards || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Pass TDs:</span>
              <span className="font-medium text-gray-900 dark:text-white">{stats.passing_tds || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Rush Yds:</span>
              <span className="font-medium text-gray-900 dark:text-white">{stats.rushing_yards || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">INTs:</span>
              <span className="font-medium text-gray-900 dark:text-white">{stats.interceptions || 0}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
