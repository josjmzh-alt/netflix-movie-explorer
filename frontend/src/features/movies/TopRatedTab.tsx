import { useCallback, useEffect, useState } from 'react';

import { api } from '../../api/client';
import type { MovieRead } from '../../api/types';
import { MovieCard } from '../../components/MovieCard';

export function TopRatedTab() {
  const [movies, setMovies] = useState<MovieRead[]>([]);
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setMovies(await api.getTopRated(limit));
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div>
      <div className="toolbar">
        <select
          className="input select"
          value={limit}
          onChange={event => setLimit(Number(event.target.value))}
        >
          {[5, 10, 20, 50].map(count => (
            <option key={count} value={count}>Top {count}</option>
          ))}
        </select>
        <button className="button" onClick={load} disabled={loading}>
          {loading ? 'Loading…' : 'Load Top Rated'}
        </button>
      </div>
      {movies.map((movie, index) => (
        <MovieCard key={movie.id} movie={movie} rank={index + 1} />
      ))}
    </div>
  );
}
