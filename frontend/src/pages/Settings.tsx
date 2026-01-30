import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSettings, ModelInfo, ProviderInfo } from '../contexts/SettingsContext';
import { apiFetch } from '../api/client';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import ProfileSelector from '../components/profile/ProfileSelector';
import { useProfile } from '../contexts/ProfileContext';
import { useAppUpdater } from '../hooks/useAppUpdater';
import { isElectron } from '../utils/electron';
import '../styles/settings.css';

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const { settings, updateSettings, loading, availableProviders } = useSettings();
  const { profiles, activeProfile, deleteProfile } = useProfile();
  const [formData, setFormData] = useState(settings);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [availableModels, setAvailableModels] = useState<Record<string, ModelInfo[]>>({});
  const [loadingModels, setLoadingModels] = useState<Record<string, boolean>>({});
  const [validatingProvider, setValidatingProvider] = useState<string | null>(null);
  const [providerValidation, setProviderValidation] = useState<Record<string, { valid: boolean; message?: string }>>({});
  
  // Auto-updater hook (only used in Electron)
  const updater = useAppUpdater();

  useEffect(() => {
    setFormData(settings);
  }, [settings]);

  const handleInputChange = (field: keyof typeof formData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setSaveSuccess(false);
    setSaveError(null);
  };

  const handleProviderEnabledChange = (providerId: string, enabled: boolean) => {
    setFormData(prev => ({
      ...prev,
      providers: {
        ...prev.providers,
        [providerId]: {
          ...prev.providers[providerId],
          enabled
        }
      }
    }));
    setSaveSuccess(false);
    setSaveError(null);
  };

  const handleProviderCredentialChange = (providerId: string, key: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      providers: {
        ...prev.providers,
        [providerId]: {
          ...prev.providers[providerId],
          credentials: {
            ...prev.providers[providerId].credentials,
            [key]: value
          }
        }
      }
    }));
    setSaveSuccess(false);
    setSaveError(null);
  };

  const loadModelsForProvider = async (providerId: string) => {
    setLoadingModels(prev => ({ ...prev, [providerId]: true }));
    try {
      const response = await apiFetch(`/api/providers/${providerId}/models`);
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(prev => ({ ...prev, [providerId]: data.models || [] }));
      }
    } catch (err) {
      console.error(`Failed to load models for ${providerId}:`, err);
    } finally {
      setLoadingModels(prev => ({ ...prev, [providerId]: false }));
    }
  };

  const validateProvider = async (providerId: string) => {
    setValidatingProvider(providerId);
    try {
      const response = await apiFetch(`/api/providers/${providerId}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          credentials: formData.providers[providerId].credentials
        })
      });
      const data = await response.json();
      setProviderValidation(prev => ({
        ...prev,
        [providerId]: {
          valid: data.valid,
          message: data.error || data.details || (data.valid ? 'Connection successful' : 'Validation failed')
        }
      }));
      
      // If valid, load models
      if (data.valid) {
        await loadModelsForProvider(providerId);
      }
    } catch (err) {
      setProviderValidation(prev => ({
        ...prev,
        [providerId]: {
          valid: false,
          message: 'Connection failed'
        }
      }));
    } finally {
      setValidatingProvider(null);
    }
  };

  useEffect(() => {
    // Load models for enabled providers on mount
    Object.entries(formData.providers).forEach(([providerId, config]) => {
      if (config.enabled && !loadingModels[providerId] && !availableModels[providerId]) {
        loadModelsForProvider(providerId);
      }
    });
  }, [formData.providers]);

  const handleSave = async () => {
    try {
      setSaving(true);
      setSaveError(null);
      await updateSettings(formData);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const getProviderInfo = (providerId: string): ProviderInfo | undefined => {
    return availableProviders.find(p => p.id === providerId);
  };

  if (loading) {
    return (
      <div className="settings-page">
        <div className="settings-loading">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <button className="settings-back-btn" onClick={() => navigate('/')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M5 12l7-7M5 12l7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Back
        </button>
        <h1 className="settings-title">Settings</h1>
      </div>

      <div className="settings-container">
        <section className="settings-section">
          <h2 className="settings-section-title">Support & Feedback</h2>
          <p className="settings-section-description">
            Help improve Zotero RAG Assistant by reporting bugs or supporting the project.
          </p>
          
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginTop: '16px' }}>
            <Button
              onClick={() => window.open('https://github.com/aahepburn/Zotero-RAG-Assistant/issues/new', '_blank', 'noopener,noreferrer')}
              variant="secondary"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Report a Bug
            </Button>
            
            <Button
              onClick={() => window.open('https://github.com/sponsors/aahepburn', '_blank', 'noopener,noreferrer')}
              variant="secondary"
              style={{ 
                display: 'flex', 
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7.655 14.916L7.648 14.91L7.641 14.903C5.787 13.29 4.328 11.984 3.316 10.781C2.315 9.59 1.8 8.55 1.8 7.5C1.8 5.821 3.021 4.6 4.7 4.6C5.746 4.6 6.77 5.171 7.34 6.025L8 7.015L8.66 6.025C9.23 5.171 10.254 4.6 11.3 4.6C12.979 4.6 14.2 5.821 14.2 7.5C14.2 8.55 13.685 9.59 12.684 10.781C11.672 11.984 10.213 13.29 8.359 14.903L8.352 14.91L8.345 14.916C8.153 15.082 7.847 15.082 7.655 14.916Z" fill="#DB61A2" stroke="#DB61A2" strokeWidth="1.2"/>
              </svg>
              <span style={{ color: '#DB61A2', fontWeight: 500 }}>Sponsor</span>
            </Button>
          </div>
          
          <p className="settings-hint" style={{ marginTop: '12px' }}>
            <strong>Found a bug?</strong> Open an issue on GitHub and include:
            <ul style={{ marginTop: '8px', marginLeft: '20px', lineHeight: '1.6' }}>
              <li>Screenshots of the problem</li>
              <li>Any error messages you see</li>
              <li>Console logs (open Dev Tools with <kbd style={{ padding: '2px 6px', backgroundColor: 'var(--bg-secondary, #e9ecef)', borderRadius: '3px', fontSize: '12px' }}>Cmd+Option+I</kbd> on Mac or <kbd style={{ padding: '2px 6px', backgroundColor: 'var(--bg-secondary, #e9ecef)', borderRadius: '3px', fontSize: '12px' }}>Ctrl+Shift+I</kbd> on Windows/Linux, then copy from the Console tab)</li>
            </ul>
            <strong>Like the app?</strong> Consider sponsoring to support continued development!
          </p>
        </section>

        <section className="settings-section">
          <h2 className="settings-section-title">Profile</h2>
          <p className="settings-section-description">
            Manage your user profiles. Each profile has its own settings, chat history, and vector database.
          </p>
          <ProfileSelector />
        </section>

        {/* Updates Section - Only shown in Electron */}
        {isElectron() && (
          <section className="settings-section">
            <h2 className="settings-section-title">Application Updates</h2>
            <p className="settings-section-description">
              Keep your application up to date with the latest features and improvements.
            </p>
            
            <div className="update-status-card">
              <div className="update-info">
                <div className="update-version">
                  <strong>Current Version:</strong> {updater.currentVersion || 'Loading...'}
                </div>
                
                {updater.status === 'idle' && (
                  <div className="update-message">
                    Click "Check for Updates" to see if a new version is available.
                  </div>
                )}
                
                {updater.status === 'checking' && (
                  <div className="update-message checking">
                    <span className="spinner"></span>
                    Checking for updates...
                  </div>
                )}
                
                {updater.status === 'not-available' && (
                  <div className="update-message up-to-date">
                     You're running the latest version
                  </div>
                )}
                
                {updater.status === 'available' && updater.updateInfo && (
                  <div className="update-message available">
                    <strong>Update Available:</strong> Version {updater.updateInfo.version}
                    {updater.updateInfo.releaseNotes && (
                      <div className="release-notes">
                        <details>
                          <summary>Release Notes</summary>
                          <div className="release-notes-content">
                            {updater.updateInfo.releaseNotes}
                          </div>
                        </details>
                      </div>
                    )}
                  </div>
                )}
                
                {updater.status === 'downloading' && updater.downloadProgress && (
                  <div className="update-message downloading">
                    <div className="download-progress">
                      <div className="progress-text">
                        Downloading update... {updater.downloadProgress.percent.toFixed(1)}%
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill" 
                          style={{ width: `${updater.downloadProgress.percent}%` }}
                        />
                      </div>
                      <div className="progress-details">
                        {(updater.downloadProgress.transferred / 1024 / 1024).toFixed(1)} MB / 
                        {(updater.downloadProgress.total / 1024 / 1024).toFixed(1)} MB
                      </div>
                    </div>
                  </div>
                )}
                
                {updater.status === 'downloaded' && updater.updateInfo && (
                  <div className="update-message downloaded">
                    <strong> Update Ready to Install</strong>
                    <p>Version {updater.updateInfo.version} has been downloaded and is ready to install.</p>
                    <p className="install-note">
                      The application will restart to complete the installation.
                    </p>
                  </div>
                )}
                
                {updater.status === 'error' && updater.error && (
                  <div className="update-message error">
                    <strong>Error:</strong> {updater.error}
                  </div>
                )}
              </div>
              
              <div className="update-actions">
                {(updater.status === 'idle' || updater.status === 'not-available' || updater.status === 'error') && (
                  <Button
                    onClick={updater.checkForUpdates}
                    variant="secondary"
                  >
                    Check for Updates
                  </Button>
                )}
              </div>
              
              {updater.status === 'available' && updater.updateInfo && (
                <div className="settings-note" style={{ 
                  marginTop: '16px',
                  padding: '16px', 
                  backgroundColor: 'var(--warning-bg, #fff3cd)', 
                  borderLeft: '4px solid var(--warning, #ffc107)', 
                  fontSize: '14px',
                  color: 'var(--text)',
                  lineHeight: '1.6'
                }}>
                  <strong style={{ display: 'block', marginBottom: '8px', fontSize: '15px' }}>
                    ⚠️ Manual Update Required
                  </strong>
                  <p style={{ margin: '0 0 12px 0' }}>
                    Version {updater.updateInfo.version} is available. To update, please download the new release file manually from GitHub Releases.
                  </p>
                  <Button
                    onClick={() => window.electron?.openExternal('https://github.com/aahepburn/Zotero-RAG-Assistant/releases/latest')}
                    variant="primary"
                    style={{ marginTop: '8px' }}
                  >
                    Download from GitHub Releases →
                  </Button>
                </div>
              )}
              
              <div className="settings-note" style={{ 
                marginTop: '16px',
                padding: '12px', 
                backgroundColor: 'var(--bg-hover, #f8f9fa)', 
                borderLeft: '3px solid var(--text-muted, #6c757d)', 
                fontSize: '13px',
                color: 'var(--text-muted)'
              }}>
                <strong>Note:</strong> Automatic updates are disabled. When a new version is available, you'll need to download and install it manually from{' '}
                <a 
                  href="https://github.com/aahepburn/Zotero-RAG-Assistant/releases" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ color: 'var(--accent, #007bff)', textDecoration: 'underline' }}
                >
                  GitHub Releases
                </a>.
              </div>
            </div>
          </section>
        )}

        <section className="settings-section">
          <h2 className="settings-section-title">Active Model</h2>
          <p className="settings-section-description">
            Select your default LLM provider and model for chat interactions.
          </p>
          <p className="settings-note" style={{ 
            padding: '12px', 
            backgroundColor: 'var(--bg-hover, #f8f9fa)', 
            borderLeft: '3px solid var(--accent, #007bff)', 
            marginBottom: '16px',
            fontSize: '14px',
            color: 'var(--text-muted)'
          }}>
            <strong>Note:</strong> Only local Ollama models have been thoroughly tested. External API providers may have limited compatibility.
          </p>

          <div className="settings-field">
            <label className="settings-label" htmlFor="active-provider">
              Provider
            </label>
            <select
              id="active-provider"
              value={formData.activeProviderId}
              onChange={(e) => handleInputChange('activeProviderId', e.target.value)}
              className="settings-select"
            >
              {availableProviders.map(provider => (
                <option key={provider.id} value={provider.id}>
                  {provider.label}
                </option>
              ))}
            </select>
          </div>

          <div className="settings-field">
            <label className="settings-label" htmlFor="active-model">
              Model
              {loadingModels[formData.activeProviderId] && <span className="settings-loading-inline"> (loading...)</span>}
            </label>
            <select
              id="active-model"
              value={formData.activeModel}
              onChange={(e) => handleInputChange('activeModel', e.target.value)}
              className="settings-select"
              disabled={loadingModels[formData.activeProviderId]}
            >
              <option value="">Default model</option>
              {availableModels[formData.activeProviderId]?.map(model => (
                <option key={model.id} value={model.id}>
                  {model.id}{model.description && ` - ${model.description}`}
                </option>
              ))}
            </select>
            <p className="settings-hint">
              Leave as "Default model" to use the provider's recommended model.
            </p>
          </div>
        </section>

        <section className="settings-section">
          <h2 className="settings-section-title">Embedding Model</h2>
          <p className="settings-section-description">
            Choose the embedding model for semantic search. Smaller models are faster but may be less accurate.
          </p>

          <div className="settings-field">
            <label className="settings-label" htmlFor="embedding-model">
              Model
            </label>
            <select
              id="embedding-model"
              value={formData.embeddingModel}
              onChange={(e) => handleInputChange('embeddingModel', e.target.value)}
              className="settings-select"
            >
              <option value="bge-base">
                BAAI/bge-base-en-v1.5 (768 dim) - Best quality, slower
              </option>
              <option value="specter">
                SPECTER (768 dim) - Optimized for scientific papers
              </option>
              <option value="minilm-l6">
                all-MiniLM-L6-v2 (384 dim) - Good quality, faster
              </option>
              <option value="minilm-l3">
                paraphrase-MiniLM-L3-v2 (384 dim) - Moderate quality, fastest
              </option>
            </select>
            <p className="settings-hint settings-warning">
               Changing the embedding model requires re-indexing your library. To preserve existing embeddings and try a different model, create a new profile instead. Each profile maintains separate embeddings and settings.
            </p>
          </div>
        </section>

        <section className="settings-section">
          <h2 className="settings-section-title">Provider Configuration</h2>
          <p className="settings-section-description">
            Configure your LLM providers. Enable the ones you want to use and provide credentials.
          </p>

          {availableProviders.map(provider => {
            const config = formData.providers[provider.id];
            const validation = providerValidation[provider.id];
            const isValidating = validatingProvider === provider.id;

            return (
              <div key={provider.id} className="provider-config-card">
                <div className="provider-header">
                  <label className="provider-toggle">
                    <input
                      type="checkbox"
                      checked={config?.enabled || false}
                      onChange={(e) => handleProviderEnabledChange(provider.id, e.target.checked)}
                    />
                    <span className="provider-name">{provider.label}</span>
                  </label>
                  {validation && (
                    <span className={`provider-status ${validation.valid ? 'valid' : 'invalid'}`}>
                      {validation.valid ? ' Connected' : ' ' + validation.message}
                    </span>
                  )}
                </div>

                {config?.enabled && (
                  <div className="provider-credentials">
                    {provider.requires_api_key && (
                      <div className="settings-field">
                        <label className="settings-label" htmlFor={`${provider.id}-api-key`}>
                          API Key
                        </label>
                        <Input
                          id={`${provider.id}-api-key`}
                          type={config.credentials.api_key === '***' ? 'text' : 'password'}
                          value={config.credentials.api_key || ''}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                            handleProviderCredentialChange(provider.id, 'api_key', e.target.value)
                          }
                          placeholder={config.credentials.api_key === '***' ? 'API key is set' : 'Enter API key'}
                          className="settings-input"
                        />
                      </div>
                    )}
                    
                    {provider.id === 'ollama' && (
                      <div className="settings-field">
                        <label className="settings-label" htmlFor="ollama-base-url">
                          Base URL
                        </label>
                        <Input
                          id="ollama-base-url"
                          type="text"
                          value={config.credentials.base_url || 'http://localhost:11434'}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                            handleProviderCredentialChange(provider.id, 'base_url', e.target.value)
                          }
                          className="settings-input"
                        />
                      </div>
                    )}

                    <Button
                      onClick={() => validateProvider(provider.id)}
                      variant="secondary"
                      disabled={isValidating}
                    >
                      {isValidating ? 'Testing...' : 'Test Connection'}
                    </Button>
                  </div>
                )}
              </div>
            );
          })}
        </section>

        <section className="settings-section">
          <h2 className="settings-section-title">Zotero Configuration</h2>
          <p className="settings-section-description">
            Configure the path to your Zotero library database.
          </p>

          <div className="settings-field">
            <label className="settings-label" htmlFor="zotero-path">
              Zotero Database Path
            </label>
            <Input
              id="zotero-path"
              type="text"
              value={formData.zoteroPath}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('zoteroPath', e.target.value)}
              placeholder="/Users/username/Zotero/zotero.sqlite"
              className="settings-input"
            />
            <p className="settings-hint">
              Path to your zotero.sqlite database file.
            </p>
          </div>

          <div className="settings-field">
            <label className="settings-label" htmlFor="chroma-path">
              Vector Database Path
            </label>
            <Input
              id="chroma-path"
              type="text"
              value={formData.chromaPath}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('chromaPath', e.target.value)}
              placeholder="/Users/username/.zotero-llm/chroma/user-1"
              className="settings-input"
            />
            <p className="settings-hint">
              Path where the ChromaDB vector database will be stored.
            </p>
          </div>
        </section>

        <div className="settings-actions">
          {saveSuccess && (
            <div className="settings-success">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Settings saved successfully
            </div>
          )}
          {saveError && (
            <div className="settings-error">
              {saveError}
            </div>
          )}
          <Button 
            onClick={handleSave} 
            disabled={saving}
            variant="primary"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
          <Button 
            onClick={() => navigate('/')} 
            variant="secondary"
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
