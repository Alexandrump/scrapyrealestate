#!/usr/bin/python3
import sys, subprocess, telebot, time, os.path, platform, os, logging, uuid, urllib.request, json, random
import scrapyrealestate.db_module as db_module
from os import path
from art import *
from unidecode import unidecode
from scrapyrealestate.settings import settings

__author__ = "mferark"
__license__ = "GPL"
__version__ = "2.0.5"

def init_logs():
    global logger
    try:
        log_level = data['log_level'].upper()
    except:
        log_level = 'INFO'

    if log_level == 'DEBUG':
        log_level = logging.DEBUG
    elif log_level == 'INFO':
        log_level = logging.INFO
    elif log_level == 'WARNING':
        log_level = logging.WARNING
    elif log_level == 'ERROR':
        log_level = logging.ERROR
    elif log_level == 'CRITICAL':
        log_level = logging.CRITICAL

    # create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(log_level)

    # create formatter
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', "%Y-%m-%d %H:%M:%S")
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


def del_json(dir):
    # Si existeixen data eliminem els json que hi pugui haver
    filelist = [f for f in os.listdir('data') if f.endswith(".json")]
    for f in filelist:
        os.remove(os.path.join(dir, f))


def del_json_flats(dir):
    # Si existeixen data eliminem els json que hi pugui haver
    filelist = [f for f in os.listdir('data') if f.endswith(".json")]
    for f in filelist:
        if f != 'config.json':
            os.remove(os.path.join(dir, f))

def mix_list(original_list):
    list = original_list[:]
    longitud_list = len(list)
    for i in range(longitud_list):
        index_random = random.randint(0, longitud_list - 1)
        temporal = list[i]
        list[i] = list[index_random]
        list[index_random] = temporal
    return list

def get_config():
    #os.chdir('../scrapyrealestate/scrapyrealestate')
    #Sino existeix el fitxer de configuració agafem les dades de la web
    if not os.path.isfile('./data/config.json'):
        #Mirem si existeix el directori data i logs, sinó el creem.
       if not os.path.exists('data'):
           os.makedirs('data')
       pid = init_app_flask()  # iniciem  flask a localhost:8080
       get_config_flask(pid)  # agafem les dades de la configuració
    else:
        with open('./data/config.json') as json_file:
            global data
            data = json.load(json_file)

def check_config(db_client, db_name):
    # creem l'objecte per enviar tg
    tb = telebot.TeleBot('5042109408:AAHBrCsNiuI3lXBEiLjmyxqXapX4h1LHbJs')

    # Sino existeix el fitxer scrapy.cfg, sortim
    if not path.exists("scrapy.cfg"):
        logger.error("NOT FILE FOUND scrapy.cfg")
        sys.exit()

    # Check urls
    urls = get_urls(data)
    urls_ok = ''
    urls_text = ''
    db_urls = ''
    urls_ok_count = 0

    # Iterem cada url i portal
    for portal in urls:
        for url in urls[portal]:
            # Mirem si hi ha mes d'una url per portal
            # Si tenim mes de x urls, sortim
            # if len(urls[portal]) > 1:
            #     logger.error(f"MAXIM URLS PORTAL (1) YOU HAVE ({len(urls[portal])}) IN {url.split('/')[2]}")
            #     info_message = tb.send_message(data['telegram_chatuserID'], f"<code>LOADING...</code>\n"
            #                                                                 f"\n"
            #                                                                 f"<code>scrapyrealestate v{__version__}\n</code>"
            #                                                                 f"\n"
            #                                                                 f"<code>MAXIM URLS PORTAL (1) YOU HAVE ({len(urls[portal])}) IN {url.split('/')[2]}</code>\n",
            #                                    parse_mode='HTML')
            #     sys.exit()
            # Si te mes de 3 parts es que es url llarga i la guardem a la llista de ok
            # url = url[0] if isinstance(url, list) else url
            # print(url)
            if len(url.split('/')) > 2:
                portal_url = url.split('/')[2]
                portal_name = portal_url.split('.')[1]
                urls_ok_count += 1
                urls_ok += f' <a href="{url}">{portal_name}</a>    '
                db_urls += f'{url};'
                try:
                    urls_text += f"\t\t- {portal_name} → {url.split('/')[4]}\n"
                except:
                    urls_text += f"\t\t- {portal_name} → {url.split('/')[3]}\n"

    # Si tenim mes de x urls, sortim
    # if urls_ok_count > 4:
    #     logger.error(f"MAXIM URLS (4) YOU HAVE ({urls_ok_count})")
    #     info_message = tb.send_message(data['telegram_chatuserID'], f"<code>LOADING...</code>\n"
    #                                                                 f"\n"
    #                                                                 f"<code>scrapyrealestate v{__version__}\n</code>"
    #                                                                 f"\n"
    #                                                                 f"<code>MAXIM URLS (4) YOU HAVE ({urls_ok_count})</code>\n",
    #                                    parse_mode='HTML')
    #     sys.exit()

    if not data['telegram_chatuserID'] is None:
        try:
            if data['start_msg'] == 'True':
                info_message = tb.send_message(data['telegram_chatuserID'], f"<code>LOADING...</code>\n"
                                                                            f"\n"
                                                                            f"<code>scrapyrealestate v{__version__}\n</code>"
                                                                            f"\n"
                                                                            f"<code>REFRESH     <b>{data['time_update']}</b>s</code>\n"
                                                                            f"<code>MIN PRICE   <b>{data['min_price']}€</b></code>\n"
                                                                            f"<code>MAX PRICE   <b>{data['max_price']}€</b> (0 = NO LIMIT)</code>\n"
                                                                            f"<code>URLS        <b>{urls_ok_count}</b>  →   </code>{urls_ok}\n",
                                               parse_mode='HTML')
            else:
                info_message = tb.send_message(data['telegram_chatuserID'],
                                               f"LOADING... scrapyrealestate v{__version__}\n")
        # Si no s'ha enviat el missatge de telegram correctament, sortim
        except telebot.apihelper.ApiTelegramException:
            logger.error('TELEGRAM CHAT ID IS NOT CORRECT OR BOT @scrapyrealestatebot NOT ADDED CORRECTLY TO CHANNEL')
            sys.exit()

        # data
        data_host = {
            'id': str(uuid.uuid4())[:8],
            'chat_id': info_message.chat.id,
            'group_name': info_message.chat.title,
            'refresh': data['time_update'],
            'min_price': data['min_price'],
            'max_price': data['max_price'],
            'urls': db_urls,
            'host_name': platform.node(),
            'connections': 0,
            'so': platform.platform()
        }

        # Si ha funcionat enviem dades
        logger.info(f"TELEGRAM {info_message.chat.title} CHANNEL VERIFIED")

        # enviem dades
        # comprovem si ja existeix una connexió igual
        query_dbcon = db_module.query_host_mysql(connection, 'sr_connections', data_host, logger)
        if not query_dbcon:
            # creem el registre a mysql
            db_module.insert_host_mysql(connection, 'sr_connections', data_host, logger)
        # So ja existeix actualitzem el valor de conexions
        else:
            db_module.update_host_mysql(connection, 'sr_connections', data_host, logger)
    else:
        logger.error('TELEGRAM CHAT ID IS EMPTY')
        sys.exit()

    return info_message


def checks():
    # Mirem el time update
    if int(data['time_update']) < 300:
        logger.error("TIME UPDATE < 300")
        sys.exit()
    time.sleep(0.05)
    connection = db_module.check_bbdd_mysql(config_db_mysql, logger)
    info_message = check_config(connection)
    return connection, info_message

def check_url(url):
    try:
        url_code = urllib.request.urlopen(url).getcode()
    except:
        url_code = 404

    return url_code


def init_app_flask():
    # comprovem si el servidor està engengat.
    # si no trobem cap pàgina a localhost:8080 executem el servidor
    localhost_code = check_url("http://localhost:8080")
    if localhost_code != 200:
        try:
            # os.system('python ./scrapyrealestate/flask_server.py &')
            proces_server = subprocess.Popen('python ./scrapyrealestate/flask_server.py &', shell=True)
        except:
            # os.system('python3 ./scrapyrealestate/flask_server.py &')
            proces_server = subprocess.Popen('python3 ./scrapyrealestate/flask_server.py &', shell=True)
        # proces_server.wait()
        pid = proces_server.pid
        real_pid = pid + 1
        # proces_server.terminate()
    else:
        real_pid = os.popen('pgrep python ./scrapyrealestate/flask_server.py').read()

    return real_pid


def get_config_flask(pid):
    while True:
        try:
            # si trobem info a localhost:8080/data guardem les dades i sortim del bucle
            with open('./data/config.json') as json_file:
                global data
                data = json.load(json_file)
                os.system(f'kill {pid}')
                break
        except:
            pass
        time.sleep(1)

def get_urls(data):
    urls = {}

    if data.get('url_idealista', '') == '' and data.get('url_pisoscom', '') == '' and data.get('url_fotocasa', '') == '' and data.get('url_habitaclia', '') == '':
        logger.warning("NO URLS ENTERED (MINIMUM 1 URL)")
        sys.exit()

    start_urls_idealista = data.get('url_idealista', [])
    start_urls_idealista = [url + '?ordenado-por=fecha-publicacion-desc' for url in start_urls_idealista]

    start_urls_pisoscom = data.get('url_pisoscom', [])
    start_urls_pisoscom = [url + 'fecharecientedesde-desc/' for url in start_urls_pisoscom]

    start_urls_fotocasa = data.get('url_fotocasa', [])

    start_urls_habitaclia = data.get('url_habitaclia', [])
    start_urls_habitaclia = [url + '?ordenar=mas_recientes' for url in start_urls_habitaclia]

    urls['start_urls_idealista'] = start_urls_idealista
    urls['start_urls_pisoscom'] = start_urls_pisoscom
    urls['start_urls_fotocasa'] = start_urls_fotocasa
    urls['start_urls_habitaclia'] = start_urls_habitaclia

    return urls


def check_new_flats(json_file_name, scrapy_rs_name, min_price, max_price, tg_chatID, connection, telegram_msg, logger):
    '''
    Función que lee un json de las viviendas con sus propiedades.
    Compara si hay alguna que no esté en la base de datos y notifica con mensaje.
    :param json:
    :return:
    '''
    # creamos el objeto para enviar tg
    tb = telebot.TeleBot('5042109408:AAHBrCsNiuI3lXBEiLjmyxqXapX4h1LHbJs')

    new_urls = []

    # Abrir json
    json_file = open(json_file_name)

    # Encapsulamos por si da error
    try:
        data_json = json.load(json_file)
    except:
        data_json = ""

    # Check if JSON is empty
    if len(data_json) == 0:
        logger.warning(f'NO DATA IN JSON {scrapy_rs_name.upper()}')
    json_file.close()

    # open file and read the content in a list
    try:
        with open("./data/ids.json", "r") as outfile:
            ids_file = json.load(outfile)
            new_ids_file = []
        outfile.close()
    except FileNotFoundError:
        ids_file = []
        new_ids_file = []
        pass

    # Iteramos cada piso del diccionario y tratamos los datos
    for flat in data_json:
        flat_id = int(flat['id'])  # Convertimos a int
        title = flat["title"].replace("\'", "")
        try:
            town = flat['town']
        except:
            town = ''
        try:
            neighbour = flat['neighbour']
        except:
            neighbour = ''
        try:
            street = flat['street']
        except:
            street = ''
        try:
            number = flat['number']
        except:
            number = ''
        try:
            type = flat['type']
        except:
            type = ''
        # Cogemos solo los dígitos de price, rooms y m2
        try:
            price_str = flat['price']
        except:
            price_str = 0

        try:
            price = int(''.join(char for char in flat['price'] if char.isdigit()))
        except:
            price = 0

        if price == 0:
            price = price_str

        try:
            rooms = int(''.join(char for char in flat['rooms'] if char.isdigit()))
        except:
            try: rooms = flat['rooms']
            except: rooms = 0
        try:
            m2 = int(''.join(char for char in flat['m2'] if char.isdigit())[:-1])
            m2_tg = f'{m2}m²'
        except:
            try:
                m2 = flat['m2']
                m2_tg = f'{m2}m²'
            except:
                m2 = 0
                m2_tg = ''
        try:
            floor = flat['floor']
        except:
            floor = ''

        href = flat['href']
        site = flat['site']

        # Si la id del flat no está en los ids del archivo:
        if not flat_id in ids_file:
            # Añadimos el id nuevo a la lista
            new_ids_file.append(flat_id)
            # data
            data_flat = {
                'id': flat_id,
                'price': price,
                'm2': m2,
                'rooms': rooms,
                'floor': floor,
                'town': town,
                'neighbour': neighbour,
                'street': street,
                'number': number,
                'title': title,
                'href': href,
                'type': type,
                'site': site,
                'online': False
            }
            # Guardamos la vivienda en la base de datos MySQL
            if not town == '':
                town_nf = unidecode(town.replace(' ', '_').lower())
                # Comparamos si hay viviendas iguales en MySQL:
                match_flat_list = db_module.query_flat_mysql(connection, 'sr_flats', data_flat, logger)
                if len(match_flat_list) > 0:
                    '''logger.debug(f"FLAT MATCH - NOT INSERTING: \n"
                                 f"{data_flat} \n"
                                 f"{match_flat_list}")'''
                    pass
                else:
                    if not site == 'fotocasa':
                        db_module.insert_flat_mysql(connection, 'sr_flats', data_flat, logger)
            if price == 'Aconsultar':
                continue
            elif price == 'A consultar':
                continue

            # Si el precio es <= max_price
            if int(max_price) >= int(price) >= int(min_price) or int(max_price) == 0 and int(price) >= int(min_price):
                # Enviar mensaje a telegram si es True
                if telegram_msg:
                    new_urls.append(href)
                    try: mitja_price_m2 = '%.2f' % (price / float(m2)) # Formateamos tg del precio, m2, media y href
                    except:
                        mitja_price_m2 = ''
                    tb.send_message(tg_chatID, f"<b>{price_str}</b> [{m2_tg}] → {mitja_price_m2}€/m²\n{href}", parse_mode='HTML')
                    logger.debug(f'{href} SENT TO TELEGRAM GROUP')
                    time.sleep(3.05)
                time.sleep(0.10)

    # open file in write mode
    with open("./data/ids.json", "w") as outfile:
        json.dump(ids_file+new_ids_file, outfile)
    outfile.close()
    if len(new_urls) > 0:
        logger.info(
            f"SPIDER FINISHED - [NEW: {len(new_urls)}] [TOTAL: {len(data_json)}]: {new_urls}")
    else:
        logger.debug(
            f"SPIDER FINISHED - [NEW: {len(new_urls)}] [TOTAL: {len(data_json)}]: {new_urls}")

def scrap_realestate(connection, telegram_msg):
    start_time = time.time()

    # Si el nombre del proyecto tiene algún "-", lo cambiamos ya que da problemas con sqlite
    scrapy_rs_name = data['scrapy_rs_name'].replace("-", "_")
    scrapy_log = data['log_level_scrapy'].upper()
    proxy_idealista = data['proxy_idealista']

    urls = []
    for key in data:
        if "url" in key and isinstance(data[key], list):
            urls += data[key]
        elif "url" in key:
            urls.append(data[key])

    # Mezclamos las urls para no repetir la misma spider
    urls_mixed = mix_list(urls)

    # Iteramos las urls que hay y hacemos scrape
    for url in urls_mixed:
        if url == '':
            continue

        portal_url = url.split('/')[2]
        portal_name = portal_url.split('.')[1]
        try:
            portal_name_url = portal_url.split('.')[1] + '.' + portal_url.split('.')[2]
        except:
            portal_name = portal_url
            portal_name_url = ''

        # Validamos que las spiders existen
        command = "scrapy list"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        if process.returncode != 0:
            logger.error("SPIDERS NOT DETECTED")
            sys.exit()

        # Hacemos crawl con la spider dependiendo del portal con la url
        logger.debug(f"SCRAPING PORTAL {portal_name_url} FROM {scrapy_rs_name}...")
        if portal_name_url == 'idealista.com':
            url_last_flats = url + '?ordenado-por=fecha-publicacion-desc'
            if proxy_idealista == 'on':
                logger.debug('IDEALISTA PROXY ACTIVATED')
                os.system(
                    f"scrapy crawl -L {scrapy_log} idealista_proxy -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
            else:
                os.system(
                    f"scrapy crawl -L {scrapy_log} idealista -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
        elif portal_name_url == 'pisos.com':
            url_last_flats = url + '/fecharecientedesde-desc/'
            os.system(
                f"scrapy crawl -L {scrapy_log} pisoscom -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")
        elif portal_name_url == 'fotocasa.es':
            os.system(f"scrapy crawl -L {scrapy_log} fotocasa -o ./data/{scrapy_rs_name}.json -a start_urls={url}")
        elif portal_name_url == 'habitaclia.com':
            url_last_flats = url + '?ordenar=mas_recientes'
            os.system(
                f"scrapy crawl -L {scrapy_log} habitaclia -o ./data/{scrapy_rs_name}.json -a start_urls={url_last_flats}")

        logger.debug(f"CRAWLED {portal_name.upper()}")

    # Arreglar JSON - Unir las diferentes partes o quitar las partes que los unen (][)
    logger.debug(f"EDITING ./data/{scrapy_rs_name}.json...")
    with open(f'./data/{scrapy_rs_name}.json', 'r') as file:
        filedata = file.read()

    # Reemplazar la cadena objetivo
    filedata = filedata.replace('\n][', ',')
    # Escribir el archivo nuevamente
    with open(f'./data/{scrapy_rs_name}.json', 'w') as file:
        file.write(filedata)
        
    # Llamar a la función que comprueba los pisos nuevos y los envía por telegram y guarda en la base de datos
    check_new_flats(f"./data/{scrapy_rs_name}.json",
                    scrapy_rs_name,
                    data['min_price'],
                    data['max_price'],
                    data['telegram_chatuserID'],
                    connection,
                    telegram_msg,
                    logger)

def init():
    global config_db_mysql
    config_db_mysql = {
        'db_user': settings.MYSQL_USER,
        'db_password': settings.MYSQL_PASSWORD,
        'db_host':  settings.MYSQL_HOST,
        'db_name': settings.MYSQL_DATABASE,
    }
    print('LOADING...')
    time.sleep(1)
    print(f'scrapyrealestate v{__version__}')
    tprint("scrapyrealestate")
    print(f'scrapyrealestate v{__version__}')

    time.sleep(0.05)
    get_config()  # Obtener la configuración
    time.sleep(0.05)
    logger = init_logs()  # Iniciar los logs
    time.sleep(0.05)
    connection, info_message = checks()  # Comprobaciones
    time.sleep(0.05)
    count = 0
    telegram_msg = False
    scrapy_rs_name = data['scrapy_rs_name'].replace("-", "_")
    send_first = data['send_first']

    while True:
        try:
            os.remove(f"./data/{scrapy_rs_name}.json")  # Eliminar el archivo json
        except:
            pass

        # Si send_first está activado o hemos pasado al segundo ciclo, cambiamos telegram_msg a true para enviar los mensajes
        if send_first == 'True' or count > 0:
            telegram_msg = True
            logger.debug('TELEGRAM MSG ENABLED')

        # try:
        # Cridem la funció d'scraping
        scrap_realestate(connection, telegram_msg)
        # except:
        #    pass

        count += 1  # Sumar 1 ciclo
        logger.info(f"SLEEPING {data['time_update']} SECONDS")
        time.sleep(int(data['time_update']))

if __name__ == "__main__":
    init()
