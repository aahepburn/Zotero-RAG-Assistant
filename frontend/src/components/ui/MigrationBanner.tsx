import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from './Button';
import '../styles/migration-banner.css';

interface MigrationBannerProps {
  onDismiss?: () => void;
}

/**
 * Banner that prompts users to migrate their database to enable metadata filtering.
 * Appears at the top of the app when migration is needed.
 */
const MigrationBanner: React.FC<MigrationBannerProps> = ({ onDismiss }) => {
  const navigate = useNavigate();

  const handleGoToSettings = () => {
    navigate('/settings');
    if (onDismiss) {
      onDismiss();
    }
  };

  return (
    <div className="migration-banner">
      <div className="migration-banner-content">
        <div className="migration-banner-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M12 2L2 7L12 12L22 7L12 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M2 17L12 22L22 17"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M2 12L12 17L22 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <div className="migration-banner-text">
          <h3 className="migration-banner-title">Database Update Required</h3>
          <p className="migration-banner-message">
            Your library needs to be updated to enable new metadata filtering features 
            (search by tags, collections, and year ranges). This quick update takes 5-10 minutes 
            and won't require re-indexing your documents.
          </p>
        </div>
        <div className="migration-banner-actions">
          <Button onClick={handleGoToSettings} variant="primary">
            Go to Settings
          </Button>
          {onDismiss && (
            <Button onClick={onDismiss} variant="secondary">
              Dismiss
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default MigrationBanner;
