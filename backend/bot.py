import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# per-chat conversation history for Claude context
chat_histories: dict[int, list[dict]] = {}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def api(method: str, path: str, **kwargs):
    url = f"{API_BASE}{path}"
    response = httpx.request(method, url, timeout=30, **kwargs)
    response.raise_for_status()
    return response.json()


# ─── Commands ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! I'm Dermé 🌿\n\n"
        "Here's what I can do:\n"
        "/add <incidecoder_url> — add a product to your stash\n"
        "/stash — view your current stash\n"
        "/wishlist — view your wishlist\n"
        "/culprit — find common irritants across reacted products\n\n"
        "Or just chat with me for skincare advice!"
    )


async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide an incidecoder URL.\n"
            "Usage: /add https://incidecoder.com/products/..."
        )
        return

    url = context.args[0]
    await update.message.reply_text("Fetching product... ⏳")

    try:
        product = api("POST", "/products/from-url", json={"url": url})
        await update.message.reply_text(
            f"✅ Added to stash!\n\n"
            f"*{product['name']}*\n"
            f"Brand: {product.get('brand') or 'Unknown'}\n"
            f"Status: {product['status']}",
            parse_mode="Markdown",
        )
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(f"❌ Failed to add product: {e.response.text}")
    except Exception as e:
        await update.message.reply_text(f"❌ Something went wrong: {e}")


async def stash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        products = api("GET", "/products")
        if not products:
            await update.message.reply_text("Your stash is empty. Use /add to add a product!")
            return

        lines = []
        for p in products:
            rating = f"{'⭐' * p['rating']}" if p.get("rating") else "unrated"
            reaction = " ⚠️" if p["had_reaction"] else ""
            lines.append(f"• *{p['name']}* — {rating}{reaction}")

        await update.message.reply_text(
            "🧴 *Your Stash*\n\n" + "\n".join(lines),
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not fetch stash: {e}")


async def wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        items = api("GET", "/wishlist")
        if not items:
            await update.message.reply_text("Your wishlist is empty.")
            return

        lines = [f"• *{item['name']}*{' — ' + item['brand'] if item.get('brand') else ''}"
                 for item in items]
        await update.message.reply_text(
            "✨ *Your Wishlist*\n\n" + "\n".join(lines),
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not fetch wishlist: {e}")


async def culprit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        suspects = api("GET", "/culprit")
        if not suspects:
            await update.message.reply_text(
                "No culprits found. Log reactions to your products first!"
            )
            return

        lines = [
            f"• *{s['name']}* — found in {s['reacted_product_count']} reacted products"
            + (" 🚩" if s["is_flagged"] else "")
            for s in suspects
        ]
        await update.message.reply_text(
            "🔍 *Culprit Finder*\n\n" + "\n".join(lines),
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not run culprit finder: {e}")


# ─── Chat (everything else) ───────────────────────────────────────────────────

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    # maintain per-chat history
    history = chat_histories.get(chat_id, [])

    await update.message.reply_chat_action("typing")

    try:
        result = api("POST", "/chat", json={"message": user_message, "history": history})
        reply = result["response"]

        # update history
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        chat_histories[chat_id] = history[-20:]  # keep last 20 messages

        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ Could not reach AI: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_product))
    app.add_handler(CommandHandler("stash", stash))
    app.add_handler(CommandHandler("wishlist", wishlist))
    app.add_handler(CommandHandler("culprit", culprit))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Dermé bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
