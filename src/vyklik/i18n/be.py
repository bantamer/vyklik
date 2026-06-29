TR = {
    "welcome": (
        "Прывітанне! Я бот для адсочвання чэргаў DUW Wrocław.\n\n"
        "Пакажу актуальны статус чэргаў і дашлю апавяшчэнне, калі выклічуць "
        "твой талон ці калі адкрыецца запіс."
    ),
    "help": (
        "Каманды:\n"
        "/queues — спіс чэргаў\n"
        "/mysubs — твае падпіскі\n"
        "/dashboard — замацаваны статус\n"
        "/stats — калі лепш прыйсці\n"
        "/feedback — напісаць аўтару\n"
        "/lang — змяніць мову\n"
        "/help — гэтае паведамленне"
    ),
    "feedback_prompt": (
        "Напішы паведамленне — я перадам яго аўтару бота (твой чат ён не ўбачыць). "
        "Або /cancel, каб скасаваць."
    ),
    "feedback_sent": "Дзякуй! Паведамленне адпраўлена. 🙏",
    "feedback_cancel": "Добра, скасаваў.",
    "feedback_unavailable": "Зваротная сувязь зараз недаступная.",
    "feedback_error": "Не атрымалася адправіць, паспрабуй пазней.",
    "choose_language": "Выберы мову:",
    "cmd_queues": "Спіс чэргаў",
    "cmd_mysubs": "Твае падпіскі",
    "cmd_dashboard": "Замацаваны статус",
    "cmd_stats": "Калі лепш прыйсці",
    "cmd_feedback": "Напісаць аўтару",
    "cmd_lang": "Змяніць мову",
    "cmd_help": "Дапамога",
    "language_set": "Мова ўстаноўлена: беларуская.",
    "status_open": "🟢 адчынена",
    "status_closed": "🔴 зачынена",
    "queues_header": "Чэргі DUW Wrocław (націсні, каб убачыць дэталі):",
    "no_queues": "Даных пакуль няма — полер яшчэ не схадзіў па чэргі.",
    "queue_card": (
        "🎫 <b>{name}</b>\n\n"
        "Статус: {status}\n"
        "Выкліканы талон: <b>{ticket}</b>\n"
        "Абслужана: {served}/{max_t}\n"
        "У чарзе: {ticket_count} · вольных месцаў: {tickets_left}\n"
        "Сяр. чаканне: {wait} · абслугоўванне: {service}"
    ),
    "queue_no_data": "Свежых даных па гэтай чарзе няма.",
    "btn_stats": "📊 Калі лепш прыйсці",
    "stats_pick": "Выберы чаргу, каб паглядзець статыстыку па днях і гадзінах:",
    "dow_1": "Пн",
    "dow_2": "Аў",
    "dow_3": "Ср",
    "dow_4": "Чц",
    "dow_5": "Пт",
    "heatmap_title": "📊 <b>{name}</b>\nКалі меншая чарга (гадзіны 8→15):",
    "heatmap_legend": "🟩 ціха · 🟨 сярэдне · 🟥 натоўп · ⬜ няма даных",
    "heatmap_advice": (
        "💡 Найцішэй: {quiet_day} {quiet_h} (~{quiet_w}). "
        "Найгорш: {busy_day} {busy_h} (~{busy_w})."
    ),
    "heatmap_no_data": "📊 <b>{name}</b>\nПакуль недастаткова даных для статыстыкі.",
    "eta_line": (
        "⏱ Перад табой: <b>{ahead}</b>\n"
        "Выклічуць прыкладна праз {low}–{high} (≈ {at_low}–{at_high})"
    ),
    "eta_called": "🎯 Цябе ўжо выклікалі ці ты наступны!",
    "eta_no_pace": (
        "⏱ Перад табой: <b>{ahead}</b>. Тэмп пакуль не вызначыць — "
        "занадта рана ці выклікаў было мала."
    ),
    "eta_today_unlikely": "⚠️ Сёння могуць не паспець выклікаць да зачынення.",
    "btn_subscribe": "🔔 Падпісацца",
    "btn_unsubscribe": "🔕 Адпісацца",
    "btn_set_ticket": "🎫 Указаць мой талон",
    "btn_clear_ticket": "❌ Прыбраць мой талон",
    "btn_refresh": "🔄 Абнавіць",
    "btn_back": "⬅️ Назад",
    "card_updated": "🕒 даныя на {time}",
    "btn_toggle_open": "📢 Алерт пра адкрыццё: {state}",
    "btn_toggle_slots": "🪑 Алерт пра новыя месцы: {state}",
    "btn_toggle_every": "🔔 Кожны выклік: {state}",
    "btn_rearm": "🔔 пры {n}",
    "on": "укл.",
    "off": "выкл.",
    "dashboard_header": "📌 <b>Мае чэргі</b> · абноўлена {time}",
    "dashboard_line_closed": "🔴 {name} — зачынена",
    "dashboard_line_open": "🟢 {name}: <b>{ticket}</b>",
    "dashboard_mine": " · твой {my}, перад табой {n}",
    "dashboard_mine_eta": " · твой {my}, перад табой {n} (~{eta})",
    "dashboard_mine_called": " · твой {my} ✅",
    "dashboard_mine_plain": " · твой {my}",
    "dashboard_empty": "У цябе няма падпісак. Адкрый /queues і выберы чаргу.",
    "dashboard_pinned": "📌 Замацаваў статус тваіх чэргаў — буду абнаўляць яго аўтаматычна.",
    "mysubs_header": "Твае падпіскі:",
    "no_subs": "Падпісак яшчэ няма. Адкрый /queues і выберы чаргу.",
    "sub_added": "Падпіска дададзена.",
    "sub_removed": "Падпіска выдалена.",
    "ticket_prompt": "Дашлі свой талон (напрыклад <code>G045</code>):",
    "ticket_invalid": (
        "Талон павінен быць у фармаце літара + лічбы (напрыклад G045). Паспрабуй яшчэ раз."
    ),
    "ticket_set": "Талон захаваны: <b>{ticket}</b>.",
    "ticket_cleared": "Талон выдалены.",
    "threshold_prompt": (
        "За колькі талонаў да твайго папярэдзіць? Дашлі лічбу (напрыклад <code>5</code>) "
        "ці <code>не</code>."
    ),
    "threshold_set": "Паведамлю, калі да твайго талона застанецца ≤ {n}.",
    "threshold_off": "Алерт пра набліжэнне выключаны.",
    "alert_called": "🎯 <b>{name}</b>\nВыкліканы твой талон <b>{ticket}</b>!",
    "alert_close": (
        "⏳ <b>{name}</b>\nДа твайго талона <b>{my}</b> засталося {n}. "
        "Толькі што выклікалі: <b>{current}</b>."
    ),
    "alert_eta": "⏱ Прыкладна праз {low}–{high} (≈ {at_low}–{at_high}).",
    "alert_every": "🔔 <b>{name}</b>\nВыклікалі <b>{current}</b> · да твайго <b>{my}</b> засталося {n}.",
    "rearm_set": "Нагадаю, калі застанецца ≤ {n}.",
    "alert_opened": "📢 <b>{name}</b>\nЗапіс толькі што адкрыўся!",
    "alert_slots": ("🪑 <b>{name}</b>\nЗ'явілася {n} вольных месцаў — паспявай запісацца!"),
}
