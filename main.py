import os
import re
import time
import requests
import shutil
import winreg
import json
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
        "dl_complete": "\nDownload complete! Successfully downloaded {success} out of {total} maps.",
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
        "exit_msg": "Exiting program. Have fun playing!"
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
        "dl_complete": "\nСкачивание завершено! Успешно скачано {success} из {total} карт.",
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
        "exit_msg": "Выход из программы. Приятной игры!"
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
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"osu!\DefaultIcon") as key:
            val, _ = winreg.QueryValueEx(key, "")
            path = val.split('"')[1] if '"' in val else val.split(',')[0]
            osu_dir = os.path.dirname(path)
            songs_dir = os.path.join(osu_dir, "Songs")
            if os.path.exists(songs_dir):
                return songs_dir
    except Exception:
        pass
        
    fallback = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'osu!', 'Songs')
    if os.path.exists(fallback):
        return fallback
    return None

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
            
            downloaded_files = []
            for i, bm_id in enumerate(beatmapset_ids, 1):
                print(_('map_progress', current=i, total=len(beatmapset_ids), id=bm_id))
                filepath = download_beatmap(bm_id, download_dir, active_mirror)
                if filepath:
                    downloaded_files.append(filepath)
                time.sleep(0.5)
                
            print(_('dl_complete', success=len(downloaded_files), total=len(beatmapset_ids)))
            
            if downloaded_files:
                osu_songs_dir = find_osu_songs_folder()
                if osu_songs_dir:
                    print(f"{_('found_osu')} {osu_songs_dir}")
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
                    
                    osu_exe_path = os.path.join(os.path.dirname(osu_songs_dir), "osu!.exe")
                    if os.path.exists(osu_exe_path):
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
