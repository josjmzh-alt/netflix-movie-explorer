import type { Status } from '../api/types';

interface HeaderProps {
  status?: Status | null;
}

export function Header({ status }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="app-logo">
        NETFLIX <span className="app-logo-subtitle">Movie Library Explorer</span>
      </div>
      {status && (
        <div className="status-list">
          {status.loading && (
            <span className="status-badge status-badge--loading">⟳ Loading Drive data…</span>
          )}
          {status.loaded && (
            <span className="status-badge status-badge--loaded">
              <span className="status-dot--loaded">● </span>
              {status.count.toLocaleString()} movies loaded
            </span>
          )}
          {status.error && (
            <span className="status-badge status-badge--error">
              <span className="status-dot--error">✕ </span>
              {status.error.slice(0, 40)}
            </span>
          )}
        </div>
      )}
    </header>
  );
}
