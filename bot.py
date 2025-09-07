import logging
import subprocess
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from io import BytesIO
from PIL import Image, ImageDraw
import random

# URL твоего проекта на Render
RENDER_URL = "https://telegram-bot.onrender.com"  # ← Замени на свой URL

def keep_awake():
    while True:
        try:
            # Делаем запрос к нашему же веб-серверу
            response = requests.get(RENDER_URL)
            print(f"✅ Будильник: ping {RENDER_URL} | Статус: {response.status_code}")
        except Exception as e:
            print(f"❌ Будильник: ошибка: {e}")
        # Ждём 14 минут (840 секунд)
        time.sleep(840)  # 14 минут — идеально (меньше 15)

# Запускаем будильник в фоне
threading.Thread(target=keep_awake, daemon=True).start()

# Установка библиотек
subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot", "Pillow", "Flask"])

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------------
# 🎲 ГЕНЕРАЦИЯ КАРТЫ
# ----------------------------

def generate_board():
    board = [{"color": "start", "type": "start"}]  # ячейка 0

    for i in range(1, 100):
        cell = {}

        if i < 70:
            cell["color"] = random.choices(["green", "yellow"], weights=[80, 20])[0]
        elif i < 80:
            cell["color"] = random.choices(["green", "yellow", "red"], weights=[40, 40, 20])[0]
        else:
            cell["color"] = random.choices(["red", "yellow", "green"], weights=[70, 20, 10])[0]

        if cell["color"] == "green":
            cell["type"] = "phrase"
        elif cell["color"] == "yellow":
            cell["type"] = "challenge"
        elif cell["color"] == "red":
            cell["type"] = "sexy_challenge"

        board.append(cell)

    # Ловушки
    trap1 = random.randint(15, 85)
    trap2 = random.randint(15, 85)
    while trap2 == trap1:
        trap2 = random.randint(15, 85)

    board[trap1] = {"color": "blue", "type": "back7", "text": "🌀 Ловушка! Откат на 7 шагов!"}
    board[trap2] = {"color": "purple", "type": "back5", "text": "⚠️ Магия провала! Откат на 5 шагов!"}

    # ⛓️ Тюрьма
    prison = random.randint(20, 90)
    while prison in [trap1, trap2]:
        prison = random.randint(20, 90)
    board[prison] = {
        "color": "black",
        "type": "prison",
        "text": "⛓️ Тюрьма! Пропусти ход и сними один элемент одежды!"
    }

    # 🎁 Подарок
    gift = random.randint(30, 95)
    while gift in [trap1, trap2, prison]:
        gift = random.randint(30, 95)
    board[gift] = {
        "color": "gold",
        "type": "gift",
        "text": "🎁 Подарок! Получено право на отказ от задания или 1000 рублей на счет от Бориса!"
    }

    # 🌪️ Хаос (2 ячейки)
    chaos_positions = []
    for _ in range(2):
        pos = random.randint(40, 95)
        while pos in [trap1, trap2, prison, gift] + chaos_positions:
            pos = random.randint(40, 95)
        chaos_positions.append(pos)
        board[pos] = {
            "color": "purple",
            "type": "chaos",
            "text": "🌀 Хаос! Случайный эффект!"
        }

    return board

BOARD = generate_board()

# ----------------------------
# 📚 КОНТЕНТ ДЛЯ ЯЧЕЕК
# ----------------------------

PHRASES_GREEN = [
"Расскажи анекдот, пока не рассмеётся партнер",
"Поделись своей самой смешной школьной историей",
"Назови три качества, которые ценишь в людях",
"Что бы ты взял(а) с собой на необитаемый остров?",
"Расскажи о самом неловком моменте в своей жизни",
"Если бы ты мог(ла) стать кем угодно на день — кем бы выбрал(а)?",
"Расскажи о самом вкусном блюде, которое ты пробовал(а)",
"Что бы ты сделал(а), если бы выиграл(а) миллион?",
"Какой самый безумный поступок ты совершал(а)?",
"Что бы ты сделал(а), если бы был(а) невидимым(ой) на один день?",
"Расскажи о своей первой любви",
"Какой твой любимый запах?",
"Что ты не можешь делать без улыбки?",
"Что бы ты хотел(а) изменить в себе?",
"Расскажи о самом необычном сне, который помнишь",
"Изобрази животное, пока соперник не угадает",
"Продолжай игру, сидя на корточках",
"Говори шепотом следующие 3 хода",
"Сделай 5 отжиманий или приседаний",
"Расскажи, что делал вчера вечером",
"Сделай комплимент партнеру",
"Признайся в самом смешном секрете",
"Покажи свои последние 3 фото в галерее",
"Скажи: Ты самый сексуальный человек в комнате",
"Выпей залпом стакан воды или алкоголя",
"Расскажи стыдную или нелепую историю из жизни",
"Надень 3 элемента одежды",
"Надень 7 элементов одежды",
"Танцуй под музыку",
"Объясни первое пришедшее на ум слово жестами рук или телом",
"Подержи пол минуты во рту лед или воду",
"Передай в губах партнеру еду",
"Прошепчи на ухо партнеру приятные слова",
"Сними 1 элемент одежды",
"Оближи губы сексуально глядя партнеру в глаза",
"Говори 1 ход с высунутым языком",
"Нарисуй себе монобровь",
"Встань на 5 секунд в планку",
"Копируй в течение минуты действия партнера",
"Качни пресс 5 раз",
"Представь что ты нищий, выпроси денег у партнера",
"Говори со странным акцентом",
"Покажи свое лицо во время оргазма",
"Ты можешь отказаться от любого задания",
]

CHALLENGES_YELLOW = [
"Расскажи историю занятия секса в необычном месте или фантазию о сексе",
"Поцелуй партнера в щёку",
"Обними партнера на 10 секунд",
"Держи руку соперника 30 секунд, не разрывая зрительного контакта",
"Прошепчи на ухо партнеру что-то романтическое",
"Сделай массаж плеч партнеру 30 секунд",
"Поменяйся футболкой с партнером (если возможно).",
"Сыграй в «Правду или действие» один раунд",
"Поцелуй пальцы рук партнеру",
"Сними 2 элемента одежды",
"Поцелуй с партнером с языком",
"Сними все элементы одежды, кроме двух",
"Поцелуй в ушко партнера",
"Пришли интимную фотку партнеру",
"Поцелуй любую часть тела партнера",
"Сделай массаж рук партнеру",
"Поцелуй партнера в 3 разные участка тела",
"Сделай массаж ступней партнеру",
"Сделай массаж головы партнеру",
"Шлепни партнера по попке 3 раза",
"Отправь партнеру максимально пошлое сообщение",
"Напиши свое имя в воздухе ягодицами",
"Все целуются с языком",
"Партнер выполняет любое твое желание внутри дома",
"Ты можешь отказаться от любого задания",
"Оставь надпись на теле партнера маркером",
"Набери в рот воды, встань над партнером и попади ему в рот этой водой",
"Сними трусики и играй без них",
"Придумай свое задание для партнера прямо сейчас",
"Партнер медленно целует тебя опускаясь от шеи к низу живота",
"Откровенно расскажи, что нового ты хотел бы попробовать в сексе",
"Называйте 3 прилагательных, а ваш партнёр должен поцеловать вас в ассоциируемую с этим часть тела",
"Откровенно обсудите, как вы относитесь к БДСМ? Что бы можно попробовать прямо сегодня?",
"Опиши тремя словами поведение партнера в постели",
"Расскажи, чего ты всегда стеснялся сказать во время секса?",
"Продемонстрируйте вдвоем позу которую ты хочешь бы попробовать?",
"Обнимитесь так, как будто вы встретились после долгой разлуки",
"Сделайте вместе 5 приседаний, держась за руки",
"Погладь партнера по голове как котёнка",
"Обнимитесь и скажите друг другу по одному комплименту",
"Обними партнера сзади",
"Поцелуй партнера в шею",
"Прошепчи на ухо: «Я хочу тебя»",
"Поцелуй партнера в губы 10 секунд",
"Сделайте настоящий страстный поцелуй",
"Скажи: «Я хочу, чтобы ты прикоснулся ко мне вот здесь…» — покажи",
"Обними партнера, и прижми к стене, как в кино",
"Скажи три вещи, которые хочешь сделать с партнером",
"Поцелуй партнера в ухо",
"Попроси партнера снять с тебя что-то",
"Ложитесь на партнера и целуйтесь",
"Погладь партнера по спине под одеждой",
"Признайся в желании: что бы ты хотел(а) сделать прямо сейчас",
]

CHALLENGES_RED = [
"Партнер целует тебе руки",
"Партнер делает массаж любой части тела",
"Ты можешь отказаться от любого задания",
"Ты шлепаешь партнера по попе 10 раз",
"Сделай партнеру куни или минет 3 минуты",
"Заняться любым видом секса на балконе",
"Если на кубике 1,2-секс в пис, 3,4-анал, 5,6-Минет или Куни",
"Тебе вылизывают и обсасывают пальцы одной руки",
"Вкусный завтрак! Намажь чем-то съедобным половые органы партнера и слижи это. Приятного аппетита!",
"Покажи как мастурбируешь",
"Вставь анальную пробку и продолжай игру",
"Золотая осень! Пописай на партнера сегодня",
"Партнер делает тебе анилингус",
"Заняться вагинальным сексом на столе",
"Заняться анальным сексом",
"Пришло время для минета",
"Ты кушаешь еду с члена или киски",
"Заняться вагинальным сексом, вставив при этом что-то в поп",
"Займитесь сексом в лифте",
"Займитесь сексом в ванной",
"Губами ласкай грудь партнера",
"Поиграйте в строгого учителя. Вы учитель, а партнер - ученик",
"Вы детектив, партнер - подозреваемый. здесь произошло преступление. Время выбить признание",
"Ролевая игра. Ты -успешный человек, а партнер-бомжара. Переспи с этим голодным бомжом",
"Ролевая игра. Снова ввели рабство и ты завел себе нового раба. Делай с ним что хочешь, раб всегда слушается",
"Ролевая игра. Ты доставщик еды, принес еду, а партнер - заказывал, но ему совсем нечем платить.",
"Займитесь сексом в позе лотоса",
"Займитесь сексом сидя на стуле. Катя садится на Бориса",
"Займитесь сексом на столе",
"Займитесь сексом на какой-то старой вещи",
"Займитесь сексом стоя",
"Займитесь сексом в позе 69",
"Займитесь сексом в пенсионерской позе",
"Займитесь сексом с завязанными глазами",
"Займитесь сексом без рук",
"Практикуйте жесткий трах в горло. Для этого Катя ложится на угол кровати",
"Практикуйте глубокий минет. Для этого Катя ложится на угол кровати",
"Займитесь сексом раком"   
]

# ----------------------------
# 🎉 СТИКЕР ПОБЕДЫ
# ----------------------------

WIN_STICKER = "BQACAgIAAxkBAAIBRmRvUq7tqX5hRZJ7z9d9J0oqV1c3AAJiAAMgBAFLhBDJ0Ko35ugeBA"

# ----------------------------
# 🖼️ ГЕНЕРАЦИЯ КАРТИНЫ КАРТЫ С НАДПИСЯМИ
# ----------------------------

def generate_board_image(p1_pos, p2_pos):
    cell_size = 60
    width = height = cell_size * 10
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    colors = {
        "start": "#4CAF50",
        "green": "#C8E6C9",
        "yellow": "#FFF9C4",
        "red": "#FFCDD2",
        "blue": "#BBDEFB",
        "purple": "#E1BEE7",
        "black": "#212121",
        "gold": "#FFD54F",
        "end": "#90A4AE"
    }

    for i in range(100):
        row = 9 - (i // 10)
        col = i % 10
        if (i // 10) % 2 == 1:
            col = 9 - col

        x0, y0 = col * cell_size, row * cell_size
        x1, y1 = x0 + cell_size, y0 + cell_size

        if i == 0:
            color = colors["start"]
        elif i == 99:
            color = colors["end"]
        else:
            cell = BOARD[i]
            color = colors.get(cell["color"], "white")

        draw.rectangle([x0, y0, x1, y1], fill=color, outline="black")
        if i < 99:
            draw.text((x0 + 5, y0 + 5), str(i), fill="black")

        # Надписи на особых ячейках
        cell = BOARD[i]
        label = ""
        if cell["type"] == "prison":
            label = "ТЮРЬМА"
            fill = "white"
        elif cell["type"] == "gift":
            label = "ПРИЗ"
            fill = "black"
        elif cell["type"] == "chaos":
            label = "ХАОС"
            fill = "white"

        if label:
            bbox = draw.textbbox((0, 0), label)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            tx = x0 + (cell_size - text_width) // 2
            ty = y0 + (cell_size - text_height) // 2 - 5
            draw.text((tx, ty), label, fill=fill, font=None)

    # Игроки
    for pos, color in [(p1_pos, "red"), (p2_pos, "blue")]:
        if pos < 100:
            row = 9 - (pos // 10)
            col = pos % 10
            if (pos // 10) % 2 == 1:
                col = 9 - col
            x, y = col * cell_size, row * cell_size
            draw.ellipse([x + 20, y + 20, x + 40, y + 40], fill=color)

    # Подписи
    draw.text((10, height - 30), "🟢 СТАРТ", fill="green")
    draw.text((width - 100, 10), "🏁 ФИНИШ", fill="gray")

    bio = BytesIO()
    img.save(bio, "PNG")
    bio.seek(0)
    return bio

# ----------------------------
# 🎮 ОБРАБОТЧИКИ
# ----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /start")

    keyboard = [
        [InlineKeyboardButton("📱 На одном устройстве", callback_data="mode_local")],
        [InlineKeyboardButton("🌍 На расстоянии", callback_data="mode_remote")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎮 Выбери режим игры:",
        reply_markup=reply_markup
    )

async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    mode = "local" if query.data == "mode_local" else "remote"
    context.user_data["mode"] = mode

    # Инициализация
    context.user_data["game_started"] = True
    context.user_data["player1_pos"] = 0
    context.user_data["player2_pos"] = 0
    context.user_data["current_player"] = 1
    context.user_data["player1_in_torture"] = False
    context.user_data["player2_in_torture"] = False
    context.user_data["player1_gift"] = False
    context.user_data["player2_gift"] = False

    context.user_data["used_phrases"] = []
    context.user_data["used_challenges_yellow"] = []
    context.user_data["used_challenges_red"] = []

    player1_name = "Катя"
    player2_name = "Борис"
    current_name = player1_name if context.user_data["current_player"] == 1 else player2_name

    board_img = generate_board_image(context.user_data["player1_pos"], context.user_data["player2_pos"])
    await query.message.reply_photo(
        photo=board_img,
        caption=(
            f"📍 Позиции:\n"
            f"🔴 {player1_name} — {context.user_data['player1_pos']}\n"
            f"🔵 {player2_name} — {context.user_data['player2_pos']}\n\n"
            f"🎮 Ходит: {'🔴 ' + player1_name if context.user_data['current_player'] == 1 else '🔵 ' + player2_name}"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_dice")]
        ])
    )

async def roll_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info("Нажата кнопка 'Бросить кубик'")

    data = context.user_data
    current_player = data["current_player"]
    pos_key = "player1_pos" if current_player == 1 else "player2_pos"
    torture_key = "player1_in_torture" if current_player == 1 else "player2_in_torture"
    gift_key = "player1_gift" if current_player == 1 else "player2_gift"

    # --- Определяем имена и род ---
    player1_name = "Катя"
    player2_name = "Борис"
    current_name = player1_name if current_player == 1 else player2_name

    throw_verb = "бросила" if current_name == "Катя" else "бросил"
    win_verb = "выиграла" if current_name == "Катя" else "выиграл"
    skip_verb = "вышла" if current_name == "Катя" else "вышел"

    # Проверка: в тюрьме?
    if data.get(torture_key, False):
        logger.info(f"{current_name} в тюрьме — пропускает ход и снимает один элемент одежды!")
        data[torture_key] = False
        await query.edit_message_text(f"⛓️ {current_name} был(а) в тюрьме и пропускает ход!\n🔓 Теперь ты свободен(а)!")
        return  # ❌ Ход пропущен, передача происходит автоматически

    # 🎲 АНИМАЦИЯ КУБИКА
    dice_msg = await query.message.reply_dice(emoji="🎲")
    dice_value = dice_msg.dice.value
    logger.info(f"Выпало: {dice_value}")

    old_pos = data[pos_key]
    new_pos = old_pos + dice_value

    # Сообщение о броске
    await query.message.reply_text(
        f"{'🔴 ' + player1_name if current_player == 1 else '🔵 ' + player2_name} {throw_verb} кубик: 🎲 {dice_value}\n"
        f"Переместилась с {old_pos} → {new_pos}"
    )

    # ПОБЕДА
    if new_pos >= 100:
        winner = player1_name if current_player == 1 else player2_name
        win_verb_winner = "выиграла" if winner == "Катя" else "выиграл"

        # Отправляем всё: текст, стикер, кнопку
        await query.message.reply_sticker(sticker=WIN_STICKER)

        await query.message.reply_text(
            f"🎉 ПОБЕДА! {winner} {win_verb_winner} и прошла всю карту!\n\n"
            f"🏆 Поздравляем, {winner} — Теперь ты определяешь, что вам делать дальше!\n\n"
            f"Хочешь начать сначала?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Начать сначала", callback_data="restart")]
            ])
        )
        return

    # Обновляем позицию
    data[pos_key] = new_pos
    cell = BOARD[new_pos]

    # 💬 Обработка ячейки
    message = ""
    if cell["type"] == "phrase":
        unused = [p for p in PHRASES_GREEN if p not in data["used_phrases"]]
        if not unused:
            phrase = random.choice(PHRASES_GREEN)
            message = f"🟢 <b>Все фразы уже были! Но вот ещё одна:</b>\n\n<b>{phrase}</b>"
        else:
            phrase = random.choice(unused)
            data["used_phrases"].append(phrase)
            message = f"🟢 <b>Зелёная ячейка! Лайт-членж:</b>\n\n<b>{phrase}</b>"

    elif cell["type"] == "challenge":
        unused = [c for c in CHALLENGES_YELLOW if c not in data["used_challenges_yellow"]]
        if not unused:
            challenge = random.choice(CHALLENGES_YELLOW)
            message = f"🟡 <b>Все задания уже были! Но вот новое:</b>\n\n<b>{challenge}</b>"
        else:
            challenge = random.choice(unused)
            data["used_challenges_yellow"].append(challenge)
            message = f"🟡 <b>Жёлтая ячейка! Членж:</b>\n\n<b>{challenge}</b>"

    elif cell["type"] == "sexy_challenge":
        unused = [c for c in CHALLENGES_RED if c not in data["used_challenges_red"]]
        if not unused:
            challenge = random.choice(CHALLENGES_RED)
            message = f"🔴 <b>Все красные задания уже были! Но вот новое:</b>\n\n<b>{challenge}</b>"
        else:
            challenge = random.choice(unused)
            data["used_challenges_red"].append(challenge)
            message = f"🔴 <b>Красная ячейка! Секс-членж:</b>\n\n<b>{challenge}</b>"

    elif cell["type"] == "back7":
        back_pos = max(new_pos - 7, 0)
        data[pos_key] = back_pos
        message = f"🌀 <b>{cell['text']} Теперь ты на {back_pos}.</b>"

    elif cell["type"] == "back15":
        back_pos = max(new_pos - 15, 0)
        data[pos_key] = back_pos
        message = f"⚠️ <b>{cell['text']} Теперь ты на {back_pos}.</b>"

    elif cell["type"] == "prison":
        message = f"⛓️ <b>{cell['text']}</b>"
        data[torture_key] = True

    elif cell["type"] == "gift":
        message = f"🎁 <b>{cell['text']}</b>"
        data[gift_key] = True

    elif cell["type"] == "chaos":
        effects = [
            "Пропусти ход!",
            "Переместись на +5!",
            "Получи право на отказ!",
            "Выполни задание партнера!",
            "Сними один элемент одежды!",
            "Сделай комплимент партнеру!"
        ]
        effect = random.choice(effects)
        message = f"🌀 <b>{cell['text']}</b>\n\n🎲 <b>Эффект: {effect}</b>"

        if "Пропусти ход" in effect:
            data[torture_key] = True
        elif "Переместись на +5" in effect:
            data[pos_key] += 5
        elif "право на отказ" in effect:
            data[gift_key] = True
        elif "Выполни задание партнера" in effect:
            extra = random.choice(PHRASES_GREEN)
            message += f"\n\n🎯 <b>Выполни: {extra}</b>"

    # Отправляем с HTML
    if message:
        await query.message.reply_text(message, parse_mode='HTML')

    # 🖼️ Обновляем карту
    p1_pos = data["player1_pos"]
    p2_pos = data["player2_pos"]
    board_img = generate_board_image(p1_pos, p2_pos)

    # Передаём ход
    data["current_player"] = 2 if current_player == 1 else 1
    next_player = data["current_player"]
    next_name = player1_name if next_player == 1 else player2_name

    await query.message.reply_photo(
        photo=board_img,
        caption=(
            f"📍 Позиции:\n"
            f"🔴 {player1_name} — {p1_pos}\n"
            f"🔵 {player2_name} — {p2_pos}\n\n"
            f"🎮 Ходит: {'🔴 ' + player1_name if next_player == 1 else '🔵 ' + player2_name}"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 Бросить кубик", callback_data="roll_dice")]
        ])
    )

async def restart_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🔄 Начинаем сначала!")
    await select_mode(update, context)

# ----------------------------
# 🚀 ЗАПУСК БОТА
# ----------------------------

def main():
    import os
    TOKEN = os.getenv("8201451808:AAEhW6kCFp688jI1ijULM7DahwSawQ_E3rc")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(select_mode, pattern="^mode_"))
    application.add_handler(CallbackQueryHandler(roll_dice, pattern="^roll_dice$"))
    application.add_handler(CallbackQueryHandler(restart_game, pattern="^restart$"))

    logger.info("🎮 Бот запущен: полностью рабочая версия")
    application.run_polling()

# Запуск веб-сервера и бота
if __name__ == "__main__":
    main()
