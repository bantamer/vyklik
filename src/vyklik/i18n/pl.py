TR = {
    # Common
    "welcome": (
        "Cześć! Jestem botem do śledzenia kolejek DUW Wrocław.\n\n"
        "Pokażę ci aktualny stan kolejek i powiadomię, gdy zawołają twój numerek "
        "lub gdy otworzy się rejestracja."
    ),
    "help": (
        "Komendy:\n"
        "/queues — lista kolejek\n"
        "/mysubs — twoje subskrypcje\n"
        "/lang — zmień język\n"
        "/help — ta wiadomość"
    ),
    "choose_language": "Wybierz język:",
    "language_set": "Język ustawiony: polski.",
    # Queue card
    "status_open": "🟢 otwarta",
    "status_closed": "🔴 zamknięta",
    "queues_header": "Kolejki DUW Wrocław (kliknij, by zobaczyć szczegóły):",
    "no_queues": "Brak danych — poller jeszcze nie pobrał żadnych kolejek.",
    "queue_card": (
        "🎫 <b>{name}</b>\n\n"
        "Status: {status}\n"
        "Wywołany numer: <b>{ticket}</b>\n"
        "Obsłużono: {served}/{max_t}\n"
        "W kolejce: {ticket_count} · wolnych miejsc: {tickets_left}\n"
        "Śr. oczekiwanie: {wait} · obsługa: {service}"
    ),
    "queue_no_data": "Brak świeżych danych dla tej kolejki.",
    "eta_line": (
        "⏱ Przed tobą: <b>{ahead}</b>\n"
        "Wywołają cię mniej więcej za {low}–{high} (≈ {at_low}–{at_high})"
    ),
    "eta_called": "🎯 Już cię wywołano albo jesteś następny!",
    "eta_no_pace": (
        "⏱ Przed tobą: <b>{ahead}</b>. Tempa jeszcze nie da się ocenić — "
        "za wcześnie albo było za mało wywołań."
    ),
    "eta_today_unlikely": "⚠️ Dziś mogą nie zdążyć cię wywołać przed zamknięciem.",
    "btn_subscribe": "🔔 Subskrybuj",
    "btn_unsubscribe": "🔕 Wypisz się",
    "btn_set_ticket": "🎫 Ustaw mój numerek",
    "btn_clear_ticket": "❌ Usuń mój numerek",
    "btn_refresh": "🔄 Odśwież",
    "btn_back": "⬅️ Wstecz",
    "card_updated": "🕒 dane z {time}",
    "btn_toggle_open": "📢 Powiadom, gdy się otworzy: {state}",
    "btn_toggle_slots": "🪑 Powiadom o nowych miejscach: {state}",
    "btn_toggle_every": "🔔 Każde wywołanie: {state}",
    "btn_rearm": "🔔 przy {n}",
    "on": "wł.",
    "off": "wył.",
    # Subscriptions
    "dashboard_header": "📌 <b>Moje kolejki</b> · aktualizacja {time}",
    "dashboard_line_closed": "🔴 {name} — zamknięta",
    "dashboard_line_open": "🟢 {name}: <b>{ticket}</b>",
    "dashboard_mine": " · twój {my}, przed tobą {n}",
    "dashboard_mine_eta": " · twój {my}, przed tobą {n} (~{eta})",
    "dashboard_mine_called": " · twój {my} ✅",
    "dashboard_mine_plain": " · twój {my}",
    "dashboard_empty": "Nie masz subskrypcji. Otwórz /queues i wybierz kolejkę.",
    "dashboard_pinned": "📌 Przypiąłem status twoich kolejek — będę go aktualizować automatycznie.",
    "mysubs_header": "Twoje subskrypcje:",
    "no_subs": "Nie masz jeszcze żadnych subskrypcji. Otwórz /queues i wybierz kolejkę.",
    "sub_added": "Subskrypcja dodana.",
    "sub_removed": "Subskrypcja usunięta.",
    # Ticket entry
    "ticket_prompt": "Wyślij swój numerek (np. <code>G045</code>):",
    "ticket_invalid": (
        "Numerek powinien być w formacie litera + cyfry (np. G045). Spróbuj jeszcze raz."
    ),
    "ticket_set": "Numerek zapisany: <b>{ticket}</b>.",
    "ticket_cleared": "Numerek usunięty.",
    "threshold_prompt": (
        "Za ile numerków przed twoim mam dać znać? Wyślij liczbę (np. <code>5</code>) "
        "albo <code>nie</code>."
    ),
    "threshold_set": "Powiadomię, gdy do twojego numerka zostanie ≤ {n}.",
    "threshold_off": "Powiadomienie o zbliżaniu się wyłączone.",
    # Alerts
    "alert_called": ("🎯 <b>{name}</b>\nWywołano twój numerek <b>{ticket}</b>!"),
    "alert_close": (
        "⏳ <b>{name}</b>\nDo twojego numerka <b>{my}</b> zostało {n}. "
        "Wywołany właśnie: <b>{current}</b>."
    ),
    "alert_eta": "⏱ Mniej więcej za {low}–{high} (≈ {at_low}–{at_high}).",
    "alert_every": "🔔 <b>{name}</b>\nWywołano <b>{current}</b> · do twojego <b>{my}</b> zostało {n}.",
    "rearm_set": "Powiadomię, gdy zostanie ≤ {n}.",
    "alert_opened": "📢 <b>{name}</b>\nRejestracja właśnie się otworzyła!",
    "alert_slots": ("🪑 <b>{name}</b>\nPojawiło się {n} wolnych miejsc — biegnij się zapisać!"),
}
