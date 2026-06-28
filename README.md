# OsuCollector Downloader 🎵

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Read this in other languages: [English](#english), [Русский](#русский).*

---

## English

A fast and interactive CLI tool to automatically download and install beatmap collections from [OsuCollector.com](https://osucollector.com/) bypassing login walls and rate limits. 

### ✨ Features
- **Bypass osu! limits:** Downloads directly from fast, unauthenticated mirrors (Nerinyan, Sayobot, Mino).
- **Auto-Mirror Selection:** Pings all available mirrors at startup to automatically pick the fastest one for your region.
- **Instant Installation:** Automatically detects your `osu!\Songs` folder (via Windows Registry) and moves all downloaded `.osz` files there.

### 🚀 Usage (Standalone Executable)
> ⚠️ **Note:** We recommend placing the `.exe` inside its own folder (e.g. `C:\Games\OsuDownloader`) rather than directly on the Desktop. When the program runs, it generates a `config.json` file and a temporary `downloads` directory.

For users without a Python environment, pre-compiled executables are available on the [Releases](../../releases) page. Download `OsuCollectorDownloader.exe` and execute it directly.

### 💻 Running from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/Cyr3ss/osu_collector_beatmap_downloader.git
   cd osu_collector_beatmap_downloader
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python main.py
   ```

### 🛠️ Building from source
Execute the included `build.bat` file. This script installs `pyinstaller` and compiles the code into a standalone executable file located in the `dist/` directory.

---

## Русский

Быстрая интерактивная утилита для автоматического скачивания и установки коллекций карт с [OsuCollector.com](https://osucollector.com/) в обход авторизации и лимитов официального сайта.

### ✨ Особенности
- **Отсутствие лимитов:** Скачивание карт происходит через сторонние зеркала (Nerinyan, Sayobot, Mino), что не требует авторизации в учетной записи.
- **Автоматический выбор зеркала:** При инициализации программа проверяет доступные серверы и выбирает оптимальный узел с наименьшей задержкой для вашего региона.
- **Автоматическая установка:** Утилита определяет директорию `osu!\Songs` через системный реестр Windows и перемещает туда загруженные файлы формата `.osz`.

### 🚀 Использование (Исполняемый файл)
> ⚠️ **Примечание:** Рекомендуется размещать `.exe` файл в выделенной директории (например, `C:\Games\OsuDownloader`), чтобы избежать захламления рабочего стола конфигурационным файлом `config.json` и директорией `downloads`.

Для использования программы без установки Python-окружения, перейдите в раздел [Releases](../../releases), загрузите файл `OsuCollectorDownloader.exe` и запустите его.

### 💻 Запуск из исходного кода
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/Cyr3ss/osu_collector_beatmap_downloader.git
   cd osu_collector_beatmap_downloader
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите скрипт:
   ```bash
   python main.py
   ```

### 🛠️ Компиляция проекта
Запустите скрипт `build.bat`. Данный скрипт автоматически установит зависимости и скомпилирует проект в исполняемый файл, который будет сохранен в директории `dist/`.
