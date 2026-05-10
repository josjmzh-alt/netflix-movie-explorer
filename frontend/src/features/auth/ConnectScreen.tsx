import { useState } from 'react';

import { api } from '../../api/client';

export function ConnectScreen() {
  const [loading, setLoading] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    try {
      const { url } = await api.getAuthUrl();
      window.location.href = url;
    } catch {
      setLoading(false);
    }
  };

  return (
    <div className="connect-screen">
      <div className="connect-icon">🍿</div>
      <div className="connect-title">Netflix Movie Library Explorer</div>
      <div className="connect-copy">
        Connect your Google account to load movie metadata from the Drive folder.
      </div>
      <button className="button button--large" onClick={handleConnect} disabled={loading}>
        {loading ? 'Redirecting to Google…' : 'Connect to Google Drive'}
      </button>
      <div className="connect-note">
        Your credentials are never stored in the app — OAuth2 tokens are saved locally only.
      </div>
    </div>
  );
}
