import { useState } from 'react';

import { ErrorState } from './components/ErrorState';
import { Header } from './components/Header';
import { LoadingState } from './components/LoadingState';
import { Tabs } from './components/Tabs';
import { tabs } from './constants/tabs';
import { ConnectScreen } from './features/auth/ConnectScreen';
import { Dashboard } from './features/dashboard/Dashboard';
import { AddMovieTab } from './features/movies/AddMovieTab';
import { FilterTab } from './features/movies/FilterTab';
import { SearchTab } from './features/movies/SearchTab';
import { TopRatedTab } from './features/movies/TopRatedTab';
import { useAppStatus } from './hooks/useAppStatus';
import './styles/app.css';
import type { Tab } from './types/tabs';

export default function App() {
  const [tab, setTab] = useState<Tab>('dashboard');
  const { status, stats, refreshStats } = useAppStatus();

  if (status && !status.authenticated) {
    return (
      <div className="app">
        <Header />
        <ConnectScreen />
      </div>
    );
  }

  return (
    <div className="app">
      <Header status={status} />

      {status?.loading && !status.loaded && <LoadingState />}
      {status?.error && <ErrorState error={status.error} />}

      {(status?.loaded || status?.loading) && (
        <main className="app-main">
          <Tabs activeTab={tab} tabs={tabs} onChange={setTab} />

          {tab === 'dashboard' && <Dashboard stats={stats} />}
          {tab === 'search' && <SearchTab />}
          {tab === 'top-rated' && <TopRatedTab />}
          {tab === 'add' && <AddMovieTab onAdd={refreshStats} />}
          {tab === 'filter' && <FilterTab />}
        </main>
      )}
    </div>
  );
}
