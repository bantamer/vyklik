TR = {
    "welcome": (
        "Привет! Я бот для отслеживания очередей DUW Wrocław.\n\n"
        "Покажу актуальный статус очередей и пришлю уведомление, когда вызовут "
        "твой билет или когда откроется запись."
    ),
    "help": (
        "Команды:\n"
        "/queues — список очередей\n"
        "/mysubs — твои подписки\n"
        "/dashboard — закреплённый статус\n"
        "/stats — когда лучше прийти\n"
        "/feedback — написать автору\n"
        "/lang — сменить язык\n"
        "/help — это сообщение"
    ),
    "feedback_prompt": (
        "Напиши сообщение — я передам его автору бота (твою личку он не увидит). "
        "Или /cancel, чтобы отменить."
    ),
    "feedback_sent": "Спасибо! Сообщение отправлено. 🙏",
    "feedback_cancel": "Окей, отменил.",
    "feedback_unavailable": "Обратная связь сейчас недоступна.",
    "feedback_error": "Не получилось отправить, попробуй позже.",
    "choose_language": "Выбери язык:",
    "language_set": "Язык установлен: русский.",
    "status_open": "🟢 открыта",
    "status_closed": "🔴 закрыта",
    "queues_header": "Очереди DUW Wrocław (тапни, чтобы увидеть детали):",
    "no_queues": "Данных пока нет — поллер ещё не сходил за очередями.",
    "queue_card": (
        "🎫 <b>{name}</b>\n\n"
        "Статус: {status}\n"
        "Вызванный билет: <b>{ticket}</b>\n"
        "Обслужено: {served}/{max_t}\n"
        "В очереди: {ticket_count} · свободных мест: {tickets_left}\n"
        "Ср. ожидание: {wait} · обслуживание: {service}"
    ),
    "queue_no_data": "Свежих данных по этой очереди нет.",
    "btn_stats": "📊 Когда лучше прийти",
    "stats_pick": "Выбери очередь, чтобы посмотреть статистику по дням и часам:",
    "dow_1": "Пн",
    "dow_2": "Вт",
    "dow_3": "Ср",
    "dow_4": "Чт",
    "dow_5": "Пт",
    "heatmap_title": "📊 <b>{name}</b>\nКогда меньше очередь (часы 8→15):",
    "heatmap_legend": "🟩 тихо · 🟨 средне · 🟥 толпа · ⬜ нет данных",
    "heatmap_advice": (
        "💡 Тише всего: {quiet_day} {quiet_h} (~{quiet_w}). "
        "Хуже всего: {busy_day} {busy_h} (~{busy_w})."
    ),
    "heatmap_no_data": "📊 <b>{name}</b>\nПока недостаточно данных для статистики.",
    "eta_line": (
        "⏱ Впереди тебя: <b>{ahead}</b>\n"
        "Вызовут примерно через {low}–{high} (≈ {at_low}–{at_high})"
    ),
    "eta_called": "🎯 Тебя уже вызвали или ты следующий!",
    "eta_no_pace": (
        "⏱ Впереди тебя: <b>{ahead}</b>. Темп пока не определить — "
        "слишком рано или вызовов было мало."
    ),
    "eta_today_unlikely": "⚠️ Сегодня могут не успеть вызвать до закрытия.",
    "btn_subscribe": "🔔 Подписаться",
    "btn_unsubscribe": "🔕 Отписаться",
    "btn_set_ticket": "🎫 Указать мой билет",
    "btn_clear_ticket": "❌ Убрать мой билет",
    "btn_refresh": "🔄 Обновить",
    "btn_back": "⬅️ Назад",
    "card_updated": "🕒 данные на {time}",
    "btn_toggle_open": "📢 Алерт об открытии: {state}",
    "btn_toggle_slots": "🪑 Алерт о новых местах: {state}",
    "btn_toggle_every": "🔔 Каждый вызов: {state}",
    "btn_rearm": "🔔 при {n}",
    "on": "вкл.",
    "off": "выкл.",
    "dashboard_header": "📌 <b>Мои очереди</b> · обновлено {time}",
    "dashboard_line_closed": "🔴 {name} — закрыта",
    "dashboard_line_open": "🟢 {name}: <b>{ticket}</b>",
    "dashboard_mine": " · твой {my}, впереди {n}",
    "dashboard_mine_eta": " · твой {my}, впереди {n} (~{eta})",
    "dashboard_mine_called": " · твой {my} ✅",
    "dashboard_mine_plain": " · твой {my}",
    "dashboard_empty": "У тебя нет подписок. Открой /queues и выбери очередь.",
    "dashboard_pinned": "📌 Закрепил статус твоих очередей — буду обновлять его автоматически.",
    "mysubs_header": "Твои подписки:",
    "no_subs": "Подписок ещё нет. Открой /queues и выбери очередь.",
    "sub_added": "Подписка добавлена.",
    "sub_removed": "Подписка удалена.",
    "ticket_prompt": "Пришли свой билет (например <code>G045</code>):",
    "ticket_invalid": (
        "Билет должен быть в формате буква + цифры (например G045). Попробуй ещё раз."
    ),
    "ticket_set": "Билет сохранён: <b>{ticket}</b>.",
    "ticket_cleared": "Билет удалён.",
    "threshold_prompt": (
        "За сколько билетов до твоего предупредить? Пришли число (например <code>5</code>) "
        "или <code>нет</code>."
    ),
    "threshold_set": "Сообщу, когда до твоего билета останется ≤ {n}.",
    "threshold_off": "Алерт о приближении выключен.",
    "alert_called": "🎯 <b>{name}</b>\nВызван твой билет <b>{ticket}</b>!",
    "alert_close": (
        "⏳ <b>{name}</b>\nДо твоего билета <b>{my}</b> осталось {n}. "
        "Только что вызвали: <b>{current}</b>."
    ),
    "alert_eta": "⏱ Примерно через {low}–{high} (≈ {at_low}–{at_high}).",
    "alert_every": "🔔 <b>{name}</b>\nВызвали <b>{current}</b> · до твоего <b>{my}</b> осталось {n}.",
    "rearm_set": "Напомню, когда останется ≤ {n}.",
    "alert_opened": "📢 <b>{name}</b>\nЗапись только что открылась!",
    "alert_slots": ("🪑 <b>{name}</b>\nПоявилось {n} свободных мест — успевай записаться!"),
}
