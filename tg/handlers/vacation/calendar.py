from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import calendar

class TelegramCalendar:
    def __init__(self):
        self.months = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

    def create_calendar(self, year=None, month=None):
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        keyboard = []
        
        # Первая строка - месяц и год
        row = [
            InlineKeyboardButton(
                "<<",
                callback_data=f"calendar-month-{year}-{month-1 if month > 1 else 12}-prev"
            ),
            InlineKeyboardButton(
                f"{self.months[month]} {year}",
                callback_data=f"calendar-ignore"
            ),
            InlineKeyboardButton(
                ">>",
                callback_data=f"calendar-month-{year}-{month+1 if month < 12 else 1}-next"
            ),
        ]
        keyboard.append(row)
        
        # Вторая строка - дни недели
        row = []
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            row.append(InlineKeyboardButton(day, callback_data="calendar-ignore"))
        keyboard.append(row)

        # Дни месяца
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            row = []
            for day in week:
                if day == 0:
                    row.append(InlineKeyboardButton(" ", callback_data="calendar-ignore"))
                else:
                    # Проверяем, что дата не в прошлом
                    date = datetime(year, month, day)
                    if date < now.replace(hour=0, minute=0, second=0, microsecond=0):
                        row.append(InlineKeyboardButton(" ", callback_data="calendar-ignore"))
                    else:
                        row.append(
                            InlineKeyboardButton(
                                str(day),
                                callback_data=f"calendar-day-{year}-{month}-{day}"
                            )
                        )
            keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    def process_calendar_selection(self, update, context):
        query = update.callback_query
        data = query.data.split("-")
        
        if data[0] != "calendar":
            return False
            
        action = data[1]
        year = int(data[2])
        month = int(data[3])
        
        if action == "ignore":
            query.answer(cache_time=60)
            return False
            
        elif action == "month":
            direction = data[4]
            if direction == "prev":
                if month == 1:
                    month = 12
                    year -= 1
                else:
                    month -= 1
            elif direction == "next":
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                    
            query.edit_message_reply_markup(
                reply_markup=self.create_calendar(year, month)
            )
            return False
            
        elif action == "day":
            day = int(data[4])
            selected_date = datetime(year, month, day)
            query.edit_message_text(
                text=f"Вы выбрали: {selected_date.strftime('%d.%m.%Y')}",
                reply_markup=None
            )
            return selected_date

def get_calendar_handler():
    calendar_obj = TelegramCalendar()
    return CallbackQueryHandler(calendar_obj.process_calendar_selection, pattern=r"calendar-.*")
