import os
import re
import time
import requests
import shutil
import winreg
import json
import zipfile
import hashlib
import struct
import psutil
from urllib.parse import unquote
from tqdm import tqdm

CONFIG_FILE = "config.json"

MIRRORS = [
    {"name": "Nerinyan", "url": "https://api.nerinyan.moe/d/{id}"},
    {"name": "Sayobot", "url": "https://txy1.sayobot.cn/beatmaps/download/full/{id}"},
    {"name": "Mino", "url": "https://catboy.best/d/{id}"}
]

TEXTS = {
    "en": {
        "lang_prompt": "Choose language / Выберите язык (1 = English, 2 = Русский): ",
        "lang_invalid": "Invalid choice. / Неверный выбор.",
        "search_mirror": "\nSearching for the fastest mirror...",
        "loaded_mirror": "\nLoaded saved mirror from config:",
        "mirror_unavail": "Unavailable",
        "mirror_selected": "✅ Selected mirror:",
        "osu_not_found": "❌ Could not automatically find osu! folder on this computer.",
        "files_saved_in": "Downloaded files are located in:",
        "welcome": " Welcome to OsuCollector Downloader! ",
        "menu": "\nMenu:",
        "menu_1": "1. Download collection",
        "menu_2": "2. Find best mirror again",
        "menu_3": "3. Exit",
        "choice": "\nChoose an action (1-3): ",
        "invalid_choice": "Invalid choice. Please enter 1, 2, or 3.",
        "enter_url": "Enter collection link (or just ID): ",
        "invalid_id": "Could not recognize collection ID from the link.",
        "fetching_info": "\nFetching info for collection {id}...",
        "coll_error": "Collection is empty, not found, or an error occurred.",
        "coll_contains": "Collection '{name}' contains {count} beatmaps.",
        "start_dl": "Start downloading? (y/n): ",
        "dl_cancelled": "Download cancelled.",
        "map_progress": "\nMap {current} of {total} (ID: {id}):",
        "map_skipped": "Map {id} is already installed, skipping download.",
        "dl_complete": "\nDownload complete! Successfully downloaded {success} out of {total} maps ({skipped} skipped).",
        "dl_failed": "Failed to download {id} from {mirror}. Code: {code}",
        "dl_error": "Error downloading {id}: {error}",
        "found_osu": "\nFound osu! Songs folder:",
        "moving_files": "Moving files automatically...",
        "move_error": "Error moving {file}: {error}",
        "install_success": "✅ Successfully installed {count} maps!",
        "press_f5": "Now just open osu! and press F5 in song selection menu to load them.",
        "launch_osu": "\nDo you want to launch osu! right now? (y/n): ",
        "launching": "Launching game...",
        "launch_fail": "Failed to launch the game:",
        "exit_msg": "Exiting program. Have fun playing!",
        "ask_collection": "Do you want to automatically create a collection named '{name}' in-game for these maps? (y/n): ",
        "close_osu_warning": "\n⚠️ WARNING: osu! is currently running! Modifying the collection database while the game is open WILL corrupt or overwrite the changes.",
        "close_osu_prompt": "Please close osu! and press Enter to continue...",
        "calc_hashes": "Extracting beatmap hashes for the collection...",
        "collection_created": "✅ Added {count} beatmap difficulties to collection '{name}'!",
        "osu_path_prompt": "\nCould not auto-detect osu! folder. Please enter the full path to your osu! folder (or 'n' to skip): ",
        "osu_path_invalid": "Invalid path or 'Songs' folder not found inside. Try again."
    },
    "ru": {
        "lang_prompt": "Choose language / Выберите язык (1 = English, 2 = Русский): ",
        "lang_invalid": "Invalid choice. / Неверный выбор.",
        "search_mirror": "\nПоиск самого быстрого зеркала для скачивания...",
        "loaded_mirror": "\nЗагружено сохраненное зеркало из конфига:",
        "mirror_unavail": "Недоступно",
        "mirror_selected": "✅ Выбрано зеркало:",
        "osu_not_found": "❌ Не удалось автоматически найти папку osu! на этом компьютере.",
        "files_saved_in": "Скачанные файлы находятся в папке:",
        "welcome": " Добро пожаловать в OsuCollector Downloader! ",
        "menu": "\nМеню:",
        "menu_1": "1. Скачать коллекцию",
        "menu_2": "2. Найти лучшее зеркало заново",
        "menu_3": "3. Выход",
        "choice": "\nВыберите действие (1-3): ",
        "invalid_choice": "Неверный выбор. Пожалуйста, введи 1, 2 или 3.",
        "enter_url": "Введите ссылку на коллекцию (или просто ID): ",
        "invalid_id": "Не удалось распознать ID коллекции из ссылки.",
        "fetching_info": "\nПолучение информации о коллекции {id}...",
        "coll_error": "Коллекция пуста, не найдена или произошла ошибка.",
        "coll_contains": "Коллекция '{name}' содержит {count} карт.",
        "start_dl": "Начать скачивание? (y/n): ",
        "dl_cancelled": "Скачивание отменено.",
        "map_progress": "\nКарта {current} из {total} (ID: {id}):",
        "map_skipped": "Карта {id} уже установлена, пропускаем скачивание.",
        "dl_complete": "\nСкачивание завершено! Успешно скачано {success} из {total} карт (пропущено {skipped}).",
        "dl_failed": "Не удалось скачать {id} с {mirror}. Код: {code}",
        "dl_error": "Ошибка при скачивании {id}: {error}",
        "found_osu": "\nНайдена папка osu! Songs:",
        "moving_files": "Автоматическое перемещение файлов...",
        "move_error": "Ошибка при перемещении {file}: {error}",
        "install_success": "✅ Успешно установлено {count} карт!",
        "press_f5": "Теперь просто зайди в osu! и нажми F5 в меню выбора песен, чтобы игра их подгрузила.",
        "launch_osu": "\nХочешь запустить osu! прямо сейчас? (y/n): ",
        "launching": "Запуск игры...",
        "launch_fail": "Не удалось запустить игру:",
        "exit_msg": "Выход из программы. Приятной игры!",
        "ask_collection": "Хочешь автоматически создать в игре коллекцию '{name}' для этих карт? (y/n): ",
        "close_osu_warning": "\n⚠️ ВНИМАНИЕ: Игра osu! сейчас запущена! Изменение базы данных коллекций при запущенной игре приведет к потере данных.",
        "close_osu_prompt": "Пожалуйста, закрой osu! и нажми Enter, чтобы продолжить...",
        "calc_hashes": "Извлечение хэшей карт для коллекции...",
        "collection_created": "✅ Добавлено {count} сложностей в коллекцию '{name}'!",
        "osu_path_prompt": "\nНе удалось автоматически найти папку osu!. Введите полный путь к папке osu! (или 'n' для отмены): ",
        "osu_path_invalid": "Неверный путь или внутри нет папки 'Songs'. Попробуйте снова."
    }
}

global_lang = "en"

def _(key, **kwargs):
    text = TEXTS[global_lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Config save error: {e}")

def setup_language():
    global global_lang
    config = load_config()
    
    if "language" in config:
        global_lang = config["language"]
        return
        
    while True:
        choice = input(TEXTS["en"]["lang_prompt"]).strip()
        if choice == '1':
            global_lang = "en"
            break
        elif choice == '2':
            global_lang = "ru"
            break
        else:
            print(TEXTS["en"]["lang_invalid"])
            
    config["language"] = global_lang
    save_config(config)

def find_osu_songs_folder():
    config = load_config()
    
    if "osu_path" in config:
        songs_dir = os.path.join(config["osu_path"], "Songs")
        if os.path.exists(songs_dir):
            return songs_dir
            
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"osu!\DefaultIcon") as key:
            val, _ = winreg.QueryValueEx(key, "")
            path = val.split('"')[1] if '"' in val else val.split(',')[0]
            osu_dir = os.path.dirname(path)
            songs_dir = os.path.join(osu_dir, "Songs")
            if os.path.exists(songs_dir):
                config["osu_path"] = osu_dir
                save_config(config)
                return songs_dir
    except Exception:
        pass
        
    fallback = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'osu!')
    songs_fallback = os.path.join(fallback, 'Songs')
    if os.path.exists(songs_fallback):
        config["osu_path"] = fallback
        save_config(config)
        return songs_fallback
        
    while True:
        user_input = input(_('osu_path_prompt')).strip()
        if user_input.lower() == 'n':
            return None
            
        if os.path.basename(user_input).lower() == 'songs':
            songs_dir = user_input
            osu_dir = os.path.dirname(user_input)
        else:
            songs_dir = os.path.join(user_input, "Songs")
            osu_dir = user_input
            
        if os.path.exists(songs_dir):
            config["osu_path"] = osu_dir
            save_config(config)
            return songs_dir
        else:
            print(_('osu_path_invalid'))

def get_installed_beatmapsets(songs_dir):
    installed = {}
    if not songs_dir or not os.path.exists(songs_dir):
        return installed
    try:
        for item in os.listdir(songs_dir):
            full_path = os.path.join(songs_dir, item)
            if os.path.isdir(full_path):
                match = re.match(r'^(\d+)', item)
                if match:
                    installed[match.group(1)] = full_path
    except Exception as e:
        pass
    return installed

def is_osu_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == 'osu!.exe':
            return True
    return False

# ----- OSU DB PARSING LOGIC -----

def read_uleb128(f):
    result = 0
    shift = 0
    while True:
        byte = f.read(1)
        if not byte:
            break
        byte = byte[0]
        result |= (byte & 0x7f) << shift
        if (byte & 0x80) == 0:
            break
        shift += 7
    return result

def write_uleb128(f, value):
    while True:
        byte = value & 0x7f
        value >>= 7
        if value != 0:
            byte |= 0x80
        f.write(bytes([byte]))
        if value == 0:
            break

def read_osu_string(f):
    b = f.read(1)
    if not b or b[0] == 0x00:
        return ""
    if b[0] == 0x0b:
        length = read_uleb128(f)
        return f.read(length).decode('utf-8')
    return ""

def write_osu_string(f, s):
    if not s:
        f.write(b'\x00')
    else:
        f.write(b'\x0b')
        encoded = s.encode('utf-8')
        write_uleb128(f, len(encoded))
        f.write(encoded)

def get_osz_md5s(filepath):
    md5s = []
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            for info in z.infolist():
                if info.filename.lower().endswith('.osu'):
                    content = z.read(info)
                    md5 = hashlib.md5(content).hexdigest()
                    md5s.append(md5)
    except Exception as e:
        pass
    return md5s

def get_local_folder_md5s(folder_path):
    md5s = []
    try:
        for f in os.listdir(folder_path):
            if f.lower().endswith('.osu'):
                with open(os.path.join(folder_path, f), 'rb') as file:
                    md5 = hashlib.md5(file.read()).hexdigest()
                    md5s.append(md5)
    except Exception:
        pass
    return md5s

def update_collection_db(db_path, collection_name, new_md5s):
    if not os.path.exists(db_path):
        with open(db_path, 'wb') as f:
            f.write(struct.pack('<I', 20240101))
            f.write(struct.pack('<I', 1))
            write_osu_string(f, collection_name)
            f.write(struct.pack('<I', len(new_md5s)))
            for md5 in new_md5s:
                write_osu_string(f, md5)
        return

    with open(db_path, 'rb') as f:
        version = struct.unpack('<I', f.read(4))[0]
        num_collections = struct.unpack('<I', f.read(4))[0]
        
        collections = {}
        for _ in range(num_collections):
            name = read_osu_string(f)
            num_maps = struct.unpack('<I', f.read(4))[0]
            maps = []
            for _ in range(num_maps):
                maps.append(read_osu_string(f))
            collections[name] = maps

    if collection_name in collections:
        existing = set(collections[collection_name])
        for m in new_md5s:
            if m not in existing:
                collections[collection_name].append(m)
    else:
        collections[collection_name] = new_md5s

    temp_path = db_path + ".tmp"
    with open(temp_path, 'wb') as f:
        f.write(struct.pack('<I', version))
        f.write(struct.pack('<I', len(collections)))
        for name, maps in collections.items():
            write_osu_string(f, name)
            f.write(struct.pack('<I', len(maps)))
            for md5 in maps:
                write_osu_string(f, md5)
    
    if os.path.exists(db_path + ".bak"):
        os.remove(db_path + ".bak")
    shutil.copy2(db_path, db_path + ".bak")
    shutil.move(temp_path, db_path)

# --------------------------------

def get_best_mirror(force_scan=False):
    config = load_config()
    
    if not force_scan and "best_mirror" in config:
        saved_mirror_name = config["best_mirror"]
        for m in MIRRORS:
            if m["name"] == saved_mirror_name:
                print(f"{_('loaded_mirror')} {saved_mirror_name}")
                return m

    print(_('search_mirror'))
    best_mirror = MIRRORS[0]
    best_time = float('inf')
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for mirror in MIRRORS:
        test_url = mirror["url"].format(id="1")
        latency = float('inf')
        
        for attempt in range(2):
            try:
                start_time = time.time()
                resp = requests.head(test_url, timeout=5, headers=headers)
                current_latency = time.time() - start_time
                resp.close()
                
                if resp.status_code in (200, 301, 302, 403, 404): 
                    latency = current_latency
                    break
            except Exception:
                time.sleep(0.5)
                
        if latency != float('inf'):
            print(f" - {mirror['name']}: {latency:.2f} s")
            if latency < best_time:
                best_time = latency
                best_mirror = mirror
        else:
            print(f" - {mirror['name']}: {_('mirror_unavail')}")
            
    print(f"{_('mirror_selected')} {best_mirror['name']}")
    
    config["best_mirror"] = best_mirror["name"]
    save_config(config)
    return best_mirror

def extract_collection_id(url):
    match = re.search(r'(?:collections/)?(\d+)', url)
    if match:
        return match.group(1)
    return None

def get_collection_beatmaps(collection_id):
    api_url = f"https://osucollector.com/api/collections/{collection_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        beatmapsets = data.get('beatmapsets', [])
        return [bm['id'] for bm in beatmapsets], data.get('name', 'Unknown Collection')
    except Exception as e:
        print(f"API Error: {e}")
        return [], ""

def download_beatmap(beatmapset_id, download_dir, mirror):
    url = mirror["url"].format(id=beatmapset_id)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, stream=True, headers=headers)
        if response.status_code == 200:
            content_disposition = response.headers.get('content-disposition', '')
            filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename_match:
                filename = unquote(filename_match.group(1))
            else:
                filename = f"{beatmapset_id}.osz"
                
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filepath = os.path.join(download_dir, filename)
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f, tqdm(
                desc=filename[:30] + ("..." if len(filename) > 30 else ""),
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
                bar_format="{desc:<32} |{bar:40}| {percentage:3.0f}% [{n_fmt}/{total_fmt}, {rate_fmt}]",
                ascii=" -#"
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    bar.update(size)
                    
            return filepath
        else:
            print(_('dl_failed', id=beatmapset_id, mirror=mirror['name'], code=response.status_code))
            return None
    except Exception as e:
        print(_('dl_error', id=beatmapset_id, error=str(e)))
        return None

def main():
    setup_language()
    
    download_dir = "downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    print("=" * 50)
    print(_('welcome'))
    print("=" * 50)
    
    active_mirror = get_best_mirror()

    while True:
        print(_('menu'))
        print(_('menu_1'))
        print(_('menu_2'))
        print(_('menu_3'))
        
        choice = input(_('choice')).strip()
        
        if choice == '1':
            url = input(_('enter_url')).strip()
            if not url:
                continue
                
            collection_id = extract_collection_id(url)
            if not collection_id:
                print(_('invalid_id'))
                continue
                
            print(_('fetching_info', id=collection_id))
            beatmapset_ids, coll_name = get_collection_beatmaps(collection_id)
            
            if not beatmapset_ids:
                print(_('coll_error'))
                continue
                
            print(_('coll_contains', name=coll_name, count=len(beatmapset_ids)))
            confirm = input(_('start_dl')).strip().lower()
            if confirm != 'y':
                print(_('dl_cancelled'))
                continue
            
            osu_songs_dir = find_osu_songs_folder()
            installed_sets = get_installed_beatmapsets(osu_songs_dir)
            
            downloaded_files = []
            skipped_sets = []
            
            for i, bm_id in enumerate(beatmapset_ids, 1):
                bm_id_str = str(bm_id)
                print(_('map_progress', current=i, total=len(beatmapset_ids), id=bm_id_str))
                
                if bm_id_str in installed_sets:
                    print(_('map_skipped', id=bm_id_str))
                    skipped_sets.append((bm_id_str, installed_sets[bm_id_str]))
                    continue
                
                filepath = download_beatmap(bm_id, download_dir, active_mirror)
                if filepath:
                    downloaded_files.append(filepath)
                time.sleep(0.5)
                
            print(_('dl_complete', success=len(downloaded_files), total=len(beatmapset_ids), skipped=len(skipped_sets)))
            
            if downloaded_files or skipped_sets:
                if osu_songs_dir:
                    print(f"{_('found_osu')} {osu_songs_dir}")
                    osu_dir = os.path.dirname(osu_songs_dir)
                    osu_exe_path = os.path.join(osu_dir, "osu!.exe")
                    
                    create_coll = input(_('ask_collection', name=coll_name)).strip().lower()
                    if create_coll == 'y':
                        if is_osu_running():
                            print(_('close_osu_warning'))
                            while is_osu_running():
                                input(_('close_osu_prompt'))
                        
                        print(_('calc_hashes'))
                        all_md5s = []
                        
                        for fpath in downloaded_files:
                            all_md5s.extend(get_osz_md5s(fpath))
                            
                        for _, folder_path in skipped_sets:
                            all_md5s.extend(get_local_folder_md5s(folder_path))
                            
                        db_path = os.path.join(osu_dir, "collection.db")
                        update_collection_db(db_path, coll_name, all_md5s)
                        print(_('collection_created', count=len(all_md5s), name=coll_name))

                    if downloaded_files:
                        print(_('moving_files'))
                        moved_count = 0
                        for file in downloaded_files:
                            try:
                                filename = os.path.basename(file)
                                target_path = os.path.join(osu_songs_dir, filename)
                                if os.path.exists(target_path):
                                    os.remove(target_path)
                                shutil.move(file, target_path)
                                moved_count += 1
                            except Exception as e:
                                print(_('move_error', file=file, error=str(e)))
                        print(_('install_success', count=moved_count))
                    
                    print(_('press_f5'))
                    
                    if os.path.exists(osu_exe_path) and not is_osu_running():
                        launch_choice = input(_('launch_osu')).strip().lower()
                        if launch_choice == 'y':
                            print(_('launching'))
                            try:
                                os.startfile(osu_exe_path)
                            except Exception as e:
                                print(f"{_('launch_fail')} {e}")
                else:
                    print(_('osu_not_found'))
                    print(f"{_('files_saved_in')} {os.path.abspath(download_dir)}")
                        
        elif choice == '2':
            active_mirror = get_best_mirror(force_scan=True)
        elif choice == '3':
            print(_('exit_msg'))
            break
        else:
            print(_('invalid_choice'))

if __name__ == "__main__":
    main()
