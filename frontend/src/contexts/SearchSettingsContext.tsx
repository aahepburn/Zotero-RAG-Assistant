import React, { createContext, useContext, useState, ReactNode } from 'react';

/**
 * Search settings for metadata filtering and search mode configuration.
 */
export interface SearchFilters {
  yearMin?: number;
  yearMax?: number;
  tags: string[];
  collections: string[];
  title?: string;
  author?: string;
  itemTypes?: string[];
}

export type SearchEngineMode = 'original' | 'metadata-aware';
export type FilterMode = 'auto' | 'manual';

export interface SearchSettings {
  // Search engine mode toggle
  searchEngineMode: SearchEngineMode;
  
  // Filter mode (auto-extract or manual specification)
  filterMode: FilterMode;
  
  // Manual filters (used when filterMode is 'manual')
  manualFilters: SearchFilters;
  
  // Whether to use RRF hybrid search
  useRRF: boolean;
}

interface SearchSettingsContextType {
  searchSettings: SearchSettings;
  updateSearchSettings: (updates: Partial<SearchSettings>) => void;
  updateManualFilters: (filters: Partial<SearchFilters>) => void;
  resetFilters: () => void;
  hasActiveFilters: () => boolean;
}

const defaultSearchSettings: SearchSettings = {
  searchEngineMode: 'original',
  filterMode: 'auto',
  manualFilters: {
    tags: [],
    collections: [],
    title: undefined,
    author: undefined,
  },
  useRRF: true,
};

const SearchSettingsContext = createContext<SearchSettingsContextType | undefined>(undefined);

export const SearchSettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [searchSettings, setSearchSettings] = useState<SearchSettings>(defaultSearchSettings);

  const updateSearchSettings = (updates: Partial<SearchSettings>) => {
    setSearchSettings(prev => ({
      ...prev,
      ...updates,
    }));
  };

  const updateManualFilters = (filters: Partial<SearchFilters>) => {
    setSearchSettings(prev => ({
      ...prev,
      manualFilters: {
        ...prev.manualFilters,
        ...filters,
      },
    }));
  };

  const resetFilters = () => {
    setSearchSettings(prev => ({
      ...prev,
      manualFilters: {
        tags: [],
        collections: [],
        title: undefined,
        author: undefined,
        itemTypes: undefined,
      },
    }));
  };

  const hasActiveFilters = (): boolean => {
    const { manualFilters, filterMode, searchEngineMode } = searchSettings;

    // No filters if using original search mode
    if (searchEngineMode === 'original') {
      return false;
    }

    // Check manual filters if in manual mode
    if (filterMode === 'manual') {
      return !!(
        manualFilters.yearMin ||
        manualFilters.yearMax ||
        manualFilters.tags.length > 0 ||
        manualFilters.collections.length > 0 ||
        manualFilters.title ||
        manualFilters.author ||
        (manualFilters.itemTypes && manualFilters.itemTypes.length > 0)
      );
    }

    // Auto mode doesn't show as "active" - filters extracted from query
    return false;
  };

  return (
    <SearchSettingsContext.Provider
      value={{
        searchSettings,
        updateSearchSettings,
        updateManualFilters,
        resetFilters,
        hasActiveFilters,
      }}
    >
      {children}
    </SearchSettingsContext.Provider>
  );
};

export const useSearchSettings = () => {
  const context = useContext(SearchSettingsContext);
  if (context === undefined) {
    throw new Error('useSearchSettings must be used within a SearchSettingsProvider');
  }
  return context;
};
