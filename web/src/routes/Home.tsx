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
          <p className="text-3xl font-bold text-green-600">Pre-Season</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            2025 NFL Season
          </p>
        </div>
        
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Historical Data
          </h3>
          <p className="text-3xl font-bold text-blue-600">5,597</p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            2024 stats for projections
          </p>
        </div>
      </div>
      
      {/* Recent Activity */}
      <div className="mt-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Activity
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Historical Data Loaded</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">2024 season stats for 2025 projections</p>
                </div>
              </div>
              <span className="text-xs text-green-600 dark:text-green-400">Just now</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">League Synced</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">My Fantasy League updated</p>
                </div>
              </div>
              <span className="text-xs text-blue-600 dark:text-blue-400">2 min ago</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">League Ready</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">2025 fantasy season prepared</p>
                </div>
              </div>
              <span className="text-xs text-purple-600 dark:text-purple-400">5 min ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
