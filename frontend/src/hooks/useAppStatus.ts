import { useCallback, useEffect, useState } from 'react';

import { api } from '../api/client';
import type { Stats, Status } from '../api/types';

export function useAppStatus() {
  const [status, setStatus] = useState<Status | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timeout: number | undefined;

    const params = new URLSearchParams(window.location.search);
    if (params.has('auth')) {
      window.history.replaceState({}, '', window.location.pathname);
    }

    const poll = async () => {
      try {
        const nextStatus = await api.getStatus();
        if (cancelled) return;
        setStatus(nextStatus);

        if (nextStatus.loaded) {
          const nextStats = await api.getStats();
          if (cancelled) return;
          setStats(nextStats);
        }

        if (nextStatus.authenticated && !nextStatus.loaded && !nextStatus.error) {
          timeout = window.setTimeout(poll, 2000);
        }
      } catch {
        if (!cancelled) timeout = window.setTimeout(poll, 3000);
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timeout) window.clearTimeout(timeout);
    };
  }, []);

  const refreshStats = useCallback(async () => {
    setStats(await api.getStats());
  }, []);

  return { status, stats, refreshStats };
}
