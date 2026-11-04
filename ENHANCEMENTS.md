# Future Enhancements

## Deployment
- [ ] Evaluate and deploy backend service — Render (free tier, simple) vs Fly.io (more control) vs AWS (scalable but overkill for personal use)
- [ ] Deploy frontend to Vercel

## Ingredient Input
- [ ] Support image upload of ingredient list — OCR the label photo instead of manual paste (e.g. Google Vision API or Tesseract)

## Data & Intelligence
- [ ] Scheduled sync / scraping from Open Beauty Facts to enrich local ingredient data
- [ ] RAG over ingredient/product data for smarter AI recommendations (Supabase pgvector)

## Auth & Multi-user
- [ ] Add Supabase Auth if sharing the app with others
- [ ] User-level DB storage (profile, stash, reactions per user)
