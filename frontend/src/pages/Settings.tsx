import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSettings } from '../contexts/SettingsContext';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import '../styles/settings.css';

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const { settings, updateSettings, loading } = useSettings();
  const [formData, setFormData] = useState(settings);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [apiKeyModified, setApiKeyModified] = useState({
    openai: false,
    anthropic: false,
  });

  useEffect(() => {
    setFormData(settings);
  }, [settings]);

  const handleInputChange = (field: keyof typeof formData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setSaveSuccess(false);
    setSaveError(null);
    
    // Track if API keys are being modified
    if (field === 'openaiApiKey') {
      setApiKeyModified(prev => ({ ...prev, openai: true }));
    } else if (field === 'anthropicApiKey') {
      setApiKeyModified(prev => ({ ...prev, anthropic: true }));
    }
  };

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

  const handleBrowseZotero = async () => {
    // In a real implementation, this would use a file picker dialog
    // For now, we'll just show a message
    alert('File picker would open here. For now, please enter the path manually.');
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
          <h2 className="settings-section-title">API Configuration</h2>
          <p className="settings-section-description">
            Configure your API keys for external language model providers. Leave blank to use local Ollama models only.
          </p>

          <div className="settings-field">
            <label className="settings-label" htmlFor="openai-key">
              OpenAI API Key
              <span className="settings-optional">Optional</span>
            </label>
            <Input
              id="openai-key"
              type={formData.openaiApiKey === '***' && !apiKeyModified.openai ? 'text' : 'password'}
              value={formData.openaiApiKey}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('openaiApiKey', e.target.value)}
              placeholder={formData.openaiApiKey === '***' ? 'API key is set (edit to change)' : 'sk-...'}
              className="settings-input"
            />
            <p className="settings-hint">
              Used for GPT-4, GPT-3.5, and other OpenAI models.{' '}
              <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">
                Get your API key
              </a>
            </p>
          </div>

          <div className="settings-field">
            <label className="settings-label" htmlFor="anthropic-key">
              Anthropic API Key
              <span className="settings-optional">Optional</span>
            </label>
            <Input
              id="anthropic-key"
              type={formData.anthropicApiKey === '***' && !apiKeyModified.anthropic ? 'text' : 'password'}
              value={formData.anthropicApiKey}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('anthropicApiKey', e.target.value)}
              placeholder={formData.anthropicApiKey === '***' ? 'API key is set (edit to change)' : 'sk-ant-...'}
              className="settings-input"
            />
            <p className="settings-hint">
              Used for Claude models.{' '}
              <a href="https://console.anthropic.com/account/keys" target="_blank" rel="noopener noreferrer">
                Get your API key
              </a>
            </p>
          </div>
        </section>

        <section className="settings-section">
          <h2 className="settings-section-title">Model Preferences</h2>
          <p className="settings-section-description">
            Choose your default language model for chat interactions.
          </p>

          <div className="settings-field">
            <label className="settings-label" htmlFor="default-model">
              Default Model
            </label>
            <select
              id="default-model"
              value={formData.defaultModel}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleInputChange('defaultModel', e.target.value)}
              className="settings-select"
            >
              <option value="ollama">Ollama (Local)</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="claude-3-opus">Claude 3 Opus</option>
              <option value="claude-3-sonnet">Claude 3 Sonnet</option>
              <option value="claude-3-haiku">Claude 3 Haiku</option>
            </select>
            <p className="settings-hint">
              This model will be used by default for all chat interactions.
            </p>
          </div>
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
            <div className="settings-input-group">
              <Input
                id="zotero-path"
                type="text"
                value={formData.zoteroPath}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange('zoteroPath', e.target.value)}
                placeholder="/Users/username/Zotero/zotero.sqlite"
                className="settings-input"
              />
              <Button onClick={handleBrowseZotero} variant="secondary">
                Browse
              </Button>
            </div>
            <p className="settings-hint">
              Path to your zotero.sqlite database file. Usually located in your Zotero data directory.
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
              Path where the ChromaDB vector database will be stored. Used for semantic search.
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
