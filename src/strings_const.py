# Файл для строковых констант оформления
from string import Template


# Ответы на комманды
WELCOME_TEXT = 'Привет!\n\n' \
			   'Это анонимный чат ВСети 😎\n\n' \
			   'Тут ты можешь найти себе новых друзей или пообщаться со старыми :)\n' \
			   'Заходи в наш телеграм канал чтобы быть в курсе всех новостей нашего проекта 💖\n\n' \
			   'Chatium Community - @vsety_community'

HELP_TEXT = 'Комманды бота:\n\n' \
			'/start - главное меню\n' \
			'/search - найти собеседника\n' \
			'/profile - профиль\n' \
			'/rating - рейтинг меню\n' \
			'/info - информация'
INFORMATION_TEXT = 'ℹ️ <b>Информация</b>'
# FIX IT
SUPPORT_INFO_TEXT = '<b>Поддержи проект!</b>'

# Кнопки мейн меню
SEARCH_TEXT = '🔍 Поиск'
RATING_TEXT = '⭐️ Рейтинг'
PROFILE_TEXT = '👤 Профиль'
INFO_TEXT = 'ℹ️ Информация'

# Кнопки второстепенных меню
SEND_BUG_REPORT_TEXT = '🐞 Отправить баг репорт'
HELP_LINK_TEXT = '🧰 Помощь'
SUPPORT_TEXT = '😉 Поддержать проект'

# Баг репорт тексты
SEND_BUG_REPORT_WELCOME_TEXT = 'Очень приятно что вы помогаете нашему проекту развиваться 💘\n\n' \
							   'Опишите баг который вы обнаружили, максимально подробно, это важно\n' \
							   'Если есть возможность укажите время когда баг произошёл'
SEND_BUG_REPORT_IMAGE = 'Прекрасно!\n\n' \
						'Теперь отправьте скриншот произошедшего бага\n' \
						'Ещё раз спасибо за содействие в улучшении проекта 🙂'
THANKS_FOR_BUG_REPORT_TEXT = 'Спасибо за баг репорт!\n' \
							 'Мы обязательно его пофиксим'

# Темплейты
PROFILE_TEMPLATE = Template('Профиль\n\n' \
							'🔎 ID: $id\n' \
							'📅 Ты с нами $days д. $hours ч. \n' \
							'⭐️ Очков рейтинга - $rating_score\n' \
							'$additional_info\n'
							'✉️ Всего отправленных сообщений: $count_messages\n' \
							'👤 Начато диалогов: $count_dialogs')
RATING_TEMPLATE = Template('Рейтинг самых активных в этом чат боте😎\n' \
						   'Очки рейтинга получаются с помощью активностей в боте\n\n$users_rating')
ADMIN_TEMPLATE = Template('Привет!\nЭто админ меню')
SCAM_TEMPLATE = 'Вас пытаются обмануть!\n' \
				'Человек попытался отправить фейковую монетку не тут-то было....\n\n' \
				'P.S ВСети :)'

# Кнопки админки
DISTRIBUTION_TEXT = '✉️ Рассылка'
SWITCH_TO_USER_MODE_TEXT = 'Перейти в админ режим'

# Кнопки чатинга
STOP_TEXT = 'Стоп 🛑'
SHARE_LINK_TEXT = 'Поделиться ссылкой 📨'
SHARE_LINK_TEMPLATE = Template('Пользователь поделился с тобой ссылкой - t.me/$username')
DIALOG_END = 'Диалог закончен :('
WAIT_MORE_2_SEC_TEXT = 'Ожидайте, скоро найдем вам кого нибудь:)'
START_SEARCH = '<i>Поиск...</i>'
END_SEARCH = 'Собеседник найден!'
COIN_FLIP_TEXT = 'Монетка 🪙'
COIN_FLIP_TEMPLATE = Template('Вам выпал $coin_flip 🪙')
ALREADY_SEARCH_TEXT = 'Мы уже ищем вам собеседника!'
NEXT_COMPANION_TEXT = 'Следующий ➡️'
EXIT_TEXT = 'Выйти ◀️'
QUIT_FROM_QUEUE = 'Мы не нашли вам никого :('
NOBODY_FOUND = 'Никого тебе не нашли😔\nЗаглядывай попозже'

TECH_PAUSE = 'Технический перерыв 😔\n' \
			 'Возвращайтесь позже, бот станет ещё лучше :)'
