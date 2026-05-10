import { useState, type FormEvent } from 'react';

import { api } from '../../api/client';
import type { MovieRead } from '../../api/types';
import { MovieCard } from '../../components/MovieCard';

export function SearchTab() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<MovieRead[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const search = async (event: FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      setResults(await api.searchMovies(query));
    } catch (err: any) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form className="search-form" onSubmit={search}>
        <input
          className="input"
          placeholder="Search by title…"
          value={query}
          onChange={event => setQuery(event.target.value)}
        />
        <button className="button search-button" type="submit" disabled={loading}>
          {loading ? '…' : 'Search'}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      {results.map(movie => <MovieCard key={movie.id} movie={movie} />)}
    </div>
  );
}
