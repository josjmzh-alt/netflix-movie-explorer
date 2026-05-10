import type { Stats } from '../../api/types';

interface DashboardProps {
  stats: Stats | null;
}

export function Dashboard({ stats }: DashboardProps) {
  if (!stats) return <div className="loading">Loading stats…</div>;

  const yearEntries = Object.entries(stats.by_year).slice(0, 10);

  return (
    <div>
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_count.toLocaleString()}</div>
          <div className="stat-label">Total Movies</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">★ {stats.average_rating}</div>
          <div className="stat-label">Average Rating</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.top_genres[0]?.genre ?? '—'}</div>
          <div className="stat-label">Top Genre</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{Object.keys(stats.by_year).length}</div>
          <div className="stat-label">Years Covered</div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="panel-title">🎬 Top 5 Genres</div>
          {stats.top_genres.map((genre, index) => (
            <div className="row" key={genre.genre}>
              <span className="row-label">{index + 1}. {genre.genre}</span>
              <span className="row-value">{genre.count}</span>
            </div>
          ))}
        </div>

        <div className="card">
          <div className="panel-title">📅 Movies by Year (recent)</div>
          {yearEntries.map(([year, data]) => (
            <div className="year-group" key={year}>
              <div className="row row--compact">
                <span className="row-label">{year}</span>
                <span className="row-value">{data.count}</span>
              </div>
              <ul className="year-movie-list">
                {data.movies.slice(0, 5).map(title => (
                  <li key={title}>{title}</li>
                ))}
              </ul>
              {data.movies.length > 5 && (
                <div className="year-more-count">+{data.movies.length - 5} more</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
