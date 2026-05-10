import type { Tab, TabItem } from '../types/tabs';

interface TabsProps {
  activeTab: Tab;
  tabs: TabItem[];
  onChange: (tab: Tab) => void;
}

export function Tabs({ activeTab, tabs, onChange }: TabsProps) {
  return (
    <nav className="tabs">
      {tabs.map(tab => (
        <button
          className={`tab-button${activeTab === tab.id ? ' tab-button--active' : ''}`}
          key={tab.id}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
