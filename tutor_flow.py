# tutor_flow.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import ElimuDatabase
from config import Config

# States for tutor registration
(
    TUTOR_NAME,
    TUTOR_PHONE,
    TUTOR_SUBJECTS,
    TUTOR_RATE,
    TUTOR_EXPERIENCE,
) = range(5)

db = ElimuDatabase()

# --- Step 1: Tutor starts registration ---
async def start_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧑‍🏫 <b>Karibu Mwalimu!</b> Tafadhali andika jina lako kamili.", parse_mode="HTML")
    return TUTOR_NAME

# --- Step 2: Get full name ---
async def handle_tutor_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("📱 Sawa, sasa andika nambari yako ya simu (mfano: 0712345678).", parse_mode="HTML")
    return TUTOR_PHONE

# --- Step 3: Get phone ---
async def handle_tutor_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📚 Ni masomo gani unayofundisha? (andika kwa koma, mfano: Math, Physics, English)", parse_mode="HTML")
    return TUTOR_SUBJECTS

# --- Step 4: Get subjects ---
async def handle_tutor_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subjects"] = update.message.text
    await update.message.reply_text("💵 Kiwango chako kwa saa moja ni kiasi gani? (mfano: 600)", parse_mode="HTML")
    return TUTOR_RATE

# --- Step 5: Get rate ---
async def handle_tutor_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["hourly_rate"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("⚠️ Tafadhali andika nambari sahihi ya kiwango. Mfano: 600", parse_mode="HTML")
        return TUTOR_RATE

    await update.message.reply_text("⌛ Umefundisha kwa muda gani? (mfano: 3 years)", parse_mode="HTML")
    return TUTOR_EXPERIENCE

# --- Step 6: Get experience and save tutor ---
async def handle_tutor_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text

    # Save tutor to database
    db.save_tutor(
        telegram_id=update.effective_user.id,
        full_name=context.user_data["full_name"],
        phone=context.user_data["phone"],
        subjects=context.user_data["subjects"],
        hourly_rate=context.user_data["hourly_rate"],
        experience=context.user_data["experience"],
    )

    # Confirmation summary
    summary = f"""
<b>📋 Taarifa zako:</b>
• <b>Jina:</b> {context.user_data['full_name']}
• <b>Simu:</b> {context.user_data['phone']}
• <b>Masomo:</b> {context.user_data['subjects']}
• <b>Kiwango:</b> KES {context.user_data['hourly_rate']}/saa
• <b>Uzoefu:</b> {context.user_data['experience']}
"""
    await update.message.reply_text(summary, parse_mode="HTML")

    # Payment pitch
    payment_info = f"""
🎉 <b>Hongera Mwalimu {context.user_data['full_name']}!</b>\n
Umefanikisha kujisajili kikamilifu.\n\n
🚀 Wanafunzi wengi wanatafuta walimu bora kama wewe kupitia ElimuBot.\n\n
<b>Kwa ada ndogo ya usajili ya KES {Config.TUTOR_SUBSCRIPTION_FEE}</b> tunakusaidia:\n
• 🚀 Kila siku kupata wanafunzi waliolipia mafunzo tayari\n
• 📲 Kuunganishwa moja kwa moja kupitia Telegram\n
• 🔒 Mfumo salama wa malipo na kuingiza kipato cha kando\n\n
💳 <b>Lipia sasa kupitia M-Pesa:</b>\n
• <b>Till Number:</b> {Config.MPESA_TILL}\n\n
⏰ Baada ya malipo, tuma screenshot kwa admin au  \n piga simu: 254731071276 au tumia command: <code>/checkpayment</code>
"""
    await update.message.reply_text(payment_info, parse_mode="HTML")


    # Debug log
    print(f"Tutor registered: {context.user_data['full_name']} ({update.effective_user.id})")

    return ConversationHandler.END

# --- Cancel handler ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Umesitisha usajili. Unaweza kuanza tena kwa kutumia /start.", parse_mode="HTML")
    return ConversationHandler.END
