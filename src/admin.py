# Admin worker
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup


async def admin_command_routing(callback_query: types.CallbackQuery):
	match callback_query.data:
		case 'distribution':
			pass
		case 'switch_to_user' | 'switch_to_admin':
			pass


