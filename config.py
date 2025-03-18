"""
Файл с конфигурационными параметрами, менеджером настроек и проверкой зависимостей.
"""

import os
import sys
import logging
import platform
from typing import Dict, Any, Optional, Union, Set
from PyQt5.QtCore import QSettings, QObject, pyqtSignal

# Проверка зависимостей
IMPORT_SUCCESS = True
IMPORT_ERROR = ""

try:
    # Библиотеки для Shogun Live
    from vicon_core_api import Client
    from shogun_live_api import CaptureServices
    
    # Библиотеки для OSC
    from pythonosc import dispatcher, osc_server
except ImportError as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)

class SettingsManager(QObject):
    """
    Класс для управления настройками приложения.
    Использует QSettings для хранения настроек в соответствии с ОС.
    """
    # Сигнал изменения настроек (ключ, значение)
    settings_changed = pyqtSignal(str, object)
    
    # Настройки приложения по умолчанию
    DEFAULT_SETTINGS = {
        "dark_mode": False,
        "osc_ip": "0.0.0.0",
        "osc_port": 5555,
        "osc_enabled": True,
        "osc_broadcast_port": 9000,  # Порт для отправки OSC-сообщений
        "osc_broadcast_ip": "255.255.255.255",  # IP для отправки OSC-сообщений (широковещательный)
        "log_level": "INFO",
        "log_to_file": True,
        "log_dir": "",  # Пустая строка означает использование стандартной директории для логов
    }
    
    # Типы значений для правильного преобразования
    VALUE_TYPES = {
        "dark_mode": bool,
        "osc_enabled": bool,
        "log_to_file": bool,
        "osc_port": int,
        "osc_broadcast_port": int,
    }
    
    def __init__(self):
        """Инициализация менеджера настроек"""
        super().__init__()
        self.logger = logging.getLogger('ShogunOSC')
        
        # Создаем хранилище настроек с учетом платформы
        self.settings = QSettings("ShogunOSC", "ShogunOSCApp")
        
        # Загружаем настройки
        self.settings_cache = {}
        self.load_settings()
        
    def get_config_dir(self) -> str:
        """
        Возвращает директорию конфигурации с учетом ОС
        
        Returns:
            str: Путь к директории конфигурации
        """
        if platform.system() == "Windows":
            # Для Windows используем %APPDATA%\ShogunOSC
            base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
            return os.path.join(base_dir, "ShogunOSC")
        elif platform.system() == "Darwin":
            # Для macOS используем ~/Library/Application Support/ShogunOSC
            return os.path.expanduser("~/Library/Application Support/ShogunOSC")
        else:
            # Для Linux и других систем используем ~/.config/shogun_osc
            return os.path.expanduser("~/.config/shogun_osc")
    
    def get_logs_dir(self) -> str:
        """
        Возвращает директорию для хранения логов с учетом ОС
        
        Returns:
            str: Путь к директории логов
        """
        # Если указана пользовательская директория для логов, используем её
        custom_log_dir = self.get("log_dir")
        if custom_log_dir:
            return custom_log_dir
            
        # Иначе используем стандартную директорию в зависимости от ОС
        config_dir = self.get_config_dir()
        return os.path.join(config_dir, "logs")
    
    def _create_dirs(self) -> None:
        """Создает необходимые директории для конфигурации и логов"""
        dirs_to_create = [self.get_config_dir(), self.get_logs_dir()]
        
        for directory in dirs_to_create:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    self.logger.debug(f"Создана директория: {directory}")
                except OSError as e:
                    self.logger.error(f"Не удалось создать директорию {directory}: {e}")
    
    def load_settings(self) -> None:
        """Загружает настройки из QSettings и обновляет кэш"""
        # Создаем необходимые директории
        self._create_dirs()
        
        # Загружаем настройки по умолчанию в кэш
        self.settings_cache = self.DEFAULT_SETTINGS.copy()
        
        # Обновляем кэш значениями из QSettings
        for key in self.DEFAULT_SETTINGS.keys():
            if self.settings.contains(key):
                value = self.settings.value(key)
                # Преобразуем значение к правильному типу
                self.settings_cache[key] = self._convert_value(key, value)
    
    def _convert_value(self, key: str, value: Any) -> Any:
        """
        Преобразует значение к правильному типу
        
        Args:
            key: Ключ настройки
            value: Значение для преобразования
            
        Returns:
            Any: Преобразованное значение
        """
        # Если ключ есть в VALUE_TYPES, преобразуем значение
        if key in self.VALUE_TYPES:
            target_type = self.VALUE_TYPES[key]
            
            # Преобразование к bool
            if target_type is bool:
                if isinstance(value, str):
                    return value.lower() in ['true', '1', 'yes', 'y', 'on']
                return bool(value)
                
            # Преобразование к int
            elif target_type is int:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    self.logger.warning(f"Не удалось преобразовать значение '{value}' к типу int для ключа '{key}'")
                    return self.DEFAULT_SETTINGS.get(key, 0)
        
        # Если тип не указан, возвращаем значение как есть
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение настройки
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию, если настройка не найдена
            
        Returns:
            Any: Значение настройки
        """
        return self.settings_cache.get(key, default if default is not None else self.DEFAULT_SETTINGS.get(key))
    
    def set(self, key: str, value: Any) -> None:
        """
        Устанавливает значение настройки
        
        Args:
            key: Ключ настройки
            value: Значение для установки
        """
        # Преобразуем значение к правильному типу
        value = self._convert_value(key, value)
        
        # Проверяем, изменилось ли значение
        if key in self.settings_cache and self.settings_cache[key] == value:
            return
        
        # Обновляем кэш и сохраняем в QSettings
        self.settings_cache[key] = value
        self.settings.setValue(key, value)
        
        # Принудительная синхронизация QSettings
        self.settings.sync()
        
        # Уведомляем об изменении
        self.settings_changed.emit(key, value)
        self.logger.debug(f"Настройка изменена: {key} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Получает все настройки
        
        Returns:
            Dict[str, Any]: Словарь со всеми настройками
        """
        return self.settings_cache.copy()
    
    def set_many(self, settings_dict: Dict[str, Any]) -> None:
        """
        Устанавливает несколько настроек одновременно
        
        Args:
            settings_dict: Словарь с настройками для установки
        """
        changes = False
        for key, value in settings_dict.items():
            # Преобразуем значение к правильному типу
            value = self._convert_value(key, value)
            
            # Проверяем, изменилось ли значение
            if key not in self.settings_cache or self.settings_cache[key] != value:
                self.settings_cache[key] = value
                self.settings.setValue(key, value)
                changes = True
                # Уведомляем об изменении
                self.settings_changed.emit(key, value)
        
        # Синхронизируем QSettings только если были изменения
        if changes:
            self.settings.sync()
            self.logger.debug("Обновлено несколько настроек")
    
    def reset(self, keys: Optional[Set[str]] = None) -> None:
        """
        Сбрасывает настройки к значениям по умолчанию
        
        Args:
            keys: Набор ключей для сброса. Если None, сбрасывает все настройки.
        """
        reset_dict = {}
        
        if keys is None:
            # Сбрасываем все настройки
            reset_dict = self.DEFAULT_SETTINGS.copy()
        else:
            # Сбрасываем только указанные настройки
            for key in keys:
                if key in self.DEFAULT_SETTINGS:
                    reset_dict[key] = self.DEFAULT_SETTINGS[key]
        
        # Применяем сброс
        self.set_many(reset_dict)
        self.logger.debug(f"Настройки сброшены: {list(reset_dict.keys())}")


# Создаем экземпляр менеджера настроек
settings_manager = SettingsManager()

# Константы, которые будут использоваться в других модулях
# Настройки OSC-сервера
DEFAULT_OSC_IP = settings_manager.get("osc_ip")
DEFAULT_OSC_PORT = settings_manager.get("osc_port")
DEFAULT_OSC_BROADCAST_IP = settings_manager.get("osc_broadcast_ip")
DEFAULT_OSC_BROADCAST_PORT = settings_manager.get("osc_broadcast_port")

# Флаг темной темы
DARK_MODE = settings_manager.get("dark_mode")

# OSC-адреса для управления Shogun Live
OSC_START_RECORDING = "/RecordStartShogunLive"
OSC_STOP_RECORDING = "/RecordStopShogunLive"
OSC_CAPTURE_NAME_CHANGED = "/ShogunLiveCaptureName"  # Адрес для уведомления об изменении имени захвата
OSC_DESCRIPTION_CHANGED = "/ShogunLiveDescription"  # Адрес для уведомления об изменении описания захвата
OSC_CAPTURE_FOLDER_CHANGED = "/ShogunLiveCaptureFolder"  # Адрес для уведомления об изменении пути к папке захвата
OSC_SET_CAPTURE_FOLDER = "/SetCaptureFolder"  # Адрес для установки пути к папке захвата

# Настройки логирования
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
LOG_MAX_LINES = 1000

# Настройки для проверки соединения с Shogun Live
MAX_RECONNECT_ATTEMPTS = 10
BASE_RECONNECT_DELAY = 1
MAX_RECONNECT_DELAY = 15

# Названия статусов для понятного отображения
STATUS_CONNECTED = "Подключено"
STATUS_DISCONNECTED = "Отключено"
STATUS_RECORDING_ACTIVE = "Активна"
STATUS_RECORDING_INACTIVE = "Не активна"

# Версия приложения
APP_VERSION = "1.0.1"

def get_app_version() -> str:
    """
    Возвращает текущую версию приложения
    
    Returns:
        str: Версия приложения
    """
    return APP_VERSION

# Для совместимости с существующим кодом
app_settings = settings_manager.get_all()
save_settings = settings_manager.set_many
