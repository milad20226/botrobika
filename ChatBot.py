import time
import requests
from pathlib import Path
from rubpy.bot import BotClient, filters
from rubpy.bot.models import Update

# ------------------------------
# 🔑 توکن‌ها (جایگزین کن)
# ------------------------------
RUBIKA_TOKEN = "your token"
GROQ_API_KEY = "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"  # ← از https://console.groq.com
HF_TOKEN = "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"  # همین توکن قدیمی کار می‌کنه

# ------------------------------
# 🧠 چت: Groq (Llama 3.1 8B)
# ------------------------------
def ai_chat(prompt: str) -> str:
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 512,
                "temperature": 0.7
            },
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        else:
            return "❌ خطا در دریافت پاسخ."
    except Exception as e:
        return f"⚠️ خطا: {str(e)}"

# ------------------------------
# 🖼️ تصویر: Hugging Face (مدل پایدار)
# ------------------------------
def ai_image(prompt: str) -> str | None:
    try:
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt},
            timeout=60
        )
        if r.status_code == 200:
            img_path = f"imgs/ChatBot_{int(time.time())}.png"
            Path("imgs").mkdir(exist_ok=True)
            with open(img_path, "wb") as f:
                f.write(r.content)
            return img_path
        return None
    except:
        return None

# ------------------------------
# 🤖 رباتChatBot
# ------------------------------
app = BotClient(RUBIKA_TOKEN)

@app.on_update(filters.text)
async def handler(client: BotClient, update: Update):
    text = update.new_message.text or ""
    chat_id = update.chat_id

    if text == "/start":
        await update.reply("🤖 سلام! من **ChatBot** هستم.\n🧠 چت: Llama 3.1 از Groq\n🖼️ تصویر: Stable Diffusion 2.1 از Hugging Face\nمثال: `عکس/یک روبات در کاروان`")
    
    elif text.startswith("عکس/"):
        prompt = text[5:].strip()
        if prompt:
            await update.reply("🖼️ در حال ساخت تصویر... (10-30 ثانیه صبر کنید)")
            img = ai_image(prompt)
            if img:
                await client.send_file(chat_id=chat_id, file=img, type="Image")
            else:
                await update.reply("❌ نتونستم تصویر بسازم. لطفاً دوباره امتحان کنید.")
        else:
            await update.reply("لطفاً یک توصیف بنویسید، مثال: `عکس/یک اژدها در آسمان`")
    
    else:
        await update.reply("🧠 در حال پاسخ...")
        reply = ai_chat(text)
        await update.reply(reply)

# ------------------------------
if __name__ == "__main__":
    print("✅ ربات ChatBot با چت (Groq) + تصویر (Hugging Face) آنلاین شد!")
    app.run()