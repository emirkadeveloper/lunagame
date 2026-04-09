import telebot
from telebot import types
import random
import json
import os
import time
from datetime import datetime, timedelta
import threading

TOKEN = '7872880291:AAFEvzovddULrkmyPstXsyhRrP914knJWAA'
bot = telebot.TeleBot(TOKEN)

USER_DATA_FILE = 'user_data.json'

if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
else:
    users = {}

def safe_text_lower(message):
    if hasattr(message, 'text') and message.text is not None:
        return message.text.lower()
    return ''

def save_users_data():
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

PROMO_DATA_FILE = 'promo_data.json'

def load_promo_data():
    if os.path.exists(PROMO_DATA_FILE):
        try:
            with open(PROMO_DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        except json.JSONDecodeError as e:
            print(f"⚠️ Ошибка чтения {PROMO_DATA_FILE}: {e}")
            return {}
    return {}

def save_promo_data():
    temp_file = PROMO_DATA_FILE + '.tmp'
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(promos, f, ensure_ascii=False, indent=4)
        os.replace(temp_file, PROMO_DATA_FILE)
    except Exception as e:
        print(f"⚠️ Ошибка сохранения промокодов: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

promos = load_promo_data()
def init_user(user_id, username):
    user_id_str = str(user_id)
    updated = False
    
    if user_id_str not in users:
        users[user_id_str] = {
            'nickname': username,
            'balance': 5000,
            'bank_balance': 0,
            'deposit_balance': 0,
            'experience': 0,
            'level': 1,
            'last_work_time': 0,
            'job': None,
            'house': None,
            'car': None,
            'phone': None,
            'farm': None,
            'farm_gpus': 0,
            'farm_income': 0,
            'last_farm_collect_time': 0,
            'business': None,
            'business_income': 0,
            'business_workers': 0,
            'last_business_collect_time': 0,
            'last_bonus_time': 0,
            'last_crypto_bonus_time': 0,
            'eth': 0,
            'ltc': 0,
            'btc': 0,
            'custom_id': random.randint(100000, 999999),
            'prefix': 'Игрок',
            'warns': 0,
            'is_banned': False,
            'pickaxe': None,
            'mine_cooldown': 0,
            'candy': 0,
            'ores': {
                'stone': 0, 'coal': 0, 'iron': 0, 'copper': 0, 'gold': 0,
                'diamond': 0, 'platinum': 0, 'netherite': 0, 'scandium': 0,
                'iridium': 0, 'rhodium': 0
            },
            'axe': None,
            'forest_cooldown': 0,
            'woods': {
                'oak': 0, 'birch': 0, 'spruce': 0, 'acacia': 0, 'dark_oak': 0,
                'jungle': 0, 'azalea': 0, 'mangrove': 0, 'cherry': 0, 'ebony': 0
            },
            'inventory': {},
            'energy': 25
        }
        updated = True
    else:
        default_data = {
            'deposit_balance': 0,
            'woods': {
                'oak': 0, 'birch': 0, 'spruce': 0, 'acacia': 0, 'dark_oak': 0,
                'jungle': 0, 'azalea': 0, 'mangrove': 0, 'cherry': 0, 'ebony': 0
            },
            'eth': 0, 'ltc': 0, 'btc': 0,
            'energy': 25,
            'phone': None
        }
        for key, value in default_data.items():
            if key not in users[user_id_str]:
                users[user_id_str][key] = value
                updated = True
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if subkey not in users[user_id_str][key]:
                        users[user_id_str][key][subkey] = subvalue
                        updated = True

    if user_id == 6392923371 and (users[user_id_str].get('prefix') in ['', None, 'Игрок']):
        users[user_id_str]['prefix'] = 'Разработчик'
        updated = True

    if updated:
        save_users_data()

def is_admin(user_id):
    return str(user_id) == '6392923371'

def is_banned(user_id):
    return users.get(str(user_id), {}).get('is_banned', False)

def exp_for_next_level(level):
    return 10

def format_number(number):
    return f"`{'{:,}'.format(number).replace(',', '.')}`"

def user_mention(user_id, tg_first_name):
    safe_name = str(tg_first_name).replace('_', '').replace('*', '').replace('`', '').replace('[', '').replace(']', '')
    if not safe_name.strip(): safe_name = "Игрок"
    return f"[{safe_name}](tg://user?id={user_id})"

def find_user_by_identifier(identifier):
    identifier = identifier.strip()
    if identifier.startswith('@'):
        target_username = identifier[1:].lower()
        for uid, data in users.items():
            if data.get('nickname', '').lower() == target_username:
                return uid, data['nickname']
    else:
        if identifier in users:
            return identifier, users[identifier]['nickname']
    return None, None

# ==================== БАЗЫ ДАННЫХ ====================

CARS = {
    1: {"name": "Самокат", "price": 10_000, "image": "cars/1.jpg"},
    2: {"name": "Велосипед", "price": 30_000, "image": "cars/2.jpg"},
    3: {"name": "Гироскутер", "price": 50_000, "image": "cars/3.jpg"},
    4: {"name": "Сегвей", "price": 75_000, "image": "cars/4.jpg"},
    5: {"name": "Мопед", "price": 100_000, "image": "cars/5.jpg"},
    6: {"name": "Мотоцикл", "price": 250_000, "image": "cars/6.jpg"},
    7: {"name": "ВАЗ 2109", "price": 500_000, "image": "cars/7.jpg"},
    8: {"name": "Квадроцикл", "price": 1_000_000, "image": "cars/8.jpg"},
    9: {"name": "Багги", "price": 5_000_000, "image": "cars/9.jpg"},
    10: {"name": "Вездеход", "price": 10_000_000, "image": "cars/10.jpg"},
    11: {"name": "Лада Xray", "price": 25_000_000, "image": "cars/11.jpg"},
    12: {"name": "Audi Q7", "price": 50_000_000, "image": "cars/12.jpg"},
    13: {"name": "BMW X6", "price": 75_000_000, "image": "cars/13.jpg"},
    14: {"name": "Toyota FT-HS", "price": 100_000_000, "image": "cars/14.jpg"},
    15: {"name": "BMW Z4 M", "price": 250_000_000, "image": "cars/15.jpg"},
    16: {"name": "Subaru WRX STI", "price": 500_000_000, "image": "cars/16.jpg"},
    17: {"name": "Lamborghini Veneno", "price": 750_000_000, "image": "cars/17.jpg"},
    18: {"name": "Tesla Roadster", "price": 1_000_000_000, "image": "cars/18.jpg"},
    19: {"name": "Yamaha YZF R6", "price": 3_000_000_000, "image": "cars/19.jpg"},
    20: {"name": "Bugatti Chiron", "price": 5_000_000_000, "image": "cars/20.jpg"},
    21: {"name": "Thrust SSC", "price": 10_000_000_000, "image": "cars/21.jpg"},
    22: {"name": "Ferrari LaFerrari", "price": 15_000_000_000, "image": "cars/22.jpg"},
    23: {"name": "Koenigsegg Regear", "price": 25_000_000_000, "image": "cars/23.jpg"},
    24: {"name": "Tesla Semi", "price": 35_000_000_000, "image": "cars/24.jpg"},
    25: {"name": "Venom GT", "price": 50_000_000_000, "image": "cars/25.jpg"},
    26: {"name": "Rolls-Royce", "price": 100_000_000_000, "image": "cars/26.jpg"},
}

jobs = [
    {'name': 'Фермер', 'emoji': '🍎', 'min_salary': 3000, 'max_salary': 5000, 'min_level': 1},
    {'name': 'Шахтёр', 'emoji': '⛏', 'min_salary': 8000, 'max_salary': 15000, 'min_level': 10},
    {'name': 'Строитель', 'emoji': '🧱', 'min_salary': 25000, 'max_salary': 50000, 'min_level': 25},
    {'name': 'Сантехник', 'emoji': '🛠', 'min_salary': 65000, 'max_salary': 100000, 'min_level': 35},
    {'name': 'Электрик', 'emoji': '💡', 'min_salary': 150000, 'max_salary': 300000, 'min_level': 45},
    {'name': 'Пожарник', 'emoji': '🧯', 'min_salary': 500000, 'max_salary': 750000, 'min_level': 50},
    {'name': 'Официант', 'emoji': '☕️', 'min_salary': 1000000, 'max_salary': 1500000, 'min_level': 55},
    {'name': 'Повар', 'emoji': '🍰', 'min_salary': 2500000, 'max_salary': 4500000, 'min_level': 60},
    {'name': 'Полицейский', 'emoji': '👮‍♂️', 'min_salary': 5000000, 'max_salary': 7500000, 'min_level': 65},
    {'name': 'Доктор', 'emoji': '👨‍⚕️', 'min_salary': 10000000, 'max_salary': 15000000, 'min_level': 70},
    {'name': 'Педагог', 'emoji': '👩‍🏫', 'min_salary': 25000000, 'max_salary': 35000000, 'min_level': 75},
    {'name': 'Пилот', 'emoji': '✈️', 'min_salary': 50000000, 'max_salary': 75000000, 'min_level': 80},
    {'name': 'Генерал', 'emoji': '👨‍✈️', 'min_salary': 100000000, 'max_salary': 125000000, 'min_level': 85},
    {'name': 'Бизнесмен', 'emoji': '💍', 'min_salary': 150000000, 'max_salary': 185000000, 'min_level': 90},
    {'name': 'Программист', 'emoji': '🖥', 'min_salary': 250000000, 'max_salary': 450000000, 'min_level': 100},
    {'name': 'Сапёр', 'emoji': '🪖', 'min_salary': 650000000, 'max_salary': 950000000, 'min_level': 125},
    {'name': 'Нефтяной магнат', 'emoji': '🛢️', 'min_salary': 1000000000, 'max_salary': 5000000000, 'min_level': 150},
    {'name': 'Актёр', 'emoji': '🎭', 'min_salary': 7500000000, 'max_salary': 12000000000, 'min_level': 175},
    {'name': 'Космонавт', 'emoji': '🚀', 'min_salary': 15000000000, 'max_salary': 30000000000, 'min_level': 200}
]

businesses = [
    {'name': 'Ларек', 'emoji': '🏪', 'price': 5000000, 'income_per_hour': 10000, 'worker_price': 30000},
    {'name': 'Маркет', 'emoji': '🛍️', 'price': 10000000, 'income_per_hour': 50000, 'worker_price': 100000},
    {'name': 'Сеть кафешек', 'emoji': '🍟', 'price': 30000000, 'income_per_hour': 100000, 'worker_price': 250000},
    {'name': 'Интернет-агенство', 'emoji': '🌐', 'price': 50000000, 'income_per_hour': 250000, 'worker_price': 500000},
    {'name': 'Ателье', 'emoji': '🧥', 'price': 70000000, 'income_per_hour': 500000, 'worker_price': 1000000},
    {'name': 'Сеть ресторанов', 'emoji': '🏠', 'price': 100000000, 'income_per_hour': 1000000, 'worker_price': 1500000},
    {'name': 'Банк', 'emoji': '💵', 'price': 500000000, 'income_per_hour': 3500000, 'worker_price': 5000000},
    {'name': 'Международный банк', 'emoji': '💶', 'price': 1000000000, 'income_per_hour': 5000000, 'worker_price': 10000000},
    {'name': 'Нефтяная скважина', 'emoji': '🗼', 'price': 5000000000, 'income_per_hour': 10000000, 'worker_price': 15000000},
    {'name': 'Ялан', 'emoji': '🏬', 'price': 10000000000, 'income_per_hour': 50000000, 'worker_price': 150000000}
]

houses = [
    {'name': 'Коробка', 'emoji': '📦', 'price': 500},
    {'name': 'Подвал', 'emoji': '🏚️', 'price': 2000},
    {'name': 'Сарай', 'emoji': '🏠', 'price': 10000},
    {'name': 'Маленький домик', 'emoji': '🏡', 'price': 25000},
    {'name': 'Квартира', 'emoji': '🏢', 'price': 50000},
    {'name': 'Огромный дом', 'emoji': '🏘️', 'price': 250000},
    {'name': 'Коттедж', 'emoji': '🏜️', 'price': 500000},
    {'name': 'Вилла', 'emoji': '🏰', 'price': 5000000},
    {'name': 'Таунхаус', 'emoji': '🏨', 'price': 25000000},
    {'name': 'Небоскрёб', 'emoji': '🏙️', 'price': 50000000},
    {'name': 'Плавучий дом', 'emoji': '🛳️', 'price': 250000000},
    {'name': 'Технологичный небоскрёб', 'emoji': '🔬', 'price': 500000000},
    {'name': 'Собственный остров', 'emoji': '🏝️', 'price': 750000000},
    {'name': 'Космическая станция', 'emoji': '🛸', 'price': 50000000000},
    {'name': 'Марсианский купол', 'emoji': '🔴', 'price': 100000000000},
    {'name': 'Подводный город', 'emoji': '🌊', 'price': 250000000000},
    {'name': 'Межгалактическая империя', 'emoji': '🌌', 'price': 500000000000}
]

farms = [
    {'name': 'Bitfury', 'emoji': '💻', 'price': 1000000, 'crypto_type': 'eth', 'income_per_gpu': 10, 'gpu_price': 20000},
    {'name': 'GigaWatt', 'emoji': '⚡', 'price': 50000000, 'crypto_type': 'ltc', 'income_per_gpu': 15, 'gpu_price': 1000000},
    {'name': 'Hive Blockchain', 'emoji': '🔋', 'price': 500000000, 'crypto_type': 'btc', 'income_per_gpu': 100, 'gpu_price': 50000000}
]

crypto_rates = {'eth': 1000, 'ltc': 10000, 'btc': 100000}
crypto_symbols = {'eth': 'ETH', 'ltc': 'LTC', 'btc': 'BTC'}
crypto_names = {'eth': 'Эфириум', 'ltc': 'Лайткоин', 'btc': 'Биткоин'}
FARM_CRYPTO_LIMITS = {'eth': 500, 'ltc': 1000, 'btc': 5000}
crypto_emoji = {'eth': '💎', 'ltc': '🔶', 'btc': '₿'}

ORES = {
    'stone': {'name': 'Камень', 'emoji': '🪨', 'price': 1000},
    'coal': {'name': 'Уголь', 'emoji': '🖤', 'price': 25000},
    'iron': {'name': 'Железо', 'emoji': '⚙️', 'price': 300000},
    'copper': {'name': 'Медь', 'emoji': '🧡', 'price': 3000000},
    'gold': {'name': 'Золото', 'emoji': '🟡', 'price': 5000000},
    'diamond': {'name': 'Алмаз', 'emoji': '💎', 'price': 25000000},
    'platinum': {'name': 'Платина', 'emoji': '⚪', 'price': 50000000},
    'netherite': {'name': 'Незерит', 'emoji': '🟤', 'price': 100000000},
    'scandium': {'name': 'Скандий', 'emoji': '🟣', 'price': 500000000},
    'iridium': {'name': 'Иридий', 'emoji': '🔵', 'price': 1000000000},
    'rhodium': {'name': 'Родий', 'emoji': '🟢', 'price': 10000000000}
}

PICKAXES = [
    {'id': 0, 'name': 'Деревянная кирка', 'emoji': '🪓', 'price': 0, 'price_ore_type': None, 'price_ore_amount': 0, 'drops': [{'ore': 'stone', 'min': 1, 'max': 5}]},
    {'id': 1, 'name': 'Каменная кирка', 'emoji': '⛏️', 'price': 100000, 'price_ore_type': 'stone', 'price_ore_amount': 50, 'drops': [{'ore': 'stone', 'min': 5, 'max': 15}, {'ore': 'coal', 'min': 1, 'max': 3}]},
    {'id': 2, 'name': 'Железная кирка', 'emoji': '⚒️', 'price': 1000000, 'price_ore_type': 'coal', 'price_ore_amount': 20, 'drops': [{'ore': 'coal', 'min': 3, 'max': 10}, {'ore': 'iron', 'min': 1, 'max': 2}]},
    {'id': 3, 'name': 'Золотая кирка', 'emoji': '🔨', 'price': 10000000, 'price_ore_type': 'iron', 'price_ore_amount': 10, 'drops': [{'ore': 'iron', 'min': 3, 'max': 10}, {'ore': 'copper', 'min': 1, 'max': 2}]},
    {'id': 4, 'name': 'Алмазная кирка', 'emoji': '💎', 'price': 50000000, 'price_ore_type': 'copper', 'price_ore_amount': 10, 'drops': [{'ore': 'gold', 'min': 2, 'max': 5}, {'ore': 'diamond', 'min': 0, 'max': 1, 'chance': 5}]},
    {'id': 5, 'name': 'Незеритовая кирка', 'emoji': '🔮', 'price': 100000000, 'price_ore_type': 'diamond', 'price_ore_amount': 1, 'drops': [{'ore': 'diamond', 'min': 1, 'max': 2}, {'ore': 'platinum', 'min': 0, 'max': 1, 'chance': 5}, {'ore': 'netherite', 'min': 0, 'max': 1, 'chance': 0.1}]},
    {'id': 6, 'name': 'Кирка Strend Pro', 'emoji': '⚔️', 'price': 0, 'price_ore_type': None, 'price_candy': 50, 'drops': [{'ore': 'platinum', 'min': 3, 'max': 10}, {'ore': 'netherite', 'min': 1, 'max': 3}, {'ore': 'scandium', 'min': 0, 'max': 1, 'chance': 5}]},
    {'id': 7, 'name': 'Кирка Bradas FiberGlass', 'emoji': '🔱', 'price': 0, 'price_ore_type': None, 'price_candy': 100, 'drops': [{'ore': 'scandium', 'min': 1, 'max': 5}, {'ore': 'iridium', 'min': 0, 'max': 3, 'chance': 5}, {'ore': 'rhodium', 'min': 0, 'max': 1, 'chance': 1}]}
]

WOODS = {
    'oak': {'name': 'Дуб', 'emoji': '🌳', 'price': 1000},
    'birch': {'name': 'Берёза', 'emoji': '🌿', 'price': 5000},
    'spruce': {'name': 'Ель', 'emoji': '🌲', 'price': 10000},
    'acacia': {'name': 'Акация', 'emoji': '🌴', 'price': 50000},
    'dark_oak': {'name': 'Тёмный дуб', 'emoji': '🌲', 'price': 100000},
    'jungle': {'name': 'Тропическое дерево', 'emoji': '🌴', 'price': 500000},
    'azalea': {'name': 'Азалия', 'emoji': '🌺', 'price': 1000000},
    'mangrove': {'name': 'Мангровое дерево', 'emoji': '🌵', 'price': 10000000},
    'cherry': {'name': 'Вишнёвое дерево', 'emoji': '🌸', 'price': 50000000},
    'ebony': {'name': 'Эбеновое дерево', 'emoji': '🖤', 'price': 0, 'price_candy': 1}
}

AXES = [
    {'id': 0, 'name': 'Деревянный топор', 'emoji': '🪓', 'price': 0, 'price_wood_type': None, 'price_wood_amount': 0, 'drops': [{'wood': 'oak', 'min': 1, 'max': 5}, {'wood': 'birch', 'min': 0, 'max': 1, 'chance': 30}]},
    {'id': 1, 'name': 'Каменный топор', 'emoji': '⛏️', 'price': 100000, 'price_wood_type': 'oak', 'price_wood_amount': 20, 'drops': [{'wood': 'birch', 'min': 3, 'max': 5}, {'wood': 'spruce', 'min': 1, 'max': 2}]},
    {'id': 2, 'name': 'Железный топор', 'emoji': '⚒️', 'price': 500000, 'price_wood_type': 'spruce', 'price_wood_amount': 15, 'drops': [{'wood': 'spruce', 'min': 3, 'max': 5}, {'wood': 'acacia', 'min': 1, 'max': 2}]},
    {'id': 3, 'name': 'Золотой топор', 'emoji': '🔨', 'price': 1000000, 'price_wood_type': 'acacia', 'price_wood_amount': 15, 'drops': [{'wood': 'acacia', 'min': 3, 'max': 5}, {'wood': 'dark_oak', 'min': 1, 'max': 3}]},
    {'id': 4, 'name': 'Алмазный топор', 'emoji': '💎', 'price': 5000000, 'price_wood_type': 'dark_oak', 'price_wood_amount': 20, 'drops': [{'wood': 'dark_oak', 'min': 1, 'max': 5}, {'wood': 'jungle', 'min': 1, 'max': 3}]},
    {'id': 5, 'name': 'Платиновый топор', 'emoji': '🔮', 'price': 25000000, 'price_wood_type': 'jungle', 'price_wood_amount': 10, 'drops': [{'wood': 'jungle', 'min': 3, 'max': 5}, {'wood': 'azalea', 'min': 1, 'max': 5}]},
    {'id': 6, 'name': 'Незеритовый топор', 'emoji': '⚔️', 'price': 300000000, 'price_wood_type': 'azalea', 'price_wood_amount': 20, 'drops': [{'wood': 'azalea', 'min': 5, 'max': 15}, {'wood': 'mangrove', 'min': 1, 'max': 3}, {'wood': 'cherry', 'min': 0, 'max': 1, 'chance': 5}, {'wood': 'cherry', 'min': 0, 'max': 2, 'chance': 0.1}]},
    {'id': 7, 'name': 'Секира звёзд', 'emoji': '🔱', 'price': 0, 'price_wood_type': None, 'price_candy': 20, 'drops': [{'wood': 'cherry', 'min': 5, 'max': 15}, {'wood': 'ebony', 'min': 0, 'max': 1, 'chance': 0.1}, {'wood': 'ebony', 'min': 0, 'max': 2, 'chance': 0.01}]}
]

PHONES = {
    1: {"name": "Nokia 3310", "price": 5000, "image": "phones/phone_1.jpg"},
    2: {"name": "Motorola Кнопочный", "price": 10000, "image": "phones/phone_2.jpg"},
    3: {"name": "BlackBerry", "price": 25000, "image": "phones/phone_3.jpg"},
    4: {"name": "DEXP", "price": 50000, "image": "phones/phone_4.jpg"},
    5: {"name": "Xiaomi Redmi 9", "price": 100000, "image": "phones/phone_5.jpg"},
    6: {"name": "POCO X3 Pro", "price": 250000, "image": "phones/phone_6.jpg"},
    7: {"name": "Samsung Galaxy A52", "price": 500000, "image": "phones/phone_7.jpg"},
    8: {"name": "Honor 50", "price": 1000000, "image": "phones/phone_8.jpg"},
    9: {"name": "Google Pixel 6", "price": 2500000, "image": "phones/phone_9.jpg"},
    10: {"name": "iPhone X", "price": 5000000, "image": "phones/phone_10.jpg"},
    11: {"name": "Samsung Galaxy S21", "price": 10000000, "image": "phones/phone_11.jpg"},
    12: {"name": "iPhone 11 Pro", "price": 25000000, "image": "phones/phone_12.jpg"},
    13: {"name": "iPhone 12 Pro Max", "price": 50000000, "image": "phones/phone_13.jpg"},
    14: {"name": "Samsung Galaxy S22 Ultra", "price": 100000000, "image": "phones/phone_14.jpg"},
    15: {"name": "iPhone 13 Pro Max", "price": 250000000, "image": "phones/phone_15.jpg"},
    16: {"name": "iPhone 15 Pro Max", "price": 500000000, "image": "phones/phone_16.jpg"},
    17: {"name": "Samsung Galaxy S24 Ultra", "price": 1000000000, "image": "phones/phone_17.jpg"},
    18: {"name": "Oppo Find X9 Ultra", "price": 2500000000, "image": "phones/phone_18.jpg"},
    19: {"name": "iPhone 17 Pro Max", "price": 5000000000, "image": "phones/phone_19.jpg"},
    20: {"name": "Vertu Signature Touch", "price": 10000000000, "image": "phones/phone_20.jpg"}
}

RP_COMMANDS = {
    'поцеловать': 'поцеловал(а)', 'обнять': 'обнял(а)', 'ударить': 'ударил(а)',
    'убить': 'убил(а)', 'кусь': 'сделал(а) кусь', 'лизь': 'лизнул(а)',
    'погладить': 'погладил(а)', 'пнуть': 'пнул(а)', 'дать пять': 'дал(а) пять',
    'пожать руку': 'пожал(а) руку', 'помахать': 'помахал(а)', 'плюнуть': 'плюнул(а) в',
    'расстрелять': 'расстрелял(а)', 'воскресить': 'воскресил(а)', 'вылечить': 'вылечил(а)',
    'отравить': 'отравил(а)', 'связать': 'связал(а)', 'развязать': 'развязал(а)',
    'укусить': 'укусил(а)', 'понюхать': 'понюхал(а)', 'потрогать': 'потрогал(а)',
    'облизать': 'облизал(а)', 'шлепнуть': 'шлепнул(а)', 'похлопать': 'похлопал(а)',
    'ущипнуть': 'ущипнул(а)', 'бросить': 'бросил(а)', 'поймать': 'поймал(а)',
    'спрятать': 'спрятал(а)', 'найти': 'нашел(а)', 'накормить': 'накормил(а)',
    'напоить': 'напоил(а)'
}

# ==================== ГЛОБАЛЬНЫЕ ПЕРЕХВАТЧИКИ И ФИЛЬТРЫ ====================

def is_ore_cmd(message):
    parts = safe_text_lower(message).split()
    return len(parts) >= 2 and parts[1] in [ore['name'].lower() for ore in ORES.values()]

def is_wood_cmd(message):
    parts = safe_text_lower(message).split()
    return len(parts) >= 2 and parts[1] in [w['name'].lower() for w in WOODS.values()]

def global_init_and_ban_check(message):
    if not hasattr(message, 'text') or message.text is None:
        return False
        
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    init_user(user_id, username)
    
    if is_banned(user_id) and not is_admin(user_id):
        text = message.text.lower()
        triggers = ('купить', 'продать', 'дать', 'кдать', 'выдать', 'квыдать', 'казино', 'монетка', 'банк', 'депозит', 'работа', 'ферм', 'бизнес', 'шахта', 'копать', 'лес', 'рубить', 'помощь', '/', '-')
        exact_triggers = ('баланс', 'б', 'balance', 'бонус', 'bonus', 'инв', 'инвентарь', 'уровень', 'опыт', 'м', 'машины', 'д', 'дома', 'кирки', 'топоры', 'энергия', 'к', 'крипта', 'курс руды', 'курс дерева', 'курс крипты', 'админ', 'профиль', 'п')
        
        if text.startswith(triggers) or text in exact_triggers:
            bot.send_message(message.chat.id, "❌ *Вы заблокированы в боте!*", parse_mode='Markdown')
            return True # Блокирует прохождение сообщения дальше
    return False

@bot.message_handler(func=global_init_and_ban_check)
def handle_banned_users(message):
    pass # Сообщение поглощается и не идет в другие обработчики

def global_callback_check(call):
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name
    init_user(user_id, username)
    if is_banned(user_id) and not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Вы заблокированы в боте!", show_alert=True)
        return True
    return False

@bot.callback_query_handler(func=global_callback_check)
def handle_banned_callbacks(call):
    pass


# ==================== ОСНОВНЫЕ КОМАНДЫ ====================

def check_level_up(user_id, chat_id, tg_first_name):
    """Проверяет и повышает уровень, отправляет поздравление отдельным сообщением."""
    user_id = str(user_id)
    user_data = users[user_id]
    start_level = user_data['level']
    
    # Цикл while для случая если получили много опыта сразу
    while user_data['experience'] >= exp_for_next_level(user_data['level']):
        user_data['experience'] -= exp_for_next_level(user_data['level'])
        user_data['level'] += 1
    
    levels_gained = user_data['level'] - start_level
    
    if levels_gained > 0:
        save_users_data()
        mention = user_mention(user_id, tg_first_name)
        new_level = user_data['level']
        
        # Проверяем открытие новых возможностей
        unlocks = []
        for lvl in range(start_level + 1, new_level + 1):
            if lvl == 10:
                unlocks.append("⛏️ Доступ в *Шахту*")
            if lvl == 25:
                unlocks.append("🌲 Доступ в *Лес*")
            for job in jobs:
                if job['min_level'] == lvl:
                    unlocks.append(f"💼 Работа: {job['emoji']} {job['name']}")
        
        unlocks_text = ""
        if unlocks:
            unlocks_text = "\n\n🔓 *Разблокировано:*\n" + "\n".join([f"• {u}" for u in unlocks])
        
        bot.send_message(
            chat_id, 
            f"🎉 *Поздравляем,* {mention}!\n\n"
            f"📊 Вы достигли *{new_level}* уровня!{unlocks_text}",
            parse_mode='Markdown'
        )
        return True
    return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('➕ Добавить в чат', url='https://t.me/TheLunaGameBot?startgroup=true'))
    
    welcome_message = f"""
☃️ *Пᴩиʙᴇᴛ,* {mention}! 🎉

🤖 Я - *Luna*, ᴛʙᴏй ʙᴇᴩный ᴋᴏʍᴨᴀньᴏн ʙ ʍиᴩᴇ ɜᴀᴩᴀбᴏᴛᴋᴀ!

💰 В ʍᴏᴇʍ ᴀᴩᴄᴇнᴀᴧᴇ ʍнᴏжᴇᴄᴛʙᴏ ʙᴏɜʍᴏжнᴏᴄᴛᴇй:
  • 💼 Рᴀбᴏᴛᴀй и ɜᴀᴩᴀбᴀтыʙᴀй ʙиᴩᴛуᴀᴧьныᴇ дᴇньᴦи
  • 🏆 Пᴏʙышᴀй ᴄʙᴏй уᴩᴏʙᴇнь и ᴏᴛᴋᴩыʙᴀй нᴏʙыᴇ ᴨᴩᴏфᴇᴄᴄии
  • 🎁 Пᴏᴧучᴀй ᴇжᴇднᴇʙныᴇ бᴏнуᴄы и ᴨᴏдᴀᴩᴋи
  • 🔄 Уᴨᴩᴀʙᴧяй ᴄʙᴏиʍ ᴨᴩᴏфиᴧᴇʍ и ᴨᴩᴏᴦᴩᴇᴄᴄᴏʍ

⏳ Пᴏᴦᴩуɜиᴄь ʙ ʍиᴩ ʙиᴩᴛуᴀᴧьнᴏй эᴋᴏнᴏʍиᴋи и ᴄᴛᴀнь ᴄᴀʍыʍ уᴄᴨᴇшныʍ!

🌟 Пᴩияᴛнᴏй иᴦᴩы и бᴏᴧьших дᴏхᴏдᴏʙ!
    """
    bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['помощь', 'help', '/help'])
def help_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👨‍💻 Основные", callback_data="help_main"),
        types.InlineKeyboardButton("💼 Заработок", callback_data="help_earn")
    )
    markup.add(
        types.InlineKeyboardButton("🏠 Имущество", callback_data="help_property"),
        types.InlineKeyboardButton("🎲 Игры", callback_data="help_games")
    )
    markup.add(
        types.InlineKeyboardButton("🎟 Промокоды", callback_data="help_promo")
    )
    
    bot.send_message(message.chat.id, f"👋 Привет, {mention}! Выбери нужную категорию помощи ниже:", parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('help_'))
def help_callback(call):
    category = call.data.split('_')[1]
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👨‍💻 Основные", callback_data="help_main"),
        types.InlineKeyboardButton("💼 Заработок", callback_data="help_earn")
    )
    markup.add(
        types.InlineKeyboardButton("🏠 Имущество", callback_data="help_property"),
        types.InlineKeyboardButton("🎲 Игры", callback_data="help_games")
    )
    markup.add(
        types.InlineKeyboardButton("🎟 Промокоды", callback_data="help_promo")
    )
    
    if category == 'main':
        text = "👨‍💻 *Основные команды:*\n\n" \
               "• `Профиль` / `П` - Ваш паспорт игрока\n" \
               "• `Баланс` / `Б` - Ваш счет\n" \
               "• `Инвентарь` / `Инв` - Ваши ресурсы\n" \
               "• `Уровень` / `Опыт` - Ваш прогресс\n" \
               "• `Сменить ник [имя]` - Изменить никнейм\n" \
               "• `Бонус` - Ежедневная награда\n" \
               "• `Крипта` - Ваш крипто-портфель\n" \
               "• `Криптобонус` - Ежедневная крипта\n" \
               "• `Энергия` - Узнать запас энергии\n" \
               "• `Дать [сумма]` - Передать деньги\n" \
               "• `Кдать [сумма]` - Передать конфеты"
    elif category == 'earn':
        text = "💼 *Команды заработка:*\n\n" \
               "• `Работа` / `Устроиться` / `Работать`\n" \
               "• `Бизнесы` / `Мой бизнес` / `Доход`\n" \
               "• `Шахта` / `Копать` - Добыча руды\n" \
               "• `Лес` / `Рубить` - Добыча дерева\n" \
               "• `Фермы` / `Моя ферма` - Майнинг\n\n" \
               "📊 *Экономика и Курсы:*\n" \
               "• `Курс руды` - Курс продажи руд\n" \
               "• `Курс дерева` - Курс продажи деревьев\n" \
               "• `Курс крипты` - Текущий курс криптовалют"
    elif category == 'property':
        text = "🏠 *Имущество:*\n\n" \
               "• `Дома` / `Купить дом [номер]` / `Мой дом`\n" \
               "• `Машины` / `Купить машину [номер]` / `Моя машина`\n" \
               "• `Телефоны` / `Купить телефон [номер]` / `Мой телефон`\n\n" \
               "🏦 *Банковская система:*\n" \
               "• `Банк` - Банковский счет\n" \
               "• `Банк положить/снять [сумма]`\n" \
               "• `Депозит положить/снять [сумма]` - Вклад под 1% в час"
    elif category == 'games':
        text = "🎲 *Игры и развлечения:*\n\n" \
               "• `Казино [ставка]` - Крутить рулетку (множители от x0 до x10)\n" \
               "• `Монетка [орёл/решка] [ставка]` - Угадай сторону монеты (x2)\n\n" \
               "🎭 *Ролевая игра:*\n" \
               "• `РП` / `РП команды` - Список всех действий"
    elif category == 'promo':
        text = "🎟 *Промокоды:*\n\n" \
               "• `Промо [название]` - Активировать промокод\n\n" \
               "⚠️ *Требования:*\n" \
               "• Минимальный уровень: 15\n" \
               "• Каждый промокод можно активировать только 1 раз\n\n" \
               "💡 *Где брать промокоды?*\n" \
               "Следите за новостями и анонсами от администрации!"
               
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='Markdown', reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['баланс', 'б', 'balance'])
def balance(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    user_data = users[user_id]
    
    prefix_emoji = "👤" if user_data['prefix'] == 'Игрок' else "👨‍💻"
    total_balance = user_data['balance'] + user_data['bank_balance'] + user_data.get('deposit_balance', 0)
    
    balance_info = f"""
💼 {mention}, *вот данные о ваших средствах:*

👤 *Ник в игре:* {user_data['nickname']}
🏷️ *Префикс:* {prefix_emoji} {user_data['prefix']}

💰 *Баланс:* {format_number(user_data['balance'])} ₽
🏦 *В банке:* {format_number(user_data['bank_balance'])} ₽
📈 *На депозите:* {format_number(user_data.get('deposit_balance', 0))} ₽
🍬 *Конфеты:* {user_data['candy']}

💵 *Всего средств:* {format_number(total_balance)} ₽
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🎁 Бонус', callback_data='get_bonus'))
    bot.send_message(message.chat.id, balance_info, parse_mode='Markdown', reply_markup=markup)


# ==================== БОНУСЫ И ПЕРЕВОДЫ ====================

def give_bonus(chat_id, user_id_int, tg_first_name):
    user_id = str(user_id_int)
    current_time = time.time()
    user_data = users[user_id]
    mention = user_mention(user_id, tg_first_name)
    
    if current_time - user_data.get('last_bonus_time', 0) < 86400:
        rem_time = 86400 - (current_time - user_data.get('last_bonus_time', 0))
        bot.send_message(chat_id, f"⏱ *Бонус еще не доступен!*\nЧерез *{int(rem_time // 3600)} ч. {int((rem_time % 3600) // 60)} мин.*", parse_mode='Markdown')
        return
    
    money_bonus = random.randint(5000, 25000)
    exp_bonus = random.randint(1, 5)
    user_data['balance'] += money_bonus
    user_data['experience'] += exp_bonus
    user_data['last_bonus_time'] = current_time
    save_users_data()
    
    bot.send_message(chat_id, f"🎁 {mention}, *ежедневный бонус получен!*\n\n💰 *Получено денег:* {format_number(money_bonus)} ₽\n⭐ *Получено опыта:* +{exp_bonus}", parse_mode='Markdown')
    
    # Проверка повышения уровня (отдельное сообщение)
    check_level_up(user_id, chat_id, tg_first_name)

@bot.callback_query_handler(func=lambda call: call.data == 'get_bonus')
def bonus_button_callback(call):
    bot.answer_callback_query(call.id)
    give_bonus(call.message.chat.id, call.from_user.id, call.from_user.first_name)

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['бонус', 'bonus'])
def bonus_command(message):
    give_bonus(message.chat.id, message.from_user.id, message.from_user.first_name)

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('дать '))
def transfer_money(message):
    user_id = str(message.from_user.id)
    parts = message.text.split()
    mention = user_mention(user_id, message.from_user.first_name)

    if len(parts) < 2:
        return bot.send_message(message.chat.id, f"❌ {mention}, формат: `дать [сумма]` (в ответ) или `дать [сумма] @username`", parse_mode='Markdown')
    
    try:
        amount = int(parts[1])
        if amount <= 0: return bot.send_message(message.chat.id, f"❌ {mention}, сумма должна быть больше 0!", parse_mode='Markdown')
    except ValueError:
        return bot.send_message(message.chat.id, f"❌ {mention}, некорректная сумма!", parse_mode='Markdown')

    if users[user_id]['balance'] < amount:
        return bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!", parse_mode='Markdown')

    target_id = None
    target_name = None

    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
        target_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
        init_user(target_id, target_name)
    elif len(parts) >= 3:
        target_id, target_name = find_user_by_identifier(parts[2])
    
    if not target_id:
        return bot.send_message(message.chat.id, f"❌ {mention}, пользователь не найден!", parse_mode='Markdown')
    if target_id == user_id:
        return bot.send_message(message.chat.id, f"❌ {mention}, нельзя передать деньги самому себе!", parse_mode='Markdown')

    users[user_id]['balance'] -= amount
    users[target_id]['balance'] += amount
    save_users_data()

    bot.send_message(message.chat.id, f"💸 {mention} перевел {format_number(amount)} ₽ пользователю {user_mention(target_id, target_name)}!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('кдать '))
def transfer_candy(message):
    user_id = str(message.from_user.id)
    parts = message.text.split()
    mention = user_mention(user_id, message.from_user.first_name)

    if len(parts) < 2:
        return bot.send_message(message.chat.id, f"❌ {mention}, формат: `кдать [сумма]` (в ответ) или `кдать [сумма] @username`", parse_mode='Markdown')
    
    try:
        amount = int(parts[1])
        if amount <= 0: return bot.send_message(message.chat.id, f"❌ {mention}, сумма должна быть больше 0!", parse_mode='Markdown')
    except ValueError:
        return bot.send_message(message.chat.id, f"❌ {mention}, некорректная сумма!", parse_mode='Markdown')

    if users[user_id]['candy'] < amount:
        return bot.send_message(message.chat.id, f"❌ {mention}, недостаточно конфет!", parse_mode='Markdown')

    target_id = None
    target_name = None

    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
        target_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
        init_user(target_id, target_name)
    elif len(parts) >= 3:
        target_id, target_name = find_user_by_identifier(parts[2])
    
    if not target_id:
        return bot.send_message(message.chat.id, f"❌ {mention}, пользователь не найден!", parse_mode='Markdown')
    if target_id == user_id:
        return bot.send_message(message.chat.id, f"❌ {mention}, нельзя передать конфеты самому себе!", parse_mode='Markdown')

    users[user_id]['candy'] -= amount
    users[target_id]['candy'] += amount
    save_users_data()

    bot.send_message(message.chat.id, f"🍬 {mention} передал {amount} конфет пользователю {user_mention(target_id, target_name)}!", parse_mode='Markdown')


# ==================== ИНВЕНТАРЬ И УРОВЕНЬ ====================

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['уровень', 'опыт'])
def show_level(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    if check_level_up(user_id, message.chat.id, message.from_user.first_name):
        pass
    
    lvl = users[user_id]['level']
    exp = users[user_id]['experience']
    need = exp_for_next_level(lvl)
    progress = int(exp / need * 100) if need > 0 else 100
    
    text = f"{mention}, *информация об уровне:*\n\n📊 *Уровень:* {lvl}\n✨ *Опыт:* {exp}/{need}\n🔄 *Прогресс:* {progress}%"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith(('сменить ник', 'ник ')))
def change_nickname(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    text_lower = safe_text_lower(message)
    new_nick = message.text[11:].strip() if text_lower.startswith('сменить ник') else message.text[3:].strip()
    if not new_nick and ' ' in message.text:
        new_nick = message.text[message.text.find(' ')+1:].strip()
        
    if new_nick:
        users[user_id]['nickname'] = new_nick
        save_users_data()
        bot.send_message(message.chat.id, f"✅ {mention}, вы сменили игровой ник на *{new_nick}*", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"❌ {mention}, вы не указали новый никнейм. Используйте: `Сменить ник [имя]`", parse_mode='Markdown')


# ==================== БАНК И ДЕПОЗИТЫ ====================

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['банк', 'bank'])
def bank_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    user_data = users[user_id]
    
    bank_info = f"""
🏦 *Банк игрока* {mention}

💰 *На руках:* {format_number(user_data['balance'])} ₽
💳 *В банке:* {format_number(user_data['bank_balance'])} ₽
📈 *На депозите (под 1% в час):* {format_number(user_data.get('deposit_balance', 0))} ₽

✅ В банк: `Банк положить [сумма]`
⛔ Из банка: `Банк снять [сумма]`
📈 На депозит: `Депозит положить [сумма]`
📉 С депозита: `Депозит снять [сумма]`
    """
    bot.send_message(message.chat.id, bank_info, parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('банк положить'))
def deposit_money(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        amount = int(message.text.split()[2])
        if amount > 0 and users[user_id]['balance'] >= amount:
            users[user_id]['balance'] -= amount
            users[user_id]['bank_balance'] += amount
            save_users_data()
            bot.send_message(message.chat.id, f"✅ {mention}, вы внесли {format_number(amount)} ₽ в банк!\n", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ {mention}, недостаточно денег или сумма неверна!", parse_mode='Markdown')
    except: bot.send_message(message.chat.id, f"❌ {mention}, укажите корректную сумму!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('банк снять'))
def withdraw_money(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        amount = int(message.text.split()[2])
        if amount > 0 and users[user_id]['bank_balance'] >= amount:
            users[user_id]['bank_balance'] -= amount
            users[user_id]['balance'] += amount
            save_users_data()
            bot.send_message(message.chat.id, f"✅ {mention}, вы сняли {format_number(amount)} ₽ из банка!\n", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ {mention}, недостаточно денег в банке!", parse_mode='Markdown')
    except: bot.send_message(message.chat.id, f"❌ {mention}, укажите корректную сумму!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('депозит положить'))
def deposit_put(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        amount = int(message.text.split()[2])
        if amount > 0 and users[user_id]['balance'] >= amount:
            users[user_id]['balance'] -= amount
            users[user_id]['deposit_balance'] += amount
            save_users_data()
            bot.send_message(message.chat.id, f"💰 {mention}, вы положили {format_number(amount)} ₽ на депозит под 1% в час!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!", parse_mode='Markdown')
    except: bot.send_message(message.chat.id, f"❌ {mention}, формат: `Депозит положить [сумма]`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('депозит снять'))
def deposit_get(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        amount = int(message.text.split()[2])
        dep = users[user_id].get('deposit_balance', 0)
        if amount > 0 and dep >= amount:
            users[user_id]['deposit_balance'] -= amount
            users[user_id]['balance'] += amount
            save_users_data()
            bot.send_message(message.chat.id, f"✅ {mention}, вы сняли {format_number(amount)} ₽ с депозита!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ {mention}, на депозите нет такой суммы!", parse_mode='Markdown')
    except: bot.send_message(message.chat.id, f"❌ {mention}, формат: `Депозит снять [сумма]`", parse_mode='Markdown')

# ==================== СИСТЕМА ПРОМОКОДОВ ====================

@bot.message_handler(func=lambda m: safe_text_lower(m) in ['промо инфо', 'промокод инфо'] and is_admin(m.from_user.id))
def promo_info(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    info_text = f"""
🎟 {mention}, *информация о промокодах:*

📝 *Создание промокода:*
`промо создать [название] [тип] [сумма] [активации] [описание]`

📋 *Аттрибуты:*
• `название` — уникальное имя промокода
• `тип` — 0 = деньги 💵, 1 = конфеты 🍬
• `сумма` — награда за активацию
• `активации` — сколько раз можно активировать
• `описание` — необязательно, текст промокода

💸 *Стоимость создания:*
Сумма × Активации = Итого списывается

📌 *Пример:*
`промо создать ЛЕТНИЙ 0 10000 5 Летний бонус!`
Создаст промокод *ЛЕТНИЙ* на 10.000₽, 5 активаций.
С вас спишется: 10.000 × 5 = 50.000₽

🗑 *Удаление промокода:*
`промо удалить [название]`

📊 *Список промокодов:*
`промо список`

👤 *Активация игроками:*
`промо [название]` — требуется 15+ уровень
    """
    bot.send_message(message.chat.id, info_text, parse_mode='Markdown')


@bot.message_handler(func=lambda m: safe_text_lower(m).startswith(('промо создать ', 'промокод создать ')) and is_admin(m.from_user.id))
def promo_create(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    # Убираем команду из текста
    text = message.text
    if text.lower().startswith('промокод создать '):
        args = text[17:].strip()
    else:
        args = text[13:].strip()
    
    parts = args.split()
    
    if len(parts) < 4:
        return bot.send_message(message.chat.id, f"❌ {mention}, недостаточно аргументов!\n\nФормат: `промо создать [название] [тип] [сумма] [активации] [описание]`\n\nИспользуйте `промо инфо` для справки.", parse_mode='Markdown')
    
    try:
        promo_name = parts[0].upper()
        promo_type = int(parts[1])  # 0 = деньги, 1 = конфеты
        promo_amount = int(parts[2])
        promo_uses = int(parts[3])
        promo_desc = ' '.join(parts[4:]) if len(parts) > 4 else None
        
        # Валидация
        if promo_type not in [0, 1]:
            return bot.send_message(message.chat.id, f"❌ {mention}, тип должен быть 0 (деньги) или 1 (конфеты)!", parse_mode='Markdown')
        if promo_amount <= 0:
            return bot.send_message(message.chat.id, f"❌ {mention}, сумма должна быть больше 0!", parse_mode='Markdown')
        if promo_uses <= 0:
            return bot.send_message(message.chat.id, f"❌ {mention}, количество активаций должно быть больше 0!", parse_mode='Markdown')
        if promo_name in promos:
            return bot.send_message(message.chat.id, f"❌ {mention}, промокод с таким названием уже существует!", parse_mode='Markdown')
        
        # Расчёт стоимости
        total_cost = promo_amount * promo_uses
        
        # Проверка баланса и списание
        if promo_type == 0:  # Деньги
            if users[user_id]['balance'] < total_cost:
                return bot.send_message(message.chat.id, f"❌ {mention}, недостаточно денег!\n\nНужно: {format_number(total_cost)} ₽\nУ вас: {format_number(users[user_id]['balance'])} ₽", parse_mode='Markdown')
            users[user_id]['balance'] -= total_cost
            currency_emoji = "💵"
            currency_name = "₽"
        else:  # Конфеты
            if users[user_id]['candy'] < total_cost:
                return bot.send_message(message.chat.id, f"❌ {mention}, недостаточно конфет!\n\nНужно: {total_cost} 🍬\nУ вас: {users[user_id]['candy']} 🍬", parse_mode='Markdown')
            users[user_id]['candy'] -= total_cost
            currency_emoji = "🍬"
            currency_name = "конфет"
        
        # Создание промокода
        promos[promo_name] = {
            'type': promo_type,
            'amount': promo_amount,
            'uses_left': promo_uses,
            'max_uses': promo_uses,
            'description': promo_desc,
            'creator_id': user_id,
            'activated_by': [],
            'created_time': time.time()
        }
        
        save_users_data()
        save_promo_data()
        
        # Сообщение о списании
        if promo_type == 0:
            cost_text = f"💸 С вас списано {format_number(total_cost)} ₽ на создание промокода."
        else:
            cost_text = f"🍬 С вас списано *{total_cost}* конфет на создание промокода."
        
        bot.send_message(message.chat.id, cost_text, parse_mode='Markdown')
        
        # Информация о промокоде
        type_text = "💵 Деньги" if promo_type == 0 else "🍬 Конфеты"
        amount_text = f"{format_number(promo_amount)} ₽" if promo_type == 0 else f"{promo_amount} 🍬"
        desc_text = f"\n📝 *Описание:* {promo_desc}" if promo_desc else ""
        
        info_msg = f"""
🎟 {mention}, вы создали промокод!

📌 *Название:* `{promo_name}`
🎁 *Тип награды:* {type_text}
💰 *Сумма:* {amount_text}
🔢 *Активаций:* {promo_uses}{desc_text}

💡 Игроки могут активировать командой: `промо {promo_name}`
        """
        bot.send_message(message.chat.id, info_msg, parse_mode='Markdown')
        
    except ValueError:
        bot.send_message(message.chat.id, f"❌ {mention}, некорректные значения! Проверьте правильность аргументов.\n\nИспользуйте `промо инфо` для справки.", parse_mode='Markdown')


@bot.message_handler(func=lambda m: safe_text_lower(m).startswith(('промо удалить ', 'промокод удалить ')) and is_admin(m.from_user.id))
def promo_delete(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    parts = message.text.split()
    if len(parts) < 3:
        return bot.send_message(message.chat.id, f"❌ {mention}, укажите название промокода!", parse_mode='Markdown')
    
    promo_name = parts[2].upper()
    
    if promo_name not in promos:
        return bot.send_message(message.chat.id, f"❌ {mention}, промокод `{promo_name}` не найден!", parse_mode='Markdown')
    
    # Возврат оставшихся средств
    promo = promos[promo_name]
    refund = promo['amount'] * promo['uses_left']
    
    if promo['type'] == 0:
        users[user_id]['balance'] += refund
        refund_text = f"💰 Возвращено {format_number(refund)} ₽ (неиспользованные активации)"
    else:
        users[user_id]['candy'] += refund
        refund_text = f"🍬 Возвращено *{refund}* конфет (неиспользованные активации)"
    
    del promos[promo_name]
    save_users_data()
    save_promo_data()
    
    bot.send_message(message.chat.id, f"✅ {mention}, промокод `{promo_name}` удалён!\n\n{refund_text}", parse_mode='Markdown')


@bot.message_handler(func=lambda m: safe_text_lower(m) in ['промо список', 'промокод список'] and is_admin(m.from_user.id))
def promo_list(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    if not promos:
        return bot.send_message(message.chat.id, f"📭 {mention}, активных промокодов нет.", parse_mode='Markdown')
    
    text = f"🎟 {mention}, *список промокодов:*\n\n"
    
    for name, data in promos.items():
        type_emoji = "💵" if data['type'] == 0 else "🍬"
        amount_text = f"{format_number(data['amount'])} ₽" if data['type'] == 0 else f"{data['amount']} 🍬"
        text += f"• `{name}` — {type_emoji} {amount_text} | Осталось: {data['uses_left']}/{data['max_uses']}\n"
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('промо ') and not any(safe_text_lower(m).startswith(x) for x in ['промо создать', 'промо удалить', 'промо список', 'промо инфо']))
def promo_activate(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    # Проверка уровня
    if users[user_id]['level'] < 15:
        return bot.send_message(message.chat.id, f"❌ {mention}, для активации промокодов нужен *15 уровень*!\n\n📊 Ваш уровень: {users[user_id]['level']}", parse_mode='Markdown')
    
    parts = message.text.split()
    if len(parts) < 2:
        return bot.send_message(message.chat.id, f"❌ {mention}, укажите название промокода!\n\nПример: `промо НАЗВАНИЕ`", parse_mode='Markdown')
    
    promo_name = parts[1].upper()
    
    if promo_name not in promos:
        return bot.send_message(message.chat.id, f"❌ {mention}, промокод `{promo_name}` не найден или истёк!", parse_mode='Markdown')
    
    promo = promos[promo_name]
    
    # Проверка на повторную активацию
    if user_id in promo['activated_by']:
        return bot.send_message(message.chat.id, f"❌ {mention}, вы уже активировали этот промокод!", parse_mode='Markdown')
    
    # Проверка на оставшиеся активации
    if promo['uses_left'] <= 0:
        return bot.send_message(message.chat.id, f"❌ {mention}, промокод `{promo_name}` больше недействителен!", parse_mode='Markdown')
    
    # Активация промокода
    if promo['type'] == 0:
        users[user_id]['balance'] += promo['amount']
        reward_text = f"💵 {format_number(promo['amount'])} ₽"
    else:
        users[user_id]['candy'] += promo['amount']
        reward_text = f"🍬 {promo['amount']} конфет"
    
    promo['uses_left'] -= 1
    promo['activated_by'].append(user_id)
    
    # Удаление промокода если активации закончились
    if promo['uses_left'] <= 0:
        del promos[promo_name]
    
    save_users_data()
    save_promo_data()
    
    desc_text = f"\n📝 {promo.get('description')}" if promo.get('description') else ""
    
    bot.send_message(message.chat.id, f"🎉 {mention}, промокод активирован!\n\n🎁 *Награда:* {reward_text}{desc_text}", parse_mode='Markdown')

# ==================== МАШИНЫ И ДОМА ====================

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['машины', 'машина', 'м'])
def cars_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    cars_text = f"{mention}, *доступные машины:*\n\n"
    for car_id, info in CARS.items():
        cars_text += f"🚗 {car_id}. {info['name']} - {format_number(info['price'])} ₽\n"
    cars_text += "\n🛒 Для покупки машины введите: `Купить машину [номер]`"
    bot.send_message(message.chat.id, cars_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('купить машину'))
def buy_car_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        car_id = int(message.text.split()[2])
        if car_id in CARS:
            if users[user_id].get('car'):
                bot.send_message(message.chat.id, f"🚗 {mention}, у вас уже есть машина. Сначала продайте её.", parse_mode='Markdown')
            elif users[user_id]['balance'] >= CARS[car_id]['price']:
                users[user_id]['balance'] -= CARS[car_id]['price']
                users[user_id]['car'] = car_id
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, вы купили машину 🚗 *{CARS[car_id]['name']}* за {format_number(CARS[car_id]['price'])} ₽!", parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!", parse_mode='Markdown')
        else: bot.send_message(message.chat.id, f"❌ {mention}, машины с таким номером нет.", parse_mode='Markdown')
    except: bot.send_message(message.chat.id, f"❌ {mention}, формат: `Купить машину [номер]`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'моя машина')
def my_car_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if not users[user_id].get('car'):
        return bot.send_message(message.chat.id, f"❌ {mention}, у вас пока нет машины.", parse_mode='Markdown')
    
    car = CARS[users[user_id]['car']]
    caption = f"🚗 *{car['name']}*\n💰 *Стоимость:* {format_number(car['price'])} ₽\n\n💡 Чтобы продать: `Продать машину`"
    try:
        with open(car['image'], 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=caption, parse_mode='Markdown')
    except: bot.send_message(message.chat.id, caption, parse_mode='Markdown')
                         
@bot.message_handler(func=lambda message: safe_text_lower(message) == 'продать машину')
def sell_car_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if not users[user_id].get('car'):
        return bot.send_message(message.chat.id, f"❌ {mention}, у вас нет машины для продажи.", parse_mode='Markdown')
    
    car = CARS[users[user_id]['car']]
    sell_price = int(car['price'] * 0.7)
    users[user_id]['balance'] += sell_price
    users[user_id]['car'] = None
    save_users_data()
    bot.send_message(message.chat.id, f"✅ {mention}, вы продали машину 🚗 *{car['name']}* за {format_number(sell_price)} ₽!", parse_mode='Markdown')              

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['дома', 'дом', 'д'])
def houses_list(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    houses_text = f"{mention}, *доступные дома:*\n\n"
    for i, house in enumerate(houses, 1):
        houses_text += f"{house['emoji']} {i}. {house['name']} - {format_number(house['price'])} ₽\n"
    houses_text += "\n🛒 Для покупки дома введите: `Купить дом [номер]`"
    bot.send_message(message.chat.id, houses_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('купить дом'))
def buy_house(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        h_num = int(message.text.split()[2]) - 1
        if 0 <= h_num < len(houses):
            if users[user_id].get('house') is not None:
                bot.send_message(message.chat.id, f"❌ {mention}, у вас уже есть дом.", parse_mode='Markdown')
            elif users[user_id]['balance'] >= houses[h_num]['price']:
                users[user_id]['balance'] -= houses[h_num]['price']
                users[user_id]['house'] = h_num
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, вы купили дом {houses[h_num]['emoji']} *{houses[h_num]['name']}* за {format_number(houses[h_num]['price'])} ₽!", parse_mode='Markdown')
            else: bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!", parse_mode='Markdown')
        else: bot.send_message(message.chat.id, f"❌ {mention}, дома с таким номером нет.", parse_mode='Markdown')
    except: bot.send_message(message.chat.id, f"❌ {mention}, формат: `Купить дом [номер]`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('мой дом'))
def my_house(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['house'] is None:
        return bot.send_message(message.chat.id, f"❌ {mention}, у вас нет дома!", parse_mode='Markdown')
    
    house_id = users[user_id]['house']
    house = houses[house_id]
    caption = f"🏠 *{house['name']}*\n💰 *Стоимость:* {format_number(house['price'])} ₽\n\n💡 Чтобы продать: `Продать дом`"
    try:
        with open(f"houses/house_{house_id + 1}.jpg", "rb") as photo:
            bot.send_photo(message.chat.id, photo, caption=caption, parse_mode='Markdown')
    except: bot.send_message(message.chat.id, caption, parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'продать дом')
def sell_house(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['house'] is None:
        return bot.send_message(message.chat.id, f"❌ {mention}, у вас нет дома для продажи!", parse_mode='Markdown')
        
    house = houses[users[user_id]['house']]
    sell_price = int(house['price'] * 0.95)
    users[user_id]['balance'] += sell_price
    users[user_id]['house'] = None
    save_users_data()
    bot.send_message(message.chat.id, f"✅ {mention}, вы продали дом {house['emoji']} *{house['name']}* и получили {format_number(sell_price)} ₽", parse_mode='Markdown')

# ==================== ТЕЛЕФОНЫ ====================

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['телефоны', 'телефон'])
def phones_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    txt = f"{mention}, *доступные телефоны:*\n\n"
    for p_id, info in PHONES.items():
        txt += f"📱 {p_id}. {info['name']} - {format_number(info['price'])} ₽\n"
    txt += "\n🛒 Для покупки введите: `Купить телефон [номер]`"
    bot.send_message(message.chat.id, txt, parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('купить телефон'))
def buy_phone_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        p_id = int(message.text.split()[2])
        if p_id in PHONES:
            if users[user_id].get('phone'):
                bot.send_message(message.chat.id, f"📱 {mention}, у вас уже есть телефон. Сначала продайте его.", parse_mode='Markdown')
            elif users[user_id]['balance'] >= PHONES[p_id]['price']:
                users[user_id]['balance'] -= PHONES[p_id]['price']
                users[user_id]['phone'] = p_id
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, вы купили телефон 📱 *{PHONES[p_id]['name']}* за {format_number(PHONES[p_id]['price'])} ₽!", parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!", parse_mode='Markdown')
        else: bot.send_message(message.chat.id, f"❌ {mention}, телефона с таким номером нет.", parse_mode='Markdown')
    except: bot.send_message(message.chat.id, f"❌ {mention}, формат: `Купить телефон [номер]`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'мой телефон')
def my_phone_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if not users[user_id].get('phone'):
        return bot.send_message(message.chat.id, f"❌ {mention}, у вас пока нет телефона.", parse_mode='Markdown')
    
    phone = PHONES[users[user_id]['phone']]
    caption = f"📱 *{phone['name']}*\n💰 *Стоимость:* {format_number(phone['price'])} ₽\n\n💡 Чтобы продать: `Продать телефон`"
    try:
        with open(phone['image'], 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=caption, parse_mode='Markdown')
    except: bot.send_message(message.chat.id, caption, parse_mode='Markdown')
                         
@bot.message_handler(func=lambda message: safe_text_lower(message) == 'продать телефон')
def sell_phone_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if not users[user_id].get('phone'):
        return bot.send_message(message.chat.id, f"❌ {mention}, у вас нет телефона для продажи.", parse_mode='Markdown')
    
    phone = PHONES[users[user_id]['phone']]
    sell_price = int(phone['price'] * 0.7)
    users[user_id]['balance'] += sell_price
    users[user_id]['phone'] = None
    save_users_data()
    bot.send_message(message.chat.id, f"✅ {mention}, вы продали телефон 📱 *{phone['name']}* за {format_number(sell_price)} ₽!", parse_mode='Markdown')

# ==================== РП КОМАНДЫ ====================

@bot.message_handler(func=lambda m: safe_text_lower(m) in ['рп', 'рп команды'])
def rp_commands_list(message):
    cmds = "\n".join([f"• `{cmd}`" for cmd in RP_COMMANDS.keys()])
    bot.send_message(message.chat.id, f"🎭 *Доступные РП команды:*\n\n{cmds}\n\n💡 *Использование:* `Поцеловать @username` или реплай.", parse_mode='Markdown')

@bot.message_handler(func=lambda m: any(safe_text_lower(m).startswith(cmd + ' ') or safe_text_lower(m) == cmd for cmd in RP_COMMANDS))
def handle_rp(message):
    text = safe_text_lower(message)
    cmd = next((c for c in RP_COMMANDS if text.startswith(c + ' ') or text == c), None)
    if not cmd: return

    user_id = str(message.from_user.id)
    actor_mention = user_mention(user_id, users[user_id]['nickname']) 

    target_id, target_name = None, None
    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
        init_user(target_id, message.reply_to_message.from_user.first_name)
        target_name = users[target_id]['nickname']
    elif len(message.text.split()) > len(cmd.split()):
        target_identifier = message.text.split(maxsplit=len(cmd.split()))[-1]
        target_id, _ = find_user_by_identifier(target_identifier)
        if target_id:
            target_name = users[target_id]['nickname']

    if target_id:
        if target_id == user_id:
            return bot.send_message(message.chat.id, f"❌ Нельзя использовать РП команду на себе!", parse_mode='Markdown')
        
        target_mention = user_mention(target_id, target_name)
        action = RP_COMMANDS[cmd]
        bot.send_message(message.chat.id, f"🎭 {actor_mention} {action} {target_mention}", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"❌ Укажите пользователя (сделайте ответ на сообщение или укажите @username).", parse_mode='Markdown')

# ==================== ШАХТА, ЛЕС, РУДЫ И ДЕРЕВО ====================

# --- ГЕНЕРАТОРЫ ТЕКСТОВ (Для кнопок и текстовых команд) ---

def get_inventory_text(user_id, tg_first_name, mode='all'):
    mention = user_mention(user_id, tg_first_name)
    text = f"{mention}, *ваш инвентарь:*\n\n🍬 *Конфеты:* {users[user_id]['candy']}\n\n"
    total_value = 0
    
    if mode in ['all', 'mine']:
        text += "⛏️ *Ваши руды:*\n"
        total_ore = 0
        for ore_id, ore in ORES.items():
            amt = users[user_id]['ores'][ore_id]
            val = amt * ore['price']
            total_ore += val
            text += f"{ore['emoji']} *{ore['name']}:* {amt} шт. (≈ {format_number(val)} ₽)\n"
        text += f"\n💰 *Стоимость руд:* {format_number(total_ore)} ₽\n\n"
        total_value += total_ore
        
    if mode in ['all', 'forest']:
        text += "🌲 *Ваши деревья:*\n"
        total_wood = 0
        for w_id, w in WOODS.items():
            amt = users[user_id]['woods'][w_id]
            price = w.get('price', 0)
            val = amt * price
            total_wood += val
            price_txt = f"{w['price_candy']} 🍬" if w.get('price_candy') else f"{format_number(price)} ₽"
            text += f"{w['emoji']} *{w['name']}:* {amt} шт. ({price_txt}/шт.)\n"
        text += f"\n💰 *Стоимость деревьев:* {format_number(total_wood)} ₽\n\n"
        total_value += total_wood
        
    if mode == 'all':
        text += f"💎 *Общая стоимость ресурсов:* {format_number(total_value)} ₽\n\n"
        text += "📝 *Для продажи:* `Продать [название]` или `Продать все руды / деревья`"
    elif mode == 'mine':
        text += "📝 *Быстрая продажа руд:* `Продать все руды`"
    elif mode == 'forest':
        text += "📝 *Быстрая продажа деревьев:* `Продать все деревья`"
        
    return text

def get_pickaxes_text(user_id, tg_first_name):
    mention = user_mention(user_id, tg_first_name)
    txt = f"{mention}, *доступные кирки:*\n\n"
    for i, p in enumerate(PICKAXES):
        price_t = "Бесплатно" if p['price']==0 and not p.get('price_candy') else f"{p.get('price_candy')} 🍬" if p.get('price_candy') else f"{format_number(p['price'])} ₽"
        if p['price_ore_type']: price_t += f" и {p['price_ore_amount']} {ORES[p['price_ore_type']]['name']}"
        txt += f"⛏️ {i+1}. {p['name']} - {price_t}\n"
    return txt + "\n🛒 Покупка: `Купить кирку [номер]`"

def get_axes_text(user_id, tg_first_name):
    mention = user_mention(user_id, tg_first_name)
    txt = f"{mention}, *доступные топоры:*\n\n"
    for i, a in enumerate(AXES):
        price_t = f"{a.get('price_candy')} 🍬" if a.get('price_candy') else f"{format_number(a['price'])} ₽"
        if a.get('price_wood_type'): price_t += f" и {a['price_wood_amount']} {WOODS[a['price_wood_type']]['name']}"
        txt += f"🪓 {i+1}. {a['name']} - {price_t}\n"
    return txt + "\n🛒 Покупка: `Купить топор [номер]`"

def get_ore_rates_text(user_id, tg_first_name):
    mention = user_mention(user_id, tg_first_name)
    txt = f"{mention}, *текущий курс руды:*\n\n"
    for ore_id, ore in ORES.items():
        txt += f"{ore['emoji']} *{ore['name']}* - {format_number(ore['price'])} ₽/шт\n"
    return txt

def get_wood_rates_text(user_id, tg_first_name):
    mention = user_mention(user_id, tg_first_name)
    txt = f"{mention}, *текущий курс дерева:*\n\n"
    for wood_id, wood in WOODS.items():
        price_text = f"{wood['price_candy']} 🍬" if wood.get('price_candy') else f"{format_number(wood['price'])} ₽"
        txt += f"{wood['emoji']} *{wood['name']}* - {price_text}/шт\n"
    return txt

def get_mine_menu_data(user_id, tg_first_name):
    mention = user_mention(user_id, tg_first_name)
    pickaxe_info = "У вас нет кирки. Купите кирку: `Кирки`"
    if users[user_id]['pickaxe'] is not None:
        p = PICKAXES[users[user_id]['pickaxe']]
        pickaxe_info = f"{p['emoji']} *Текущая кирка:* {p['name']}"
        
    text = f"⛏️ *Шахта игрока* {mention}\n\n{pickaxe_info}\n\n" \
           f"📜 *Команды шахты:*\n" \
           f"• `Копать` — добыть руду\n" \
           f"• `Кирки` — магазин кирок\n" \
           f"• `Курс руды` — цены на продажу\n" \
           f"• `Продать [название]` — продать руду\n" \
           f"• `Продать все руды` — быстрая продажа"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⛏️ Кирки", callback_data='edit_pickaxes'),
        types.InlineKeyboardButton("🎒 Инвентарь руд", callback_data='edit_inv_mine')
    )
    markup.add(types.InlineKeyboardButton("📊 Курс руды", callback_data='edit_ore_rates'))
    return text, markup

def get_forest_menu_data(user_id, tg_first_name):
    mention = user_mention(user_id, tg_first_name)
    axe_info = "У вас нет топора. Купите: `Топоры`"
    if users[user_id]['axe'] is not None:
        a = AXES[users[user_id]['axe']]
        axe_info = f"{a['emoji']} *Текущий топор:* {a['name']}"
        
    text = f"🌲 *Лес игрока* {mention}\n\n{axe_info}\n\n" \
           f"📜 *Команды леса:*\n" \
           f"• `Рубить` — добыть дерево\n" \
           f"• `Топоры` — магазин топоров\n" \
           f"• `Курс дерева` — цены на продажу\n" \
           f"• `Продать [название]` — продать дерево\n" \
           f"• `Продать все деревья` — быстрая продажа"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🪓 Топоры", callback_data='edit_axes'),
        types.InlineKeyboardButton("🎒 Инвентарь деревьев", callback_data='edit_inv_forest')
    )
    markup.add(types.InlineKeyboardButton("📊 Курс дерева", callback_data='edit_wood_rates'))
    return text, markup

# --- ТЕКСТОВЫЕ КОМАНДЫ (Отправляют новые сообщения) ---

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['инв', 'инвентарь'])
def show_inventory(message):
    user_id = str(message.from_user.id)
    bot.send_message(message.chat.id, get_inventory_text(user_id, message.from_user.first_name, mode='all'), parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'курс руды')
def show_ore_rates(message):
    bot.send_message(message.chat.id, get_ore_rates_text(str(message.from_user.id), message.from_user.first_name), parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'курс дерева')
def show_wood_rates(message):
    bot.send_message(message.chat.id, get_wood_rates_text(str(message.from_user.id), message.from_user.first_name), parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'кирки')
def show_pickaxes(message):
    bot.send_message(message.chat.id, get_pickaxes_text(str(message.from_user.id), message.from_user.first_name), parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'топоры')
def show_axes(message):
    bot.send_message(message.chat.id, get_axes_text(str(message.from_user.id), message.from_user.first_name), parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['шахта', 'копи'])
def mine_menu(message):
    user_id = str(message.from_user.id)
    if users[user_id]['level'] < 10: return bot.send_message(message.chat.id, "❌ Доступ к шахте с 10 уровня!", parse_mode='Markdown')
    text, markup = get_mine_menu_data(user_id, message.from_user.first_name)
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['лес', 'роща'])
def forest_menu(message):
    user_id = str(message.from_user.id)
    if users[user_id]['level'] < 25: return bot.send_message(message.chat.id, "❌ Доступ к лесу с 25 уровня!", parse_mode='Markdown')
    text, markup = get_forest_menu_data(user_id, message.from_user.first_name)
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['энергия', 'energy'])
def check_energy(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    energy = users[user_id].get('energy', 0)
    
    text = f"⚡ {mention}, *ваш запас энергии:* {energy}/25\n\n" \
           f"💡 _Энергия нужна для добычи ресурсов в шахте и лесу. Она восстанавливается автоматически: +1 ед. каждые 5 минут._"
           
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# --- ОБРАБОТЧИК КНОПОК МЕНЮ (Редактирует сообщения) ---

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_') or call.data.startswith('back_'))
def handle_resource_menus(call):
    user_id = str(call.from_user.id)
    tg_first_name = call.from_user.first_name
    text = ""
    markup = types.InlineKeyboardMarkup()
    
    try:
        if call.data == 'back_mine':
            text, markup = get_mine_menu_data(user_id, tg_first_name)
        elif call.data == 'back_forest':
            text, markup = get_forest_menu_data(user_id, tg_first_name)
        elif call.data == 'back_profile':
            text = get_profile_text(user_id, tg_first_name)
            markup.add(types.InlineKeyboardButton('🎒 Открыть инвентарь', callback_data='edit_inv_profile'))
            
        # Открытие инвентарей
        elif call.data == 'edit_inv_profile':
            text = get_inventory_text(user_id, tg_first_name, mode='all')
            markup.add(types.InlineKeyboardButton("🔙 Назад в профиль", callback_data='back_profile'))
        elif call.data == 'edit_inv_mine':
            text = get_inventory_text(user_id, tg_first_name, mode='mine')
            markup.add(types.InlineKeyboardButton("🔙 Назад в шахту", callback_data='back_mine'))
        elif call.data == 'edit_inv_forest':
            text = get_inventory_text(user_id, tg_first_name, mode='forest')
            markup.add(types.InlineKeyboardButton("🔙 Назад в лес", callback_data='back_forest'))
            
        # Прочие кнопки
        elif call.data == 'edit_pickaxes':
            text = get_pickaxes_text(user_id, tg_first_name)
            markup.add(types.InlineKeyboardButton("🔙 Назад в шахту", callback_data='back_mine'))
        elif call.data == 'edit_ore_rates':
            text = get_ore_rates_text(user_id, tg_first_name)
            markup.add(types.InlineKeyboardButton("🔙 Назад в шахту", callback_data='back_mine'))
        elif call.data == 'edit_axes':
            text = get_axes_text(user_id, tg_first_name)
            markup.add(types.InlineKeyboardButton("🔙 Назад в лес", callback_data='back_forest'))
        elif call.data == 'edit_wood_rates':
            text = get_wood_rates_text(user_id, tg_first_name)
            markup.add(types.InlineKeyboardButton("🔙 Назад в лес", callback_data='back_forest'))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='Markdown', reply_markup=markup)
    except:
        pass # Игнорируем ошибку, если текст остался тем же
    
    bot.answer_callback_query(call.id)

# --- ЭКОНОМИКА (Купля, продажа, добыча) ---

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('купить ') and is_ore_cmd(m))
def buy_ore(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        parts = safe_text_lower(message).split()
        if len(parts) < 3: return
        ore_name = parts[1].lower()
        ore_id = next((k for k, v in ORES.items() if v['name'].lower() == ore_name), None)
        buy_amount = int(parts[2])
        if ore_id and buy_amount > 0:
            cost = buy_amount * ORES[ore_id]['price']
            if users[user_id]['balance'] >= cost:
                users[user_id]['balance'] -= cost
                users[user_id]['ores'][ore_id] += buy_amount
                save_users_data()
                bot.send_message(message.chat.id, f"💰 {mention}, вы купили {ORES[ore_id]['emoji']} {buy_amount} {ORES[ore_id]['name']} за {format_number(cost)} ₽!", parse_mode='Markdown')
            else: bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!", parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('продать ') and is_ore_cmd(m))
def sell_ore(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        parts = safe_text_lower(message).split()
        ore_name = parts[1].lower()
        ore_id = next((k for k, v in ORES.items() if v['name'].lower() == ore_name), None)
        if ore_id:
            user_amt = users[user_id]['ores'][ore_id]
            if user_amt <= 0:
                return bot.send_message(message.chat.id, f"❌ {mention}, у вас нет этой руды!", parse_mode='Markdown')
            sell_amt = min(int(parts[2]) if len(parts) > 2 else user_amt, user_amt)
            if sell_amt > 0:
                cost = sell_amt * ORES[ore_id]['price']
                users[user_id]['ores'][ore_id] -= sell_amt
                users[user_id]['balance'] += cost
                save_users_data()
                bot.send_message(message.chat.id, f"💰 {mention}, вы продали {ORES[ore_id]['emoji']} {sell_amt} {ORES[ore_id]['name']} за {format_number(cost)} ₽!", parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('купить ') and is_wood_cmd(m))
def buy_resource(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        parts = safe_text_lower(message).split()
        if len(parts) < 3: return
        wood_name = parts[1].lower()
        amount = int(parts[2])
        wood_id = next((k for k, v in WOODS.items() if v['name'].lower() == wood_name), None)
        
        if wood_id and amount > 0:
            price = WOODS[wood_id]['price'] * amount
            if users[user_id]['balance'] >= price:
                users[user_id]['balance'] -= price
                users[user_id]['woods'][wood_id] += amount
                save_users_data()
                bot.send_message(message.chat.id, f"🌲 {mention}, вы купили {WOODS[wood_id]['emoji']} {amount} {WOODS[wood_id]['name']} за {format_number(price)} ₽!", parse_mode='Markdown')
            else:
                bot.send_message(message.chat.id, f"❌ {mention}, недостаточно денег!", parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('продать ') and is_wood_cmd(m))
def sell_resource(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        parts = safe_text_lower(message).split()
        wood_name = parts[1].lower()
        wood_id = next((k for k, v in WOODS.items() if v['name'].lower() == wood_name), None)
        
        if wood_id:
            user_amt = users[user_id]['woods'][wood_id]
            if user_amt <= 0: return bot.send_message(message.chat.id, f"❌ {mention}, у вас нет этого дерева!", parse_mode='Markdown')
            if WOODS[wood_id]['price'] <= 0: return bot.send_message(message.chat.id, f"❌ {mention}, это дерево нельзя продать!", parse_mode='Markdown')
            
            sell_amt = min(int(parts[2]) if len(parts) > 2 else user_amt, user_amt)
            if sell_amt > 0:
                cost = sell_amt * WOODS[wood_id]['price']
                users[user_id]['woods'][wood_id] -= sell_amt
                users[user_id]['balance'] += cost
                save_users_data()
                bot.send_message(message.chat.id, f"💰 {mention}, вы продали {WOODS[wood_id]['emoji']} {sell_amt} {WOODS[wood_id]['name']} за {format_number(cost)} ₽!", parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['продать руду', 'продать все руды'])
def sell_all_ore(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    total_value = 0
    sold_ores = []
    for ore_id, ore_amount in users[user_id]['ores'].items():
        if ore_amount > 0:
            val = ore_amount * ORES[ore_id]['price']
            total_value += val
            sold_ores.append(f"{ORES[ore_id]['emoji']} {ore_amount} {ORES[ore_id]['name']} - {format_number(val)} ₽")
            users[user_id]['ores'][ore_id] = 0
    if total_value > 0:
        users[user_id]['balance'] += total_value
        save_users_data()
        bot.send_message(message.chat.id, f"💰 {mention}, вы продали все руды и получили {format_number(total_value)} ₽!\n\n" + "\n".join(sold_ores), parse_mode='Markdown')
    else: bot.send_message(message.chat.id, f"❌ {mention}, у вас нет руд для продажи!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['продать дерево', 'продать все деревья'])
def sell_all_wood(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    total_value = 0
    sold_woods = []
    for w_id, w_amount in users[user_id]['woods'].items():
        if w_amount > 0 and WOODS[w_id]['price'] > 0:
            val = w_amount * WOODS[w_id]['price']
            total_value += val
            sold_woods.append(f"{WOODS[w_id]['emoji']} {w_amount} {WOODS[w_id]['name']} - {format_number(val)} ₽")
            users[user_id]['woods'][w_id] = 0
    if total_value > 0:
        users[user_id]['balance'] += total_value
        save_users_data()
        bot.send_message(message.chat.id, f"💰 {mention}, вы продали все деревья и получили {format_number(total_value)} ₽!\n\n" + "\n".join(sold_woods), parse_mode='Markdown')
    else: bot.send_message(message.chat.id, f"❌ {mention}, у вас нет дерева для продажи!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('купить кирку'))
def buy_pickaxe(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['level'] < 10: return bot.send_message(message.chat.id, "❌ Доступ в шахту с 10 уровня!")
    
    try:
        num = int(message.text.split()[2]) - 1
        if 0 <= num < len(PICKAXES):
            p = PICKAXES[num]
            if users[user_id]['pickaxe'] is not None and users[user_id]['pickaxe'] >= num:
                return bot.send_message(message.chat.id, f"❌ У вас уже есть эта (или лучшая) кирка!", parse_mode='Markdown')
            
            if p.get('price_candy'):
                if users[user_id]['candy'] < p['price_candy']: return bot.send_message(message.chat.id, "❌ Недостаточно конфет!")
                users[user_id]['candy'] -= p['price_candy']
            else:
                if users[user_id]['balance'] < p['price']: return bot.send_message(message.chat.id, "❌ Недостаточно денег!")
                if p['price_ore_type']:
                    if users[user_id]['ores'][p['price_ore_type']] < p['price_ore_amount']: return bot.send_message(message.chat.id, "❌ Недостаточно руды для крафта!")
                    users[user_id]['ores'][p['price_ore_type']] -= p['price_ore_amount']
                users[user_id]['balance'] -= p['price']
            users[user_id]['pickaxe'] = num
            save_users_data()
            bot.send_message(message.chat.id, f"✅ {mention}, вы приобрели {p['emoji']} *{p['name']}*!", parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('купить топор'))
def buy_axe(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['level'] < 25: return bot.send_message(message.chat.id, "❌ Доступ в лес с 25 уровня!")
    
    try:
        num = int(message.text.split()[2]) - 1
        if 0 <= num < len(AXES):
            a = AXES[num]
            if users[user_id]['axe'] is not None and users[user_id]['axe'] >= num:
                return bot.send_message(message.chat.id, f"❌ У вас уже есть этот (или лучший) топор!", parse_mode='Markdown')
            
            if a.get('price_candy'):
                if users[user_id]['candy'] < a['price_candy']: return bot.send_message(message.chat.id, "❌ Недостаточно конфет!")
                users[user_id]['candy'] -= a['price_candy']
            else:
                if users[user_id]['balance'] < a['price']: return bot.send_message(message.chat.id, "❌ Недостаточно денег!")
                if a.get('price_wood_type'):
                    if users[user_id]['woods'][a['price_wood_type']] < a['price_wood_amount']: return bot.send_message(message.chat.id, "❌ Недостаточно дерева для крафта!")
                    users[user_id]['woods'][a['price_wood_type']] -= a['price_wood_amount']
                users[user_id]['balance'] -= a['price']
            users[user_id]['axe'] = num
            save_users_data()
            bot.send_message(message.chat.id, f"✅ {mention}, вы приобрели {a['emoji']} *{a['name']}*!", parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'копать')
def mine_resources(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    if users[user_id]['level'] < 10: return
    if users[user_id]['pickaxe'] is None: return bot.send_message(message.chat.id, f"❌ {mention}, купите кирку: `Кирки`", parse_mode='Markdown')
    if users[user_id]['energy'] <= 0: return bot.send_message(message.chat.id, f"❌ {mention}, нет энергии!", parse_mode='Markdown')
    
    ct = time.time()
    if ct - users[user_id]['mine_cooldown'] < 60:
        return bot.send_message(message.chat.id, f"⏱ {mention}, ждите {int(60 - (ct - users[user_id]['mine_cooldown']))} сек.", parse_mode='Markdown')
    
    users[user_id]['energy'] -= 1
    users[user_id]['mine_cooldown'] = ct
    p = PICKAXES[users[user_id]['pickaxe']]
    mined = []
    exp = 0
    
    for drop in p['drops']:
        if random.randint(1, 100) <= drop.get('chance', 100):
            amt = random.randint(drop['min'], drop['max'])
            if amt > 0:
                users[user_id]['ores'][drop['ore']] += amt
                exp += amt
                mined.append(f"{ORES[drop['ore']]['emoji']} {amt} {ORES[drop['ore']]['name']}")
    
    users[user_id]['experience'] += exp
    save_users_data()
    
    if mined:
        txt = f"⛏️ {mention}, вы добыли:\n{', '.join(mined)}\n⭐ *Опыт:* +{exp}"
    else:
        txt = f"😔 {mention}, ничего не найдено."
    
    bot.send_message(message.chat.id, txt, parse_mode='Markdown')
    
    if exp > 0:
        check_level_up(user_id, message.chat.id, message.from_user.first_name)

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'рубить')
def chop_wood(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    if users[user_id]['level'] < 25: return
    if users[user_id]['axe'] is None: return bot.send_message(message.chat.id, f"❌ {mention}, купите топор: `Топоры`", parse_mode='Markdown')
    if users[user_id]['energy'] <= 0: return bot.send_message(message.chat.id, f"❌ {mention}, нет энергии!", parse_mode='Markdown')
    
    ct = time.time()
    if ct - users[user_id]['forest_cooldown'] < 60:
        return bot.send_message(message.chat.id, f"⏱ {mention}, ждите {int(60 - (ct - users[user_id]['forest_cooldown']))} сек.", parse_mode='Markdown')
    
    users[user_id]['energy'] -= 1
    users[user_id]['forest_cooldown'] = ct
    a = AXES[users[user_id]['axe']]
    mined = []
    exp = 0
    
    for drop in a['drops']:
        if random.randint(1, 100) <= drop.get('chance', 100):
            amt = random.randint(drop['min'], drop['max'])
            if amt > 0:
                users[user_id]['woods'][drop['wood']] += amt
                exp += amt
                mined.append(f"{WOODS[drop['wood']]['emoji']} {amt} {WOODS[drop['wood']]['name']}")
    
    users[user_id]['experience'] += exp
    save_users_data()
    
    if mined:
        txt = f"🪓 {mention}, вы срубили:\n{', '.join(mined)}\n⭐ *Опыт:* +{exp}"
    else:
        txt = f"😔 {mention}, ничего не найдено."
    
    bot.send_message(message.chat.id, txt, parse_mode='Markdown')
    
    if exp > 0:
        check_level_up(user_id, message.chat.id, message.from_user.first_name)

# ==================== РАБОТА И БИЗНЕС ====================

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['работа', 'работы', 'work'])
def work_menu(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    jobs_list = f"{mention}, *доступные работы:*\n\n"
    for i, job in enumerate(jobs, 1):
        jobs_list += f"{job['emoji']} {i}. {job['name']} - {format_number(job['min_salary'])}-{format_number(job['max_salary'])} ₽  *[{job['min_level']}lvl]*\n"
    bot.send_message(message.chat.id, jobs_list + "\n📝 Устроиться: `Устроиться [номер]`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('устроиться'))
def get_job(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        j_num = int(message.text.split()[1]) - 1
        if 0 <= j_num < len(jobs):
            if users[user_id]['job'] is not None:
                bot.send_message(message.chat.id, f"❌ {mention}, сначала увольтесь: `Уволиться`", parse_mode='Markdown')
            elif users[user_id]['level'] >= jobs[j_num]['min_level']:
                users[user_id]['job'] = j_num
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, вы устроились на {jobs[j_num]['emoji']} *{jobs[j_num]['name']}*!", parse_mode='Markdown')
            else: bot.send_message(message.chat.id, f"❌ Нужен {jobs[j_num]['min_level']} уровень!", parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['уволиться'])
def quit_job(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['job'] is None: return bot.send_message(message.chat.id, f"❌ Вы не работаете!", parse_mode='Markdown')
    users[user_id]['job'] = None
    save_users_data()
    bot.send_message(message.chat.id, f"✅ {mention}, вы уволились!", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['работать'])
def work_job(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['job'] is None: return bot.send_message(message.chat.id, f"❌ Сначала устройтесь на работу!", parse_mode='Markdown')
    
    ct = time.time()
    if ct - users[user_id]['last_work_time'] < 60:
        return bot.send_message(message.chat.id, f"⏱ Ждите {int(60 - (ct - users[user_id]['last_work_time']))} сек.", parse_mode='Markdown')
    
    job = jobs[users[user_id]['job']]
    sal = random.randint(job['min_salary'], job['max_salary'])
    exp = random.randint(1, 5)
    
    users[user_id]['balance'] += sal
    users[user_id]['experience'] += exp
    users[user_id]['last_work_time'] = ct
    save_users_data()
    
    bot.send_message(message.chat.id, f"💼 {mention}, *вы поработали {job['emoji']}*\n\n💰 *Заработано:* {format_number(sal)} ₽\n⭐ *Опыт:* +{exp}", parse_mode='Markdown')
    
    check_level_up(user_id, message.chat.id, message.from_user.first_name)

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['бизнесы', 'бизнес'])
def business_list(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    txt = f"{mention}, *доступные бизнесы:*\n\n"
    for i, b in enumerate(businesses, 1):
        txt += f"{b['emoji']} {i}. {b['name']} - {format_number(b['price'])} ₽\n"
    bot.send_message(message.chat.id, txt + "\n🛒 Купить: `Купить бизнес [номер]`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('купить бизнес'))
def buy_business(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        b_num = int(message.text.split()[2]) - 1
        if 0 <= b_num < len(businesses):
            if users[user_id]['business'] is not None:
                return bot.send_message(message.chat.id, f"❌ У вас уже есть бизнес!", parse_mode='Markdown')
            if users[user_id]['balance'] >= businesses[b_num]['price']:
                users[user_id]['balance'] -= businesses[b_num]['price']
                users[user_id]['business'] = b_num
                users[user_id]['business_workers'] = 1
                users[user_id]['business_income'] = 0
                users[user_id]['last_business_collect_time'] = time.time()
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, вы купили {businesses[b_num]['emoji']} *{businesses[b_num]['name']}*!", parse_mode='Markdown')
            else: bot.send_message(message.chat.id, f"❌ Недостаточно средств!")
    except: pass

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'мой бизнес')
def my_business(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['business'] is None: return bot.send_message(message.chat.id, "❌ Нет бизнеса!")
    
    b = businesses[users[user_id]['business']]
    w = users[user_id]['business_workers']
    inc_per_h = b['income_per_hour'] * w
    
    txt = f"💼 *Владелец:* {mention}\n{b['emoji']} *Название:* {b['name']}\n💸 Прибыль: {format_number(inc_per_h)} ₽/час\n👨‍💼 Рабочих: {w}/50\n💰 На счету: {format_number(users[user_id]['business_income'])} ₽\n\n❗️ Нанять: `Нанять рабочих [кол-во]`\n⚠️ Продать (комиссия 20%): `Продать бизнес`"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💵 Собрать', callback_data=f'collect_income:{user_id}'))
    bot.send_message(message.chat.id, txt, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'продать бизнес')
def sell_business(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['business'] is None: return
    
    b = businesses[users[user_id]['business']]
    workers = users[user_id]['business_workers']
    worker_investment = sum([b['worker_price'] * (i + 1) for i in range(workers)])
    total_investment = b['price'] + worker_investment
    sell_price = int(total_investment * 0.8) + users[user_id]['business_income']
    
    users[user_id]['balance'] += sell_price
    users[user_id]['business'] = None
    users[user_id]['business_workers'] = 0
    users[user_id]['business_income'] = 0
    save_users_data()
    bot.send_message(message.chat.id, f"✅ {mention}, бизнес продан! Выручка: {format_number(sell_price)} ₽", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('нанять рабочих'))
def hire_workers(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['business'] is None: return
    try:
        count = int(message.text.split()[2])
        curr = users[user_id]['business_workers']
        if count > 0 and curr + count <= 50:
            b = businesses[users[user_id]['business']]
            cost = sum([b['worker_price'] * (curr + i + 1) for i in range(count)])
            if users[user_id]['balance'] >= cost:
                users[user_id]['balance'] -= cost
                users[user_id]['business_workers'] += count
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, нанято {count} рабочих за {format_number(cost)} ₽!", parse_mode='Markdown')
            else: 
                bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!\n\n💰 Нужно: {format_number(cost)} ₽\n💵 У вас: {format_number(users[user_id]['balance'])} ₽", parse_mode='Markdown')
        else: 
            bot.send_message(message.chat.id, f"❌ {mention}, превышен лимит рабочих (50) или неверное число!", parse_mode='Markdown')
    except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('collect_income:'))
def collect_income_callback(call):
    user_id = call.data.split(':')[1]
    if str(call.from_user.id) != user_id: 
        return bot.answer_callback_query(call.id, "❌ Это не ваш бизнес!", show_alert=True)
    if users[user_id]['business_income'] <= 0: 
        return bot.answer_callback_query(call.id, "⏱ Прибыли пока нет!", show_alert=True)
    
    bot.answer_callback_query(call.id)
    
    inc = users[user_id]['business_income']
    users[user_id]['balance'] += inc
    users[user_id]['business_income'] = 0
    users[user_id]['last_business_collect_time'] = time.time()
    save_users_data()
    
    mention = user_mention(user_id, call.from_user.first_name)
    bot.send_message(call.message.chat.id, f"💰 {mention}, вы собрали {format_number(inc)} ₽ с бизнеса!", parse_mode='Markdown')
    
    b = businesses[users[user_id]['business']]
    w = users[user_id]['business_workers']
    inc_per_h = b['income_per_hour'] * w
    
    txt = f"💼 *Владелец:* {mention}\n{b['emoji']} *Название:* {b['name']}\n💸 Прибыль: {format_number(inc_per_h)} ₽/час\n👨‍💼 Рабочих: {w}/50\n💰 На счету: 0 ₽\n\n❗️ Нанять: `Нанять рабочих [кол-во]`\n⚠️ Продать (комиссия 20%): `Продать бизнес`"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💵 Собрать', callback_data=f'collect_income:{user_id}'))
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt, parse_mode='Markdown', reply_markup=markup)
    except:
        pass


# ==================== ФЕРМЫ И КРИПТА ====================

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['фермы', 'ферма'])
def farms_list(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    txt = f"{mention}, *майнинг-фермы:*\n\n"
    for i, f in enumerate(farms, 1):
        txt += f"{f['emoji']} {i}. {f['name']} - {format_number(f['price'])} ₽ (Майнит: {crypto_names[f['crypto_type']]})\n"
    bot.send_message(message.chat.id, txt + "\n🛒 Купить: `Купить ферму [номер]`", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('купить ферму'))
def buy_farm(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        num = int(message.text.split()[2]) - 1
        if 0 <= num < len(farms):
            if users[user_id]['farm'] is not None: return bot.send_message(message.chat.id, "❌ У вас уже есть ферма!")
            if users[user_id]['balance'] >= farms[num]['price']:
                users[user_id]['balance'] -= farms[num]['price']
                users[user_id]['farm'] = num
                users[user_id]['farm_gpus'] = 1
                users[user_id]['farm_income'] = 0
                users[user_id]['last_farm_collect_time'] = time.time()
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, куплена ферма {farms[num]['emoji']} *{farms[num]['name']}*!", parse_mode='Markdown')
            else: bot.send_message(message.chat.id, "❌ Недостаточно средств!")
    except: pass

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'моя ферма')
def my_farm(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['farm'] is None: return bot.send_message(message.chat.id, "❌ Нет фермы!")
    
    f = farms[users[user_id]['farm']]
    g = users[user_id]['farm_gpus']
    inc = users[user_id]['farm_income']
    lim = FARM_CRYPTO_LIMITS[f['crypto_type']]
    
    txt = f"💻 *Владелец:* {mention}\n{f['emoji']} *Ферма:* {f['name']}\n💷 Доход: {f['income_per_gpu']*g} {crypto_symbols[f['crypto_type']]}/час\n📝 Видеокарт: {g}/50\n💰 На счету: {int(inc)}/{lim} {crypto_emoji[f['crypto_type']]}\n\n❗️ Улучшить: `Нанять видеокарту [кол-во]`\n⚠️ Продать (комиссия 20%): `Продать ферму`"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 Собрать", callback_data=f"collect_farm:{user_id}"))
    bot.send_message(message.chat.id, txt, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'продать ферму')
def sell_farm(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['farm'] is None: return
    
    f = farms[users[user_id]['farm']]
    gpus = users[user_id]['farm_gpus']
    gpu_investment = sum([f['gpu_price'] * (i + 1) for i in range(gpus)])
    total_investment = f['price'] + gpu_investment
    sell_price = int(total_investment * 0.8)
    
    users[user_id]['balance'] += sell_price
    users[user_id][f['crypto_type']] += users[user_id]['farm_income']
    users[user_id]['farm'] = None
    users[user_id]['farm_gpus'] = 0
    users[user_id]['farm_income'] = 0
    save_users_data()
    bot.send_message(message.chat.id, f"✅ {mention}, ферма продана! Выручка: {format_number(sell_price)} ₽", parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('нанять видеокарту'))
def hire_gpu(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    if users[user_id]['farm'] is None: return
    try:
        count = int(message.text.split()[2]) if len(message.text.split()) > 2 else 1
        curr = users[user_id]['farm_gpus']
        if count > 0 and curr + count <= 50:
            f = farms[users[user_id]['farm']]
            cost = sum([f['gpu_price'] * (curr + i + 1) for i in range(count)])
            if users[user_id]['balance'] >= cost:
                users[user_id]['balance'] -= cost
                users[user_id]['farm_gpus'] += count
                save_users_data()
                bot.send_message(message.chat.id, f"✅ {mention}, куплено {count} видеокарт за {format_number(cost)} ₽!", parse_mode='Markdown')
            else: 
                bot.send_message(message.chat.id, f"❌ {mention}, недостаточно средств!\n\n💰 Нужно: {format_number(cost)} ₽\n💵 У вас: {format_number(users[user_id]['balance'])} ₽", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ {mention}, превышен лимит видеокарт (50) или неверное число!", parse_mode='Markdown')
    except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('collect_farm:'))
def collect_farm_callback(call):
    user_id = call.data.split(':')[1]
    if str(call.from_user.id) != user_id: 
        return bot.answer_callback_query(call.id, "❌ Это не ваша ферма!", show_alert=True)
    if users[user_id]['farm_income'] <= 0: 
        return bot.answer_callback_query(call.id, "⏱ Ничего не намайнилось!", show_alert=True)
    
    bot.answer_callback_query(call.id)
    
    inc = users[user_id]['farm_income']
    ctype = farms[users[user_id]['farm']]['crypto_type']
    users[user_id][ctype] += inc
    users[user_id]['farm_income'] = 0
    users[user_id]['last_farm_collect_time'] = time.time()
    save_users_data()
    
    mention = user_mention(user_id, call.from_user.first_name)
    bot.send_message(call.message.chat.id, f"💰 {mention}, вы собрали {int(inc)} {crypto_symbols[ctype]} {crypto_emoji[ctype]} с фермы!", parse_mode='Markdown')
    
    f = farms[users[user_id]['farm']]
    g = users[user_id]['farm_gpus']
    lim = FARM_CRYPTO_LIMITS[f['crypto_type']]
    
    txt = f"💻 *Владелец:* {mention}\n{f['emoji']} *Ферма:* {f['name']}\n💷 Доход: {f['income_per_gpu']*g} {crypto_symbols[f['crypto_type']]}/час\n📝 Видеокарт: {g}/50\n💰 На счету: 0/{lim} {crypto_emoji[f['crypto_type']]}\n\n❗️ Улучшить: `Нанять видеокарту [кол-во]`\n⚠️ Продать (комиссия 20%): `Продать ферму`"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 Собрать", callback_data=f"collect_farm:{user_id}"))
    
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=txt, parse_mode='Markdown', reply_markup=markup)
    except:
        pass

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'курс крипты')
def show_crypto_rates_command(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    txt = f"📊 *Курс криптовалют для* {mention}:\n\n"
    for cid, rate in crypto_rates.items():
        txt += f"{crypto_emoji[cid]} *{crypto_names[cid]}* - {format_number(rate)} ₽\n"
    bot.send_message(message.chat.id, txt, parse_mode='Markdown')

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['к', 'крипта'])
def crypto_balance(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    
    eth_v = round(users[user_id]['eth'] * crypto_rates['eth'])
    ltc_v = round(users[user_id]['ltc'] * crypto_rates['ltc'])
    btc_v = round(users[user_id]['btc'] * crypto_rates['btc'])
    tot = eth_v + ltc_v + btc_v
    
    txt = f"{mention}, *крипто-портфель:*\n\n" \
          f"{crypto_emoji['eth']} {int(users[user_id]['eth'])} ETH (≈ {format_number(eth_v)} ₽)\n" \
          f"{crypto_emoji['ltc']} {int(users[user_id]['ltc'])} LTC (≈ {format_number(ltc_v)} ₽)\n" \
          f"{crypto_emoji['btc']} {int(users[user_id]['btc'])} BTC (≈ {format_number(btc_v)} ₽)\n\n" \
          f"💰 *Итого:* {format_number(tot)} ₽\n\n" \
          f"📉 Продать: `Продать крипту` или `Продать [тип] [кол-во]`\n" \
          f"📈 Купить: `Купить [тип] [кол-во]`"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎁 Крипто-Бонус", callback_data=f"cryptobonus:{user_id}"))
    bot.send_message(message.chat.id, txt, parse_mode='Markdown', reply_markup=markup)

def give_crypto_bonus(chat_id, user_id_int, tg_first_name):
    user_id = str(user_id_int)
    current_time = time.time()
    user_data = users[user_id]
    mention = user_mention(user_id, tg_first_name)
    
    if current_time - user_data.get('last_crypto_bonus_time', 0) < 86400:
        rem_time = 86400 - (current_time - user_data.get('last_crypto_bonus_time', 0))
        bot.send_message(chat_id, f"⏱ *Крипто-бонус еще не доступен!*\nЧерез *{int(rem_time // 3600)} ч. {int((rem_time % 3600) // 60)} мин.*", parse_mode='Markdown')
        return
    
    bonus = random.randint(5, 10)
    user_data['eth'] += bonus
    user_data['last_crypto_bonus_time'] = current_time
    save_users_data()
    
    bot.send_message(chat_id, f"🎁 {mention}, *ежедневный крипто-бонус получен!*\n\n💎 *Получено эфириума:* {bonus} ETH", parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('cryptobonus:'))
def crypto_bonus_callback(call):
    user_id = call.data.split(':')[1]
    if str(call.from_user.id) != user_id: 
        return bot.answer_callback_query(call.id, "❌ Не ваш бонус!", show_alert=True)
    
    bot.answer_callback_query(call.id)
    give_crypto_bonus(call.message.chat.id, call.from_user.id, call.from_user.first_name)

@bot.message_handler(func=lambda message: safe_text_lower(message) == 'криптобонус')
def crypto_bonus_cmd(message):
    give_crypto_bonus(message.chat.id, message.from_user.id, message.from_user.first_name)


# ==================== ИГРЫ (КАЗИНО, МОНЕТКА) ====================

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('казино'))
def casino_game(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        amount = int(message.text.split()[1])
        if amount <= 0 or users[user_id]['balance'] < amount:
            return bot.send_message(message.chat.id, f"❌ {mention}, неверная сумма или недостаточно средств!", parse_mode='Markdown')
            
        users[user_id]['balance'] -= amount
        outcomes = [(0, 0.20), (0.25, 0.20), (0.5, 0.20), (0.75, 0.20), (1, 0.10), (1.25, 0.15), (1.5, 0.15), (1.75, 0.15), (2, 0.10), (5, 0.05), (10, 0.01)]
        rand, cum = random.random(), 0
        multiplier = 0
        for val, prob in outcomes:
            cum += prob
            if rand < cum:
                multiplier = val
                break
                
        payout = int(amount * multiplier)
        users[user_id]['balance'] += payout
        save_users_data()
        
        emoji = "🎉" if payout > amount else ("😐" if payout == amount else "💸")
        status = "ВЫИГРЫШ" if payout > amount else ("ВОЗВРАТ" if payout == amount else "ПРОИГРЫШ")
        
        txt = f"🎰 *КАЗИНО*\n\n👤 Игрок: {mention}\n💵 Ставка: {format_number(amount)} ₽\n🎲 Множитель: *x{multiplier}*\n\n{emoji} *{status}!* Вы получили {format_number(payout)} ₽"
        bot.send_message(message.chat.id, txt, parse_mode='Markdown')
    except: pass

@bot.message_handler(func=lambda message: safe_text_lower(message).startswith('монетка'))
def coin_flip(message):
    user_id = str(message.from_user.id)
    mention = user_mention(user_id, message.from_user.first_name)
    try:
        parts = safe_text_lower(message).split()
        if len(parts) < 3: return bot.send_message(message.chat.id, "❌ Формат: `Монетка [орёл/решка] [ставка]`", parse_mode='Markdown')
        
        choice = parts[1].replace('ё', 'е')
        if choice not in ['орел', 'решка']: return bot.send_message(message.chat.id, "❌ Выберите 'орёл' или 'решка'!")
        
        amount = int(parts[2])
        if amount <= 0 or users[user_id]['balance'] < amount:
            return bot.send_message(message.chat.id, "❌ Неверная сумма или мало денег!")
            
        users[user_id]['balance'] -= amount
        res = random.choice(['орел', 'решка'])
        payout = amount * 2 if choice == res else 0
        users[user_id]['balance'] += payout
        save_users_data()
        
        emoji = "🎉" if payout > 0 else "💸"
        status = "ПОБЕДА" if payout > 0 else "ПОРАЖЕНИЕ"
        
        txt = f"🪙 *МОНЕТКА*\n\n👤 Игрок: {mention}\n💵 Ставка: {format_number(amount)} ₽ на *{choice.capitalize()}*\n🌀 Выпало: *{res.capitalize()}*\n\n{emoji} *{status}!* Вы получили {format_number(payout)} ₽"
        bot.send_message(message.chat.id, txt, parse_mode='Markdown')
    except: pass

def get_profile_text(user_id, tg_first_name):
    mention = user_mention(user_id, tg_first_name)
    user_data = users[user_id]
    
    job_name = jobs[user_data['job']]['name'] if user_data.get('job') is not None else "Безработный"
    house_name = houses[user_data['house']]['name'] if user_data.get('house') is not None else "Нет"
    car_name = CARS[user_data['car']]['name'] if user_data.get('car') is not None else "Нет"
    phone_name = PHONES[user_data['phone']]['name'] if user_data.get('phone') is not None else "Нет"
    biz_name = businesses[user_data['business']]['name'] if user_data.get('business') is not None else "Нет"
    farm_name = farms[user_data['farm']]['name'] if user_data.get('farm') is not None else "Нет"
    
    pickaxe_name = PICKAXES[user_data['pickaxe']]['name'] if user_data.get('pickaxe') is not None else "Нет"
    axe_name = AXES[user_data['axe']]['name'] if user_data.get('axe') is not None else "Нет"

    owned_ores = [f"{ORES[k]['name']} ({v})" for k, v in user_data.get('ores', {}).items() if v > 0]
    ores_str = ", ".join(owned_ores) if owned_ores else "Нет"
    
    owned_woods = [f"{WOODS[k]['name']} ({v})" for k, v in user_data.get('woods', {}).items() if v > 0]
    woods_str = ", ".join(owned_woods) if owned_woods else "Нет"

    prefix_emoji = "👤" if user_data['prefix'] == 'Игрок' else "👨‍💻"
    exp_need = exp_for_next_level(user_data['level'])

    return f"""
🪪 *Профиль игрока* {mention}

📝 *Ник:* {user_data['nickname']}
🏷 *Префикс:* {prefix_emoji} {user_data['prefix']}
📊 *Уровень:* {user_data['level']} ({user_data['experience']}/{exp_need} EXP)
⚡ *Энергия:* {user_data.get('energy', 0)}/25

💰 *Финансы:*
💵 Наличные: {format_number(user_data['balance'])} ₽
🏦 Банк: {format_number(user_data['bank_balance'])} ₽
📈 Депозит: {format_number(user_data.get('deposit_balance', 0))} ₽
🍬 Конфеты: {format_number(user_data['candy'])}

🏢 *Карьера и Бизнес:*
💼 Работа: {job_name}
🏪 Бизнес: {biz_name}
💻 Ферма: {farm_name}

🏠 *Имущество:*
🏡 Дом: {house_name}
🚗 Машина: {car_name}
📱 Телефон: {phone_name}

🎒 *Инструменты и Ресурсы:*
⛏ Кирка: {pickaxe_name}
🪓 Топор: {axe_name}
🪨 Руды: {ores_str}
🌲 Деревья: {woods_str}
"""

@bot.message_handler(func=lambda message: safe_text_lower(message) in ['профиль', 'profile', 'п'])
def profile_command(message):
    user_id = str(message.from_user.id)
    text = get_profile_text(user_id, message.from_user.first_name)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🎒 Открыть инвентарь', callback_data='edit_inv_profile'))
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== АДМИН-ПАНЕЛЬ ====================

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id): return
    help_text = """
🛡 *Команды администратора:*

📊 *Управление пользователями (Бот):*
• `/ban_idb [ID]` или `-ban [ID|reply]` - Выдать бан в боте
• `/unban_idb [ID]` или `-unban [ID|reply]` - Снять бан в боте
• `-warn [ID|reply]` - Выдать предупреждение (3 = бан)
• `-unwarn [ID|reply]` - Снять предупреждение
• `инфо` (в ответ) - Статус и статистика игрока
• `обнулить` (в ответ) / `/reset_id [ID]` - Полный сброс аккаунта

💰 *Экономика:*
• `выдать [сумма] [@user|reply]` - Выдать рубли
• `квыдать [сумма] [@user|reply]` - Выдать конфеты
• `забрать [сумма] [@user|reply]` - Изъять рубли

👮‍♂️ *Модерация группы:*
• `-гбан` (в ответ) - Бан/кик в группе
• `-гразбан` (в ответ) - Разбан в группе
• `-гмут` (в ответ) - Выдать ReadOnly (мут)
• `-гразмут` (в ответ) - Снять ReadOnly
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Вспомогательная функция для получения ID цели из команды (реплай или аргумент)
def get_target_from_message(message, command_parts_offset=1):
    parts = message.text.split()
    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
        target_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
        init_user(target_id, target_name)
        return target_id, target_name
    elif len(parts) > command_parts_offset:
        identifier = parts[command_parts_offset]
        target_id, target_name = find_user_by_identifier(identifier)
        if target_id:
            return target_id, target_name
        elif identifier.isdigit() and identifier in users:
            return identifier, users[identifier]['nickname']
    return None, None

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('выдать ') and is_admin(m.from_user.id))
def admin_give_money(message):
    parts = message.text.split()
    if len(parts) < 2: return
    try:
        amount = int(parts[1])
        target_id, target_name = get_target_from_message(message, 2)
            
        if target_id:
            users[target_id]['balance'] += amount
            save_users_data()
            bot.send_message(message.chat.id, f"✅ Выдано {format_number(amount)} ₽ пользователю {user_mention(target_id, target_name)}!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
    except: bot.send_message(message.chat.id, "❌ Ошибка формата!")

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('квыдать ') and is_admin(m.from_user.id))
def admin_give_candy(message):
    parts = message.text.split()
    if len(parts) < 2: return
    try:
        amount = int(parts[1])
        target_id, target_name = get_target_from_message(message, 2)
            
        if target_id:
            users[target_id]['candy'] += amount
            save_users_data()
            bot.send_message(message.chat.id, f"✅ Выдано {amount} 🍬 пользователю {user_mention(target_id, target_name)}!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
    except: bot.send_message(message.chat.id, "❌ Ошибка формата!")

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('забрать ') and is_admin(m.from_user.id))
def admin_take_money(message):
    parts = message.text.split()
    if len(parts) < 2: return
    try:
        amount = int(parts[1])
        target_id, target_name = get_target_from_message(message, 2)
            
        if target_id:
            users[target_id]['balance'] = max(0, users[target_id]['balance'] - amount)
            save_users_data()
            bot.send_message(message.chat.id, f"✅ Изъято {format_number(amount)} ₽ у пользователя {user_mention(target_id, target_name)}!", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "❌ Пользователь не найден!")
    except: bot.send_message(message.chat.id, "❌ Ошибка формата!")

@bot.message_handler(func=lambda m: safe_text_lower(m) == 'инфо' and is_admin(m.from_user.id))
def admin_info(message):
    if not message.reply_to_message:
        return bot.send_message(message.chat.id, "❌ Сделайте ответ на сообщение пользователя!")
        
    target_id = str(message.reply_to_message.from_user.id)
    target_name = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
    init_user(target_id, target_name)
    u = users[target_id]
    
    status = "🔴 Заблокирован" if u.get('is_banned') else "🟢 Активен"
    
    text = f"📊 *Инфо об игроке* {user_mention(target_id, u['nickname'])}\n\n" \
           f"ID: `{target_id}`\n" \
           f"Игровой ID: `{u['custom_id']}`\n" \
           f"Уровень: {u['level']} ({u['experience']} EXP)\n\n" \
           f"💰 Наличные: {format_number(u['balance'])} ₽\n" \
           f"🏦 Банк: {format_number(u['bank_balance'])} ₽\n" \
           f"📈 Депозит: {format_number(u.get('deposit_balance', 0))} ₽\n" \
           f"🍬 Конфеты: {u['candy']}\n\n" \
           f"⚠️ Варны: {u.get('warns', 0)}/3\n" \
           f"🛡 Статус: {status}"
           
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# --- БЛОКИРОВКА В БОТЕ ---

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith(('-ban', '/ban_idb')) and is_admin(m.from_user.id))
def admin_ban_bot(message):
    target_id, target_name = get_target_from_message(message)
    if not target_id:
        return bot.send_message(message.chat.id, "❌ Игрок не найден. Используйте реплай или ID.")
    
    if is_admin(target_id):
        return bot.send_message(message.chat.id, "❌ Нельзя заблокировать администратора!")

    users[target_id]['is_banned'] = True
    save_users_data()
    bot.send_message(message.chat.id, f"⛔ Пользователь {user_mention(target_id, target_name)} заблокирован в боте!", parse_mode='Markdown')

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith(('-unban', '/unban_idb')) and is_admin(m.from_user.id))
def admin_unban_bot(message):
    target_id, target_name = get_target_from_message(message)
    if not target_id:
        return bot.send_message(message.chat.id, "❌ Игрок не найден. Используйте реплай или ID.")

    users[target_id]['is_banned'] = False
    users[target_id]['warns'] = 0 # Обнуляем варны при разбане
    save_users_data()
    bot.send_message(message.chat.id, f"✅ Пользователь {user_mention(target_id, target_name)} разблокирован в боте!", parse_mode='Markdown')

# --- СИСТЕМА ПРЕДУПРЕЖДЕНИЙ ---

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('-warn') and is_admin(m.from_user.id))
def admin_warn(message):
    target_id, target_name = get_target_from_message(message)
    if not target_id:
        return bot.send_message(message.chat.id, "❌ Игрок не найден.")
    if is_admin(target_id):
        return bot.send_message(message.chat.id, "❌ Нельзя выдать варн администратору!")

    warns = users[target_id].get('warns', 0) + 1
    users[target_id]['warns'] = warns
    
    if warns >= 3:
        users[target_id]['is_banned'] = True
        users[target_id]['warns'] = 0
        bot.send_message(message.chat.id, f"⛔ {user_mention(target_id, target_name)} получил 3/3 предупреждений и был автоматически заблокирован!", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"⚠️ Выдано предупреждение {user_mention(target_id, target_name)}. Текущее количество: {warns}/3", parse_mode='Markdown')
    save_users_data()

@bot.message_handler(func=lambda m: safe_text_lower(m).startswith('-unwarn') and is_admin(m.from_user.id))
def admin_unwarn(message):
    target_id, target_name = get_target_from_message(message)
    if not target_id:
        return bot.send_message(message.chat.id, "❌ Игрок не найден.")

    warns = users[target_id].get('warns', 0)
    if warns > 0:
        users[target_id]['warns'] -= 1
        save_users_data()
        bot.send_message(message.chat.id, f"✅ Снято 1 предупреждение у {user_mention(target_id, target_name)}. Осталось: {users[target_id]['warns']}/3", parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, f"ℹ️ У пользователя {user_mention(target_id, target_name)} нет предупреждений.", parse_mode='Markdown')

# --- ОБНУЛЕНИЕ ПРОФИЛЯ ---

@bot.message_handler(func=lambda m: (safe_text_lower(m) == 'обнулить' or safe_text_lower(m).startswith('/reset_id')) and is_admin(m.from_user.id))
def admin_reset_user(message):
    target_id, target_name = get_target_from_message(message)
    
    if not target_id:
        return bot.send_message(message.chat.id, "❌ Игрок не найден. Сделайте ответ на сообщение или укажите ID: `/reset_id [ID]`", parse_mode='Markdown')
    
    if is_admin(target_id):
        return bot.send_message(message.chat.id, "❌ Нельзя обнулить профиль администратора!", parse_mode='Markdown')

    # Сохраняем ник и ID, удаляем профиль и создаем заново с дефолтными значениями
    old_nickname = users[target_id]['nickname']
    del users[target_id]
    init_user(target_id, old_nickname)
    
    bot.send_message(message.chat.id, f"♻️ Профиль игрока {user_mention(target_id, old_nickname)} был полностью обнулен!", parse_mode='Markdown')

# --- МОДЕРАЦИЯ ГРУППЫ ---

def handle_moderation_error(e, chat_id, action_type):
    bot.send_message(chat_id, f"❌ Ошибка модерации ({action_type}): боту нужны права администратора в чате.", parse_mode='Markdown')

@bot.message_handler(func=lambda m: safe_text_lower(m) == "-гбан" and is_admin(m.from_user.id))
def gban_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        if is_admin(target_id): return bot.send_message(message.chat.id, "❌ Невозможно забанить администратора.")
        try:
            bot.ban_chat_member(message.chat.id, target_id)
            bot.send_message(message.chat.id, f"⛔ Пользователь {user_mention(target_id, message.reply_to_message.from_user.first_name)} исключен из группы!", parse_mode='Markdown')
        except Exception as e: handle_moderation_error(e, message.chat.id, "Групповой бан")

@bot.message_handler(func=lambda m: safe_text_lower(m) == "-гразбан" and is_admin(m.from_user.id))
def gunban_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        try:
            bot.unban_chat_member(message.chat.id, target_id, only_if_banned=True)
            bot.send_message(message.chat.id, f"✅ Пользователь {user_mention(target_id, message.reply_to_message.from_user.first_name)} разблокирован в группе!", parse_mode='Markdown')
        except Exception as e: handle_moderation_error(e, message.chat.id, "Групповой разбан")

@bot.message_handler(func=lambda m: safe_text_lower(m) == "-гмут" and is_admin(m.from_user.id))
def gmute_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        if is_admin(target_id): return bot.send_message(message.chat.id, "❌ Невозможно замутить администратора.")
        try:
            # Забираем права на отправку сообщений
            bot.restrict_chat_member(message.chat.id, target_id, can_send_messages=False)
            bot.send_message(message.chat.id, f"🔇 Пользователю {user_mention(target_id, message.reply_to_message.from_user.first_name)} запрещено писать в чат (Мут)!", parse_mode='Markdown')
        except Exception as e: handle_moderation_error(e, message.chat.id, "Мут")

@bot.message_handler(func=lambda m: safe_text_lower(m) == "-гразмут" and is_admin(m.from_user.id))
def gunmute_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        try:
            # Возвращаем все стандартные права
            bot.restrict_chat_member(message.chat.id, target_id, 
                                     can_send_messages=True, 
                                     can_send_media_messages=True, 
                                     can_send_other_messages=True, 
                                     can_add_web_page_previews=True)
            bot.send_message(message.chat.id, f"🔊 Мут снят. Пользователь {user_mention(target_id, message.reply_to_message.from_user.first_name)} снова может писать!", parse_mode='Markdown')
        except Exception as e: handle_moderation_error(e, message.chat.id, "Размут")

# ==================== ФОНОВЫЕ ПРОЦЕССЫ ====================

def hourly_update():
    current_time = int(time.time())
    for uid, data in users.items():
        # Депозит
        dep = data.get('deposit_balance', 0)
        if dep > 0: data['deposit_balance'] += int(dep * 0.01)
        
        # Бизнес
        if data.get('business') is not None:
            data['business_income'] += businesses[data['business']]['income_per_hour'] * data.get('business_workers', 0)
            
        # Ферма
        if data.get('farm') is not None:
            f = farms[data['farm']]
            if data['farm_income'] < FARM_CRYPTO_LIMITS[f['crypto_type']]:
                inc = f['income_per_gpu'] * data.get('farm_gpus', 0)
                data['farm_income'] = min(data['farm_income'] + inc, FARM_CRYPTO_LIMITS[f['crypto_type']])
                
    save_users_data()
    
    ct = int(time.time())
    next_h = ct - (ct % 3600) + 3600
    threading.Timer(next_h - ct, hourly_update).start()

def energy_update():
    for uid, data in users.items():
        if data.get('energy', 0) < 25:
            data['energy'] = min(25, data['energy'] + 1)
    save_users_data()
    threading.Timer(300, energy_update).start()

ct = int(time.time())
threading.Timer((ct - (ct % 3600) + 3600) - ct, hourly_update).start()
threading.Timer(300, energy_update).start()

if __name__ == '__main__':
    bot.polling(none_stop=True)