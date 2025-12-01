# Contributing to Zotero LLM Plugin

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. **Fork and clone** the repository
2. **Run setup**: `./setup.sh`
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Make changes** and test locally
5. **Submit a pull request**

## Development Setup

See [SETUP.md](SETUP.md) for detailed installation instructions.

Quick start:
```bash
./setup.sh
source .venv/bin/activate
uvicorn backend.main:app --reload  # Terminal 1
cd frontend && npm run dev          # Terminal 2
```

## Code Style

### Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings for functions and classes
- Run tests before committing

### TypeScript/React
- Use TypeScript for type safety
- Follow React hooks best practices
- Use functional components
- Keep components focused and reusable

## Testing

```bash
# Python tests
source .venv/bin/activate
pytest backend/tests/

# Frontend tests (if available)
cd frontend
npm test
```

## Security and Privacy

**CRITICAL: Never commit sensitive data!**

Before committing, verify:
```bash
# Check what's staged
git status

# Review changes
git diff --staged

# Verify no sensitive files
git ls-files | grep -E '\.env$|settings\.json|api.key'
```

### Files to NEVER commit:
- `.env` with real values (use `.env.example` instead)
- `settings.json` with API keys
- `~/.zotero-llm/` directory contents
- Personal database paths
- Chat history or sessions
- API keys or credentials

### Always safe to commit:
- Source code changes
- Documentation updates
- Configuration templates (`.example` files)
- Test files (with mock data only)
- Setup scripts

See [SECURITY.md](SECURITY.md) for complete guidelines.

## Pull Request Process

1. **Update documentation** if adding features
2. **Add tests** for new functionality
3. **Verify .gitignore** excludes sensitive files
4. **Test locally** with your own Zotero library
5. **Write clear commit messages**:
   ```
   feat: Add support for new LLM provider
   fix: Resolve indexing crash on empty PDFs
   docs: Update setup instructions
   ```

6. **Submit PR** with:
   - Clear description of changes
   - Screenshots/GIFs for UI changes
   - Testing steps
   - Related issue numbers

## Project Structure

```
backend/          # FastAPI Python backend
  main.py         # API endpoints
  interface.py    # Chatbot logic
  vector_db.py    # ChromaDB interface
  model_providers/ # LLM provider implementations
  
frontend/         # React TypeScript frontend
  src/
    components/   # Reusable UI components
    features/     # Feature-specific components
    contexts/     # React context providers
    hooks/        # Custom React hooks
    
docs/             # Documentation
```

## Feature Requests

Open an issue with:
- Clear use case description
- Expected behavior
- Why it would be valuable
- Potential implementation approach

## Bug Reports

Include:
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version, Node version)
- Error messages or logs
- Screenshots if applicable

**DO NOT** include:
- API keys
- Personal file paths
- Chat history
- Full database dumps

## Areas for Contribution

### Backend
- New LLM provider integrations
- Improved RAG algorithms
- Better PDF parsing
- Metadata enrichment
- Performance optimizations

### Frontend
- UI/UX improvements
- New features (export, visualization)
- Accessibility enhancements
- Mobile responsiveness
- Dark mode improvements

### Documentation
- Setup guides
- API documentation
- User tutorials
- Translation to other languages

### Testing
- Unit tests
- Integration tests
- End-to-end tests
- Performance benchmarks

## Development Tips

### Using Test Data

```bash
# Create test profile
mkdir -p ~/.zotero-llm/profiles/test/chroma

# Use test Zotero library
export ZOTERO_DB_PATH=/path/to/test/library.sqlite
```

### Debugging

```bash
# Backend logs
# Watch Terminal 1 where uvicorn is running

# Frontend logs
# Open browser DevTools Console

# Check profile data
cat ~/.zotero-llm/profiles/default/settings.json
```

### Hot Reloading

- Backend: `--reload` flag auto-restarts on changes
- Frontend: Vite auto-refreshes on saves

## Questions?

- Check existing [documentation](docs/)
- Search [issues](https://github.com/aahepburn/zotero-llm-plugin/issues)
- Open a discussion or new issue
- Join our community (link TBD)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for helping make Zotero LLM Plugin better! 🎉
