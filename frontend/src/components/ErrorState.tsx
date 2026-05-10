interface ErrorStateProps {
  error: string;
}

export function ErrorState({ error }: ErrorStateProps) {
  return (
    <div className="error-page">
      <div className="error">
        <strong>Failed to load Drive data:</strong> {error}
        <br />
        <br />
        Make sure <code>credentials.json</code> is in the backend folder and your Gmail is a test user.
      </div>
    </div>
  );
}
