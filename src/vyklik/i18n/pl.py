TR = {
    "welcome": (
        "Dzień dobry! Ten bot śledzi kolejki DUW Wrocław.\n\n"
        "Pokazuje aktualny status kolejek i wysyła powiadomienie, gdy zostanie "
        "wywołany Twój numerek lub otworzy się rejestracja."
    ),
    "help": (
        "Ten bot śledzi kolejki DUW Wrocław i powiadamia, gdy zbliża się "
        "Twoja kolej.\n\n"
        "/queues — status wszystkich kolejek; proszę otworzyć dowolną, "
        "aby się zapisać i podać swój numerek.\n"
        "/mysubs — wszystkie Twoje subskrypcje w jednym miejscu.\n"
        "/dashboard — przypięta wiadomość ze statusem wszystkich Twoich kolejek; "
        "aktualizuje się automatycznie.\n"
        "/stats — statystyki wg dni i godzin: kiedy mniej osób "
        "i krótsze oczekiwanie.\n"
        "/feedback — napisać do autora bota.\n"
        "/lang — zmienić język."
    ),
    "feedback_prompt": (
        "Proszę napisać wiadomość — przekażemy ją autorowi bota "
        "(Twoje konto pozostanie ukryte). Aby anulować, proszę wysłać /cancel."
    ),
    "feedback_sent": "Dziękujemy, wiadomość została wysłana.",
    "feedback_cancel": "Anulowano.",
    "feedback_unavailable": "Opinie są obecnie niedostępne.",
    "feedback_error": "Nie udało się wysłać. Proszę spróbować później.",
    "choose_language": "Proszę wybrać język:",
    "cmd_queues": "Lista kolejek",
    "cmd_mysubs": "Twoje subskrypcje",
    "cmd_dashboard": "Przypięty status",
    "cmd_stats": "Kiedy najlepiej przyjść",
    "cmd_feedback": "Napisz do autora",
    "cmd_lang": "Zmień język",
    "cmd_help": "Pomoc",
    "language_set": "Język ustawiony: polski.",
    "status_open": "🟢 otwarta",
    "status_closed": "🔴 zamknięta",
    "queues_header": "Kolejki DUW Wrocław (proszę kliknąć, aby zobaczyć szczegóły):",
    "no_queues": "Brak danych.",
    "queue_card": (
        "🎫 <b>{name}</b>\n\n"
        "Status: {status}\n"
        "Wywołany numer: <b>{ticket}</b>\n"
        "Obsłużono: {served}/{max_t}\n"
        "W kolejce: {ticket_count} · wolnych miejsc: {tickets_left}\n"
        "Śr. oczekiwanie: {wait} · obsługa: {service}"
    ),
    "queue_no_data": "Brak świeżych danych dla tej kolejki.",
    "btn_stats": "📊 Kiedy najlepiej przyjść",
    "stats_pick": "Proszę wybrać kolejkę, aby zobaczyć statystyki wg dni i godzin:",
    "dow_1": "Pn",
    "dow_2": "Wt",
    "dow_3": "Śr",
    "dow_4": "Cz",
    "dow_5": "Pt",
    "heatmap_title": "📊 <b>{name}</b>\nCzas oczekiwania wg dni i godzin:",
    "heatmap_legend": "🟩 krótko · 🟨 średnio · 🟥 długo · ⬜ brak danych",
    "heatmap_advice": (
        "💡 Najkrócej: {quiet_day} {quiet_h} (~{quiet_w}). "
        "Najdłużej: {busy_day} {busy_h} (~{busy_w})."
    ),
    "heatmap_no_data": "📊 <b>{name}</b>\nZa mało danych na statystyki.",
    "eta_line": ("⏱ Przed Tobą: <b>{ahead}</b>\nJeszcze ~{range} czekania (≈ {at_low}–{at_high})"),
    "eta_called": "🎯 Już Cię wywołano lub jesteś następny.",
    "eta_no_pace": (
        "⏱ Przed Tobą: <b>{ahead}</b>. Tempa na razie nie da się ocenić — "
        "za wcześnie lub było za mało wywołań."
    ),
    "eta_today_unlikely": "⚠️ Dziś mogą nie zdążyć wywołać przed zamknięciem.",
    "btn_subscribe": "🔔 Subskrybuj",
    "btn_unsubscribe": "🔕 Wypisz się",
    "btn_set_ticket": "🎫 Ustaw mój numerek",
    "btn_clear_ticket": "❌ Usuń mój numerek",
    "btn_refresh": "🔄 Odśwież",
    "btn_back": "⬅️ Wstecz",
    "card_updated": "🕒 dane z {time}",
    "btn_toggle_open": "📢 Powiadomienie o otwarciu: {state}",
    "btn_toggle_slots": "🪑 Powiadomienie o nowych miejscach: {state}",
    "btn_toggle_every": "🔔 Każde wywołanie: {state}",
    "btn_rearm": "🔔 Przypomnij przy {n}",
    "on": "wł.",
    "off": "wył.",
    "dur_h": "godz",
    "dur_min": "min",
    "dur_s": "s",
    "dashboard_header": "📌 <b>Moje kolejki</b> · aktualizacja {time}",
    "dashboard_line_closed": "🔴 {name} — zamknięta",
    "dashboard_line_open": "🟢 {name}: <b>{ticket}</b>",
    "dashboard_mine": " · Twój {my}, przed Tobą {n}",
    "dashboard_mine_eta": " · Twój {my}, przed Tobą {n} (~{eta})",
    "dashboard_mine_called": " · Twój {my} ✅",
    "dashboard_mine_plain": " · Twój {my}",
    "dashboard_empty": "Brak subskrypcji. Proszę otworzyć /queues i wybrać kolejkę.",
    "dashboard_pinned": (
        "📌 Status Twoich kolejek został przypięty — będzie aktualizowany automatycznie."
    ),
    "mysubs_header": "Twoje subskrypcje:",
    "no_subs": "Brak subskrypcji. Proszę otworzyć /queues i wybrać kolejkę.",
    "sub_added": "Subskrypcja dodana.",
    "sub_removed": "Subskrypcja usunięta.",
    "ticket_prompt": "Proszę wysłać swój numerek (np. <code>G045</code>):",
    "ticket_invalid": (
        "Numerek powinien mieć format litera + cyfry (np. G045). Proszę spróbować ponownie."
    ),
    "ticket_wrong_series": (
        "Ta kolejka wydaje numerki serii «{prefix}», a podano {ticket}. "
        "To chyba numerek z innej kolejki — proszę sprawdzić."
    ),
    "ticket_set": "Numerek zapisany: <b>{ticket}</b>.",
    "ticket_cleared": "Numerek usunięty.",
    "threshold_prompt": (
        "Na ile numerków przed Twoim mamy dać znać? Proszę wysłać liczbę "
        "(np. <code>5</code>) lub <code>nie</code>."
    ),
    "threshold_set": "Powiadomimy, gdy do Twojego numerka zostanie ≤ {n}.",
    "threshold_off": "Powiadomienie o zbliżaniu się wyłączone.",
    "alert_called": "🎯 <b>{name}</b>\nWywołano Twój numerek <b>{ticket}</b>.",
    "alert_close": (
        "⏳ <b>{name}</b>\nDo Twojego numerka <b>{my}</b> zostało {n}. "
        "Przed chwilą wywołano: <b>{current}</b>."
    ),
    "alert_eta": "⏱ Jeszcze ~{range} czekania (≈ {at_low}–{at_high}).",
    "alert_every": (
        "🔔 <b>{name}</b>\nWywołano <b>{current}</b> · do Twojego <b>{my}</b> zostało {n}."
    ),
    "rearm_set": "Powiadomimy, gdy zostanie ≤ {n}.",
    "alert_opened": "📢 <b>{name}</b>\nRejestracja właśnie się otworzyła.",
    "alert_slots": ("🪑 <b>{name}</b>\nPojawiło się {n} wolnych miejsc — proszę się zapisać."),
}
