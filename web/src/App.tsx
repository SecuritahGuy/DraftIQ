import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import { Layout } from './components/Layout';
import { Home } from './routes/Home';
import { Leagues } from './routes/Leagues';
import { LeagueDashboard } from './routes/LeagueDashboard';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/leagues" element={<Leagues />} />
            <Route path="/league/:leagueKey" element={<LeagueDashboard />} />
            <Route path="/lineup" element={<div>Lineup Page</div>} />
            <Route path="/waivers" element={<div>Waivers Page</div>} />
            <Route path="/trades" element={<div>Trades Page</div>} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
