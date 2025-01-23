from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
# from config import get_session
# from models import User
import datetime
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Временное хранилище данных для пользователя
user_data = {}

# Фиксированное количество дней отпуска
VACATION_DAYS = 20

async def inline_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Показать дни отпуска", callback_data="show_days")],
        [InlineKeyboardButton("Запрос отпуска", callback_data="request_vacation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # user_id = query.from_user.id
    # session = get_session()

    # try:
    if query.data == "show_days":
        # user = session.query(User).filter_by(id=user_id).first()
        # if user:
        #     await query.edit_message_text(f"У вас осталось {user.vacation_days} дней отпуска.")
        # else:
        await query.edit_message_text(f"У вас осталось {VACATION_DAYS} дней отпуска.")

    elif query.data == "request_vacation":
        keyboard = [
            [InlineKeyboardButton("Отпуск по дням", callback_data="vacation_by_days")],
            [InlineKeyboardButton("Отпуск на часы", callback_data="vacation_by_hours")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите тип отпуска:", reply_markup=reply_markup)

    # except Exception as e:
    #     logger.error(f"Ошибка при обработке запроса: {e}")
    #     await query.edit_message_text("Произошла ошибка. Попробуйте позже.")
    # finally:
    #     session.close()

async def vacation_by_days_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_data[query.from_user.id] = {"type": "by_days"}
    await query.edit_message_text("Введите дату начала отпуска (в формате ДД.ММ.ГГГГ):")

async def vacation_by_hours_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_data[query.from_user.id] = {"type": "by_hours"}
    await query.edit_message_text("Введите время начала отпуска (в формате ЧЧ:ММ):")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_input = update.message.text
    global VACATION_DAYS

    if user_id not in user_data:
        await update.message.reply_text("Пожалуйста, выберите действие сначала через /start.")
        return

    user_state = user_data[user_id]
    # session = get_session()

    try:
        if user_state["type"] == "by_days":
            if "start_date" not in user_state:
                try:
                    start_date = datetime.datetime.strptime(user_input, "%d.%m.%Y").date()
                    user_state["start_date"] = start_date
                    await update.message.reply_text("Введите дату окончания отпуска (в формате ДД.ММ.ГГГГ):")
                except ValueError:
                    await update.message.reply_text("Некорректный формат даты. Попробуйте снова (ДД.ММ.ГГГГ).")
            elif "end_date" not in user_state:
                try:
                    end_date = datetime.datetime.strptime(user_input, "%d.%m.%Y").date()
                    start_date = user_state["start_date"]

                    if end_date <= start_date:
                        await update.message.reply_text("Дата окончания должна быть позже даты начала. Попробуйте снова.")
                        return

                    user_state["end_date"] = end_date
                    days = (end_date - start_date).days + 1

                    # user = session.query(User).filter_by(id=user_id).first()
                    # if user and user.vacation_days >= days:
                    #     user.vacation_days -= days
                    #     session.commit()
                    if VACATION_DAYS >= days:
                        VACATION_DAYS -= days
                        await update.message.reply_text(f"Отпуск одобрен с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')} (всего {days} дней).")
                    else:
                        await update.message.reply_text("Недостаточно дней отпуска.")

                    del user_data[user_id]
                except ValueError:
                    await update.message.reply_text("Некорректный формат даты. Попробуйте снова (ДД.ММ.ГГГГ).")

        elif user_state["type"] == "by_hours":
            if "start_time" not in user_state:
                try:
                    start_time = datetime.datetime.strptime(user_input, "%H:%M").time()
                    user_state["start_time"] = start_time
                    await update.message.reply_text("Введите продолжительность отпуска в часах (число):")
                except ValueError:
                    await update.message.reply_text("Некорректный формат времени. Попробуйте снова (ЧЧ:ММ).")
            elif "duration" not in user_state:
                try:
                    duration = int(user_input)
                    if duration <= 0:
                        await update.message.reply_text("Продолжительность должна быть больше 0. Попробуйте снова.")
                        return

                    start_time = user_state["start_time"]
                    # Конвертируем часы в дни для списания отпуска
                    days = duration / 8  # Предполагаем 8-часовой рабочий день

                    # user = session.query(User).filter_by(id=user_id).first()
                    # if user and user.vacation_days >= days:
                    #     user.vacation_days -= days
                    #     session.commit()
                    if VACATION_DAYS >= days:
                        VACATION_DAYS -= days
                        await update.message.reply_text(f"Отпуск одобрен с {start_time.strftime('%H:%M')} на {duration} часов.")
                    else:
                        await update.message.reply_text("Недостаточно дней отпуска.")

                    del user_data[user_id]
                except ValueError:
                    await update.message.reply_text("Некорректный формат продолжительности. Введите число.")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
    # finally:
    #     session.close()

def register(application):
    application.add_handler(CommandHandler("start", inline_start))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="show_days|request_vacation"))
    application.add_handler(CallbackQueryHandler(vacation_by_days_handler, pattern="vacation_by_days"))
    application.add_handler(CallbackQueryHandler(vacation_by_hours_handler, pattern="vacation_by_hours"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

def main():
    BOT_TOKEN = "YOUR_BOT_TOKEN"
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    register(application)

    print("Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
