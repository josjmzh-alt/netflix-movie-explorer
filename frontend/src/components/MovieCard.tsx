import type { MovieRead } from '../api/types';

interface MovieCardProps {
  movie: MovieRead;
  rank?: number;
}

function ratingClass(rating: number) {
  if (rating >= 8) return 'rating-badge rating-badge--high';
  if (rating >= 6) return 'rating-badge rating-badge--medium';
  return 'rating-badge rating-badge--low';
}

export function MovieCard({ movie, rank }: MovieCardProps) {
  return (
    <div className="movie-card">
      <div className="movie-card-header">
        <div className="movie-title">
          {rank && <span className="movie-rank">#{rank}</span>}
          {movie.title}
          {movie.source === 'added' && <span className="added-badge">NEW</span>}
        </div>
        <span className={ratingClass(movie.rating)}>★ {movie.rating.toFixed(1)}</span>
      </div>
      <div className="movie-meta">
        <span className="tag">{movie.genre}</span>
        {movie.year != null && <span>{movie.year}</span>}
        {movie.director && <span>Dir: {movie.director}</span>}
        {movie.description && (
          <span className="movie-description">
            {movie.description.slice(0, 120)}
            {movie.description.length > 120 ? '…' : ''}
          </span>
        )}
      </div>
    </div>
  );
}
