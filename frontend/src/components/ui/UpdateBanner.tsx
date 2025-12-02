/**
 * UpdateBanner Component
 * 
 * Shows notifications about available updates when running in Electron.
 * Handles the complete update flow: detection, download, and installation.
 */

import React, { useState, useEffect } from 'react';
import { 
  isElectron, 
  setupAutoUpdateListeners, 
  downloadUpdate, 
  installUpdate 
} from '../../utils/electron';
import '../../styles/updateBanner.css';

interface UpdateInfo {
  version: string;
  releaseNotes?: string;
}

interface UpdateProgress {
  percent: number;
  transferred: number;
  total: number;
}

type UpdateState = 'idle' | 'available' | 'downloading' | 'downloaded' | 'error';

export function UpdateBanner() {
  const [updateState, setUpdateState] = useState<UpdateState>('idle');
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo | null>(null);
  const [downloadProgress, setDownloadProgress] = useState<UpdateProgress | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only setup listeners if running in Electron
    if (!isElectron()) {
      return;
    }

    setupAutoUpdateListeners({
      onUpdateAvailable: (info) => {
        console.log('Update available:', info);
        setUpdateInfo(info);
        setUpdateState('available');
      },

      onUpdateDownloadProgress: (progress) => {
        console.log('Download progress:', progress);
        setDownloadProgress(progress);
        setUpdateState('downloading');
      },

      onUpdateDownloaded: (info) => {
        console.log('Update downloaded:', info);
        setUpdateInfo(info);
        setUpdateState('downloaded');
      }
    });
  }, []);

  const handleDownload = async () => {
    setUpdateState('downloading');
    setError(null);

    const result = await downloadUpdate();
    
    if (!result.success) {
      setError(result.error || 'Failed to download update');
      setUpdateState('error');
    }
  };

  const handleInstall = () => {
    installUpdate();
    // App will restart here
  };

  const handleDismiss = () => {
    setUpdateState('idle');
    setUpdateInfo(null);
    setDownloadProgress(null);
    setError(null);
  };

  // Don't render anything if not in Electron or no update
  if (!isElectron() || updateState === 'idle') {
    return null;
  }

  return (
    <div className="update-banner">
      {/* Update Available */}
      {updateState === 'available' && (
        <div className="update-banner__content update-banner__content--info">
          <div className="update-banner__message">
            <strong>Update Available!</strong>
            <span>Version {updateInfo?.version} is ready to download.</span>
          </div>
          <div className="update-banner__actions">
            <button 
              onClick={handleDownload}
              className="update-banner__button update-banner__button--primary"
            >
              Download Update
            </button>
            <button 
              onClick={handleDismiss}
              className="update-banner__button update-banner__button--text"
            >
              Later
            </button>
          </div>
        </div>
      )}

      {/* Downloading */}
      {updateState === 'downloading' && downloadProgress && (
        <div className="update-banner__content update-banner__content--progress">
          <div className="update-banner__message">
            <strong>Downloading Update...</strong>
            <span>
              {downloadProgress.percent.toFixed(0)}% 
              ({(downloadProgress.transferred / 1024 / 1024).toFixed(1)} MB / 
              {(downloadProgress.total / 1024 / 1024).toFixed(1)} MB)
            </span>
          </div>
          <div className="update-banner__progress">
            <div 
              className="update-banner__progress-bar"
              style={{ width: `${downloadProgress.percent}%` }}
            />
          </div>
        </div>
      )}

      {/* Downloaded - Ready to Install */}
      {updateState === 'downloaded' && (
        <div className="update-banner__content update-banner__content--success">
          <div className="update-banner__message">
            <strong>Update Ready!</strong>
            <span>Version {updateInfo?.version} has been downloaded. Restart to apply.</span>
          </div>
          <div className="update-banner__actions">
            <button 
              onClick={handleInstall}
              className="update-banner__button update-banner__button--primary"
            >
              Restart & Update
            </button>
            <button 
              onClick={handleDismiss}
              className="update-banner__button update-banner__button--text"
            >
              Later
            </button>
          </div>
        </div>
      )}

      {/* Error */}
      {updateState === 'error' && (
        <div className="update-banner__content update-banner__content--error">
          <div className="update-banner__message">
            <strong>Update Failed</strong>
            <span>{error || 'An error occurred while updating.'}</span>
          </div>
          <div className="update-banner__actions">
            <button 
              onClick={handleDownload}
              className="update-banner__button update-banner__button--primary"
            >
              Try Again
            </button>
            <button 
              onClick={handleDismiss}
              className="update-banner__button update-banner__button--text"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
