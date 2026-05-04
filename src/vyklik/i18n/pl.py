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
    "btn_subscribe": "🔔 Subskrybuj",
    "btn_unsubscribe": "🔕 Wypisz się",
    "btn_set_ticket": "🎫 Ustaw mój numerek",
    "btn_clear_ticket": "❌ Usuń mój numerek",
    "btn_back": "⬅️ Wstecz",
    "btn_toggle_open": "📢 Powiadom, gdy się otworzy: {state}",
    "btn_toggle_slots": "🪑 Powiadom o nowych miejscach: {state}",
    "on": "wł.",
    "off": "wył.",
    # Subscriptions
    "mysubs_header": "Twoje subskrypcje:",
    "no_subs": "Nie masz jeszcze żadnych subskrypcji. Otwórz /queues i wybierz kolejkę.",
    "sub_added": "Subskrypcja dodana.",
    "sub_removed": "Subskrypcja usunięta.",
    # Ticket entry
    "ticket_prompt": "Wyślij swój numerek (np. <code>G045</code>):",
    "ticket_invalid": "Numerek powinien być w formacie litera + cyfry (np. G045). Spróbuj jeszcze raz.",
    "ticket_set": "Numerek zapisany: <b>{ticket}</b>.",
    "ticket_cleared": "Numerek usunięty.",
    "threshold_prompt": (
        "Za ile numerków przed twoim mam dać znać? Wyślij liczbę (np. <code>5</code>) "
        "albo <code>nie</code>."
    ),
    "threshold_set": "Powiadomię, gdy do twojego numerka zostanie ≤ {n}.",
    "threshold_off": "Powiadomienie o zbliżaniu się wyłączone.",
    # Alerts
    "alert_called": (
        "🎯 <b>{name}</b>\nWywołano twój numerek <b>{ticket}</b>!"
    ),
    "alert_close": (
        "⏳ <b>{name}</b>\nDo twojego numerka <b>{my}</b> zostało {n}. "
        "Wywołany właśnie: <b>{current}</b>."
    ),
    "alert_opened": "📢 <b>{name}</b>\nRejestracja właśnie się otworzyła!",
    "alert_slots": (
        "🪑 <b>{name}</b>\nPojawiło się {n} wolnych miejsc — biegnij się zapisać!"
    ),
}
