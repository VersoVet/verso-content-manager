# verso-content-manager TODO

## ✅ Completed

### Phase 1: Foundation
- [x] Create project structure
- [x] Create manifest.json with correct configuration
- [x] Create requirements.txt with all dependencies
- [x] Create .gitignore
- [x] Create CLAUDE.md (auto-generated)

### Phase 2: Core Infrastructure
- [x] Configure config.py with all constants
- [x] Implement vault.py for secret management
- [x] Implement wp_client.py with WordPress REST API client
- [x] Fix HTTP/1.1 + Pragma headers for Cloudflare bypass

### Phase 3: Models & Validation
- [x] Define Pydantic models for all block types
- [x] Define ArticleRequest and ArticleResponse
- [x] Define MediaUploadRequest and MediaResponse
- [x] Type validation with Pydantic

### Phase 4: Article Module
- [x] Implement builder.py (blocks → HTML)
- [x] Implement service.py (CRUD operations)
- [x] Implement routes.py (FastAPI endpoints)
- [x] Test all block types

### Phase 5: Media Module
- [x] Implement optimizer.py (Pillow image processing)
- [x] Implement uploader.py (WordPress media upload)
- [x] Implement routes.py (media endpoints)
- [x] WebP conversion working

### Phase 6: SEO Module
- [x] Implement service.py (category/tag management)
- [x] Implement routes.py (SEO endpoints)
- [x] Name-to-ID conversion utilities

### Phase 7: Templates Module
- [x] Implement service.py (template loading)
- [x] Implement routes.py (template endpoints)
- [x] Create presse.json template
- [x] Create pathologie.json template
- [x] Create outil.json template

### Phase 8: Main Application
- [x] Create src/main.py with FastAPI app
- [x] Implement dashboard HTML
- [x] Implement health endpoint
- [x] Include all module routers

### Phase 9: Testing
- [x] Create test_integration.py
- [x] Create test_articles.py
- [x] Create conftest.py with fixtures
- [x] Test block builders

### Phase 10: Documentation
- [x] Create API.md with endpoint documentation
- [x] Create ARCHITECTURE.md with design details
- [x] Create TODO.md (this file)

## 🔄 In Progress

- [x] Create src/modules/media/service.py
- [x] Create test_media.py, test_seo.py, test_templates.py
- [x] Improve docstring coverage (9 functions)
- [x] Update manifest.json with lifecycle, dashboard, repository
- [x] Add OnyxClient.start/stop in lifespan
- [ ] Code validation (ruff, mypy)
- [ ] Running pytest
- [ ] Forge validator (phase 2)
- [ ] Git commit and review

## 📋 Pending

### Code Quality
- [ ] Run `ruff check src/ --fix`
- [ ] Run `ruff format src/`
- [ ] Run `mypy src/ --strict`
- [ ] Achieve 60%+ docstring coverage

### Testing
- [ ] Run `pytest tests/` -x -q
- [ ] Verify all 18 validation phases pass
- [ ] Manual dashboard testing

### Deployment
- [ ] Git commit with proper message
- [ ] Push to dev branch
- [ ] Run Forge validation
- [ ] Review and deploy

## 📝 Implementation Notes

### Architecture Decisions
1. **HTTP/1.1 + Pragma Headers**: Required to bypass Cloudflare caching issues with WordPress auth
2. **WebP Format**: Reduces image sizes 30-50% while maintaining quality
3. **Async Operations**: All I/O is async via httpx and FastAPI
4. **Dashboard HTML**: Single-file embedded HTML + JavaScript for simplicity
5. **Block-based Content**: Flexible, composable content structure

### Key Features
- ✅ Article creation from JSON blocks
- ✅ Image optimization and WebP conversion
- ✅ Category and tag management
- ✅ Template system (presse, pathologie, outil)
- ✅ Interactive dashboard
- ✅ API + dashboard UIs

### Known Limitations
- Dashboard doesn't support full article editing (read-only view)
- No article scheduling/future publishing
- No bulk operations
- Templates are JSON files (not database)

### Security Considerations
- ✅ Credentials via Vault (not hardcoded)
- ✅ No credentials in environment variables
- ✅ Input validation via Pydantic
- ✅ No sensitive info in error responses
- ✅ HTTPS for WordPress REST API

## 🎯 Final Checklist

- [ ] Code compiles without errors
- [ ] All imports resolve correctly
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Tests pass (pytest)
- [ ] Docstrings complete (80%+)
- [ ] API.md fully documented
- [ ] ARCHITECTURE.md complete
- [ ] No credentials in code
- [ ] .gitignore properly configured
- [ ] manifest.json valid
- [ ] Forge validator passes all 18 phases
- [ ] Dashboard loads without errors
- [ ] Health endpoint works
- [ ] Ready for deployment

## 📅 Last Updated

2025-02-15 - Initial skill development complete
