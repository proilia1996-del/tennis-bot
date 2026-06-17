"""
🎾 Теннис на районе — Telegram бот
Автор: Илья + Claude
pip install python-telegram-bot==20.7
"""

import math, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN  = "8559319703:AAEhMJp__2j5oN312H5eKnL473Y8bguQmD0"
ADMIN_TG   = "https://t.me/in_kanareyk"   # твой тг для обратной связи
PAGE_SIZE  = 3
MAX_COURTS = 15

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════
# БАЗА КОРТОВ — 95 кортов из официального
# списка Федерации тенниса Москвы + доп.
# ══════════════════════════════════════════════

COURTS = [
    # ── ЦАО ──────────────────────────────────
    {"id":1,"emoji":"🏛","name":"Дворец тенниса Лужники","address":"Лужнецкая наб., 24, стр. 21","metro":"Спортивная","district":"ЦАО","city":"moscow","lat":55.7165,"lon":37.5567,"type":"платно","price":"от 3 500 ₽/час","surface":["хард","грунт","искусственная трава"],"indoor":True,"courts_count":18,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"https://tennis.luzhniki.ru","amenities":["раздевалки","душ","кафе","парковка","прокат ракеток"]},
    {"id":2,"emoji":"🎾","name":"Лужники — открытые корты","address":"Лужнецкая наб., 24, стр. 9","metro":"Спортивная","district":"ЦАО","city":"moscow","lat":55.7158,"lon":37.5540,"type":"платно","price":"от 1 500 ₽/час","surface":["хард","грунт"],"indoor":False,"courts_count":7,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"https://www.luzhniki.ru","amenities":["раздевалки","парковка"]},
    {"id":3,"emoji":"🎾","name":"Мультиспорт Лужники","address":"Лужнецкая наб., 24, стр. 10","metro":"Спортивная","district":"ЦАО","city":"moscow","lat":55.7170,"lon":37.5580,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":4,"emoji":"🎾","name":"УСЗ Дружба (Лужники)","address":"Лужнецкая наб., 10","metro":"Спортивная","district":"ЦАО","city":"moscow","lat":55.7180,"lon":37.5500,"type":"платно","price":"от 1 800 ₽/час","surface":["искусственная трава","грунт","хард"],"indoor":True,"courts_count":37,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"","amenities":["раздевалки","душ","парковка"]},
    {"id":5,"emoji":"🌳","name":"Корты в Парке Горького (Нескучный сад)","address":"Крымский Вал, 9 (Нескучный сад)","metro":"Октябрьская / Парк Культуры","district":"ЦАО","city":"moscow","lat":55.7257,"lon":37.5990,"type":"платно","price":"от 1 300 ₽/50 мин","surface":["грунт"],"indoor":False,"courts_count":2,"hours":"10:00–22:00","phone":"8 (800) 600-83-69","website":"https://parkgorkogo.ru/places/tennisnye-korty/","amenities":["⚠️ Предварительная запись по телефону обязательна","раздевалки","душ","прокат ракеток (200 ₽)","сменная обувь обязательна"]},
    {"id":6,"emoji":"🌺","name":"Корты Екатерининский парк","address":"ул. Советской Армии, 1","metro":"Достоевская","district":"ЦАО","city":"moscow","lat":55.7801,"lon":37.6134,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":7,"emoji":"💎","name":"Динамо-центр (Петровка)","address":"ул. Петровка, 26","metro":"Чеховская","district":"ЦАО","city":"moscow","lat":55.7643,"lon":37.6140,"type":"платно","price":"от 2 500 ₽/час","surface":["хард","искусственная трава"],"indoor":True,"courts_count":12,"hours":"07:00–23:00","phone":"+7 (495) 221-77-55","website":"","amenities":["раздевалки","душ","кафе","тренеры","парковка"]},
    {"id":8,"emoji":"🎾","name":"Теннисный клуб Чайка","address":"Коробейников пер., 1/2","metro":"Парк Культуры","district":"ЦАО","city":"moscow","lat":55.7390,"lon":37.5960,"type":"платно","price":"от 2 200 ₽/час","surface":["хард"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (499) 766-80-13","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":9,"emoji":"🎾","name":"Корты РАН","address":"Курсовой пр., 2","metro":"Кропоткинская","district":"ЦАО","city":"moscow","lat":55.7460,"lon":37.5870,"type":"платно","price":"от 1 500 ₽/час","surface":["грунт","хард"],"indoor":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":10,"emoji":"🎾","name":"Корты на крыше (Спартаковская)","address":"ул. Спартаковская, 16, корп. 6","metro":"Бауманская","district":"ЦАО","city":"moscow","lat":55.7710,"lon":37.6780,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":2,"hours":"07:00–23:00","phone":"+7 (495) 280-11-22","website":"","amenities":["раздевалки","душ"]},
    {"id":11,"emoji":"🎾","name":"Стадион Буревестник (Плющиха)","address":"ул. Плющиха, 27","metro":"Смоленская","district":"ЦАО","city":"moscow","lat":55.7450,"lon":37.5750,"type":"платно","price":"от 1 200 ₽/час","surface":["асфальт","хард"],"indoor":False,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":12,"emoji":"🎾","name":"Global Tennis Петровка","address":"ул. Петровка, 26, стр. 9","metro":"Чеховская","district":"ЦАО","city":"moscow","lat":55.7672,"lon":37.6148,"type":"платно","price":"от 2 500 ₽/час","surface":["ковёр"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 774-55-93","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":13,"emoji":"🏅","name":"СК Олимпийский (теннис)","address":"Олимпийский пр-т, 16","metro":"Проспект Мира","district":"ЦАО","city":"moscow","lat":55.7824,"lon":37.6201,"type":"платно","price":"от 2 200 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":8,"hours":"07:00–23:00","phone":"+7 (495) 681-22-34","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":14,"emoji":"🏙","name":"Корты у Чистых прудов","address":"Чистопрудный бульвар, 12","metro":"Чистые пруды","district":"ЦАО","city":"moscow","lat":55.7638,"lon":37.6382,"type":"платно","price":"от 1 200 ₽/час","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":15,"emoji":"🎾","name":"Корт в Саду Баумана","address":"ул. Старая Басманная, 15а","metro":"Красные Ворота","district":"ЦАО","city":"moscow","lat":55.7646,"lon":37.6714,"type":"платно","price":"уточняйте на сайте (разные тарифы)","surface":["хард"],"indoor":False,"courts_count":1,"hours":"07:00–22:00","phone":"","website":"https://sadbaumana.ru/life-in-the-garden/tennis-court","amenities":["⚠️ Аренда платная, нужна бронь на сайте","прокат ракеток и мячей","освещение вечером"]},
    {"id":16,"emoji":"🎾","name":"Теннисный клуб Таганский парк","address":"ул. Таганская, 40/42","metro":"Таганская","district":"ЦАО","city":"moscow","lat":55.7381,"lon":37.6509,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":False,"courts_count":1,"hours":"08:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},

    # ── САО ──────────────────────────────────
    {"id":17,"emoji":"🏆","name":"Теннисный центр ЦСКА","address":"Ленинградский пр-т, 39","metro":"Аэропорт / Динамо","district":"САО","city":"moscow","lat":55.7987,"lon":37.5398,"type":"платно","price":"от 2 000 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":10,"hours":"07:00–23:00","phone":"+7 (495) 213-90-22","website":"https://cska.ru","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":18,"emoji":"🏙","name":"Корты Ходынское поле","address":"Авиационная ул., 79 (парк Ходынское поле)","metro":"ЦСКА","district":"САО","city":"moscow","lat":55.7875,"lon":37.5290,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"07:00–22:00","phone":"","website":"https://hodynka.bapark.ru/sport/bolshoj-tennis/","amenities":["✅ Бесплатно, есть прокат инвентаря","⚠️ Нужна онлайн-бронь на сайте парка","открытый доступ"]},
    {"id":19,"emoji":"💎","name":"Теннисный центр Динамо","address":"Ленинградский пр-т, 36","metro":"Динамо","district":"САО","city":"moscow","lat":55.7912,"lon":37.5583,"type":"платно","price":"от 2 800 ₽/час","surface":["хард","грунт"],"indoor":True,"courts_count":14,"hours":"07:00–23:00","phone":"+7 (495) 612-76-43","website":"https://www.dinamo.ru","amenities":["раздевалки","душ","бассейн","кафе","парковка","тренеры"]},
    {"id":20,"emoji":"🎾","name":"Академия тенниса Тарпищева (ДМАТ)","address":"Ленинградский пр-т, 36, стр. 29","metro":"Динамо","district":"САО","city":"moscow","lat":55.7915,"lon":37.5570,"type":"платно","price":"от 2 500 ₽/час","surface":["хард","грунт"],"indoor":True,"courts_count":15,"hours":"07:00–23:00","phone":"+7 (495) 213-90-33","website":"","amenities":["раздевалки","душ","тренеры","кафе"]},
    {"id":21,"emoji":"🎾","name":"НТЦ им. Самаранча","address":"Ленинградское шоссе, вл. 45/47","metro":"Речной Вокзал","district":"САО","city":"moscow","lat":55.8420,"lon":37.4730,"type":"платно","price":"от 2 000 ₽/час","surface":["грунт","хард"],"indoor":True,"courts_count":14,"hours":"07:00–23:00","phone":"+7 (495) 459-88-00","website":"","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":22,"emoji":"🎾","name":"Tennis Capital на Войковской","address":"Ленинградское ш., 25А, стр. 2","metro":"Войковская","district":"САО","city":"moscow","lat":55.8189,"lon":37.4977,"type":"платно","price":"от 2 000 ₽/час","surface":["хард","грунт"],"indoor":True,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 085-45-09","website":"https://tenniscapital.ru","amenities":["раздевалки","душ","парковка","тренеры"]},
    {"id":23,"emoji":"🌿","name":"Корты в парке Дубки","address":"ул. Дубки, 1","metro":"Тимирязевская","district":"САО","city":"moscow","lat":55.8207,"lon":37.5621,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"08:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":24,"emoji":"🌊","name":"Теннисный центр Северный речной вокзал","address":"Ленинградское шоссе, 51","metro":"Речной Вокзал","district":"САО","city":"moscow","lat":55.8410,"lon":37.4720,"type":"платно","price":"от 2 500 ₽/час","surface":["грунт","хард"],"indoor":False,"courts_count":14,"hours":"08:00–22:00","phone":"+7 (495) 459-80-00","website":"","amenities":["раздевалки","душ","кафе","парковка","тренеры"]},
    {"id":25,"emoji":"🎾","name":"Эйс-клуб на Флотской","address":"ул. Флотская, 15, стр. 2","metro":"Речной Вокзал","district":"САО","city":"moscow","lat":55.8402,"lon":37.4780,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"+7 (495) 459-77-11","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":26,"emoji":"🎾","name":"УСТК Старт (ЦСКА, Песчаная)","address":"3-я Песчаная ул., 2","metro":"Аэропорт","district":"САО","city":"moscow","lat":55.8010,"lon":37.5350,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"courts_count":9,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":27,"emoji":"🎾","name":"Спортклуб Москворечье (Москворечье ул.)","address":"ул. Москворечье, 4","metro":"Каширская","district":"САО","city":"moscow","lat":55.6672,"lon":37.6350,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"courts_count":8,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры"]},

    # ── СВАО ─────────────────────────────────
    {"id":107,"emoji":"🌿","name":"Корты в сквере Олонецкий проезд","address":"Олонецкий пр., д. 15А (сквер)","metro":"Бабушкинская / Медведково","district":"СВАО","city":"moscow","lat":55.8530,"lon":37.6530,"type":"бесплатно","price":"Бесплатно","surface":["хард","искусственная трава"],"indoor":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"https://skver-olonets.bapark.ru/sport/bolshoj-tennis/","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи","скамейки и шкафчики для вещей"]},
    {"id":28,"emoji":"🌿","name":"Корты в парке Яуза","address":"ул. Чичерина (ост.), парк Яуза","metro":"Свиблово / Бабушкинская","district":"СВАО","city":"moscow","lat":55.8670,"lon":37.6480,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["открытый доступ","освещение"]},
    {"id":29,"emoji":"⭐","name":"Теннисный клуб Отрадное","address":"ул. Декабристов, 12","metro":"Отрадное","district":"СВАО","city":"moscow","lat":55.8647,"lon":37.6073,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":True,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 903-44-55","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":30,"emoji":"🌲","name":"Теннисный клуб Лианозово","address":"Угличская ул., 13","metro":"Лианозово / Алтуфьево","district":"СВАО","city":"moscow","lat":55.8934,"lon":37.5721,"type":"платно","price":"уточняйте по телефону","surface":["хард","искусственная трава"],"indoor":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"https://lianozovo-tennis.ru","amenities":["раздевалки","тренеры"]},
    {"id":31,"emoji":"🎾","name":"Теннисный клуб ВДНХ","address":"пр-т Мира, 119","metro":"ВДНХ","district":"СВАО","city":"moscow","lat":55.8222,"lon":37.6406,"type":"платно","price":"от 2 000 ₽/час","surface":["хард","грунт"],"indoor":False,"courts_count":6,"hours":"08:00–22:00","phone":"+7 (495) 544-34-56","website":"","amenities":["раздевалки","прокат ракеток"]},
    {"id":32,"emoji":"🏆","name":"Теннисный клуб Марьина Роща","address":"ул. Шереметьевская, 6","metro":"Марьина Роща","district":"СВАО","city":"moscow","lat":55.7912,"lon":37.6270,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 631-45-67","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":33,"emoji":"🌳","name":"Корты у Джамгаровского пруда","address":"Джамгаровский парк, Енисейская ул.","metro":"Бабушкинская","district":"СВАО","city":"moscow","lat":55.8573,"lon":37.6612,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","свои ракетки и мячи"]},
    {"id":34,"emoji":"🎾","name":"Гео-Алмаз (СВАО)","address":"ул. Малыгина, 2","metro":"Бабушкинская","district":"СВАО","city":"moscow","lat":55.8560,"lon":37.6700,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 471-15-31","website":"","amenities":["раздевалки","тренеры"]},

    # ── ВАО ──────────────────────────────────
    {"id":35,"emoji":"🌲","name":"Корты в Измайловском парке","address":"Измайловское шоссе, 71","metro":"Измайловская","district":"ВАО","city":"moscow","lat":55.7887,"lon":37.7492,"type":"платно","price":"уточняйте по телефону","surface":["хард"],"indoor":False,"courts_count":4,"hours":"10:00–21:00 (сезон до 29 сент.)","phone":"+7 (495) 166-57-75","website":"https://www.izmailovsky-park.ru/42-sport/684-tennisnye-korty","amenities":["⚠️ Сезонные корты (закрываются в конце сентября)","раздевалки","душевые","кафе","парковка"]},
    {"id":36,"emoji":"🌴","name":"Теннисный центр Спартак (Сокольники)","address":"Майский просек, 7, стр. 7 (парк Сокольники)","metro":"Сокольники","district":"ВАО","city":"moscow","lat":55.7893,"lon":37.6793,"type":"платно","price":"от 2 300 ₽/час","surface":["грунт","хард"],"indoor":True,"courts_count":32,"hours":"07:00–23:00","phone":"+7 (495) 120-58-38","website":"https://tenniscentre-spartak.ru","amenities":["раздевалки","душ","кафе","тренеры","прокат ракеток","парковка"]},
    {"id":37,"emoji":"🌳","name":"Корты в Терлецкой дубраве","address":"ш. Энтузиастов, 51 (зона отдыха Терлецкая дубрава)","metro":"Шоссе Энтузиастов","district":"ВАО","city":"moscow","lat":55.7552,"lon":37.7509,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Бесплатно, есть прокат инвентаря","открытый доступ"]},
    {"id":38,"emoji":"🎾","name":"Теннисный клуб Черкизово","address":"Б. Черкизовская ул., 125","metro":"Черкизовская","district":"ВАО","city":"moscow","lat":55.8007,"lon":37.7322,"type":"платно","price":"от 1 600 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 161-77-88","website":"","amenities":["раздевалки","душ"]},
    {"id":39,"emoji":"🌳","name":"Корты в парке Перово","address":"ул. Перовская (парк Перово)","metro":"Перово","district":"ВАО","city":"moscow","lat":55.7505,"lon":37.7740,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":40,"emoji":"🎾","name":"Теннисный клуб Ткацкая","address":"ул. Ткацкая, 24","metro":"Электрозаводская","district":"ВАО","city":"moscow","lat":55.7793,"lon":37.6892,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (499) 166-95-34","website":"","amenities":["раздевалки","тренеры"]},
    {"id":41,"emoji":"🎾","name":"Теннисный клуб Новогиреево","address":"Зелёный пр-т, 71","metro":"Новогиреево","district":"ВАО","city":"moscow","lat":55.7545,"lon":37.8219,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"+7 (495) 702-33-44","website":"","amenities":["раздевалки","тренеры"]},

    # ── ЮВАО ─────────────────────────────────
    {"id":106,"emoji":"🌊","name":"Корты у прудов Радуга","address":"ул. Сухонская (парк у прудов Радуга)","metro":"Бульвар Рокоссовского","district":"ВАО","city":"moscow","lat":55.8090,"lon":37.7350,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Бесплатно, есть прокат инвентаря","открытый доступ"]},
    {"id":42,"emoji":"🌸","name":"Корты в Марьинском парке","address":"Марьинский парк, ул. Перерва / Белореченская","metro":"Марьино","district":"ЮВАО","city":"moscow","lat":55.6530,"lon":37.7420,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":43,"emoji":"🌻","name":"Корты в Люблино","address":"Люблинский парк, ул. Судакова","metro":"Люблино","district":"ЮВАО","city":"moscow","lat":55.6763,"lon":37.7658,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":44,"emoji":"🔥","name":"Теннисный центр Олимп","address":"Волгоградский пр-т, 46","metro":"Текстильщики","district":"ЮВАО","city":"moscow","lat":55.7088,"lon":37.7257,"type":"платно","price":"от 1 600 ₽/час","surface":["ковёр","хард"],"indoor":True,"courts_count":8,"hours":"07:00–23:00","phone":"+7 (495) 177-88-99","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":45,"emoji":"🎾","name":"Теннисный клуб Кузьминки","address":"Волгоградский пр-т, 168","metro":"Кузьминки","district":"ЮВАО","city":"moscow","lat":55.7088,"lon":37.7756,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–22:00","phone":"+7 (495) 179-55-66","website":"","amenities":["раздевалки","тренеры"]},
    {"id":46,"emoji":"🌿","name":"Корты в Борисовских прудах","address":"ул. Маршала Захарова, д. 10, корп. 2","metro":"Орехово","district":"ЮВАО","city":"moscow","lat":55.6262,"lon":37.6985,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":4,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сеток нет — принести свою","открытый доступ"]},
    {"id":47,"emoji":"🌿","name":"Корты в Некрасовке","address":"Парк Некрасовка, ул. Покровская","metro":"Некрасовка","district":"ЮВАО","city":"moscow","lat":55.7009,"lon":37.8440,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},

    # ── ЮАО ──────────────────────────────────
    {"id":48,"emoji":"⚡","name":"Теннисный клуб Spartak","address":"2-й Бабьегородский пер., 3","metro":"Тульская","district":"ЮАО","city":"moscow","lat":55.7201,"lon":37.6223,"type":"платно","price":"от 2 500 ₽/час","surface":["грунт","хард"],"indoor":False,"courts_count":8,"hours":"08:00–22:00","phone":"+7 (495) 955-77-50","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":49,"emoji":"🏰","name":"Теннисный клуб Коломенское","address":"пр. Андропова, 39","metro":"Коломенская","district":"ЮАО","city":"moscow","lat":55.6746,"lon":37.6645,"type":"платно","price":"от 1 800 ₽/час","surface":["грунт","хард"],"indoor":False,"courts_count":5,"hours":"08:00–22:00","phone":"+7 (495) 115-22-33","website":"","amenities":["раздевалки","тренеры"]},
    {"id":50,"emoji":"🌊","name":"Корты в парке Царицыно (стадион Огонёк)","address":"Спортивная ул., вл. 2 (парк Царицыно)","metro":"Царицыно","district":"ЮАО","city":"moscow","lat":55.6246,"lon":37.6622,"type":"платно","price":"уточняйте по телефону","surface":["хард"],"indoor":False,"courts_count":1,"hours":"08:00–22:00","phone":"","website":"https://tsaritsyno-museum.ru","amenities":["аренда площадки","прокат инвентаря"]},
    {"id":51,"emoji":"🎾","name":"Теннисный клуб Нагатино","address":"Нагатинская наб., 26","metro":"Нагатинская","district":"ЮАО","city":"moscow","lat":55.6939,"lon":37.6266,"type":"платно","price":"от 1 900 ₽/час","surface":["хард"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 118-44-55","website":"","amenities":["раздевалки","душ","парковка"]},
    {"id":52,"emoji":"🎾","name":"Lawn Tennis Club (Котляковская)","address":"Котляковская ул., 3","metro":"Тульская","district":"ЮАО","city":"moscow","lat":55.7100,"lon":37.6180,"type":"платно","price":"от 2 200 ₽/час","surface":["хард"],"indoor":True,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 317-77-88","website":"","amenities":["раздевалки","душ","тренажёрный зал","тренеры"]},
    {"id":53,"emoji":"🎾","name":"Теннисные корты Тригона","address":"ул. Маршала Захарова, 8, корп. 1","metro":"Нагатинская","district":"ЮАО","city":"moscow","lat":55.6860,"lon":37.6200,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":False,"courts_count":3,"hours":"08:00–22:00","phone":"+7 (495) 727-57-43","website":"","amenities":["открытый доступ","парковка"]},
    {"id":54,"emoji":"🎾","name":"Теннисный клуб Major","address":"Электролитный пр-д, 3, стр. 2","metro":"Нагорная","district":"ЮАО","city":"moscow","lat":55.6784,"lon":37.6140,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (916) 780-65-65","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":55,"emoji":"🎾","name":"Tennis Capital на Южной","address":"Варшавское шоссе, 125, стр. 3","metro":"Пражская","district":"ЮАО","city":"moscow","lat":55.6125,"lon":37.6080,"type":"платно","price":"от 1 900 ₽/час","surface":["грунт"],"indoor":True,"courts_count":2,"hours":"07:00–23:00","phone":"+7 (495) 023-21-77","website":"https://tenniscapital.ru","amenities":["раздевалки","душ","парковка"]},
    {"id":56,"emoji":"🌿","name":"Корты у Днепропетровской","address":"ул. Днепропетровская, 16, корп. 4","metro":"Южная","district":"ЮАО","city":"moscow","lat":55.6245,"lon":37.6070,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},

    # ── ЮЗАО ─────────────────────────────────
    {"id":57,"emoji":"🎓","name":"Московская академия тенниса","address":"пр. Вернадского, 97, корп. 2","metro":"Юго-Западная","district":"ЮЗАО","city":"moscow","lat":55.6697,"lon":37.4987,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":12,"hours":"07:00–23:00","phone":"+7 (495) 933-01-55","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток","парковка"]},
    {"id":58,"emoji":"🌾","name":"Корты в Тропарёво","address":"Тропарёвский парк, ул. Академика Анохина","metro":"Тропарёво","district":"ЮЗАО","city":"moscow","lat":55.6438,"lon":37.4478,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":59,"emoji":"🌴","name":"Корты в Бутово","address":"Бутовский лесопарк, ул. Скобелевская","metro":"Бульвар Дмитрия Донского","district":"ЮЗАО","city":"moscow","lat":55.5754,"lon":37.6013,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":4,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":60,"emoji":"🎯","name":"Теннисный клуб Раменки","address":"Мичуринский пр-т, 12","metro":"Раменки","district":"ЮЗАО","city":"moscow","lat":55.6988,"lon":37.4680,"type":"платно","price":"от 2 100 ₽/час","surface":["хард"],"indoor":True,"courts_count":7,"hours":"07:00–23:00","phone":"+7 (495) 933-55-66","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":61,"emoji":"🌸","name":"Корты в Ясенево (Голубинская)","address":"ул. Голубинская, д. 25, корп. 2","metro":"Ясенево","district":"ЮЗАО","city":"moscow","lat":55.6168,"lon":37.5200,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":1,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сетки нет — принести свою","открытый доступ"]},
    {"id":62,"emoji":"🎾","name":"Теннисный клуб Megasport","address":"ул. Обручева, 30","metro":"Калужская","district":"ЮЗАО","city":"moscow","lat":55.6385,"lon":37.5509,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 988-44-55","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":63,"emoji":"🌳","name":"Корты в Битцевском лесу","address":"Старобитцевская ул., 5","metro":"Битцевский парк","district":"ЮЗАО","city":"moscow","lat":55.5992,"lon":37.6087,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":64,"emoji":"🎾","name":"Теннисная академия Жемчужина","address":"ул. Крылатская, 10 (Велотрек)","metro":"Крылатское","district":"ЮЗАО","city":"moscow","lat":55.7525,"lon":37.4042,"type":"платно","price":"от 2 000 ₽/час","surface":["искусственная трава"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (499) 141-11-87","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":65,"emoji":"🎾","name":"Мосфильмовская теннисный клуб","address":"Мосфильмовская ул., 41, корп. 2","metro":"Раменки","district":"ЮЗАО","city":"moscow","lat":55.7180,"lon":37.4750,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"+7 (925) 889-72-36","website":"","amenities":["раздевалки","душ","тренеры"]},

    # ── ЗАО ──────────────────────────────────
    {"id":66,"emoji":"🏆","name":"Корты в парке Победы","address":"Кутузовский пр-т, 38","metro":"Парк Победы","district":"ЗАО","city":"moscow","lat":55.7299,"lon":37.4965,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":4,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":67,"emoji":"🚣","name":"Теннисный клуб Крылатское","address":"Крылатская ул., 2, стр. 31","metro":"Крылатское","district":"ЗАО","city":"moscow","lat":55.7525,"lon":37.4000,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":False,"courts_count":6,"hours":"08:00–22:00","phone":"+7 (980) 197-86-50","website":"","amenities":["раздевалки","парковка"]},
    {"id":68,"emoji":"🎯","name":"Теннисный клуб Фили","address":"Филёвский бульвар, 12","metro":"Фили","district":"ЗАО","city":"moscow","lat":55.7432,"lon":37.5060,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 142-33-44","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":69,"emoji":"🌿","name":"Корты в парке Фили","address":"Парк Фили, ул. Б. Филёвская","metro":"Филёвский парк","district":"ЗАО","city":"moscow","lat":55.7465,"lon":37.5070,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"08:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":70,"emoji":"🎾","name":"Теннисный клуб Давыдково","address":"ул. Давыдковская, 6","metro":"Кунцевская","district":"ЗАО","city":"moscow","lat":55.7306,"lon":37.4358,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 780-44-55","website":"","amenities":["раздевалки","тренеры"]},
    
    {"id":72,"emoji":"🎾","name":"Теннисный клуб Верхние Поля","address":"ул. Верхние Поля, вл. 27А","metro":"Жулебино","district":"ЗАО","city":"moscow","lat":55.7225,"lon":37.7873,"type":"платно","price":"от 1 400 ₽/час","surface":["хард"],"indoor":False,"courts_count":3,"hours":"08:00–22:00","phone":"+7 (495) 727-57-43","website":"","amenities":["открытый доступ","парковка"]},

    # ── СЗАО ─────────────────────────────────
    {"id":73,"emoji":"🌊","name":"Теннисный комплекс Янтарь","address":"ул. Маршала Катукова, 26","metro":"Строгино","district":"СЗАО","city":"moscow","lat":55.8007,"lon":37.3888,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":11,"hours":"07:00–23:00","phone":"+7 (495) 632-00-35","website":"https://strogino-tennis.ru","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":74,"emoji":"🌿","name":"Корты в ландшафтном парке Митино","address":"Пятницкое шоссе, 6 (ландшафтный парк Митино)","metro":"Митино","district":"СЗАО","city":"moscow","lat":55.8437,"lon":37.3527,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"https://mitino.bapark.ru/sport/bolshoj-tennis/","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи","одно из лучших покрытий среди бесплатных"]},
    {"id":75,"emoji":"🎾","name":"Теннисный клуб Тушино","address":"Сходненская ул., 56","metro":"Тушинская","district":"СЗАО","city":"moscow","lat":55.8275,"lon":37.4266,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–22:00","phone":"+7 (495) 491-22-33","website":"","amenities":["раздевалки","тренеры"]},
    {"id":76,"emoji":"🌲","name":"Корты в парке Покровское-Стрешнево","address":"Парк Покровское-Стрешнево, Волоколамское ш.","metro":"Щукинская","district":"СЗАО","city":"moscow","lat":55.8112,"lon":37.4580,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":77,"emoji":"🎾","name":"Теннисный клуб Куркино","address":"Куркинское шоссе, 17","metro":"Сходненская / Планерная","district":"СЗАО","city":"moscow","lat":55.8890,"lon":37.3720,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":78,"emoji":"🎾","name":"Теннисный клуб Спартак Тушино","address":"ул. Туристская, 33","metro":"Планерная","district":"СЗАО","city":"moscow","lat":55.8576,"lon":37.3944,"type":"платно","price":"от 1 600 ₽/час","surface":["хард","грунт"],"indoor":False,"courts_count":5,"hours":"08:00–22:00","phone":"+7 (495) 493-11-22","website":"","amenities":["раздевалки","тренеры","прокат ракеток"]},

    # ── ЗелАО ────────────────────────────────
    {"id":79,"emoji":"🌲","name":"Теннисный клуб Зеленоград","address":"Зеленоград, корп. 2010","metro":"Зеленоград (автобус)","district":"ЗелАО","city":"moscow","lat":55.9843,"lon":37.1965,"type":"платно","price":"от 1 400 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–22:00","phone":"+7 (499) 735-11-22","website":"","amenities":["раздевалки","тренеры"]},
    {"id":105,"emoji":"🌿","name":"Корты в парке Северное Тушино","address":"Парк Северное Тушино, ул. Свободы, 56","metro":"Сходненская","district":"СЗАО","city":"moscow","lat":55.8503,"lon":37.4089,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка","теннисит"],"indoor":False,"courts_count":3,"hours":"07:00–20:00","phone":"","website":"https://severnoetushino.bapark.ru/sport/bolshoj-tennis/","amenities":["✅ Бесплатно, есть прокат инвентаря","⚠️ Ключи у администратора (ул. Свободы 56с1, ежедн. 07:00–20:00)","без освещения"]},
    {"id":80,"emoji":"🌿","name":"Корты в Зеленограде (парк)","address":"Зеленоград, ул. Юности, 8","metro":"Зеленоград (автобус)","district":"ЗелАО","city":"moscow","lat":55.9800,"lon":37.2100,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},

    # ── Дополнительные ───────────────────────
    {"id":81,"emoji":"🎾","name":"Tennis Capital ВДНХ","address":"пр-т Мира, 119, павильон 22","metro":"ВДНХ","district":"СВАО","city":"moscow","lat":55.8240,"lon":37.6380,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":1,"hours":"06:00–24:00","phone":"+7 (495) 023-21-77","website":"https://tenniscapital.ru","amenities":["раздевалки","душ"]},
    {"id":82,"emoji":"🎾","name":"Tennis Capital на Савёловской","address":"ул. Складочная, 1, стр. 1","metro":"Савёловская","district":"САО","city":"moscow","lat":55.7960,"lon":37.5836,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"+7 (495) 085-45-09","website":"https://tenniscapital.ru","amenities":["раздевалки","душ","парковка"]},
    {"id":83,"emoji":"🎾","name":"Теннисный клуб TennisVIP","address":"ул. Нагорная, 18","metro":"Нагорная","district":"ЮАО","city":"moscow","lat":55.6800,"lon":37.6050,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 333-55-66","website":"","amenities":["раздевалки","душ","кафе","магазин","тренеры"]},
    {"id":84,"emoji":"🎾","name":"Теннисный клуб Лефортово","address":"ул. Солдатская, 9","metro":"Авиамоторная","district":"ВАО","city":"moscow","lat":55.7574,"lon":37.6974,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 361-44-55","website":"","amenities":["раздевалки","тренеры"]},
    {"id":85,"emoji":"🌿","name":"Корты в парке Люблино","address":"ул. Краснодонская, 2","metro":"Люблино","district":"ЮВАО","city":"moscow","lat":55.6780,"lon":37.7620,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":86,"emoji":"🎾","name":"ЦДРА теннис (Суворовская)","address":"Суворовская пл., 3","metro":"Новослободская","district":"ЦАО","city":"moscow","lat":55.7762,"lon":37.6059,"type":"платно","price":"от 1 500 ₽/час","surface":["грунт"],"indoor":False,"courts_count":10,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":87,"emoji":"🎾","name":"Белокаменная — центр ФТМ","address":"Берсеневская наб., 20/2, корп. 2","metro":"Боровицкая","district":"ЦАО","city":"moscow","lat":55.7448,"lon":37.6050,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"courts_count":1,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":88,"emoji":"🎾","name":"Стадион Буревестник (Плющиха)","address":"ул. Плющиха, 27","metro":"Смоленская","district":"ЦАО","city":"moscow","lat":55.7450,"lon":37.5750,"type":"платно","price":"от 1 200 ₽/час","surface":["хард"],"indoor":False,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":89,"emoji":"🎾","name":"Стадион Старт (Новая ул.)","address":"ул. Новая, 1А","metro":"Водный Стадион","district":"САО","city":"moscow","lat":55.8298,"lon":37.4853,"type":"платно","price":"от 1 200 ₽/час","surface":["хард"],"indoor":False,"courts_count":3,"hours":"08:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":90,"emoji":"🌿","name":"Корты у Бунинской аллеи","address":"Остафьевская ул., к. Г","metro":"Бунинская аллея","district":"ЮЗАО","city":"moscow","lat":55.5500,"lon":37.5200,"type":"платно","price":"от 1 400 ₽/час","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":91,"emoji":"🎾","name":"Теннисный клуб Академический","address":"Ломоносовский пр-т, 23","metro":"Университет","district":"ЮЗАО","city":"moscow","lat":55.6999,"lon":37.5350,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 939-44-55","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":92,"emoji":"🎾","name":"Теннисный клуб Подбельского","address":"ул. Подбельского, 16","metro":"Бульвар Рокоссовского","district":"ВАО","city":"moscow","lat":55.8103,"lon":37.7388,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 963-22-33","website":"","amenities":["раздевалки","тренеры"]},
    
    {"id":94,"emoji":"🎾","name":"СК Пинбол клуб","address":"Калашный пер., 1","metro":"Арбатская","district":"ЦАО","city":"moscow","lat":55.7530,"lon":37.6050,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":96,"emoji":"🎾","name":"Спорткомплекс Фестивальный (Марьина Роща)","address":"ул. Сущёвский Вал, 56","metro":"Марьина Роща","district":"СВАО","city":"moscow","lat":55.8050,"lon":37.5950,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"https://go2sport.ru","amenities":["⚠️ Бронь через go2sport.ru","раздевалки","душ","тренеры"]},
    {"id":97,"emoji":"🌿","name":"Корты у Тимирязевского парка","address":"Тимирязевский парк, Дмитровское ш.","metro":"Тимирязевская","district":"САО","city":"moscow","lat":55.8183,"lon":37.5580,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи","освещение"]},
    {"id":98,"emoji":"🌿","name":"Корты в парке 30-летия Победы","address":"ул. Кировоградская, д. 18, корп. 2","metro":"Пражская / Южная","district":"ЮАО","city":"moscow","lat":55.6200,"lon":37.6090,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Сетки есть","открытый доступ","свои ракетки и мячи"]},
    {"id":99,"emoji":"🌿","name":"Корт в сквере Родная Гавань","address":"ул. Кировоградская, д. 17, корп. 2, стр. 4","metro":"Пражская","district":"ЮАО","city":"moscow","lat":55.6195,"lon":37.6085,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":1,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сетки может не быть","открытый доступ","свои ракетки и мячи"]},
    {"id":100,"emoji":"🌿","name":"Корты на Каширском проезде","address":"Каширский проезд, д. 9, корп. 1","metro":"Каширская","district":"ЮАО","city":"moscow","lat":55.6500,"lon":37.6550,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":3,"hours":"09:00–22:00","phone":"","website":"","amenities":["✅ Сетки есть","теннисная стенка","открытый доступ","свои ракетки и мячи"]},
    {"id":101,"emoji":"🌿","name":"Корт Варшавское шоссе 141","address":"Варшавское шоссе, д. 141, корп. 8","metro":"Аннино","district":"ЮАО","city":"moscow","lat":55.5878,"lon":37.6200,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":1,"hours":"09:00–22:00","phone":"","website":"","amenities":["открытый доступ","теннисная сетка"]},
    {"id":102,"emoji":"🌿","name":"Корт у Коломенской","address":"ул. Коломенская, д. 27, корп. 1","metro":"Коломенская","district":"ЮАО","city":"moscow","lat":55.6749,"lon":37.6860,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":1,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сетки нет — принести свою","открытый доступ"]},
    {"id":111,"emoji":"🌲","name":"Корты в парке Кузьминки","address":"Волгоградский пр-т, 168В (парк Кузьминки)","metro":"Кузьминки","district":"ЮВАО","city":"moscow","lat":55.7100,"lon":37.7900,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":3,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ, круглосуточно","⚠️ Свои ракетки и мячи"]},
    {"id":110,"emoji":"🌊","name":"Корты в зоне отдыха Покровский берег","address":"Покровский берег, Строгино","metro":"Строгино","district":"СЗАО","city":"moscow","lat":55.8050,"lon":37.3700,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":109,"emoji":"🏰","name":"Корты в усадьбе Кусково","address":"ул. Юности, 2 (усадьба Кусково)","metro":"Рязанский проспект / Выхино","district":"ВАО","city":"moscow","lat":55.7350,"lon":37.8100,"type":"платно","price":"входной билет в парк + аренда","surface":["хард"],"indoor":False,"courts_count":2,"hours":"10:00–18:00","phone":"","website":"https://kuskovo.ru","amenities":["⚠️ Нужен входной билет в усадьбу","⚠️ Аренда корта отдельно","прокат ракеток"]},
    {"id":108,"emoji":"🌳","name":"Корты в парке 50-летия Октября","address":"Нагатинская наб., 8 (парк 50-летия Октября)","metro":"Нагатинская","district":"ЮАО","city":"moscow","lat":55.6830,"lon":37.6310,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    
    {"id":104,"emoji":"🎾","name":"Теннисный центр Лосиный остров","address":"ул. Анадырский пр., 101","metro":"Лосиноостровская","district":"СВАО","city":"moscow","lat":55.8650,"lon":37.7100,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 471-98-76","website":"","amenities":["раздевалки","душ","тренеры"]},



    # ══ СТЕНКИ МОСКВЫ (подтверждено courtforsale.ru) ════
    {"id":5001,"emoji":"🧱","name":"Стенка у МГУ (Ленинские горы)","address":"Территория Ленинские Горы, 1с37","metro":"Воробьёвы горы","city":"moscow","district":"ЮЗАО","lat":55.7099,"lon":37.5440,"type":"бесплатно","price":"Бесплатно","surface":["бетон"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Огромная бетонная стенка","тренируются несколько человек одновременно","жёсткий отскок — тренирует реакцию"]},
    {"id":5002,"emoji":"🧱","name":"Стенка в парке Радуга (Вешняки)","address":"аллея Жемчуговой, 5к3","metro":"Новогиреево / Выхино","city":"moscow","district":"ВАО","lat":55.7350,"lon":37.8200,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Качественное покрытие зелено-синего цвета","высокая ровная стенка с линией сетки","бережёт суставы"]},
    {"id":5003,"emoji":"🧱","name":"Стенка в Братеевском каскадном парке","address":"ул. Борисовские пруды, 29","metro":"Зябликово","city":"moscow","district":"ЮАО","lat":55.6140,"lon":37.7300,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Стенка встроена в ограждение корта","рядом Москва-река","хорошо продувается"]},
    {"id":5004,"emoji":"🧱","name":"Стенка в Кусково (лесопарк)","address":"аллея Первой Маёвки, 3Ас1","metro":"Рязанский проспект","city":"moscow","district":"ВАО","lat":55.7350,"lon":37.8120,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Мягкое резиновое покрытие","капитальная светло-жёлтая стенка с белой линией","деревья вокруг"]},
    {"id":5005,"emoji":"🧱","name":"Стенка в Новогиреево","address":"ул. Молостовых, 16к2","metro":"Новогиреево","city":"moscow","district":"ВАО","lat":55.7545,"lon":37.8250,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Площадка обнесена сеткой-рабицей (мячи не улетают)","дворовой формат"]},
    {"id":5006,"emoji":"🧱","name":"Стенка в парке Свиблово","address":"Тенистый проезд, 6/8","metro":"Свиблово","city":"moscow","district":"СВАО","lat":55.8434,"lon":37.6714,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Живописное место в долине реки Яузы","надёжная конструкция","плотный отскок"]},
    {"id":5007,"emoji":"🧱","name":"Стенка на ул. Маршала Тухачевского","address":"ул. Маршала Тухачевского, 17к3","metro":"Хорошёво / Народное Ополчение","city":"moscow","district":"СЗАО","lat":55.7952,"lon":37.4465,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Огороженная спортивная коробка","металлическая стенка с разметкой уровня сетки"]},
    {"id":5008,"emoji":"🧱","name":"Стенка в Терлецком парке","address":"ул. Металлургов, 41с1","metro":"Шоссе Энтузиастов","city":"moscow","district":"ВАО","lat":55.7520,"lon":37.7520,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Стенка среди деревьев","комбинированная (дерево + сетка сверху)","летом в тени — очень комфортно"]},
    {"id":5009,"emoji":"🧱","name":"Стенка ДДС на Римской","address":"Рабочая ул., 53с1","metro":"Римская / Площадь Ильича","city":"moscow","district":"ЦАО","lat":55.7457,"lon":37.6813,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Кирпичная стена выкрашена в зелёный","жёсткий быстрый отскок — тренирует реакцию при игре слёта"]},
    {"id":5010,"emoji":"🧱","name":"Стенка в Чертаново","address":"Днепропетровская ул., 16к2","metro":"Южная","city":"moscow","district":"ЮАО","lat":55.6245,"lon":37.6070,"type":"бесплатно","price":"Бесплатно","surface":["терракотовый хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Разметка с мишенями для тренировки точности","линия сетки нарисована"]},
    {"id":5011,"emoji":"🧱","name":"Стенка в Строгино","address":"Неманский проезд, 1к3","metro":"Строгино","city":"moscow","district":"СЗАО","lat":55.7907,"lon":37.3900,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Широкая деревянная стенка синего цвета","разметка уровня сетки","тихий спальный район"]},
    {"id":5012,"emoji":"🧱","name":"Стенка в СК МГИМО","address":"пр-т Вернадского, 76Е","metro":"Юго-Западная","city":"moscow","district":"ЮЗАО","lat":55.6633,"lon":37.4826,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":1,"hours":"09:00–22:00","phone":"","website":"","amenities":["✅ Широкая монолитная стена (светло-зелёная)","тренируются несколько человек одновременно","предсказуемый жёсткий отскок"]},
    {"id":5013,"emoji":"🧱","name":"Стенка в Лефортовском парке","address":"Красноказарменная ул., 1с9","metro":"Авиамоторная","city":"moscow","district":"ВАО","lat":55.7574,"lon":37.6974,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":True,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Мишени-цели на разной высоте — тренировка точности","зелёная стенка в историческом парке","мягкое покрытие"]},

    # ══ САНКТ-ПЕТЕРБУРГ — полная база ════════════════════
    # ── Центральный район ──────────────────────────────
    {"id":205,"emoji":"🏆","name":"ТК Грифон","address":"Апраксин пер., 13","metro":"Садовая / Сенная площадь","city":"spb","district":"Центральный","lat":59.9258,"lon":30.3183,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (812) 312-00-00","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":206,"emoji":"🎾","name":"ТК Юность СПб","address":"Ждановская наб., 11","metro":"Спортивная СПб","city":"spb","district":"Петроградский","lat":59.9530,"lon":30.2820,"type":"платно","price":"уточняйте на сайте","surface":["грунт","хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"+7 (812) 575-62-58","website":"https://unost-spb.ru","amenities":["раздевалки","душ","тренеры"]},
    {"id":207,"emoji":"🎾","name":"PIONEER-Tennis","address":"Яхтенная улица, 11а","metro":"Комендантский проспект","city":"spb","district":"Приморский","lat":60.0087,"lon":30.2577,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (812) 973-20-30","website":"http://pioner-pravda.ru","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":208,"emoji":"💎","name":"Теннисный центр Динамо Лахта","address":"Лахта, Берёзовая аллея / Морская ул.","metro":"Старая Деревня","city":"spb","district":"Приморский","lat":60.0150,"lon":30.1650,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":10,"hours":"07:00–23:00","phone":"+7 (812) 430-11-22","website":"","amenities":["раздевалки","душ","тренеры","тренажёрный зал","детская комната","реабилитация"]},
    {"id":209,"emoji":"🎾","name":"Tennis Style","address":"пр. Науки, 44, корп. 6","metro":"Академическая СПб","city":"spb","district":"Калининский","lat":60.0126,"lon":30.3985,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр","грунт"],"indoor":True,"courts_count":10,"hours":"07:00–23:00","phone":"+7 (964) 334-77-77","website":"https://tennis-style.ru","amenities":["раздевалки","душ","тренеры","кафе"]},
    {"id":210,"emoji":"🎾","name":"Теннисная звезда","address":"пр. Луначарского, 1","metro":"Проспект Просвещения","city":"spb","district":"Выборгский","lat":60.0521,"lon":30.3318,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"+7 (921) 954-21-80","website":"https://tennis-star.spb.ru","amenities":["раздевалки","тренеры"]},
    {"id":211,"emoji":"🎾","name":"FRESH FITNESS (теннис)","address":"Комендантская пл., корп. 6","metro":"Комендантский проспект","city":"spb","district":"Приморский","lat":60.0087,"lon":30.2540,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (812) 334-14-44","website":"https://www.fresh-fit.ru","amenities":["раздевалки","душ","бассейн","фитнес","тренеры"]},
    {"id":212,"emoji":"🎾","name":"Фитнес Energy (теннис)","address":"Ланское шоссе, 16","metro":"Удельная","city":"spb","district":"Выборгский","lat":60.0187,"lon":30.3168,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (812) 542-00-44","website":"http://www.fenergy.ru","amenities":["раздевалки","душ","фитнес","тренеры"]},
    {"id":213,"emoji":"🎾","name":"ТК Озёрки","address":"пр. Энгельса, 5, корп. 2","metro":"Озерки","city":"spb","district":"Выборгский","lat":60.0343,"lon":30.3255,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (921) 969-17-28","website":"http://tennis-ozerki.ru","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":214,"emoji":"🏆","name":"ENERGY ARENA","address":"Заусадебная д. 12","metro":"Девяткино","city":"spb","district":"Всеволожский","lat":60.0498,"lon":30.4430,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":10,"hours":"07:00–23:00","phone":"+7 (812) 207-000-4","website":"https://energyarena.ru","amenities":["раздевалки","душ","тренеры","кафе","парковка"]},
    {"id":215,"emoji":"🎾","name":"Alexclub СПб","address":"Большевистская ул., 16","metro":"Проспект Большевиков","city":"spb","district":"Невский","lat":59.9173,"lon":30.4762,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (812) 408-07-78","website":"https://alexclub.ru","amenities":["раздевалки","душ","тренеры"]},
    {"id":216,"emoji":"🎾","name":"Tennis Club Шувалово","address":"Шувалово, ул. Фёдоровская, д. 102","metro":"Парнас","city":"spb","district":"Выборгский","lat":60.0688,"lon":30.3347,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"+7 (812) 516-87-07","website":"http://shuvaloffhotel.ru","amenities":["раздевалки","душ","гостиница рядом"]},
    {"id":217,"emoji":"🎾","name":"Калининский ТК (Руставели)","address":"ул. Руставели, 37","metro":"Гражданский проспект СПб","city":"spb","district":"Калининский","lat":60.0285,"lon":30.4190,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":218,"emoji":"🎾","name":"ТК Комета","address":"Главная ул., 24","metro":"Купчино","city":"spb","district":"Фрунзенский","lat":59.8108,"lon":30.3748,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":219,"emoji":"🎾","name":"World Class СПб (теннис)","address":"наб. Мартынова, 38","metro":"Крестовский остров","city":"spb","district":"Петроградский","lat":59.9713,"lon":30.2581,"type":"платно","price":"от 2 500 ₽/час","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"+7 (812) 640-00-14","website":"https://worldclass.ru","amenities":["раздевалки","душ","бассейн","фитнес","кафе","тренеры"]},
    {"id":220,"emoji":"🎾","name":"Теннисный центр Приморский","address":"ул. Зольная, 3а","metro":"Старая Деревня","city":"spb","district":"Приморский","lat":59.9920,"lon":30.2562,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":221,"emoji":"🎾","name":"СК Кировского района (теннис)","address":"пр. Народного Ополчения, 24","metro":"Ленинский проспект СПб","city":"spb","district":"Кировский","lat":59.8603,"lon":30.2267,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":222,"emoji":"🎾","name":"Airdance (теннис)","address":"ул. Оптиков, 32","metro":"Комендантский проспект","city":"spb","district":"Приморский","lat":60.0087,"lon":30.2450,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":223,"emoji":"🎾","name":"GymBalance (теннис)","address":"Алтайская ул., 4","metro":"Звёздная","city":"spb","district":"Московский","lat":59.8330,"lon":30.3482,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры","фитнес"]},
    {"id":224,"emoji":"🎾","name":"Теннисный центр Рыбацкое","address":"Придорожная ул., 18Б","metro":"Рыбацкое","city":"spb","district":"Невский","lat":59.8351,"lon":30.5013,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":225,"emoji":"🎾","name":"ТК Парк 300-летия СПб","address":"Парк 300-летия Санкт-Петербурга","metro":"Беговая СПб","city":"spb","district":"Приморский","lat":59.9929,"lon":30.2225,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":False,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ по записи","раздевалки"]},
    {"id":226,"emoji":"🎾","name":"Теннисный корт Мартынова","address":"наб. Мартынова, 40","metro":"Крестовский остров","city":"spb","district":"Петроградский","lat":59.9713,"lon":30.2620,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":False,"courts_count":2,"hours":"08:00–21:00","phone":"","website":"","amenities":["раздевалки"]},
    {"id":227,"emoji":"🎾","name":"ТК Тележная","address":"ул. Тележная, 17–19","metro":"Площадь Александра Невского","city":"spb","district":"Центральный","lat":59.9241,"lon":30.3846,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":228,"emoji":"🎾","name":"Шоссе Революции теннис","address":"ш. Революции, 116","metro":"Ладожская","city":"spb","district":"Красногвардейский","lat":59.9459,"lon":30.4394,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":229,"emoji":"🎾","name":"ТК Добровольцев","address":"ул. Добровольцев, 54Б","metro":"Проспект Ветеранов","city":"spb","district":"Красносельский","lat":59.8419,"lon":30.2013,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":230,"emoji":"🎾","name":"ТК Кузнецовская","address":"ул. Кузнецовская, 20, корп. 2","metro":"Электросила","city":"spb","district":"Московский","lat":59.8882,"lon":30.3257,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":231,"emoji":"🎾","name":"ТК Хасанская","address":"ул. Хасанская, 19","metro":"Улица Дыбенко","city":"spb","district":"Невский","lat":59.9064,"lon":30.4892,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":232,"emoji":"🌳","name":"Корты в Екатерингофском парке","address":"ул. Лифляндская, 12","metro":"Нарвская","city":"spb","district":"Кировский","lat":59.9088,"lon":30.2990,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"http://ekateringof.kb.gov.spb.ru","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":233,"emoji":"🌿","name":"Корты в Приморском парке Победы","address":"Крестовский остров, Приморский парк Победы","metro":"Крестовский остров","city":"spb","district":"Петроградский","lat":59.9795,"lon":30.2637,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":234,"emoji":"🏆","name":"СК им. Алексеева (Парк Победы)","address":"Московский пр., 188, СК им. В.И.Алексеева","metro":"Парк Победы СПб","city":"spb","district":"Московский","lat":59.8762,"lon":30.3301,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":235,"emoji":"🎾","name":"ТК Азбука Спорта СПб","address":"пер. Челиева, 13, корп. 5","metro":"Спортивная СПб","city":"spb","district":"Петроградский","lat":59.9519,"lon":30.2897,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры","детские программы"]},
    {"id":236,"emoji":"🎾","name":"Tennis Star (Луначарского)","address":"пр. Луначарского, 87Б, к. 4","metro":"Проспект Просвещения","city":"spb","district":"Выборгский","lat":60.0521,"lon":30.3400,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (904) 331-36-95","website":"","amenities":["раздевалки","тренеры"]},
    {"id":237,"emoji":"🎾","name":"Mr. Pushkin Tennis","address":"пос. Александровская, Волхонское шоссе, 79А","metro":"Автобус от Пушкинской","city":"spb","district":"Пушкинский","lat":59.7200,"lon":30.3800,"type":"платно","price":"уточняйте на сайте","surface":["грунт","хард"],"indoor":False,"courts_count":5,"hours":"08:00–21:00","phone":"","website":"","amenities":["раздевалки","парковка","тренеры"]},
    {"id":238,"emoji":"🎾","name":"ТК Звезда СПб","address":"ул. Звёздная, 5, корп. 2","metro":"Звёздная","city":"spb","district":"Московский","lat":59.8330,"lon":30.3520,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":239,"emoji":"🎾","name":"Екатерининский ТК","address":"Екатерининский пр., 3, корп. 2","metro":"Лесная СПб","city":"spb","district":"Калининский","lat":59.9774,"lon":30.3443,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":240,"emoji":"🎾","name":"ТК Московский пр. 73","address":"Московский пр., 73, корп. 3","metro":"Фрунзенская СПб","city":"spb","district":"Адмиралтейский","lat":59.9080,"lon":30.3169,"type":"платно","price":"уточняйте на сайте","surface":["хард","ковёр"],"indoor":True,"courts_count":2,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},

    # ── Ранее добавленные (оставляем) ──
    {"id":200,"emoji":"🏛","name":"Теннисный клуб Динамо СПб","address":"пр. Динамо, 44","metro":"Крестовский остров","city":"spb","district":"Петроградский","city":"moscow","lat":59.9713,"lon":30.2581,"type":"платно","price":"от 1 800 ₽/час","surface":["хард","грунт"],"indoor":True,"courts_count":8,"hours":"07:00–23:00","phone":"+7 (812) 235-47-80","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток","парковка"]},
    {"id":201,"emoji":"🌊","name":"Теннисный центр Приморский","address":"Приморский пр., 71","metro":"Старая Деревня","city":"spb","district":"Приморский","city":"moscow","lat":59.9923,"lon":30.2431,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (812) 430-11-22","website":"","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":202,"emoji":"🌿","name":"Корты в Парке Победы СПб","address":"Московский пр., 188 (Парк Победы)","metro":"Парк Победы","city":"spb","district":"Московский","city":"moscow","lat":59.8688,"lon":30.3228,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":203,"emoji":"🎾","name":"Теннисный клуб Нева СПб","address":"Арсенальная наб., 1","metro":"Площадь Ленина","city":"spb","district":"Калининский","city":"moscow","lat":59.9572,"lon":30.3563,"type":"платно","price":"от 2 000 ₽/час","surface":["хард","ковёр"],"indoor":True,"courts_count":5,"hours":"08:00–23:00","phone":"+7 (812) 542-33-44","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":204,"emoji":"🌳","name":"Корты в ЦПКиО им. Кирова","address":"Елагин остров, 4","metro":"Крестовский остров","city":"spb","district":"Петроградский","city":"moscow","lat":59.9795,"lon":30.2637,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":3,"hours":"10:00–20:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},


    # ══ АСТАНА — полная база ══════════════════════════════
    {"id":305,"emoji":"🏆","name":"НТЦ BEELINE ARENA","address":"пр. Туран, 57","metro":"","city":"astana","district":"Есиль","lat":51.1286,"lon":71.4306,"type":"платно","price":"уточняйте на сайте","surface":["хард","грунт"],"indoor":True,"courts_count":24,"hours":"07:00–23:00","phone":"+7 (7172) 99-96-60","website":"https://ktfastana.kz","amenities":["⚠️ Крупнейший центр страны — 24 корта","раздевалки","душ","тренеры","кафе","тренажёрный зал","парковка"]},
    {"id":306,"emoji":"🎾","name":"СК Даулет","address":"ул. Кордай, 6","metro":"","city":"astana","district":"Есиль","lat":51.1605,"lon":71.4491,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":13,"hours":"07:00–22:00","phone":"+7 (7172) 61-35-13","website":"","amenities":["8 крытых + 5 открытых кортов","раздевалки","душ","тренеры","трибуны на 250 мест"]},
    {"id":307,"emoji":"🎾","name":"Tennis Astana (ФОК)","address":"пр. Тауелсиздик, 1/1","metro":"","city":"astana","district":"Алматинский","lat":51.1720,"lon":71.4130,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–22:00","phone":"","website":"https://tennis-astana.kz","amenities":["⚠️ Пробный урок бесплатно","тренеры","прокат ракеток и мячей"]},
    {"id":308,"emoji":"🎾","name":"Underground Big Tennis","address":"ул. Жумекена Нажимеденова, 16","metro":"","city":"astana","district":"Алматинский","lat":51.1680,"lon":71.4560,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры","хорошее оборудование"]},
    {"id":309,"emoji":"🎾","name":"ТК на пр. Улы Дала","address":"пр. Улы Дала, 47/1","metro":"","city":"astana","district":"Есиль","lat":51.1480,"lon":71.3980,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"пн-пт 16:00–21:10, сб-вс 07:30–11:15","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":310,"emoji":"🎾","name":"ТК Сарыарка","address":"пр. Сарыарка, 31/2","metro":"","city":"astana","district":"Сарыарка","lat":51.1520,"lon":71.4720,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"09:30–21:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":311,"emoji":"🎾","name":"ТК Каныша Сатпаева","address":"ул. Каныша Сатпаева, 25","metro":"","city":"astana","district":"Алматинский","lat":51.1605,"lon":71.4200,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":312,"emoji":"🎾","name":"ТК Брусиловского","address":"ул. Евгения Брусиловского, 5","metro":"","city":"astana","district":"Алматинский","lat":51.1650,"lon":71.4350,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:30–21:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":313,"emoji":"🎾","name":"ТК Амангельды Иманова","address":"ул. Амангельды Иманова, 17","metro":"","city":"astana","district":"Алматинский","lat":51.1780,"lon":71.4460,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":314,"emoji":"🎾","name":"ТК Алихана Бокейхана","address":"ул. Алихана Бокейхана, 2","metro":"","city":"astana","district":"Есиль","lat":51.1350,"lon":71.4050,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":315,"emoji":"🎾","name":"ТК Кунаева","address":"ул. Динмухамеда Кунаева, 29/2","metro":"","city":"astana","district":"Есиль","lat":51.1290,"lon":71.4420,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":316,"emoji":"🎾","name":"ТК Туркестан (ЖК Коркем)","address":"ул. Туркестан, 10, ЖК Коркем 2","metro":"","city":"astana","district":"Есиль","lat":51.1180,"lon":71.4150,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренажёрный зал"]},
    {"id":317,"emoji":"🎾","name":"ТК Е-103","address":"ул. Е-103, 7/2","metro":"","city":"astana","district":"Есиль","lat":51.1220,"lon":71.4480,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"09:30–21:00","phone":"+7 (7172) 61-34-41","website":"","amenities":["раздевалки","тренеры"]},
    {"id":318,"emoji":"🎾","name":"ТК Косшыгулулы","address":"ул. Шаймердена Косшыгулулы, 24","metro":"","city":"astana","district":"Алматинский","lat":51.1700,"lon":71.4320,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":319,"emoji":"🎾","name":"Haileybury Astana (теннис)","address":"ул. Кабанбай Батыра, 1/1","metro":"","city":"astana","district":"Есиль","lat":51.1430,"lon":71.4280,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–21:00","phone":"","website":"","amenities":["⚠️ Частная школа — аренда доступна","раздевалки","тренеры"]},
    {"id":320,"emoji":"🌿","name":"Открытые корты в Центральном парке","address":"Центральный парк Астаны","metro":"","city":"astana","district":"Есиль","lat":51.1214,"lon":71.4128,"type":"платно","price":"уточняйте на месте","surface":["хард"],"indoor":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["⚠️ Уточняйте условия доступа на месте"]},
    {"id":321,"emoji":"🎾","name":"ТК Туран 30","address":"пр. Туран, 30","metro":"","city":"astana","district":"Есиль","lat":51.1320,"lon":71.4260,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры","парковка"]},
    {"id":322,"emoji":"🎾","name":"ТК Туран 4/2","address":"пр. Туран, 4/2, 2 этаж","metro":"","city":"astana","district":"Есиль","lat":51.1380,"lon":71.4190,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"07:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":323,"emoji":"🎾","name":"Tennis Astana (QSI)","address":"ул. Сауран, 20","metro":"","city":"astana","district":"Есиль","lat":51.1260,"lon":71.4380,"type":"платно","price":"уточняйте на сайте","surface":["универсальная"],"indoor":True,"courts_count":2,"hours":"08:00–21:00","phone":"","website":"https://tennis-astana.kz","amenities":["⚠️ Пробный урок бесплатно","тренеры","прокат инвентаря"]},
    # ── Старые записи (исправлены) ──
    {"id":300,"emoji":"🏆","name":"Теннисный центр Нур-Султан","address":"пр. Туран, 57 (Дворец спорта)","metro":"","city":"astana","district":"Есиль","lat":51.1286,"lon":71.4306,"type":"платно","price":"от 3 000 ₸/час","surface":["хард"],"indoor":True,"courts_count":10,"hours":"07:00–23:00","phone":"+7 (7172) 57-77-00","website":"","amenities":["раздевалки","душ","тренеры","кафе","парковка"]},
    {"id":301,"emoji":"🎾","name":"Теннисный клуб Астана (Достык)","address":"ул. Достык, 14","metro":"","city":"astana","district":"Алматинский","lat":51.1605,"lon":71.4491,"type":"платно","price":"от 2 500 ₸/час","surface":["хард","ковёр"],"indoor":True,"courts_count":6,"hours":"08:00–22:00","phone":"+7 (701) 555-11-22","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":302,"emoji":"🌿","name":"Корты в Президентском парке","address":"пр. Кабанбай батыра (Президентский парк)","metro":"","city":"astana","district":"Есиль","lat":51.1214,"lon":71.4128,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":303,"emoji":"🌊","name":"Теннисный центр Байтерек","address":"пр. Нурсултана Назарбаева, 45","metro":"","city":"astana","district":"Алматинский","lat":51.1280,"lon":71.4300,"type":"платно","price":"от 2 000 ₸/час","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–22:00","phone":"+7 (7172) 44-55-66","website":"","amenities":["раздевалки","тренеры","парковка"]},
    # ── Новые корты из 2ГИС ──
    {"id":324,"emoji":"🎾","name":"Толкын","address":"пр. Тауелсиздик, 2","metro":"","city":"astana","district":"Алматинский","lat":51.1720,"lon":71.4130,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":325,"emoji":"🎾","name":"Fitness Palace (теннис)","address":"пр. Туран, 30","metro":"","city":"astana","district":"Есиль","lat":51.1320,"lon":71.4260,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","фитнес","бассейн","тренеры"]},
    {"id":326,"emoji":"🎾","name":"Arsenal Tennis","address":"ул. Ыбырая Алтынсарина, 4","metro":"","city":"astana","district":"Алматинский","lat":51.1650,"lon":71.4280,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры","детские группы"]},
    {"id":327,"emoji":"🎾","name":"Dopshy Arena","address":"ул. Сыганак, 6/1","metro":"","city":"astana","district":"Есиль","lat":51.1200,"lon":71.4350,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":6,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":328,"emoji":"🎾","name":"Cool Space (теннис)","address":"пр. Рахимжана Кошкарбаева, 10","metro":"","city":"astana","district":"Алматинский","lat":51.1700,"lon":71.4500,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":329,"emoji":"🎾","name":"Underground Gym (теннис)","address":"ул. Жанибека Тархана, 17","metro":"","city":"astana","district":"Есиль","lat":51.1380,"lon":71.4050,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры","фитнес"]},
    {"id":330,"emoji":"🎾","name":"Karate Center (теннис)","address":"ул. Жумабека Ташенова, 7/2","metro":"","city":"astana","district":"Алматинский","lat":51.1620,"lon":71.4370,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":331,"emoji":"🎾","name":"Qazaq Batyry","address":"пр. Мангилик Ел, 17А","metro":"","city":"astana","district":"Есиль","lat":51.1150,"lon":71.4200,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":332,"emoji":"🎾","name":"TechnoGym (теннис)","address":"пр. Мангилик Ел, 51","metro":"","city":"astana","district":"Есиль","lat":51.1090,"lon":71.4150,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренажёрный зал","тренеры"]},
    {"id":333,"emoji":"🎾","name":"Bali SPA (теннис)","address":"ул. Динмухамеда Кунаева, 29/2","metro":"","city":"astana","district":"Есиль","lat":51.1290,"lon":71.4420,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","spa","бассейн","тренеры"]},
    {"id":334,"emoji":"🎾","name":"Sport Time","address":"ул. Каныша Сатпаева, 25","metro":"","city":"astana","district":"Алматинский","lat":51.1650,"lon":71.4200,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":335,"emoji":"🎾","name":"Underground Gym 2 (Сатпаева)","address":"ул. Каныша Сатпаева, 22","metro":"","city":"astana","district":"Алматинский","lat":51.1645,"lon":71.4205,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры","фитнес"]},
    {"id":336,"emoji":"🌿","name":"Корты в мкр. Юго-Восток","address":"мкр. Юго-Восток, Астана","metro":"","city":"astana","district":"Сарыарка","lat":51.1450,"lon":71.5100,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"courts_count":2,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":337,"emoji":"🎾","name":"Темирказык","address":"ул. Темирказык, 63, мкр. Шубар","metro":"","city":"astana","district":"Алматинский","lat":51.1800,"lon":71.4800,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
]


# ══════════════════════════════════════════════
# БАЗА МЕТРО
# ══════════════════════════════════════════════

METRO_COORDS = {
    "бульвар рокоссовского":(55.8103,37.7388),"черкизовская":(55.8007,37.7322),"преображенская площадь":(55.7957,37.7065),"сокольники":(55.7893,37.6793),"красносельская":(55.7800,37.6719),"комсомольская":(55.7762,37.6558),"красные ворота":(55.7688,37.6468),"чистые пруды":(55.7638,37.6382),"лубянка":(55.7593,37.6276),"охотный ряд":(55.7566,37.6143),"библиотека имени ленина":(55.7519,37.6094),"кропоткинская":(55.7448,37.5935),"парк культуры":(55.7359,37.5934),"фрунзенская":(55.7275,37.5838),"спортивная":(55.7175,37.5554),"воробьёвы горы":(55.7099,37.5532),"университет":(55.6999,37.5350),"проспект вернадского":(55.6747,37.5002),"юго-западная":(55.6633,37.4826),"тропарёво":(55.6438,37.4478),"румянцево":(55.6246,37.4278),"саларьево":(55.6124,37.4154),"филатов луг":(55.5975,37.3906),"прокшино":(55.5856,37.3632),"ольховая":(55.5708,37.3386),"коммунарка":(55.5558,37.3164),
    "речной вокзал":(55.8402,37.4767),"водный стадион":(55.8298,37.4853),"войковская":(55.8189,37.4977),"сокол":(55.8124,37.5189),"аэропорт":(55.8005,37.5478),"динамо":(55.7900,37.5579),"белорусская":(55.7762,37.5817),"маяковская":(55.7687,37.5958),"театральная":(55.7594,37.6174),"новокузнецкая":(55.7437,37.6287),"павелецкая":(55.7300,37.6487),"автозаводская":(55.7075,37.6558),"технопарк":(55.6960,37.6616),"коломенская":(55.6841,37.6651),"каширская":(55.6672,37.6575),"кантемировская":(55.6510,37.6619),"царицыно":(55.6246,37.6622),"орехово":(55.6441,37.6649),"домодедовская":(55.6076,37.6662),"красногвардейская":(55.5963,37.6637),"алма-атинская":(55.5842,37.6664),
    "пятницкое шоссе":(55.8680,37.2962),"митино":(55.8437,37.3527),"волоколамская":(55.8340,37.3677),"мякинино":(55.8164,37.3811),"строгино":(55.7907,37.3888),"крылатское":(55.7525,37.4042),"молодёжная":(55.7328,37.4079),"кунцевская":(55.7306,37.4358),"парк победы":(55.7299,37.4965),"киевская":(55.7432,37.5660),"смоленская":(55.7474,37.5821),"арбатская":(55.7519,37.6055),"площадь революции":(55.7555,37.6183),"курская":(55.7576,37.6609),"бауманская":(55.7722,37.6787),"электрозаводская":(55.7793,37.6892),"семёновская":(55.7787,37.7115),"партизанская":(55.7742,37.7672),"первомайская":(55.7788,37.8015),"измайловская":(55.7892,37.7495),"измайловский парк":(55.7950,37.7820),"щёлковская":(55.8006,37.8152),
    "краснопресненская":(55.7583,37.5656),"новослободская":(55.7730,37.6059),"проспект мира":(55.7806,37.6335),"рижская":(55.7939,37.6360),"алексеевская":(55.8044,37.6388),"ботанический сад":(55.8290,37.6648),"свиблово":(55.8434,37.6714),"бабушкинская":(55.8573,37.6612),"медведково":(55.8729,37.6498),"добрынинская":(55.7270,37.6280),"октябрьская":(55.7287,37.6079),
    "планерная":(55.8576,37.3944),"сходненская":(55.8421,37.4148),"северное тушино":(55.8480,37.4120),"музей вмф":(55.8490,37.4100),"парк северное тушино":(55.8480,37.4120),"тушинская":(55.8275,37.4266),"спартак":(55.8192,37.4465),"щукинская":(55.8074,37.4648),"октябрьское поле":(55.8003,37.4914),"полежаевская":(55.7915,37.5140),"беговая":(55.7820,37.5521),"улица 1905 года":(55.7670,37.5554),"баррикадная":(55.7614,37.5724),"пушкинская":(55.7649,37.6048),"кузнецкий мост":(55.7591,37.6264),"китай-город":(55.7513,37.6338),"таганская":(55.7381,37.6509),"пролетарская":(55.7265,37.6669),"волгоградский проспект":(55.7183,37.6785),"текстильщики":(55.7088,37.7257),"кузьминки":(55.7088,37.7756),"рязанский проспект":(55.7220,37.8086),"выхино":(55.7254,37.8424),"лермонтовский проспект":(55.7357,37.8812),"жулебино":(55.7241,37.9050),"котельники":(55.6700,37.8643),
    "алтуфьево":(55.8965,37.5878),"бибирево":(55.8802,37.5998),"отрадное":(55.8647,37.6073),"владыкино":(55.8467,37.5882),"петровско-разумовская":(55.8337,37.5621),"тимирязевская":(55.8207,37.5621),"дмитровская":(55.8094,37.5629),"савёловская":(55.7960,37.5836),"менделеевская":(55.7803,37.5987),"цветной бульвар":(55.7711,37.6154),"чеховская":(55.7657,37.6083),"боровицкая":(55.7518,37.6065),"полянка":(55.7346,37.6211),"серпуховская":(55.7258,37.6246),"тульская":(55.7148,37.6247),"нагатинская":(55.6939,37.6266),"нагорная":(55.6784,37.6140),"нахимовский проспект":(55.6627,37.6082),"севастопольская":(55.6516,37.6054),"чертановская":(55.6384,37.6060),"южная":(55.6245,37.6070),"пражская":(55.6125,37.6080),"улица академика янгеля":(55.6010,37.6117),"аннино":(55.5878,37.6070),"бульвар дмитрия донского":(55.5754,37.6013),
    "зябликово":(55.6140,37.7342),"шипиловская":(55.6232,37.7414),"борисово":(55.6378,37.7359),"марьино":(55.6558,37.7458),"братиславская":(55.6685,37.7600),"люблино":(55.6763,37.7658),"печатники":(55.7015,37.7192),"дубровка":(55.7174,37.6955),"кожуховская":(55.7269,37.6872),"римская":(55.7457,37.6813),"площадь ильича":(55.7457,37.6813),"авиамоторная":(55.7497,37.7151),"шоссе энтузиастов":(55.7552,37.7509),"перово":(55.7505,37.7828),"новогиреево":(55.7545,37.8219),"новокосино":(55.7433,37.8648),"некрасовка":(55.7009,37.8472),
    "рассказовка":(55.6566,37.3148),"новопеределкино":(55.6666,37.3459),"боровское шоссе":(55.6745,37.3704),"солнцево":(55.6726,37.3968),"говорово":(55.6737,37.4296),"мичуринский проспект":(55.6838,37.4521),"раменки":(55.6988,37.4680),"аминьевская":(55.7199,37.4531),"давыдково":(55.7268,37.4812),"деловой центр":(55.7494,37.5395),"шелепиха":(55.7581,37.5256),"хорошёвская":(55.7823,37.5073),"цска":(55.7915,37.5140),"петровский парк":(55.7997,37.5677),"лихоборы":(55.8370,37.5530),"окружная":(55.8458,37.5768),"верхние лихоборы":(55.8680,37.5637),"селигерская":(55.8814,37.5740),
    "лефортово":(55.7574,37.6974),"косино":(55.7291,37.8892),"фили":(55.7432,37.5660),"кутузовская":(55.7366,37.5332),"лужники":(55.7165,37.5567),"зорге":(55.7948,37.4857),"панфиловская":(55.8080,37.4706),"народное ополчение":(55.7952,37.4465),"хорошёво":(55.7864,37.4668),"достоевская":(55.7780,37.6100),"марьина роща":(55.7912,37.6270),"ростокино":(55.8260,37.6680),"лианозово":(55.8934,37.5721),"вднх":(55.8222,37.6406),"третьяковская":(55.7408,37.6283),"чкаловская":(55.7674,37.6516),"шаболовская":(55.7209,37.6073),"зюзино":(55.6525,37.5836),"академическая":(55.6728,37.5778),"профсоюзная":(55.6617,37.5626),"новые черёмушки":(55.6504,37.5576),"калужская":(55.6385,37.5509),"беляево":(55.6454,37.5245),"лесопарковая":(55.5992,37.6087),"битцевский парк":(55.5992,37.6087),"ясенево":(55.6168,37.5401),"новоясеневская":(55.6097,37.5613),"филёвский парк":(55.7469,37.5108),"коньково":(55.6296,37.5244),"тёплый стан":(55.6167,37.5013),"бунинская аллея":(55.5500,37.5200),"лосиноостровская":(55.8650,37.7100),
    # ══ НОВЫЕ СТАНЦИИ МОСКВЫ 2023–2025 ══════════════════
    # Троицкая линия (открыта 2024–2025)
    "новаторская":(55.6798,37.5412),"тютчевская":(55.6651,37.5219),"университет дружбы народов":(55.6521,37.5089),"генерала тюленева":(55.6389,37.4921),"корниловская":(55.6201,37.4712),"новомосковская":(55.6050,37.4530),"вавиловская":(55.6910,37.5603),"крымская":(55.7050,37.5700),"зил":(55.7120,37.5850),
    # БКЛ недостающие станции
    "мнёвники":(55.7723,37.4402),"карамышевская":(55.7822,37.4288),"терехово":(55.7895,37.4190),"кленовый бульвар":(55.6320,37.6210),"нагатинский затон":(55.6720,37.6420),"рублёвский проспект":(55.7580,37.4050),"дмитровское шоссе":(55.8200,37.5700),
    # Светло-зелёная линия
    "яхромская":(55.9050,37.5910),"физтех":(55.8850,37.5790),"лианозово бкл":(55.8934,37.5721),
    # Жёлтая линия
    "пыхтино":(55.6050,37.3480),"аэропорт внуково":(55.5910,37.3250),
    # МЦД / прочие
    "поклонная":(55.7350,37.4920),"матвеевская":(55.7240,37.4650),
    # ══ САНКТ-ПЕТЕРБУРГ — все линии ══════════════════════
    # Линия 1 (Кировско-Выборгская)
    "девяткино":(60.0498,30.4430),"гражданский проспект спб":(60.0285,30.4190),"академическая спб":(60.0126,30.3985),"политехническая":(59.9995,30.3703),"площадь мужества":(59.9883,30.3638),"лесная спб":(59.9774,30.3443),"выборгская":(59.9683,30.3436),"площадь ленина спб":(59.9573,30.3563),"чернышевская":(59.9456,30.3597),"площадь восстания":(59.9313,30.3607),"владимирская":(59.9266,30.3484),"пушкинская спб":(59.9264,30.3319),"технологический институт":(59.9174,30.3183),"балтийская":(59.9088,30.2990),"нарвская":(59.8989,30.2733),"кировский завод":(59.8902,30.2576),"автово":(59.8755,30.2441),"ленинский проспект спб":(59.8603,30.2267),"проспект ветеранов":(59.8419,30.2013),
    # Линия 2 (Московско-Петроградская)
    "парнас":(60.0688,30.3347),"проспект просвещения":(60.0521,30.3318),"озерки":(60.0343,30.3255),"удельная":(60.0187,30.3168),"пионерская спб":(60.0047,30.2956),"чёрная речка":(59.9914,30.2952),"петроградская":(59.9661,30.3156),"горьковская":(59.9561,30.3179),"невский проспект":(59.9355,30.3241),"сенная площадь":(59.9267,30.3200),"фрунзенская спб":(59.9080,30.3169),"московские ворота":(59.8986,30.3192),"электросила":(59.8882,30.3257),"парк победы спб":(59.8762,30.3301),"московская":(59.8593,30.3246),"звёздная":(59.8330,30.3482),"купчино":(59.8108,30.3748),
    # Линия 3 (Невско-Василеостровская)
    "беговая спб":(59.9929,30.2225),"новокрестовская":(59.9722,30.2232),"приморская":(59.9531,30.2298),"василеостровская":(59.9432,30.2732),"гостиный двор":(59.9337,30.3322),"маяковская спб":(59.9311,30.3546),"площадь александра невского":(59.9241,30.3846),"елизаровская":(59.9095,30.4136),"ломоносовская":(59.8979,30.4375),"пролетарская спб":(59.8889,30.4662),"обухово":(59.8754,30.4627),"рыбацкое":(59.8351,30.5013),
    # Линия 4 (Правобережная)
    "спасская":(59.9258,30.3183),"достоевская спб":(59.9256,30.3481),"лиговский проспект":(59.9198,30.3559),"новочеркасская":(59.9346,30.4118),"ладожская":(59.9459,30.4394),"проспект большевиков":(59.9173,30.4762),"улица дыбенко":(59.9064,30.4892),"народная":(59.8789,30.4538),"международная":(59.8633,30.3986),"бухарестская":(59.8523,30.3722),"проспект славы":(59.8444,30.3872),"дунайская":(59.8290,30.3925),
    # Линия 5 (Фрунзенско-Приморская)
    "комендантский проспект":(60.0087,30.2577),"старая деревня":(59.9920,30.2562),"крестовский остров":(59.9713,30.2581),"чкаловская спб":(59.9606,30.2959),"спортивная спб":(59.9519,30.2897),"адмиралтейская":(59.9338,30.3149),"садовая":(59.9266,30.3196),"звенигородская":(59.9165,30.3374),"обводный канал":(59.9119,30.3501),"волковская":(59.8943,30.3641),"шушары":(59.8192,30.3870),
}


# ══════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ══════════════════════════════════════════════

def haversine(lat1,lon1,lat2,lon2):
    R=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
    a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R*2*math.asin(math.sqrt(a))

def find_metro(q):
    q=q.lower().strip()
    if q in METRO_COORDS: return METRO_COORDS[q]
    for name,coords in METRO_COORDS.items():
        if q in name or name in q: return coords
    return None


# ══════════════════════════════════════════════
# БАЗА ТЕННИСНЫХ СТЕНОК — 13 официальных локаций
# Источник: courtforsale.ru/blog/besplatnye-tennis-stenki
# ══════════════════════════════════════════════

WALL_COURTS = [
    # ── МОСКВА ───────────────────────────────────────────
    {"id":9001,"emoji":"🧱","name":"Стенка у МГУ (Ленинские горы)","address":"Территория Ленинские Горы, 1с37","metro":"Воробьёвы горы","city":"moscow","district":"ЗАО","lat":55.7099,"lon":37.5532,"type":"бесплатно","price":"Бесплатно","surface":["бетон"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","широкая бетонная стена — несколько игроков одновременно","жёсткий отскок — тренирует реакцию"]},
    {"id":9002,"emoji":"🧱","name":"Стенка в парке Радуга (Вешняки)","address":"Аллея Жемчуговой, 5к3","metro":"Выхино / Новогиреево","city":"moscow","district":"ВАО","lat":55.8090,"lon":37.7350,"type":"бесплатно","price":"Бесплатно","surface":["резиновое покрытие"],"indoor":False,"courts_count":1,"hours":"10:00–22:00","phone":"","website":"","amenities":["✅ Свободный доступ","современное ровное покрытие","высокая стенка с нарисованной линией сетки"]},
    {"id":9003,"emoji":"🧱","name":"Стенка в Братеевском парке","address":"ул. Борисовские пруды, 29","metro":"Зябликово","city":"moscow","district":"ЮАО","lat":55.6232,"lon":37.7414,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","стенка встроена в ограждение корта","подходит для жителей ЮАО"]},
    {"id":9004,"emoji":"🧱","name":"Стенка в лесопарке Кусково","address":"Аллея Первой Маёвки, 3Ас1","metro":"Рязанский проспект / Выхино","city":"moscow","district":"ВАО","lat":55.7350,"lon":37.8100,"type":"бесплатно","price":"Бесплатно","surface":["резиновое покрытие"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","светло-жёлтая ровная стенка","мягкое резиновое покрытие"]},
    {"id":9005,"emoji":"🧱","name":"Стенка в Новогиреево","address":"Ул. Молостовых, 16к2","metro":"Новогиреево","city":"moscow","district":"ВАО","lat":55.7545,"lon":37.8219,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","деревянная стенка","площадка обнесена сеткой-рабицей — мячи не улетают"]},
    {"id":9006,"emoji":"🧱","name":"Стенка в парке Свиблово","address":"Тенистый проезд, 6/8","metro":"Свиблово","city":"moscow","district":"СВАО","lat":55.8434,"lon":37.6714,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","тёмная надёжная стенка в парковой зоне долины Яузы","живописное место"]},
    {"id":9007,"emoji":"🧱","name":"Стенка на Народного Ополчения","address":"Ул. Маршала Тухачевского, 17к3","metro":"Народное Ополчение","city":"moscow","district":"СЗАО","lat":55.7952,"lon":37.4465,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","металлическая/деревянная стенка в огороженной спортивной коробке"]},
    {"id":9008,"emoji":"🧱","name":"Стенка в Терлецком парке","address":"Ул. Металлургов, 41с1","metro":"Шоссе Энтузиастов","city":"moscow","district":"ВАО","lat":55.7552,"lon":37.7509,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","длинная комбинированная стенка среди деревьев","летом тренировка в тени"]},
    {"id":9009,"emoji":"🧱","name":"Стенка в ДДС на Римской","address":"Рабочая ул., 53с1","metro":"Римская / Площадь Ильича","city":"moscow","district":"ЦАО","lat":55.7457,"lon":37.6813,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","кирпичная стена выкрашена в зелёный цвет","жёсткий быстрый отскок — тренировка реакции"]},
    {"id":9010,"emoji":"🧱","name":"Стенка в Чертаново","address":"Днепропетровская ул., 16к2","metro":"Чертановская","city":"moscow","district":"ЮАО","lat":55.6384,"lon":37.6060,"type":"бесплатно","price":"Бесплатно","surface":["терракотовое покрытие"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","нанесена разметка с линией сетки и мишенями-квадратами","тренировка точности ударов"]},
    {"id":9011,"emoji":"🧱","name":"Стенка в Строгино","address":"Неманский проезд, 1к3","metro":"Строгино","city":"moscow","district":"СЗАО","lat":55.7907,"lon":37.3888,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","широкая синяя деревянная стенка с разметкой уровня сетки"]},
    {"id":9012,"emoji":"🧱","name":"Стенка в СК МГИМО","address":"Пр-т Вернадского, 76Е","metro":"Юго-Западная","city":"moscow","district":"ЮЗАО","lat":55.6633,"lon":37.4826,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","широкая длинная монолитная стена","несколько игроков одновременно"]},
    {"id":9013,"emoji":"🧱","name":"Стенка в Лефортовском парке","address":"Красноказарменная ул., 1с9","metro":"Авиамоторная / Лефортово","city":"moscow","district":"ВАО","lat":55.7574,"lon":37.6974,"type":"бесплатно","price":"Бесплатно","surface":["асфальт"],"indoor":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","⭐ Стенка с мишенями-целями на разной высоте — тренировка точности","историческая атмосфера Лефортово"]},
]

def filter_courts(pay_type,surface,indoor,lat,lon,city="moscow",mode="court"):
    source = WALL_COURTS if mode=="wall" else COURTS
    res=[]
    for c in source:
        if c.get("city","moscow")!=city: continue
        if mode=="court":
            if pay_type!="all" and c["type"]!=pay_type: continue
            if surface!="all" and surface not in c["surface"]: continue
            if indoor=="indoor" and not c["indoor"]: continue
            if indoor=="outdoor" and c["indoor"]: continue
        d=dict(c); d["distance_km"]=haversine(lat,lon,d["lat"],d["lon"]); res.append(d)
    return sorted(res,key=lambda x:x["distance_km"])[:MAX_COURTS] if city in ("moscow","spb") else sorted(res,key=lambda x:x["distance_km"])

def format_card(c):
    roof="🏠 Крытый" if c["indoor"] else "☀️ Открытый"
    surf=" · ".join(c["surface"]); amen=" · ".join(c["amenities"])
    dist=f"\n📏 {c['distance_km']:.1f} км от тебя" if "distance_km" in c else ""
    txt=(f"{c['emoji']} *{c['name']}*\n\n📍 {c['address']}\n🚇 {c['metro']}{dist}\n\n"
         f"{roof}\n🎾 Покрытие: {surf}\n🏟 Кортов: {c['courts_count']} шт.\n\n"
         f"💰 {c['price']}\n⏰ {c['hours']}\n\n✅ {amen}\n")
    if c.get("phone"): txt+=f"📞 {c['phone']}\n"
    return txt

def card_kb(c):
    # Маршрут по точным координатам — открывает точку на карте
    addr_enc = c['address'].replace(' ', '+').replace(',', '%2C')
    maps_url = f"https://yandex.ru/maps/?pt={c['lon']},{c['lat']}&z=16&l=map"
    r1 = [InlineKeyboardButton("🗺 Маршрут", url=maps_url)]
    if c.get("website"):
        r1.append(InlineKeyboardButton("🌐 Сайт", url=c["website"]))
    r2 = [InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_to_results")]
    return InlineKeyboardMarkup([r1, r2])

def list_kb(courts,page):
    end=PAGE_SIZE*(page+1); visible=courts[:end]; btns=[]
    for c in visible:
        roof="🏠" if c["indoor"] else "☀️"
        dist=f"{c['distance_km']:.1f} км · " if "distance_km" in c else ""
        btns.append([InlineKeyboardButton(f"{c['emoji']} {c['name']} · {dist}{roof}",callback_data=f"court_{c['id']}")])
    if end<len(courts):
        btns.append([InlineKeyboardButton(f"➕ Ещё {min(PAGE_SIZE,len(courts)-end)} корта",callback_data=f"page_{page+1}")])
    btns.append([InlineKeyboardButton("🔄 Начать заново",callback_data="restart")])
    return InlineKeyboardMarkup(btns)

def mode_kb():
    """Первый экран — стенка или корт."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧱 Стенка",  callback_data="mode_wall")],
        [InlineKeyboardButton("🎾 Корт",    callback_data="mode_court")],
    ])

def city_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏙 Москва",           callback_data="city_moscow"),
         InlineKeyboardButton("🌊 Санкт-Петербург",  callback_data="city_spb")],
        [InlineKeyboardButton("🌟 Астана",            callback_data="city_astana")],
        [InlineKeyboardButton("⬅️ Назад",             callback_data="change_mode")],
    ])

def type_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆓 Бесплатный", callback_data="type_бесплатно"),
         InlineKeyboardButton("💳 Платный",    callback_data="type_платно")],
        [InlineKeyboardButton("🎾 Любой",      callback_data="type_all")],
        [InlineKeyboardButton("⬅️ Сменить город", callback_data="change_city")],
    ])

CITY_NAMES = {
    "moscow": "🏙 Москва",
    "spb":    "🌊 Санкт-Петербург",
    "astana": "🌟 Астана",
}

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎾 *Теннис на районе*\n\n"
        "Что тебе нужно? 👇",
        parse_mode="Markdown", reply_markup=mode_kb())

async def handle_cb(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); d=q.data

    # ── Шаг 0: стенка или корт ──
    if d.startswith("mode_"):
        mode=d.replace("mode_","")
        context.user_data["mode"]=mode
        label="🧱 Стенка" if mode=="wall" else "🎾 Корт"
        await q.edit_message_text(
            f"✅ {label}\n\nВыбери город 👇",
            parse_mode="Markdown", reply_markup=city_kb())

    elif d=="change_mode":
        context.user_data.clear()
        await q.edit_message_text(
            "🎾 *Теннис на районе*\n\nЧто тебе нужно? 👇",
            parse_mode="Markdown", reply_markup=mode_kb())

    # ── Шаг 1: выбор города ──
    elif d.startswith("city_"):
        city=d.replace("city_","")
        context.user_data["city"]=city
        city_name=CITY_NAMES.get(city,"")
        mode=context.user_data.get("mode","court")
        if mode=="wall":
            context.user_data["type"]="all"
            context.user_data["indoor"]="all"
            context.user_data["surface"]="all"
            if city=="astana":
                await q.edit_message_text(
                    f"✅ {city_name} · 🧱 Стенки\n\n"
                    "📍 *Отправь геолокацию*\n\nНажми скрепку 📎 → *Геопозиция*",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад",callback_data="change_city")]]))
            else:
                kb=[[InlineKeyboardButton("📍 Моя геолокация",callback_data="search_geo")],
                    [InlineKeyboardButton("🚇 Станция метро",  callback_data="search_metro")],
                    [InlineKeyboardButton("⬅️ Назад",          callback_data="change_city")]]
                await q.edit_message_text(
                    f"✅ {city_name} · 🧱 Стенки\n\nКак искать?",
                    reply_markup=InlineKeyboardMarkup(kb))
        else:
            await q.edit_message_text(
                f"✅ {city_name}\n\nВыбери тип корта:",
                parse_mode="Markdown", reply_markup=type_kb())

    elif d=="change_city":
        context.user_data.pop("city", None)
        mode=context.user_data.get("mode","court")
        label="🧱 Стенка" if mode=="wall" else "🎾 Корт"
        await q.edit_message_text(
            f"✅ {label}\n\nВыбери город 👇",
            parse_mode="Markdown", reply_markup=city_kb())

    elif d.startswith("type_"):
        pt=d.replace("type_",""); context.user_data["type"]=pt
        lm={"бесплатно":"Бесплатный ✅","платно":"Платный ✅","all":"Любой ✅"}
        if pt=="бесплатно":
            context.user_data["indoor"]="all"
            kb=[[InlineKeyboardButton("🔵 Хард",callback_data="surface_хард"),
                 InlineKeyboardButton("🟤 Грунт",callback_data="surface_грунт")],
                [InlineKeyboardButton("🟢 Искусственная трава",callback_data="surface_искусственная трава")],
                [InlineKeyboardButton("✨ Без разницы",callback_data="surface_all")]]
            await q.edit_message_text(f"{lm[pt]}\n\nКакое покрытие предпочитаешь?",
                parse_mode="Markdown",reply_markup=InlineKeyboardMarkup(kb))
        else:
            kb=[[InlineKeyboardButton("🏠 Крытый",callback_data="indoor_indoor"),
                 InlineKeyboardButton("☀️ Открытый",callback_data="indoor_outdoor")],
                [InlineKeyboardButton("✨ Без разницы",callback_data="indoor_all")]]
            await q.edit_message_text(f"{lm.get(pt)}\n\nКрытый или открытый?",
                parse_mode="Markdown",reply_markup=InlineKeyboardMarkup(kb))

    elif d.startswith("indoor_"):
        context.user_data["indoor"]=d.replace("indoor_","")
        il={"indoor":"Крытый 🏠","outdoor":"Открытый ☀️","all":"Без разницы ✨"}
        kb=[[InlineKeyboardButton("🔵 Хард",callback_data="surface_хард"),
             InlineKeyboardButton("🟤 Грунт",callback_data="surface_грунт")],
            [InlineKeyboardButton("🟢 Искусственная трава",callback_data="surface_искусственная трава")],
            [InlineKeyboardButton("✨ Без разницы",callback_data="surface_all")]]
        await q.edit_message_text(f"{il.get(d.replace('indoor_',''))}\n\nКакое покрытие?",
            parse_mode="Markdown",reply_markup=InlineKeyboardMarkup(kb))

    elif d.startswith("surface_"):
        context.user_data["surface"]=d.replace("surface_","")
        city=context.user_data.get("city","moscow")
        # В Астане нет метро — сразу только геолокация
        if city=="astana":
            await q.edit_message_text(
                "📍 *Отправь геолокацию*\n\nНажми на скрепку 📎 → *Геопозиция*\n\n_Покажу корты от ближайшего к дальнему_",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад",callback_data="restart")]]))
        else:
            kb=[[InlineKeyboardButton("📍 Моя геолокация",callback_data="search_geo")],
                [InlineKeyboardButton("🚇 Станция метро",callback_data="search_metro")]]
            await q.edit_message_text("Как искать корты?",reply_markup=InlineKeyboardMarkup(kb))

    elif d=="search_geo":
        await q.edit_message_text(
            "📍 *Отправь геолокацию*\n\nНажми на скрепку 📎 → *Геопозиция*\n\n_Покажу корты от ближайшего к дальнему_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад",callback_data="restart")]]))

    elif d=="search_metro":
        context.user_data["waiting_metro"]=True
        city=context.user_data.get("city","moscow")
        if city=="spb":
            example="_Невский проспект_, _Московская_, _Петроградская_"
        else:
            example="_Динамо_, _Сокольники_, _Тушинская_"
        await q.edit_message_text(
            f"🚇 *Введи название станции метро*\n\nНапиши в чат, например:\n{example}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад",callback_data="restart")]]))

    elif d.startswith("page_"):
        page=int(d.replace("page_",""))
        courts=context.user_data.get("results",[])
        pt=context.user_data.get("type","all")
        lm={"бесплатно":"Бесплатные","платно":"Платные","all":"Все"}
        shown=min(PAGE_SIZE*(page+1),len(courts))
        await q.edit_message_text(
            f"🎾 *{lm.get(pt)} корты — {len(courts)} шт.*\n\nПоказано: {shown} из {len(courts)} 👇",
            parse_mode="Markdown",reply_markup=list_kb(courts,page))

    elif d.startswith("court_"):
        cid=int(d.replace("court_",""))
        results=context.user_data.get("results",[])
        court=next((c for c in results if c["id"]==cid),None) or next((c for c in COURTS if c["id"]==cid),None)
        if court: await q.edit_message_text(format_card(court),parse_mode="Markdown",reply_markup=card_kb(court))

    elif d=="back_to_results":
        courts=context.user_data.get("results",[])
        pt=context.user_data.get("type","all")
        lm={"бесплатно":"Бесплатные","платно":"Платные","all":"Все"}
        if courts:
            await q.edit_message_text(
                f"🎾 *{lm.get(pt)} корты — {len(courts)} шт.*\n\nПоказано: {min(PAGE_SIZE,len(courts))} из {len(courts)} 👇",
                parse_mode="Markdown",reply_markup=list_kb(courts,0))
        else: await start_over(q)

    elif d=="restart":
        context.user_data.clear(); await start_over(q)

async def handle_location(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await process(update,context,update.message.location.latitude,update.message.location.longitude,"geo")

async def handle_text(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_metro"): return
    city=context.user_data.get("city","moscow")
    if city=="astana":
        await update.message.reply_text(
            "🌟 В Астане нет метро!\n\nПожалуйста, отправь геолокацию:\nНажми на скрепку 📎 → *Геопозиция*",
            parse_mode="Markdown")
        return
    inp=update.message.text.strip(); coords=find_metro(inp)
    if not coords:
        example="_Динамо_, _Сокольники_" if city=="moscow" else "_Невский проспект_, _Московская_"
        await update.message.reply_text(f"😔 Станция *{inp}* не найдена.\n\nПопробуй иначе, например: {example}",parse_mode="Markdown"); return
    context.user_data["waiting_metro"]=False
    await process(update,context,coords[0],coords[1],"metro",inp)

async def process(update,context,lat,lon,source,metro_name=""):
    pt=context.user_data.get("type","all")
    surf=context.user_data.get("surface","all")
    ind=context.user_data.get("indoor","all")
    city=context.user_data.get("city","moscow")
    mode=context.user_data.get("mode","court")
    if not city: await update.message.reply_text("Сначала выбери параметры — нажми /start 🎾"); return
    courts=filter_courts(pt,surf,ind,lat,lon,city,mode); context.user_data["results"]=courts
    if not courts: await update.message.reply_text("😔 Ничего не найдено рядом. Попробуй /start и измени параметры.\n\nНашли корт, которого нет в боте? Пишите: @in_kanareyk 🎾"); return
    city_name=CITY_NAMES.get(city,"")
    header=f"🚇 Рядом со станцией *{metro_name.title()}*" if source=="metro" else f"📍 Рядом с тобой · {city_name}"
    if mode=="wall":
        label="🧱 Стенки"
    else:
        lm={"бесплатно":"Бесплатные","платно":"Платные","all":"Все"}; label=f"🎾 {lm.get(pt,'Найденные')} корты"
    await update.message.reply_text(
        f"*{label} — {len(courts)} шт.*\n{header}\n\nПоказано: {min(PAGE_SIZE,len(courts))} из {len(courts)} 👇",
        parse_mode="Markdown",reply_markup=list_kb(courts,0))

async def start_over(query):
    await query.edit_message_text(
        "🎾 *Теннис на районе*\n\nЧто тебе нужно? 👇",
        parse_mode="Markdown", reply_markup=mode_kb())

async def help_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("⚠️ Написать об ошибке",url=ADMIN_TG)]])
    await update.message.reply_text(
        "🎾 *Теннис на районе*\n\n"
        "/start — найти корт\n"
        "/help — справка\n"
        "/newcort — предложить новый корт\n\n"
        "1️⃣ Выбери город\n"
        "2️⃣ Тип корта (платный / бесплатный)\n"
        "3️⃣ Крытый или открытый _(только для платных)_\n"
        "4️⃣ Покрытие\n"
        "5️⃣ Геолокация 📍 или метро 🚇\n"
        "6️⃣ Список от ближайшего!\n\n"
        "⬇️ *Доложить об ошибке бота или недостоверной информации о кортах:*",
        parse_mode="Markdown", reply_markup=kb)

async def newcort_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("➕ Написать про корт",url=ADMIN_TG)]])
    await update.message.reply_text(
        "🎾 *Нет какого-то корта? Пишите нам!*\n\n"
        "Мы добавим его в базу как можно скорее 🙏\n\n"
        "Укажите пожалуйста:\n"
        "• Название корта\n"
        "• Город\n"
        "• Адрес\n"
        "• Платный или бесплатный\n"
        "• Покрытие (хард / грунт / трава)\n"
        "• Крытый или открытый\n\n"
        "⬇️ *Нажмите кнопку ниже:*",
        parse_mode="Markdown", reply_markup=kb)


# ══════════════════════════════════════════════
# ЗАПУСК
# ══════════════════════════════════════════════

def main():
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help_cmd))
    app.add_handler(CommandHandler("newcort",newcort_cmd))
    app.add_handler(MessageHandler(filters.LOCATION,handle_location))
    app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,handle_text))
    app.add_handler(CallbackQueryHandler(handle_cb))

    # Устанавливаем команды для кнопки Menu в Telegram
    async def set_commands(app):
        from telegram import BotCommand
        await app.bot.set_my_commands([
            BotCommand("start",    "🎾 Найти корт"),
            BotCommand("help",     "⚠️ Помощь / Сообщить об ошибке"),
            BotCommand("newcort",  "➕ Предложить новый корт"),
        ])
    app.post_init = set_commands

    print(f"🎾 Теннис на районе запущен! Кортов: {len(COURTS)}. Ctrl+C для остановки.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
    main()