from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import profile, products, ingredients, reactions, culprit, wishlist, chat

app = FastAPI(title="Dermé API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(products.router)
app.include_router(ingredients.router)
app.include_router(reactions.router)
app.include_router(culprit.router)
app.include_router(wishlist.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
