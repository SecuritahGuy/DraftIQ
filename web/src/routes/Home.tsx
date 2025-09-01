// Home page component

import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useLeagues } from '../hooks/useLeagues';

export const Home: React.FC = () => {
  const { user } = useAuth();
  const { leagues, isLoading: leaguesLoading } = useLeagues();
  
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Welcome back, {user?.display_name || user?.username}!
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Ready to dominate your fantasy league?
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Quick Stats Cards */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Active Leagues
          </h3>
          <p className="text-3xl font-bold text-primary-600">
            {leaguesLoading ? '...' : leagues?.length || 0}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Connected leagues
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            This Week
          </h3>
          <p className="text-3xl font-bold text-green-600">Week 1</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            2024 NFL Season
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Projections
          </h3>
          <p className="text-3xl font-bold text-blue-600">0</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Players analyzed
          </p>
        </div>
      </div>
      
      {/* Recent Activity */}
      <div className="mt-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Activity
          </h3>
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p>No recent activity</p>
            <p className="text-sm">Connect your leagues to see updates here</p>
          </div>
        </div>
      </div>
    </div>
  );
};
