export interface MovieRead {
  id: string;
  title: string;
  genre: string;
  rating: number;
  year?: number;
  description?: string;
  director?: string;
  source: 'drive' | 'added';
}

export interface GenreCount {
  genre: string;
  count: number;
}

export interface YearData {
  count: number;
  movies: string[];
}

export interface Stats {
  total_count: number;
  average_rating: number;
  top_genres: GenreCount[];
  by_year: Record<string, YearData>;
}

export interface Status {
  authenticated: boolean;
  loaded: boolean;
  loading: boolean;
  count: number;
  error?: string;
}

export interface MovieCreate {
  title: string;
  genre: string;
  rating: number;
  year?: number;
  description?: string;
  director?: string;
}

export interface FilterParams {
  genre?: string;
  min_rating?: number;
  year?: number;
}
