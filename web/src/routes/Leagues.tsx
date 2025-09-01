// Leagues page component

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLeagues } from '../hooks/useLeagues';

export const Leagues: React.FC = () => {
  const navigate = useNavigate();
  const { leagues, isLoading, error, syncLeagueData, isSyncing } = useLeagues();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-2 text-gray-600">Loading leagues...</span>
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
            Error Loading Leagues
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {error.message || 'Failed to load your leagues'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Your Leagues
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage and sync your Yahoo Fantasy Football leagues
        </p>
      </div>
      
      {leagues.length === 0 ? (
        <div className="card">
          <div className="text-center py-8">
            <div className="text-gray-400 mb-4">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No Leagues Found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Connect your Yahoo Fantasy Football account to see your leagues
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="btn-primary"
            >
              Go to Home
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {leagues.map((league: any) => (
            <div key={league.league_key} className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {league.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Season {league.season}
                  </p>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                  {league.num_teams} teams
                </span>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Type:</span>
                  <span className="text-gray-900 dark:text-white">{league.league_type}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Status:</span>
                  <span className={`text-gray-900 dark:text-white ${league.is_finished ? 'text-red-600' : 'text-green-600'}`}>
                    {league.is_finished ? 'Finished' : 'Active'}
                  </span>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => syncLeagueData(league.league_key)}
                  disabled={isSyncing}
                  className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSyncing ? 'Syncing...' : 'Sync Data'}
                </button>
                <button
                  onClick={() => navigate(`/league/${league.league_key}`)}
                  className="flex-1 btn-secondary"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
