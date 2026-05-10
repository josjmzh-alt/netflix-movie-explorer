import { useState, type FormEvent } from 'react';

import { api } from '../../api/client';
import type { FilterParams, MovieRead } from '../../api/types';
import { MovieCard } from '../../components/MovieCard';

export function FilterTab() {
  const [params, setParams] = useState<FilterParams>({});
  const [results, setResults] = useState<MovieRead[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);

  const set = (key: keyof FilterParams) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setParams(current => ({
      ...current,
      [key]: value === '' ? undefined : key === 'genre' ? value : Number(value),
    }));
  };

  const search = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      setResults(await api.filterMovies(params));
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card technical-card">
        <div className="technical-label">🔧 TECHNICAL ENDPOINT</div>
        <code className="technical-code">GET /api/movies?genre=Action&amp;min_rating=7&amp;year=2020</code>
      </div>
      <form className="filter-form" onSubmit={search}>
        <div>
          <label className="label">Genre</label>
          <input className="input" placeholder="e.g. Action" onChange={set('genre')} />
        </div>
        <div>
          <label className="label">Min Rating</label>
          <input
            className="input"
            type="number"
            step="0.1"
            min="0"
            max="10"
            placeholder="e.g. 7.5"
            onChange={set('min_rating')}
          />
        </div>
        <div>
          <label className="label">Year</label>
          <input className="input" type="number" placeholder="e.g. 2020" onChange={set('year')} />
        </div>
        <button className="button" type="submit" disabled={loading}>Filter</button>
      </form>
      {searched && <div className="result-count">{results.length} result(s)</div>}
      {results.map(movie => <MovieCard key={movie.id} movie={movie} />)}
    </div>
  );
}
