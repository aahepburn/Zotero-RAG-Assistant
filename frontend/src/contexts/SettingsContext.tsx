import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface Settings {
  openaiApiKey: string;
  anthropicApiKey: string;
  defaultModel: string;
  zoteroPath: string;
  chromaPath: string;
}

interface SettingsContextType {
  settings: Settings;
  updateSettings: (newSettings: Partial<Settings>) => Promise<void>;
  loading: boolean;
  error: string | null;
}

const defaultSettings: Settings = {
  openaiApiKey: '',
  anthropicApiKey: '',
  defaultModel: 'ollama',
  zoteroPath: '',
  chromaPath: '',
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load settings from backend on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await fetch('/settings');
        if (response.ok) {
          const text = await response.text();
          try {
            const data = JSON.parse(text);
            setSettings(data);
          } catch (parseErr) {
            console.error('Failed to parse settings JSON:', parseErr);
            setError('Failed to parse settings. Using defaults.');
            // Fall back to defaults
            setSettings(defaultSettings);
          }
        } else {
          console.error('Settings request failed:', response.status);
          setError('Failed to load settings from server');
        }
      } catch (err) {
        console.error('Failed to load settings:', err);
        setError('Failed to load settings');
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  const updateSettings = async (newSettings: Partial<Settings>) => {
    try {
      setError(null);
      const updatedSettings = { ...settings, ...newSettings };
      
      const response = await fetch('/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedSettings),
      });

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }

      const result = await response.json();
      
      // After saving, reload settings to get the masked versions
      const reloadResponse = await fetch('/settings');
      if (reloadResponse.ok) {
        const data = await reloadResponse.json();
        setSettings(data);
      } else {
        // If reload fails, still update local state
        setSettings(updatedSettings);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save settings';
      setError(errorMessage);
      throw err;
    }
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, loading, error }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
