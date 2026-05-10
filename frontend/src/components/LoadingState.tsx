export function LoadingState() {
  return (
    <div className="loading loading--page">
      <div className="spinner" />
      <div className="loading-title">Connecting to Google Drive…</div>
      <div className="loading-subtitle">Traversing nested folders and parsing JSON files</div>
    </div>
  );
}
