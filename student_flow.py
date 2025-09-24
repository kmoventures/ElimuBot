# student_flow.py
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from database import ElimuDatabase

# States for student onboarding
(
    STUDENT_NAME,
    STUDENT_PHONE,
    STUDENT_LEVEL,
    STUDENT_SUBJECT,
    STUDENT_BUDGET,
) = range(5)

db = ElimuDatabase()


# --- Step 1: Start ---
async def start_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Karibu ElimuBot! Tafadhali andika jina lako kamili.")
    return STUDENT_NAME


# --- Step 2: Get name ---
async def handle_student_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("📱 Sawa, sasa andika nambari yako ya simu (mfano: 0712345678).")
    return STUDENT_PHONE


# --- Step 3: Get phone ---
async def handle_student_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    keyboard = [
        ["🎨 ECDE / Pre-Primary", "✏️ Primary (Grade 1–6)"],
        ["📘 Junior Secondary (Grade 7–9)", "📚 Secondary (Form 1–4)"],
        ["🎓 College / Skills Training"],
    ]
    await update.message.reply_text(
        "📚 Sawa! Hebu tuanze...\n\n👉 Unahitaji msaada kwa kiwango gani?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return STUDENT_LEVEL


# --- Step 4a: Get level ---
async def handle_student_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    level = update.message.text
    context.user_data["level"] = level

    # Map subjects dynamically
    subjects_map = {
        "🎨 ECDE / Pre-Primary": ["Numbers", "Reading", "Writing", "Drawing", "Environmental"],
        "✏️ Primary (Grade 1–6)": ["Math", "English", "Kiswahili", "Environmental", "Hygiene", "CRE/IRE", "Arts & Music"],
        "📘 Junior Secondary (Grade 7–9)": ["Math", "English", "Kiswahili", "Integrated Science", "Social Studies", "Business Studies", "Agriculture"],
        "📚 Secondary (Form 1–4)": ["Math", "Physics", "Chemistry", "Biology", "Geography", "History", "CRE", "Business", "Literature", "English", "Kiswahili"],
        "🎓 College / Skills Training": ["Computer Packages", "Coding", "Graphic Design", "Driving", "French", "German", "Chinese"],
    }

    subjects = subjects_map.get(level, ["General Studies"])
    keyboard = [[s] for s in subjects]

    await update.message.reply_text(
        f"📘 Umechagua *{level}*. Sasa chagua somo unalohitaji msaada:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return STUDENT_SUBJECT


# --- Step 4b: Get subject ---
async def handle_student_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text
    await update.message.reply_text("💵 Bajeti yako kwa saa moja ni kiasi gani? (mfano: 500)")
    return STUDENT_BUDGET


# --- Step 5: Get budget, save student, show tutors ---
async def handle_student_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["budget"] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("⚠️ Tafadhali andika nambari sahihi. Mfano: 500")
        return STUDENT_BUDGET

    # Save student to DB
    db.save_student(
        telegram_id=update.effective_user.id,
        full_name=context.user_data["full_name"],
        phone=context.user_data["phone"],
        level=context.user_data["level"],
        subject=context.user_data["subject"],
        budget=context.user_data["budget"],
    )

    # Fetch tutors from DB
    tutors = db.get_matching_tutors(
        subject=context.user_data["subject"], budget=context.user_data["budget"], limit=3
    )

    # Student summary
    summary = f"""
✅ Asante {context.user_data['full_name']}!  

📋 *Taarifa zako:*  
• Jina: {context.user_data['full_name']}  
• Simu: {context.user_data['phone']}  
• Kiwango: {context.user_data['level']}  
• Somo: {context.user_data['subject']}  
• Bajeti: KES {context.user_data['budget']}  
"""
    await update.message.reply_text(summary, parse_mode="Markdown")

    if not tutors:
        await update.message.reply_text("😔 Pole, hakuna walimu wanaolingana na vigezo hivi kwa sasa.")
        return ConversationHandler.END

    # Build tutor list + buttons
    text = "🎉 Nimekupatia walimu 3 wanaofaa:\n\n"
    keyboard = []
    for i, (name, rate, experience, telegram_id) in enumerate(tutors, start=1):
        text += f"{i}️⃣ {name} – {experience} exp – KES {rate}/hr\n"
        keyboard.append([InlineKeyboardButton(f"Chagua {name}", url=f"tg://user?id={telegram_id}", callback_data=f"choose_{telegram_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text + "\n👉 Bonyeza *Chagua Mwalimu* kuunganishwa moja kwa moja.",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

    return ConversationHandler.END


# --- Notify tutor if chosen ---
async def notify_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tutor_id = int(query.data.split("_")[1])
    student_name = context.user_data.get("full_name", "Mwanafunzi")

    try:
        await context.bot.send_message(
            chat_id=tutor_id,
            text=f"📢 Habari Mwalimu! 🎓\n\nMwanafunzi *{student_name}* ana nia ya huduma zako. Tafadhali wasiliana naye moja kwa moja.",
            parse_mode="Markdown",
        )
    except Exception as e:
        print(f"Failed to notify tutor {tutor_id}: {e}")


# --- Cancel handler ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Umesitisha usajili. Unaweza kuanza tena kwa kutumia /start.")
    return ConversationHandler.END


# Export extra handlers (for inline callbacks)
student_extra_handlers = [
    CallbackQueryHandler(notify_tutor, pattern="^choose_"),
]
