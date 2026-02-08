import time
import requests
from pathlib import Path
from rubpy.bot import BotClient, filters
from rubpy.bot.models import Update

# ------------------------------
# 🔑 توکن‌ها
# ------------------------------
RUBIKA_TOKEN = "FHHFJ0OJMZILNKKTVETBTZOSVHFKDPHKOTCPRFPYYCAVLBLCPFBQGASLYKKMAIUY"
GROQ_API_KEY = "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"  # ← از https://console.groq.com
HF_TOKEN = "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"       # ← از https://huggingface.co/settings/tokens

# ------------------------------
# 🧠 چت با Groq
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
        return "❌ خطا در دریافت پاسخ چت."
    except Exception as e:
        return f"⚠️ خطا چت: {str(e)}"

# ------------------------------
# 🖼️ تصویر با Hugging Face
# ------------------------------
def ai_image(prompt: str) -> str | None:
    try:
        r = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt},
            timeout=90
        )
        if r.status_code == 200:
            Path("imgs").mkdir(exist_ok=True)
            img_path = f"imgs/miai1_{int(time.time())}.png"
            with open(img_path, "wb") as f:
                f.write(r.content)
            return img_path
        return None
    except Exception as e:
        print(f"[Image Error] {e}")
        return None

# ------------------------------
# 🤖 تشخیص چت خصوصی
# ------------------------------
def is_private(update: Update) -> bool:
    return update.object_guid == update.chat_id

# ------------------------------
# 🤖 ربات اصلی
# ------------------------------
app = BotClient(RUBIKA_TOKEN)

@app.on_update(filters.text)
async def handler(client: BotClient, update: Update):
    text = update.new_message.text or ""
    chat_id = update.chat_id
    in_private = is_private(update)

    # 🔹 در گروه: فقط با "miai"
    if not in_private and "miai" not in text.lower():
        return

    # 🔹 /start
    if in_private and text == "/start":
        await update.reply(
            "🤖 سلام! من **miai1** هستم.\n"
            "🧠 چت: Llama 3.1 از Groq\n"
            "🖼️ تصویر: Stable Diffusion 2.1\n"
            "مثال: `عکس/یک روبات در تخت جمشید`"
        )
        return

    # 🔹 دستور عکس (در هر دو حالت)
    if "عکس/" in text:
        try:
            if in_private:
                prompt = text.split("عکس/", 1)[1].strip()
            else:
                # در گروه، دنبال "عکس/" بگرد (حتی بعد از miai)
                lower_text = text.lower()
                if "عکس/" in lower_text:
                    prompt = text.split("عکس/", 1)[1].strip()
                else:
                    prompt = ""
            if prompt:
                await update.reply("🖼️ در حال ساخت تصویر...")
                img = ai_image(prompt)
                if img:
                    await client.send_file(chat_id=chat_id, file=img, type="Image")
                else:
                    await update.reply("❌ ساخت تصویر ناموفق بود.")
                return
        except:
            pass

    # 🔹 چت معمولی
    if in_private:
        prompt = text
    else:
        # در گروه، کل متن به عنوان سوال در نظر گرفته می‌شود
        prompt = text

    if not prompt.strip():
        return

    await update.reply("🧠 در حال پاسخ...")
    reply = ai_chat(prompt)
    await update.reply(reply)

# ------------------------------
if __name__ == "__main__":
    print("✅ ربات miai1 (چت + تصویر + گروه با miai) آنلاین شد!")
    app.run()