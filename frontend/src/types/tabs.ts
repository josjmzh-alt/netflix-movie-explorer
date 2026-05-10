export type Tab = 'dashboard' | 'search' | 'top-rated' | 'add' | 'filter';

export interface TabItem {
  id: Tab;
  label: string;
}
