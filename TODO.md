# verso-content-manager TODO

## Completed

### Phase 1-10: Foundation to Documentation
- [x] Project structure, manifest, requirements, .gitignore
- [x] Core: config.py, vault.py, wp_client.py (HTTP/1.1 + Pragma)
- [x] Models: Pydantic models for blocks, articles, media
- [x] Articles: builder.py (blocks -> HTML), service.py (CRUD), routes.py
- [x] Media: optimizer.py (WebP), uploader.py, routes.py
- [x] SEO: categories/tags management
- [x] Templates: presse, pathologie, outil
- [x] Main app: FastAPI + dashboard + health
- [x] Tests: integration + unit tests per module
- [x] Docs: API.md, ARCHITECTURE.md

### Phase 11: Content Publishing (article-writer integration)
- [x] WrittenContent models (RedactionContext, WrittenSection, etc.)
- [x] Dropbox image download (API + fallback dl=1)
- [x] Publishing orchestration service
- [x] POST /content/publish endpoint
- [x] Markdown to HTML conversion with citation removal

### Phase 12: Pipeline alignment (2026-09-27)
- [x] Fix heading hierarchy: h2 (section) -> h3 (sub) -> h4 (sub-sub)
- [x] Fix XSS: html.escape() on all user content in builder.py
- [x] Fix image captions resolution from SelectedImage objects
- [x] Add VersoArticleRequest model for structured verso format
- [x] Add POST /content/publish-verso endpoint
- [x] Move URLs from hardcoded to config/verso-content-manager.yaml
- [x] Add cron.json with daily-health-check
- [x] Add DIAGRAM.md (auto-generated)
- [x] Change port 8091 -> 8090 (conflict with onyx-ged)
- [x] Version auto-sync from manifest.json
- [x] Validate article status before WordPress API calls
- [x] asyncio.gather for parallel category/tag resolution
- [x] Update dashboard with article-writer integration panel
- [x] Update tests for new service signatures

### article-writer side (2026-09-27)
- [x] Add src/verso_formatter.py (heading shift, excerpt, category mapping)
- [x] Add GET /write/contents/{id}/verso endpoint
- [x] Update API.md and ARCHITECTURE.md

## In Progress

(none)

## Pending

### Testing
- [ ] End-to-end test with real article-writer content (Zotero + images)
- [ ] Verify Dropbox image download + WebP optimization in production
- [ ] Load testing with large articles (10+ sections, multiple images)

### Future Enhancements
- [ ] Article scheduling (future publication dates)
- [ ] Media library browser in dashboard
- [ ] Bulk operations (CSV/JSON import)
- [ ] Article revision tracking
- [ ] Live preview before publishing

## Architecture Notes

### Heading Hierarchy
- WordPress post title: h1 (theme-managed)
- Section titles: h2
- Sub-headings in content (## shifted to ###): h3
- Sub-sub-headings (### shifted to ####): h4

### Pipeline
```
article-writer                    verso-content-manager              WordPress
GET /write/contents/{id}/verso -> POST /content/publish-verso    -> verso-vet.com
     (structured format)              (images + HTML + publish)      (draft/publish)
```

### Port
- Production: 8090 on OnyxAxon (10.0.0.21)
- Previously 8091 (now used by onyx-ged)

## Last Updated

2026-09-27 - Phase 12: Pipeline alignment with article-writer

