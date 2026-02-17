import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { checkMetadataVersion, migrateMetadata, MetadataVersionInfo, MigrationResponse } from '../api/metadata';

interface MigrationContextType {
  versionInfo: MetadataVersionInfo | null;
  loading: boolean;
  migrating: boolean;
  showBanner: boolean;
  error: string | null;
  checkVersion: () => Promise<void>;
  startMigration: () => Promise<MigrationResponse>;
  dismissBanner: () => void;
}

const MigrationContext = createContext<MigrationContextType | undefined>(undefined);

export const MigrationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [versionInfo, setVersionInfo] = useState<MetadataVersionInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [migrating, setMigrating] = useState(false);
  const [showBanner, setShowBanner] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check version on mount
  useEffect(() => {
    checkVersion();
  }, []);

  const checkVersion = async () => {
    setLoading(true);
    setError(null);
    try {
      const info = await checkMetadataVersion();
      setVersionInfo(info);
      
      // Show banner if migration is needed and user hasn't dismissed it
      const dismissed = localStorage.getItem('migration-banner-dismissed');
      if (info.migration_needed && !dismissed) {
        setShowBanner(true);
      }
    } catch (err) {
      console.error('Failed to check metadata version:', err);
      setError(err instanceof Error ? err.message : 'Failed to check metadata version');
    } finally {
      setLoading(false);
    }
  };

  const startMigration = async (): Promise<MigrationResponse> => {
    setMigrating(true);
    setError(null);
    try {
      const response = await migrateMetadata();
      
      if (response.status === 'completed' || response.status === 'not_needed') {
        // Re-check version after successful migration
        await checkVersion();
        setShowBanner(false);
        // Clear dismissed flag so banner can show again if needed in future
        localStorage.removeItem('migration-banner-dismissed');
      }
      
      return response;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Migration failed';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setMigrating(false);
    }
  };

  const dismissBanner = () => {
    setShowBanner(false);
    // Remember dismissal for this session (but will show again on next app launch if still needed)
    localStorage.setItem('migration-banner-dismissed', 'true');
  };

  return (
    <MigrationContext.Provider
      value={{
        versionInfo,
        loading,
        migrating,
        showBanner,
        error,
        checkVersion,
        startMigration,
        dismissBanner,
      }}
    >
      {children}
    </MigrationContext.Provider>
  );
};

export const useMigration = () => {
  const context = useContext(MigrationContext);
  if (!context) {
    throw new Error('useMigration must be used within MigrationProvider');
  }
  return context;
};
