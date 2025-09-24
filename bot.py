import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import Config
from student_flow import (
    start_student,
    handle_student_name,
    handle_student_phone,
    handle_student_level,
    handle_student_subject,
    handle_student_budget,
    cancel as student_cancel,
    student_extra_handlers,
)
from tutor_flow import (
    start_tutor,
    handle_tutor_name,
    handle_tutor_phone,
    handle_tutor_subjects,
    handle_tutor_rate,
    handle_tutor_experience,
    cancel as tutor_cancel,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Mimi ni Mwalimu", "Mimi ni Mwanafunzi"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Karibu *ElimuBot!*\n\n"
        "Tafadhali chagua moja ya chaguo:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


def main():
    app = Application.builder().token(Config.BOT_TOKEN).build()

    # --- Tutor registration flow ---
    tutor_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Mimi ni Mwalimu$"), start_tutor)
        ],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tutor_name)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tutor_phone)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tutor_subjects)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tutor_rate)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tutor_experience)],
        },
        fallbacks=[CommandHandler("cancel", tutor_cancel)],
    )

    # --- Student onboarding flow ---
    student_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Mimi ni Mwanafunzi$"), start_student)
        ],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_name)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_phone)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_level)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_subject)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_student_budget)],
        },
        fallbacks=[CommandHandler("cancel", student_cancel)],
    )

    # --- Register handlers ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(tutor_conv)
    app.add_handler(student_conv)

    # Add extra inline button handlers from student flow (Chagua Mwalimu)
    for h in student_extra_handlers:
        app.add_handler(h)

    logger.info("✅ Bot started successfully...")
    app.run_polling()


if __name__ == "__main__":
    main()
