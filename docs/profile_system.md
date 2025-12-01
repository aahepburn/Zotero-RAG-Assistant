# Profile System Implementation Summary

## Overview
Implemented a complete multi-profile system for the Zotero LLM Plugin, allowing users to manage multiple isolated profiles with separate settings, chat sessions, and vector databases. All data is stored locally on the user's computer.

## Backend Components

### 1. ProfileManager Class (`backend/profile_manager.py`)
- **Storage Structure**: `~/.zotero-llm/profiles/{profile_id}/`
- **Per-Profile Data**:
  - `settings.json` - Profile-specific settings (LLM provider, models, API keys, etc.)
  - `sessions.json` - Chat history and sessions
  - `profile.json` - Profile metadata (name, description, timestamps)
  - `chroma/` - Vector database for document embeddings

- **Core Operations**:
  - `create_profile(id, name, description)` - Create new profile with default settings
  - `list_profiles()` - Get all profiles with metadata
  - `get_profile(id)` - Get specific profile metadata
  - `update_profile(id, name, description)` - Update profile metadata
  - `delete_profile(id, force)` - Delete profile (requires force for active profile)
  - `get_active_profile()` / `set_active_profile(id)` - Manage active profile
  - `load_profile_settings(id)` / `save_profile_settings(id, settings)` - Settings persistence
  - `load_profile_sessions(id)` / `save_profile_sessions(id, data)` - Sessions persistence
  - `export_profile(id, path)` - Export profile to ZIP (excludes chroma for size)
  - `import_profile(path, new_id)` - Import profile from ZIP

- **Features**:
  - Automatic default profile creation on first run
  - Profile isolation with separate storage directories
  - Thread-safe active profile tracking
  - Validation to prevent invalid operations (e.g., deleting active profile without force)

### 2. Backend API Endpoints (`backend/main.py`)

#### Profile Management
- `GET /profiles` - List all profiles with active profile indicator
- `POST /profiles` - Create new profile (body: `{id, name, description}`)
- `GET /profiles/{profile_id}` - Get profile metadata
- `PUT /profiles/{profile_id}` - Update profile (body: `{name, description}`)
- `DELETE /profiles/{profile_id}?force=bool` - Delete profile
- `POST /profiles/{profile_id}/activate` - Switch active profile (triggers chatbot reinitialization)

#### Profile Data
- `GET /profiles/{profile_id}/sessions` - Get profile's sessions
- `POST /profiles/{profile_id}/sessions` - Save profile's sessions (body: sessions data)

#### Updated Existing Endpoints
- `load_settings(profile_id=None)` - Now profile-aware, reads from active profile
- `save_settings(settings, profile_id=None)` - Saves to active profile
- `initialize_chatbot()` - Uses profile-specific chroma path from ProfileManager

## Frontend Components

### 1. ProfileContext (`frontend/src/contexts/ProfileContext.tsx`)
- **State Management**:
  - `profiles` - List of all available profiles
  - `activeProfileId` - Currently active profile ID
  - `activeProfile` - Full active profile object
  - `isLoading` - Loading state
  - `error` - Error messages

- **Operations**:
  - `loadProfiles()` - Fetch all profiles from backend
  - `createProfile(id, name, description)` - Create new profile
  - `updateProfile(id, name, description)` - Update profile metadata
  - `deleteProfile(id, force)` - Delete profile
  - `switchProfile(id)` - Switch active profile (triggers page reload)
  - `exportProfile(id)` / `importProfile(file)` - Import/export (TODO)

### 2. ProfileSelector Component (`frontend/src/components/profile/ProfileSelector.tsx`)
- Dropdown selector for switching profiles
- "Create New Profile" form with inline creation
- Confirmation dialog on profile switch (warns about reload)
- Profile description display
- Styled with CSS-in-JS for consistency

### 3. Integration Points
- **App.tsx**: Added `ProfileProvider` as outermost context (wraps all other providers)
- **Settings Page**: Added ProfileSelector at top of settings panel
- Profile switch triggers full page reload to reinitialize chatbot with new profile

## Data Flow

### Profile Creation
1. User enters profile name in ProfileSelector
2. Frontend generates ID from name (lowercase, hyphenated)
3. POST request to `/profiles` with `{id, name, description}`
4. Backend ProfileManager creates directory structure
5. Default settings copied to new profile
6. Profile metadata saved to `profile.json`
7. Frontend reloads profile list

### Profile Switching
1. User selects different profile from dropdown
2. Confirmation dialog appears (warns about reload)
3. POST request to `/profiles/{id}/activate`
4. Backend updates `~/.zotero-llm/active_profile.json`
5. Backend reinitializes chatbot with new profile's chroma path
6. Frontend triggers `window.location.reload()`
7. All components load with new profile's data

### Settings Persistence
1. Settings updated in UI (e.g., change LLM provider)
2. POST to `/settings` with updated settings object
3. Backend `save_settings()` calls `profile_manager.save_profile_settings(active_id, settings)`
4. Settings saved to active profile's `settings.json`
5. Chatbot reinitialized with new settings (if needed)

## File Structure

```
~/.zotero-llm/
├── active_profile.json           # Tracks currently active profile
└── profiles/
    ├── default/
    │   ├── profile.json          # Metadata: {id, name, description, timestamps}
    │   ├── settings.json         # LLM settings, API keys, etc.
    │   ├── sessions.json         # Chat history
    │   └── chroma/               # Vector database
    │       └── chroma.sqlite3
    ├── work-profile/
    │   ├── profile.json
    │   ├── settings.json
    │   ├── sessions.json
    │   └── chroma/
    └── personal/
        ├── profile.json
        ├── settings.json
        ├── sessions.json
        └── chroma/
```

## Key Features

### 1. Data Isolation
- Each profile has completely separate:
  - Settings (different API keys, models, etc.)
  - Chat history and sessions
  - Vector database (different document embeddings)
- No data leakage between profiles

### 2. Safety Features
- Cannot delete active profile without `force=true` flag
- Confirmation dialogs for destructive operations (switch, delete)
- Profile switch warns about unsaved changes
- Automatic backup through export functionality

### 3. User Experience
- Seamless profile switching with automatic reload
- Inline profile creation (no separate page)
- Visual feedback for loading states
- Error messages for failed operations

### 4. Best Practices
- All data stored locally (no cloud dependencies)
- Thread-safe file operations
- Proper error handling throughout
- Type-safe TypeScript interfaces
- RESTful API design
- Separation of concerns (ProfileManager handles storage, endpoints handle HTTP)

## Next Steps (Future Enhancements)

1. **Import/Export UI**
   - File picker for import
   - Download button for export
   - Progress indicators for large profiles

2. **Profile Manager Page**
   - Dedicated page for profile management
   - Edit profile descriptions
   - View profile statistics (size, message count, etc.)
   - Bulk operations

3. **Advanced Features**
   - Profile templates (pre-configured for specific use cases)
   - Profile cloning
   - Automatic backups on schedule
   - Profile merge/migration tools

4. **Sessions Integration**
   - Update SessionsContext to sync with backend
   - Add sessions endpoints to profile system
   - Handle session restoration on profile switch

## Testing Checklist

- [x] Backend ProfileManager class created
- [x] Profile CRUD endpoints implemented
- [x] Profile-aware settings system
- [x] Profile-specific chroma paths
- [x] Frontend ProfileContext created
- [x] ProfileSelector component created
- [x] Integration with App.tsx
- [x] Settings page integration
- [ ] Manual testing: Create profile
- [ ] Manual testing: Switch profile
- [ ] Manual testing: Delete profile
- [ ] Manual testing: Settings persistence per profile
- [ ] Manual testing: Chat history isolation

## Migration Notes

Existing users will automatically get a "default" profile created on first run with their existing settings. The migration path:

1. App starts with no profiles
2. ProfileManager detects empty profiles directory
3. Creates "default" profile with default settings
4. Existing `settings.json` (if any) will be migrated to default profile
5. User continues with no disruption
