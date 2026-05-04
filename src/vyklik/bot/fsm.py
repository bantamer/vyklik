from aiogram.fsm.state import State, StatesGroup


class TicketEntry(StatesGroup):
    waiting_for_value = State()
    waiting_for_threshold = State()
