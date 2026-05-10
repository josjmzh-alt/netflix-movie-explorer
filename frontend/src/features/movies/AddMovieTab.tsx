import { useState, type FormEvent } from 'react';

import { api } from '../../api/client';

interface AddMovieTabProps {
  onAdd: () => void;
}

interface FormState {
  title: string;
  genre: string;
  rating: string;
  year: string;
  description: string;
  director: string;
}

const emptyForm: FormState = {
  title: '',
  genre: '',
  rating: '',
  year: '',
  description: '',
  director: '',
};

export function AddMovieTab({ onAdd }: AddMovieTabProps) {
  const [form, setForm] = useState<FormState>(emptyForm);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (key: keyof FormState) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    setForm(current => ({ ...current, [key]: event.target.value }));
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const movie = await api.addMovie({
        title: form.title,
        genre: form.genre,
        rating: parseFloat(form.rating),
        year: parseInt(form.year),
        description: form.description || undefined,
        director: form.director || undefined,
      });
      setSuccess(`✅ "${movie.title}" added successfully!`);
      setForm(emptyForm);
      onAdd();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-shell">
      <form onSubmit={submit}>
        <div className="form-grid">
          <div>
            <label className="label">Title *</label>
            <input className="input" value={form.title} onChange={set('title')} required />
          </div>
          <div>
            <label className="label">Genre *</label>
            <input className="input" value={form.genre} onChange={set('genre')} required />
          </div>
          <div>
            <label className="label">Rating (0–10) *</label>
            <input
              className="input"
              type="number"
              step="0.1"
              min="0"
              max="10"
              value={form.rating}
              onChange={set('rating')}
              required
            />
          </div>
          <div>
            <label className="label">Year *</label>
            <input
              className="input"
              type="number"
              min="1888"
              max="2100"
              value={form.year}
              onChange={set('year')}
              required
            />
          </div>
          <div>
            <label className="label">Director</label>
            <input className="input" value={form.director} onChange={set('director')} />
          </div>
        </div>
        <div className="field-spacer">
          <label className="label">Description</label>
          <textarea className="input textarea" value={form.description} onChange={set('description')} />
        </div>
        {error && <div className="error form-message">{error}</div>}
        {success && <div className="success">{success}</div>}
        <button className="button submit-button" type="submit" disabled={loading}>
          {loading ? 'Adding…' : 'Add Movie'}
        </button>
      </form>
    </div>
  );
}
