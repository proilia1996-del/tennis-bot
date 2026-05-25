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
    {"id":1,"emoji":"🏛","name":"Дворец тенниса Лужники","address":"Лужнецкая наб., 24, стр. 21","metro":"Спортивная","district":"ЦАО","lat":55.7165,"lon":37.5567,"type":"платно","price":"от 3 500 ₽/час","surface":["хард","грунт","искусственная трава"],"indoor":True,"wall":False,"courts_count":18,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"https://tennis.luzhniki.ru","amenities":["раздевалки","душ","кафе","парковка","прокат ракеток"]},
    {"id":2,"emoji":"🎾","name":"Лужники — открытые корты","address":"Лужнецкая наб., 24, стр. 9","metro":"Спортивная","district":"ЦАО","lat":55.7158,"lon":37.5540,"type":"платно","price":"от 1 500 ₽/час","surface":["хард","грунт"],"indoor":False,"wall":True,"courts_count":7,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"https://www.luzhniki.ru","amenities":["раздевалки","парковка"]},
    {"id":3,"emoji":"🎾","name":"Мультиспорт Лужники","address":"Лужнецкая наб., 24, стр. 10","metro":"Спортивная","district":"ЦАО","lat":55.7170,"lon":37.5580,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":4,"emoji":"🎾","name":"УСЗ Дружба (Лужники)","address":"Лужнецкая наб., 10","metro":"Спортивная","district":"ЦАО","lat":55.7180,"lon":37.5500,"type":"платно","price":"от 1 800 ₽/час","surface":["искусственная трава","грунт","хард"],"indoor":True,"wall":False,"courts_count":37,"hours":"07:00–23:00","phone":"+7 (495) 780-08-08","website":"","amenities":["раздевалки","душ","парковка"]},
    {"id":5,"emoji":"🌳","name":"Корты в Парке Горького","address":"Крымский Вал, 9","metro":"Октябрьская / Парк Культуры","district":"ЦАО","lat":55.7298,"lon":37.6011,"type":"платно","price":"от 700 ₽/час","surface":["грунт"],"indoor":False,"wall":False,"courts_count":4,"hours":"07:00–22:00","phone":"+7 (495) 995-00-20","website":"https://park-gorkogo.com","amenities":["⚠️ Бронь через сайт парка обязательна","раздевалки","прокат ракеток и мячей"]},
    {"id":6,"emoji":"🌺","name":"Корты Екатерининский парк","address":"ул. Советской Армии, 1","metro":"Достоевская","district":"ЦАО","lat":55.7801,"lon":37.6134,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":7,"emoji":"💎","name":"Динамо-центр (Петровка)","address":"ул. Петровка, 26","metro":"Чеховская","district":"ЦАО","lat":55.7643,"lon":37.6140,"type":"платно","price":"от 2 500 ₽/час","surface":["хард","искусственная трава"],"indoor":True,"wall":False,"courts_count":12,"hours":"07:00–23:00","phone":"+7 (495) 221-77-55","website":"","amenities":["раздевалки","душ","кафе","тренеры","парковка"]},
    {"id":8,"emoji":"🎾","name":"Теннисный клуб Чайка","address":"Коробейников пер., 1/2","metro":"Парк Культуры","district":"ЦАО","lat":55.7390,"lon":37.5960,"type":"платно","price":"от 2 200 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (499) 766-80-13","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":9,"emoji":"🎾","name":"Корты РАН","address":"Курсовой пр., 2","metro":"Кропоткинская","district":"ЦАО","lat":55.7460,"lon":37.5870,"type":"платно","price":"от 1 500 ₽/час","surface":["грунт","хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":10,"emoji":"🎾","name":"Корты на крыше (Спартаковская)","address":"ул. Спартаковская, 16, корп. 6","metro":"Бауманская","district":"ЦАО","lat":55.7710,"lon":37.6780,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":2,"hours":"07:00–23:00","phone":"+7 (495) 280-11-22","website":"","amenities":["раздевалки","душ"]},
    {"id":11,"emoji":"🎾","name":"Стадион Буревестник (Плющиха)","address":"ул. Плющиха, 27","metro":"Смоленская","district":"ЦАО","lat":55.7450,"lon":37.5750,"type":"платно","price":"от 1 200 ₽/час","surface":["асфальт","хард"],"indoor":False,"wall":False,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":12,"emoji":"🎾","name":"Global Tennis Петровка","address":"ул. Петровка, 26, стр. 9","metro":"Чеховская","district":"ЦАО","lat":55.7672,"lon":37.6148,"type":"платно","price":"от 2 500 ₽/час","surface":["ковёр"],"indoor":True,"wall":False,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 774-55-93","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":13,"emoji":"🏅","name":"СК Олимпийский (теннис)","address":"Олимпийский пр-т, 16","metro":"Проспект Мира","district":"ЦАО","lat":55.7824,"lon":37.6201,"type":"платно","price":"от 2 200 ₽/час","surface":["хард","ковёр"],"indoor":True,"wall":False,"courts_count":8,"hours":"07:00–23:00","phone":"+7 (495) 681-22-34","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":14,"emoji":"🏙","name":"Корты у Чистых прудов","address":"Чистопрудный бульвар, 12","metro":"Чистые пруды","district":"ЦАО","lat":55.7638,"lon":37.6382,"type":"платно","price":"от 1 200 ₽/час","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":15,"emoji":"🎾","name":"Корт в Саду Баумана","address":"ул. Старая Басманная, 15а","metro":"Красные Ворота","district":"ЦАО","lat":55.7646,"lon":37.6714,"type":"платно","price":"уточняйте на сайте (разные тарифы)","surface":["хард"],"indoor":False,"wall":False,"courts_count":1,"hours":"07:00–22:00","phone":"","website":"https://sadbaumana.ru/life-in-the-garden/tennis-court","amenities":["⚠️ Аренда платная, нужна бронь на сайте","прокат ракеток и мячей","освещение вечером"]},
    {"id":16,"emoji":"🎾","name":"Теннисный клуб Таганский парк","address":"ул. Таганская, 40/42","metro":"Таганская","district":"ЦАО","lat":55.7381,"lon":37.6509,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":False,"wall":False,"courts_count":1,"hours":"08:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},

    # ── САО ──────────────────────────────────
    {"id":17,"emoji":"🏆","name":"Теннисный центр ЦСКА","address":"Ленинградский пр-т, 39","metro":"Аэропорт / Динамо","district":"САО","lat":55.7987,"lon":37.5398,"type":"платно","price":"от 2 000 ₽/час","surface":["хард","ковёр"],"indoor":True,"wall":False,"courts_count":10,"hours":"07:00–23:00","phone":"+7 (495) 213-90-22","website":"https://cska.ru","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":18,"emoji":"🏙","name":"Корты Ходынское поле","address":"Авиационная ул., 79","metro":"ЦСКА","district":"САО","lat":55.7921,"lon":37.5274,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":2,"hours":"07:00–23:00","phone":"","website":"","amenities":["⚠️ Нужна онлайн-бронь (mos.ru)","инвентарь бесплатно","открытый доступ"]},
    {"id":19,"emoji":"💎","name":"Теннисный центр Динамо","address":"Ленинградский пр-т, 36","metro":"Динамо","district":"САО","lat":55.7912,"lon":37.5583,"type":"платно","price":"от 2 800 ₽/час","surface":["хард","грунт"],"indoor":True,"wall":False,"courts_count":14,"hours":"07:00–23:00","phone":"+7 (495) 612-76-43","website":"https://www.dinamo.ru","amenities":["раздевалки","душ","бассейн","кафе","парковка","тренеры"]},
    {"id":20,"emoji":"🎾","name":"Академия тенниса Тарпищева (ДМАТ)","address":"Ленинградский пр-т, 36, стр. 29","metro":"Динамо","district":"САО","lat":55.7915,"lon":37.5570,"type":"платно","price":"от 2 500 ₽/час","surface":["хард","грунт"],"indoor":True,"wall":False,"courts_count":15,"hours":"07:00–23:00","phone":"+7 (495) 213-90-33","website":"","amenities":["раздевалки","душ","тренеры","кафе"]},
    {"id":21,"emoji":"🎾","name":"НТЦ им. Самаранча","address":"Ленинградское шоссе, вл. 45/47","metro":"Речной Вокзал","district":"САО","lat":55.8420,"lon":37.4730,"type":"платно","price":"от 2 000 ₽/час","surface":["грунт","хард"],"indoor":True,"wall":False,"courts_count":14,"hours":"07:00–23:00","phone":"+7 (495) 459-88-00","website":"","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":22,"emoji":"🎾","name":"Tennis Capital на Войковской","address":"Ленинградское ш., 25А, стр. 2","metro":"Войковская","district":"САО","lat":55.8189,"lon":37.4977,"type":"платно","price":"от 2 000 ₽/час","surface":["хард","грунт"],"indoor":True,"wall":False,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 085-45-09","website":"https://tenniscapital.ru","amenities":["раздевалки","душ","парковка","тренеры"]},
    {"id":23,"emoji":"🌿","name":"Корты в парке Дубки","address":"ул. Дубки, 1","metro":"Тимирязевская","district":"САО","lat":55.8207,"lon":37.5621,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":24,"emoji":"🌊","name":"Теннисный центр Северный речной вокзал","address":"Ленинградское шоссе, 51","metro":"Речной Вокзал","district":"САО","lat":55.8410,"lon":37.4720,"type":"платно","price":"от 2 500 ₽/час","surface":["грунт","хард"],"indoor":False,"wall":False,"courts_count":14,"hours":"08:00–22:00","phone":"+7 (495) 459-80-00","website":"","amenities":["раздевалки","душ","кафе","парковка","тренеры"]},
    {"id":25,"emoji":"🎾","name":"Эйс-клуб на Флотской","address":"ул. Флотская, 15, стр. 2","metro":"Речной Вокзал","district":"САО","lat":55.8402,"lon":37.4780,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":3,"hours":"07:00–23:00","phone":"+7 (495) 459-77-11","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":26,"emoji":"🎾","name":"УСТК Старт (ЦСКА, Песчаная)","address":"3-я Песчаная ул., 2","metro":"Аэропорт","district":"САО","lat":55.8010,"lon":37.5350,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":9,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":27,"emoji":"🎾","name":"Спортклуб Москворечье (Москворечье ул.)","address":"ул. Москворечье, 4","metro":"Каширская","district":"САО","lat":55.6672,"lon":37.6350,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":8,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","душ","тренеры"]},

    # ── СВАО ─────────────────────────────────
    {"id":107,"emoji":"🌿","name":"Корты в сквере Олонецкий проезд","address":"Олонецкий пр., д. 15А (сквер)","metro":"Бабушкинская / Медведково","district":"СВАО","lat":55.8530,"lon":37.6530,"type":"бесплатно","price":"Бесплатно","surface":["хард","искусственная трава"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"https://skver-olonets.bapark.ru/sport/bolshoj-tennis/","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи","скамейки и шкафчики для вещей"]},
    {"id":28,"emoji":"🌿","name":"Корты в парке Яуза","address":"ул. Чичерина (ост.), парк Яуза","metro":"Свиблово / Бабушкинская","district":"СВАО","lat":55.8670,"lon":37.6480,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":False,"courts_count":1,"hours":"Круглосуточно","phone":"","website":"","amenities":["открытый доступ","освещение"]},
    {"id":29,"emoji":"⭐","name":"Теннисный клуб Отрадное","address":"ул. Декабристов, 12","metro":"Отрадное","district":"СВАО","lat":55.8647,"lon":37.6073,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 903-44-55","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":30,"emoji":"🌲","name":"Теннисный клуб Лианозово","address":"Угличская ул., 13","metro":"Лианозово / Алтуфьево","district":"СВАО","lat":55.8934,"lon":37.5721,"type":"платно","price":"уточняйте по телефону","surface":["хард","искусственная трава"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"https://lianozovo-tennis.ru","amenities":["раздевалки","тренеры"]},
    {"id":31,"emoji":"🎾","name":"Теннисный клуб ВДНХ","address":"пр-т Мира, 119","metro":"ВДНХ","district":"СВАО","lat":55.8222,"lon":37.6406,"type":"платно","price":"от 2 000 ₽/час","surface":["хард","грунт"],"indoor":False,"wall":True,"courts_count":6,"hours":"08:00–22:00","phone":"+7 (495) 544-34-56","website":"","amenities":["раздевалки","прокат ракеток"]},
    {"id":32,"emoji":"🏆","name":"Теннисный клуб Марьина Роща","address":"ул. Шереметьевская, 6","metro":"Марьина Роща","district":"СВАО","lat":55.7912,"lon":37.6270,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 631-45-67","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":33,"emoji":"🌳","name":"Корты у Джамгаровского пруда","address":"Джамгаровский парк, Енисейская ул.","metro":"Бабушкинская","district":"СВАО","lat":55.8573,"lon":37.6612,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","свои ракетки и мячи"]},
    {"id":34,"emoji":"🎾","name":"Гео-Алмаз (СВАО)","address":"ул. Малыгина, 2","metro":"Бабушкинская","district":"СВАО","lat":55.8560,"lon":37.6700,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 471-15-31","website":"","amenities":["раздевалки","тренеры"]},

    # ── ВАО ──────────────────────────────────
    {"id":35,"emoji":"🌲","name":"Корты в Измайловском парке","address":"Измайловское шоссе, 71","metro":"Измайловская","district":"ВАО","lat":55.7887,"lon":37.7492,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":4,"hours":"10:00–21:00","phone":"","website":"","amenities":["⚠️ Свои ракетки и мячи","открытый доступ","раздевалки"]},
    {"id":36,"emoji":"🌴","name":"Теннисный центр Спартак (Сокольники)","address":"Майский просек, 7, стр. 7 (парк Сокольники)","metro":"Сокольники","district":"ВАО","lat":55.7893,"lon":37.6793,"type":"платно","price":"от 2 300 ₽/час","surface":["грунт","хард"],"indoor":True,"wall":False,"courts_count":32,"hours":"07:00–23:00","phone":"+7 (495) 120-58-38","website":"https://tenniscentre-spartak.ru","amenities":["раздевалки","душ","кафе","тренеры","прокат ракеток","парковка"]},
    {"id":37,"emoji":"🌳","name":"Корты в парке Терлецкий","address":"Шоссе Энтузиастов, 51","metro":"Шоссе Энтузиастов","district":"ВАО","lat":55.7552,"lon":37.7509,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":38,"emoji":"🎾","name":"Теннисный клуб Черкизово","address":"Б. Черкизовская ул., 125","metro":"Черкизовская","district":"ВАО","lat":55.8007,"lon":37.7322,"type":"платно","price":"от 1 600 ₽/час","surface":["хард","ковёр"],"indoor":True,"wall":False,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 161-77-88","website":"","amenities":["раздевалки","душ"]},
    {"id":39,"emoji":"🌳","name":"Корты в парке Перово","address":"ул. Перовская, 66","metro":"Перово","district":"ВАО","lat":55.7505,"lon":37.7828,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":40,"emoji":"🎾","name":"Теннисный клуб Ткацкая","address":"ул. Ткацкая, 24","metro":"Электрозаводская","district":"ВАО","lat":55.7793,"lon":37.6892,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (499) 166-95-34","website":"","amenities":["раздевалки","тренеры"]},
    {"id":41,"emoji":"🎾","name":"Теннисный клуб Новогиреево","address":"Зелёный пр-т, 71","metro":"Новогиреево","district":"ВАО","lat":55.7545,"lon":37.8219,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":3,"hours":"08:00–22:00","phone":"+7 (495) 702-33-44","website":"","amenities":["раздевалки","тренеры"]},

    # ── ЮВАО ─────────────────────────────────
    {"id":106,"emoji":"🌊","name":"Корты в парке у прудов Радуга","address":"ул. Сухонская, д. 9 (парк у прудов Радуга)","metro":"Бульвар Рокоссовского","district":"ВАО","lat":55.8090,"lon":37.7350,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка","искусственная трава"],"indoor":False,"wall":False,"courts_count":3,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи","сетки есть на 1 корте"]},
    {"id":42,"emoji":"🌸","name":"Корты в Марьино","address":"Марьинский парк, ул. Белореченская","metro":"Марьино","district":"ЮВАО","lat":55.6558,"lon":37.7458,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":4,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":43,"emoji":"🌻","name":"Корты в Люблино","address":"Люблинский парк, ул. Судакова","metro":"Люблино","district":"ЮВАО","lat":55.6763,"lon":37.7658,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":44,"emoji":"🔥","name":"Теннисный центр Олимп","address":"Волгоградский пр-т, 46","metro":"Текстильщики","district":"ЮВАО","lat":55.7088,"lon":37.7257,"type":"платно","price":"от 1 600 ₽/час","surface":["ковёр","хард"],"indoor":True,"wall":False,"courts_count":8,"hours":"07:00–23:00","phone":"+7 (495) 177-88-99","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":45,"emoji":"🎾","name":"Теннисный клуб Кузьминки","address":"Волгоградский пр-т, 168","metro":"Кузьминки","district":"ЮВАО","lat":55.7088,"lon":37.7756,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"08:00–22:00","phone":"+7 (495) 179-55-66","website":"","amenities":["раздевалки","тренеры"]},
    {"id":46,"emoji":"🌿","name":"Корты в Борисовских прудах","address":"ул. Маршала Захарова, д. 10, корп. 2","metro":"Орехово","district":"ЮВАО","lat":55.6262,"lon":37.6985,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":False,"courts_count":4,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сеток нет — принести свою","открытый доступ"]},
    {"id":47,"emoji":"🌿","name":"Корты в Некрасовке","address":"ул. Покровская, 14","metro":"Некрасовка","district":"ЮВАО","lat":55.7009,"lon":37.8472,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},

    # ── ЮАО ──────────────────────────────────
    {"id":48,"emoji":"⚡","name":"Теннисный клуб Spartak","address":"2-й Бабьегородский пер., 3","metro":"Тульская","district":"ЮАО","lat":55.7201,"lon":37.6223,"type":"платно","price":"от 2 500 ₽/час","surface":["грунт","хард"],"indoor":False,"wall":True,"courts_count":8,"hours":"08:00–22:00","phone":"+7 (495) 955-77-50","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":49,"emoji":"🏰","name":"Теннисный клуб Коломенское","address":"пр. Андропова, 39","metro":"Коломенская","district":"ЮАО","lat":55.6746,"lon":37.6645,"type":"платно","price":"от 1 800 ₽/час","surface":["грунт","хард"],"indoor":False,"wall":True,"courts_count":5,"hours":"08:00–22:00","phone":"+7 (495) 115-22-33","website":"","amenities":["раздевалки","тренеры"]},
    {"id":50,"emoji":"🌊","name":"Корты в парке Царицыно (стадион Огонёк)","address":"Спортивная ул., вл. 2 (парк Царицыно)","metro":"Царицыно","district":"ЮАО","lat":55.6246,"lon":37.6622,"type":"платно","price":"уточняйте по телефону","surface":["хард"],"indoor":False,"wall":False,"courts_count":1,"hours":"08:00–22:00","phone":"","website":"https://tsaritsyno-museum.ru","amenities":["аренда площадки","прокат инвентаря"]},
    {"id":51,"emoji":"🎾","name":"Теннисный клуб Нагатино","address":"Нагатинская наб., 26","metro":"Нагатинская","district":"ЮАО","lat":55.6939,"lon":37.6266,"type":"платно","price":"от 1 900 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 118-44-55","website":"","amenities":["раздевалки","душ","парковка"]},
    {"id":52,"emoji":"🎾","name":"Lawn Tennis Club (Котляковская)","address":"Котляковская ул., 3","metro":"Тульская","district":"ЮАО","lat":55.7100,"lon":37.6180,"type":"платно","price":"от 2 200 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 317-77-88","website":"","amenities":["раздевалки","душ","тренажёрный зал","тренеры"]},
    {"id":53,"emoji":"🎾","name":"Теннисные корты Тригона","address":"ул. Маршала Захарова, 8, корп. 1","metro":"Нагатинская","district":"ЮАО","lat":55.6860,"lon":37.6200,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–22:00","phone":"+7 (495) 727-57-43","website":"","amenities":["открытый доступ","парковка"]},
    {"id":54,"emoji":"🎾","name":"Теннисный клуб Major","address":"Электролитный пр-д, 3, стр. 2","metro":"Нагорная","district":"ЮАО","lat":55.6784,"lon":37.6140,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (916) 780-65-65","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток"]},
    {"id":55,"emoji":"🎾","name":"Tennis Capital на Южной","address":"Варшавское шоссе, 125, стр. 3","metro":"Пражская","district":"ЮАО","lat":55.6125,"lon":37.6080,"type":"платно","price":"от 1 900 ₽/час","surface":["грунт"],"indoor":True,"wall":False,"courts_count":2,"hours":"07:00–23:00","phone":"+7 (495) 023-21-77","website":"https://tenniscapital.ru","amenities":["раздевалки","душ","парковка"]},
    {"id":56,"emoji":"🌿","name":"Корты у Днепропетровской","address":"ул. Днепропетровская, 16, корп. 4","metro":"Южная","district":"ЮАО","lat":55.6245,"lon":37.6070,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},

    # ── ЮЗАО ─────────────────────────────────
    {"id":57,"emoji":"🎓","name":"Московская академия тенниса","address":"пр. Вернадского, 97, корп. 2","metro":"Юго-Западная","district":"ЮЗАО","lat":55.6697,"lon":37.4987,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":12,"hours":"07:00–23:00","phone":"+7 (495) 933-01-55","website":"","amenities":["раздевалки","душ","тренеры","прокат ракеток","парковка"]},
    {"id":58,"emoji":"🌾","name":"Корты в Тропарёво","address":"Тропарёвский парк, ул. Академика Анохина","metro":"Тропарёво","district":"ЮЗАО","lat":55.6438,"lon":37.4478,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":59,"emoji":"🌴","name":"Корты в Бутово","address":"Бутовский лесопарк, ул. Скобелевская","metro":"Бульвар Дмитрия Донского","district":"ЮЗАО","lat":55.5754,"lon":37.6013,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":4,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":60,"emoji":"🎯","name":"Теннисный клуб Раменки","address":"Мичуринский пр-т, 12","metro":"Раменки","district":"ЮЗАО","lat":55.6988,"lon":37.4680,"type":"платно","price":"от 2 100 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":7,"hours":"07:00–23:00","phone":"+7 (495) 933-55-66","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":61,"emoji":"🌸","name":"Корты в Ясенево (Голубинская)","address":"ул. Голубинская, д. 25, корп. 2","metro":"Ясенево","district":"ЮЗАО","lat":55.6168,"lon":37.5200,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":False,"courts_count":1,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сетки нет — принести свою","открытый доступ"]},
    {"id":62,"emoji":"🎾","name":"Теннисный клуб Megasport","address":"ул. Обручева, 30","metro":"Калужская","district":"ЮЗАО","lat":55.6385,"lon":37.5509,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"wall":False,"courts_count":6,"hours":"07:00–23:00","phone":"+7 (495) 988-44-55","website":"","amenities":["раздевалки","душ","кафе","тренеры"]},
    {"id":63,"emoji":"🌳","name":"Корты в Битцевском лесу","address":"Старобитцевская ул., 5","metro":"Битцевский парк","district":"ЮЗАО","lat":55.5992,"lon":37.6087,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":64,"emoji":"🎾","name":"Теннисная академия Жемчужина","address":"ул. Крылатская, 10 (Велотрек)","metro":"Крылатское","district":"ЮЗАО","lat":55.7525,"lon":37.4042,"type":"платно","price":"от 2 000 ₽/час","surface":["искусственная трава"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (499) 141-11-87","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":65,"emoji":"🎾","name":"Мосфильмовская теннисный клуб","address":"Мосфильмовская ул., 41, корп. 2","metro":"Раменки","district":"ЮЗАО","lat":55.7180,"lon":37.4750,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":3,"hours":"07:00–23:00","phone":"+7 (925) 889-72-36","website":"","amenities":["раздевалки","душ","тренеры"]},

    # ── ЗАО ──────────────────────────────────
    {"id":66,"emoji":"🏆","name":"Корты в парке Победы","address":"Кутузовский пр-т, 38","metro":"Парк Победы","district":"ЗАО","lat":55.7299,"lon":37.4965,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":4,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":67,"emoji":"🚣","name":"Теннисный клуб Крылатское","address":"Крылатская ул., 2, стр. 31","metro":"Крылатское","district":"ЗАО","lat":55.7525,"lon":37.4000,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":False,"wall":False,"courts_count":6,"hours":"08:00–22:00","phone":"+7 (980) 197-86-50","website":"","amenities":["раздевалки","парковка"]},
    {"id":68,"emoji":"🎯","name":"Теннисный клуб Фили","address":"Филёвский бульвар, 12","metro":"Фили","district":"ЗАО","lat":55.7432,"lon":37.5060,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"wall":False,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 142-33-44","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":69,"emoji":"🌿","name":"Корты в парке Фили","address":"Большая Филёвская ул., 22","metro":"Филёвский парк","district":"ЗАО","lat":55.7469,"lon":37.5108,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":70,"emoji":"🎾","name":"Теннисный клуб Давыдково","address":"ул. Давыдковская, 6","metro":"Кунцевская","district":"ЗАО","lat":55.7306,"lon":37.4358,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 780-44-55","website":"","amenities":["раздевалки","тренеры"]},
    {"id":71,"emoji":"🌿","name":"Корты в Солнцево","address":"ул. Попутная, 5","metro":"Солнцево","district":"ЗАО","lat":55.6726,"lon":37.3968,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":72,"emoji":"🎾","name":"Теннисный клуб Верхние Поля","address":"ул. Верхние Поля, вл. 27А","metro":"Жулебино","district":"ЗАО","lat":55.7225,"lon":37.7873,"type":"платно","price":"от 1 400 ₽/час","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–22:00","phone":"+7 (495) 727-57-43","website":"","amenities":["открытый доступ","парковка"]},

    # ── СЗАО ─────────────────────────────────
    {"id":73,"emoji":"🌊","name":"Теннисный комплекс Янтарь","address":"ул. Маршала Катукова, 26","metro":"Строгино","district":"СЗАО","lat":55.8007,"lon":37.3888,"type":"платно","price":"от 1 900 ₽/час","surface":["хард","ковёр"],"indoor":True,"wall":False,"courts_count":11,"hours":"07:00–23:00","phone":"+7 (495) 632-00-35","website":"https://strogino-tennis.ru","amenities":["раздевалки","душ","тренеры","парковка"]},
    {"id":74,"emoji":"🌿","name":"Корты в ландшафтном парке Митино","address":"Пятницкое шоссе, 6 (ландшафтный парк Митино)","metro":"Митино","district":"СЗАО","lat":55.8437,"lon":37.3527,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"https://mitino.bapark.ru/sport/bolshoj-tennis/","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи","одно из лучших покрытий среди бесплатных"]},
    {"id":75,"emoji":"🎾","name":"Теннисный клуб Тушино","address":"Сходненская ул., 56","metro":"Тушинская","district":"СЗАО","lat":55.8275,"lon":37.4266,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"08:00–22:00","phone":"+7 (495) 491-22-33","website":"","amenities":["раздевалки","тренеры"]},
    {"id":76,"emoji":"🌲","name":"Корты в Покровском-Стрешнево","address":"Волоколамское шоссе, 52","metro":"Щукинская","district":"СЗАО","lat":55.8074,"lon":37.4648,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":77,"emoji":"🎾","name":"Теннисный клуб Куркино","address":"Куркинское шоссе, 17","metro":"Сходненская / Планерная","district":"СЗАО","lat":55.8890,"lon":37.3720,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":78,"emoji":"🎾","name":"Теннисный клуб Спартак Тушино","address":"ул. Туристская, 33","metro":"Планерная","district":"СЗАО","lat":55.8576,"lon":37.3944,"type":"платно","price":"от 1 600 ₽/час","surface":["хард","грунт"],"indoor":False,"wall":False,"courts_count":5,"hours":"08:00–22:00","phone":"+7 (495) 493-11-22","website":"","amenities":["раздевалки","тренеры","прокат ракеток"]},

    # ── ЗелАО ────────────────────────────────
    {"id":79,"emoji":"🌲","name":"Теннисный клуб Зеленоград","address":"Зеленоград, корп. 2010","metro":"Зеленоград (автобус)","district":"ЗелАО","lat":55.9843,"lon":37.1965,"type":"платно","price":"от 1 400 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"08:00–22:00","phone":"+7 (499) 735-11-22","website":"","amenities":["раздевалки","тренеры"]},
    {"id":105,"emoji":"🌿","name":"Корты в парке Северное Тушино","address":"ул. Свободы, 56 (парк Северное Тушино)","metro":"Сходненская / Планерная","district":"СЗАО","lat":55.8480,"lon":37.4120,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка","теннисит"],"indoor":False,"wall":False,"courts_count":3,"hours":"07:00–20:00","phone":"","website":"https://mosparks.ru/places/severnoe-tushino/tennis","amenities":["⚠️ Ключи у администратора (ул. Свободы 56с1, ежедн. 07:00–20:00)","свои ракетки и мячи","без освещения"]},
    {"id":80,"emoji":"🌿","name":"Корты в Зеленограде (парк)","address":"Зеленоград, ул. Юности, 8","metro":"Зеленоград (автобус)","district":"ЗелАО","lat":55.9800,"lon":37.2100,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},

    # ── Дополнительные ───────────────────────
    {"id":81,"emoji":"🎾","name":"Tennis Capital ВДНХ","address":"пр-т Мира, 119, павильон 22","metro":"ВДНХ","district":"СВАО","lat":55.8240,"lon":37.6380,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":1,"hours":"06:00–24:00","phone":"+7 (495) 023-21-77","website":"https://tenniscapital.ru","amenities":["раздевалки","душ"]},
    {"id":82,"emoji":"🎾","name":"Tennis Capital на Савёловской","address":"ул. Складочная, 1, стр. 1","metro":"Савёловская","district":"САО","lat":55.7960,"lon":37.5836,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":3,"hours":"07:00–23:00","phone":"+7 (495) 085-45-09","website":"https://tenniscapital.ru","amenities":["раздевалки","душ","парковка"]},
    {"id":83,"emoji":"🎾","name":"Теннисный клуб TennisVIP","address":"ул. Нагорная, 18","metro":"Нагорная","district":"ЮАО","lat":55.6800,"lon":37.6050,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":5,"hours":"07:00–23:00","phone":"+7 (495) 333-55-66","website":"","amenities":["раздевалки","душ","кафе","магазин","тренеры"]},
    {"id":84,"emoji":"🎾","name":"Теннисный клуб Лефортово","address":"ул. Солдатская, 9","metro":"Авиамоторная","district":"ВАО","lat":55.7574,"lon":37.6974,"type":"платно","price":"от 1 700 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 361-44-55","website":"","amenities":["раздевалки","тренеры"]},
    {"id":85,"emoji":"🌿","name":"Корты в парке Люблино","address":"ул. Краснодонская, 2","metro":"Люблино","district":"ЮВАО","lat":55.6780,"lon":37.7620,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":True,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":86,"emoji":"🎾","name":"ЦДРА теннис (Суворовская)","address":"Суворовская пл., 3","metro":"Новослободская","district":"ЦАО","lat":55.7762,"lon":37.6059,"type":"платно","price":"от 1 500 ₽/час","surface":["грунт"],"indoor":False,"wall":False,"courts_count":10,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":87,"emoji":"🎾","name":"Белокаменная — центр ФТМ","address":"Берсеневская наб., 20/2, корп. 2","metro":"Боровицкая","district":"ЦАО","lat":55.7448,"lon":37.6050,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":1,"hours":"08:00–22:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":88,"emoji":"🎾","name":"Стадион Буревестник (Плющиха)","address":"ул. Плющиха, 27","metro":"Смоленская","district":"ЦАО","lat":55.7450,"lon":37.5750,"type":"платно","price":"от 1 200 ₽/час","surface":["хард"],"indoor":False,"wall":False,"courts_count":4,"hours":"08:00–22:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":89,"emoji":"🎾","name":"Стадион Старт (Новая ул.)","address":"ул. Новая, 1А","metro":"Водный Стадион","district":"САО","lat":55.8298,"lon":37.4853,"type":"платно","price":"от 1 200 ₽/час","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"08:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":90,"emoji":"🌿","name":"Корты у Бунинской аллеи","address":"Остафьевская ул., к. Г","metro":"Бунинская аллея","district":"ЮЗАО","lat":55.5500,"lon":37.5200,"type":"платно","price":"от 1 400 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":3,"hours":"07:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":91,"emoji":"🎾","name":"Теннисный клуб Академический","address":"Ломоносовский пр-т, 23","metro":"Университет","district":"ЮЗАО","lat":55.6999,"lon":37.5350,"type":"платно","price":"от 1 800 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 939-44-55","website":"","amenities":["раздевалки","душ","тренеры"]},
    {"id":92,"emoji":"🎾","name":"Теннисный клуб Подбельского","address":"ул. Подбельского, 16","metro":"Бульвар Рокоссовского","district":"ВАО","lat":55.8103,"lon":37.7388,"type":"платно","price":"от 1 600 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 963-22-33","website":"","amenities":["раздевалки","тренеры"]},
    {"id":93,"emoji":"🌿","name":"Корты в Алтуфьево","address":"Алтуфьевское шоссе, 147","metro":"Алтуфьево","district":"СВАО","lat":55.8965,"lon":37.5878,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ"]},
    {"id":94,"emoji":"🎾","name":"СК Пинбол клуб","address":"Калашный пер., 1","metro":"Арбатская","district":"ЦАО","lat":55.7530,"lon":37.6050,"type":"платно","price":"от 2 000 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":2,"hours":"08:00–23:00","phone":"","website":"","amenities":["раздевалки","тренеры"]},
    {"id":96,"emoji":"🎾","name":"Спорткомплекс Фестивальный (Марьина Роща)","address":"ул. Сущёвский Вал, 56","metro":"Марьина Роща","district":"СВАО","lat":55.8050,"lon":37.5950,"type":"платно","price":"уточняйте на сайте","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"","website":"https://go2sport.ru","amenities":["⚠️ Бронь через go2sport.ru","раздевалки","душ","тренеры"]},
    {"id":97,"emoji":"🌿","name":"Корты у Тимирязевского парка","address":"напротив ост. «Префектура САО»","metro":"Тимирязевская","district":"САО","lat":55.8152,"lon":37.5618,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":3,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ","освещение","лавочки"]},
    {"id":98,"emoji":"🌿","name":"Корты в парке 30-летия Победы","address":"ул. Кировоградская, д. 18, корп. 2","metro":"Пражская / Южная","district":"ЮАО","lat":55.6200,"lon":37.6090,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Сетки есть","открытый доступ","свои ракетки и мячи"]},
    {"id":99,"emoji":"🌿","name":"Корт в сквере Родная Гавань","address":"ул. Кировоградская, д. 17, корп. 2, стр. 4","metro":"Пражская","district":"ЮАО","lat":55.6195,"lon":37.6085,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":1,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сетки может не быть","открытый доступ","свои ракетки и мячи"]},
    {"id":100,"emoji":"🌿","name":"Корты на Каширском проезде","address":"Каширский проезд, д. 9, корп. 1","metro":"Каширская","district":"ЮАО","lat":55.6500,"lon":37.6550,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":True,"courts_count":3,"hours":"09:00–22:00","phone":"","website":"","amenities":["✅ Сетки есть","теннисная стенка","открытый доступ","свои ракетки и мячи"]},
    {"id":101,"emoji":"🌿","name":"Корт Варшавское шоссе 141","address":"Варшавское шоссе, д. 141, корп. 8","metro":"Аннино","district":"ЮАО","lat":55.5878,"lon":37.6200,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":False,"courts_count":1,"hours":"09:00–22:00","phone":"","website":"","amenities":["открытый доступ","теннисная сетка"]},
    {"id":102,"emoji":"🌿","name":"Корт у Коломенской","address":"ул. Коломенская, д. 27, корп. 1","metro":"Коломенская","district":"ЮАО","lat":55.6749,"lon":37.6860,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":1,"hours":"09:00–21:00","phone":"","website":"","amenities":["⚠️ Сетки нет — принести свою","открытый доступ"]},
    {"id":111,"emoji":"🌲","name":"Корты в парке Кузьминки","address":"Волгоградский пр-т, 168В (парк Кузьминки)","metro":"Кузьминки","district":"ЮВАО","lat":55.7100,"lon":37.7900,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":False,"courts_count":3,"hours":"Круглосуточно","phone":"","website":"","amenities":["✅ Свободный доступ, круглосуточно","⚠️ Свои ракетки и мячи"]},
    {"id":110,"emoji":"🌊","name":"Корты в зоне отдыха Покровский берег","address":"Покровский берег, Строгино","metro":"Строгино","district":"СЗАО","lat":55.8050,"lon":37.3700,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":109,"emoji":"🏰","name":"Корты в усадьбе Кусково","address":"ул. Юности, 2 (усадьба Кусково)","metro":"Выхино / Рязанский проспект","district":"ВАО","lat":55.7350,"lon":37.8100,"type":"бесплатно","price":"Бесплатно","surface":["хард"],"indoor":False,"wall":False,"courts_count":2,"hours":"09:00–21:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":108,"emoji":"🌳","name":"Корты в парке 50-летия Октября","address":"Нагатинская наб., 8 (парк 50-летия Октября)","metro":"Нагатинская","district":"ЮАО","lat":55.6830,"lon":37.6310,"type":"бесплатно","price":"Бесплатно","surface":["резиновая крошка"],"indoor":False,"wall":False,"courts_count":2,"hours":"08:00–22:00","phone":"","website":"","amenities":["✅ Свободный доступ","⚠️ Свои ракетки и мячи"]},
    {"id":103,"emoji":"🌿","name":"Корт в Красной Пахре","address":"Квартал 49, пос. Краснопахорское","metro":"Автобус от Тёплого Стана","district":"ТиНАО","lat":55.4395,"lon":37.2582,"type":"бесплатно","price":"Бесплатно","surface":["искусственная трава"],"indoor":False,"wall":False,"courts_count":1,"hours":"09:00–21:00","phone":"","website":"","amenities":["открытый доступ","теннисная сетка"]},
    {"id":104,"emoji":"🎾","name":"Теннисный центр Лосиный остров","address":"ул. Анадырский пр., 101","metro":"Лосиноостровская","district":"СВАО","lat":55.8650,"lon":37.7100,"type":"платно","price":"от 1 500 ₽/час","surface":["хард"],"indoor":True,"wall":False,"courts_count":4,"hours":"07:00–23:00","phone":"+7 (495) 471-98-76","website":"","amenities":["раздевалки","душ","тренеры"]},
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

def filter_courts(pay_type,surface,indoor,lat,lon):
    res=[]
    for c in COURTS:
        if pay_type!="all" and c["type"]!=pay_type: continue
        if surface!="all" and surface not in c["surface"]: continue
        if indoor=="indoor" and not c["indoor"]: continue
        if indoor=="outdoor" and c["indoor"]: continue
        d=dict(c); d["distance_km"]=haversine(lat,lon,d["lat"],d["lon"]); res.append(d)
    return sorted(res,key=lambda x:x["distance_km"])[:MAX_COURTS]

def format_card(c):
    roof="🏠 Крытый" if c["indoor"] else "☀️ Открытый"
    surf=" · ".join(c["surface"]); amen=" · ".join(c["amenities"])
    wall="" if c["indoor"] else "\n🧱 Стенка: "+("✅ Есть" if c.get("wall") else "❌ Нет")
    dist=f"\n📏 {c['distance_km']:.1f} км от тебя" if "distance_km" in c else ""
    txt=(f"{c['emoji']} *{c['name']}*\n\n📍 {c['address']}\n🚇 {c['metro']}{dist}\n\n"
         f"{roof}{wall}\n🎾 Покрытие: {surf}\n🏟 Кортов: {c['courts_count']} шт.\n\n"
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

def start_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🆓 Бесплатный",callback_data="type_бесплатно"),
         InlineKeyboardButton("💳 Платный",callback_data="type_платно")],
        [InlineKeyboardButton("🎾 Любой",callback_data="type_all")],
    ])


# ══════════════════════════════════════════════
# ОБРАБОТЧИКИ
# ══════════════════════════════════════════════

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🎾 *Теннис на районе*\n\nНайду ближайший корт за несколько секунд 🏙\n\nВыбери тип корта:",
        parse_mode="Markdown", reply_markup=start_kb())

async def handle_cb(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); d=q.data

    if d.startswith("type_"):
        pt=d.replace("type_",""); context.user_data["type"]=pt
        lm={"бесплатно":"Бесплатный ✅","платно":"Платный ✅","all":"Любой ✅"}

        if pt=="бесплатно":
            # ── Бесплатный: сразу покрытие, пропускаем крытый/открытый ──
            context.user_data["indoor"]="all"
            kb=[[InlineKeyboardButton("🔵 Хард",callback_data="surface_хард"),
                 InlineKeyboardButton("🟤 Грунт",callback_data="surface_грунт")],
                [InlineKeyboardButton("🟢 Искусственная трава",callback_data="surface_искусственная трава")],
                [InlineKeyboardButton("✨ Без разницы",callback_data="surface_all")]]
            await q.edit_message_text(f"{lm[pt]}\n\nКакое покрытие предпочитаешь?",
                parse_mode="Markdown",reply_markup=InlineKeyboardMarkup(kb))
        else:
            # ── Платный / Любой: показываем крытый/открытый ──
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
        await q.edit_message_text(
            "🚇 *Введи название станции метро*\n\nНапиши в чат, например:\n_Динамо_, _Сокольники_, _Тушинская_",
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
    inp=update.message.text.strip(); coords=find_metro(inp)
    if not coords:
        await update.message.reply_text(f"😔 Станция *{inp}* не найдена.\n\nПопробуй иначе, например: _Динамо_, _Сокольники_",parse_mode="Markdown"); return
    context.user_data["waiting_metro"]=False
    await process(update,context,coords[0],coords[1],"metro",inp)

async def process(update,context,lat,lon,source,metro_name=""):
    pt=context.user_data.get("type","all"); surf=context.user_data.get("surface","all"); ind=context.user_data.get("indoor","all")
    if not pt: await update.message.reply_text("Сначала выбери параметры — нажми /start 🎾"); return
    courts=filter_courts(pt,surf,ind,lat,lon); context.user_data["results"]=courts
    if not courts: await update.message.reply_text("😔 Кортов не найдено. Попробуй /start и измени фильтры."); return
    lm={"бесплатно":"Бесплатные","платно":"Платные","all":"Все"}; label=lm.get(pt,"Найденные")
    header=f"🚇 Рядом со станцией *{metro_name.title()}*" if source=="metro" else "📍 Рядом с тобой"
    await update.message.reply_text(
        f"🎾 *{label} корты — {len(courts)} шт.*\n{header}\n\nПоказано: {min(PAGE_SIZE,len(courts))} из {len(courts)} 👇",
        parse_mode="Markdown",reply_markup=list_kb(courts,0))

async def start_over(query):
    await query.edit_message_text(
        "🎾 *Теннис на районе*\n\nВыбери тип корта:",
        parse_mode="Markdown",reply_markup=start_kb())

async def help_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("⚠️ Написать об ошибке",url=ADMIN_TG)]])
    await update.message.reply_text(
        "🎾 *Теннис на районе*\n\n"
        "/start — найти корт\n"
        "/help — справка\n"
        "/newcort — предложить новый корт\n\n"
        "1️⃣ Тип корта (платный / бесплатный)\n"
        "2️⃣ Крытый или открытый _(только для платных)_\n"
        "3️⃣ Покрытие\n"
        "4️⃣ Геолокация 📍 или метро 🚇\n"
        "5️⃣ Список от ближайшего!\n\n"
        "⬇️ *Доложить об ошибке бота или недостоверной информации о кортах:*",
        parse_mode="Markdown", reply_markup=kb)

async def newcort_cmd(update:Update,context:ContextTypes.DEFAULT_TYPE):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("➕ Написать про корт",url=ADMIN_TG)]])
    await update.message.reply_text(
        "🎾 *Нет какого-то корта? Пишите нам!*\n\n"
        "Мы добавим его в базу как можно скорее 🙏\n\n"
        "Укажите пожалуйста:\n"
        "• Название корта\n"
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