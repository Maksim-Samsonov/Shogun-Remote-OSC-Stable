"""
Модуль настройки логирования для приложения.
Включает кастомный форматтер для цветного отображения логов в QTextEdit.
"""

import logging
import queue
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Union

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QTextCursor

import config

class ColoredFormatter(logging.Formatter):
    """Форматтер логов с цветами для отображения в HTML"""
    COLORS = {
        'DEBUG': 'gray',
        'INFO': 'darkgreen',
        'WARNING': 'darkorange',
        'ERROR': 'red',
        'CRITICAL': 'purple',
    }

    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, 'black')
        return f'<span style="color:{color};">{log_message}</span>'

class QTextEditLogger(logging.Handler):
    """Хендлер логов для вывода в QTextEdit с использованием очереди"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.setFormatter(ColoredFormatter(config.LOG_FORMAT))
        
        # Создаем таймер для обновления интерфейса
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_logs)
        self.update_timer.start(100)  # Обновление каждые 100 мс
        
    def emit(self, record):
        """Добавляет запись лога в очередь"""
        self.queue.put(record)
        
    def update_logs(self):
        """Обновляет текстовый виджет логами из очереди"""
        # Ограничиваем количество обрабатываемых записей за один раз
        # для предотвращения блокировки интерфейса
        max_records_per_update = 10
        records_processed = 0
        
        while not self.queue.empty() and records_processed < max_records_per_update:
            try:
                record = self.queue.get_nowait()
                formatted_message = self.format(record)
                self.text_widget.append(formatted_message)
                self.text_widget.moveCursor(QTextCursor.End)
                records_processed += 1
            except queue.Empty:
                break
            except Exception as e:
                # Логируем ошибку в консоль, так как логгер может быть недоступен
                print(f"Ошибка при обновлении логов: {e}", file=sys.stderr)

def get_log_level(level_name: str) -> int:
    """
    Преобразует строковое представление уровня логирования в константу logging
    
    Args:
        level_name: Имя уровня логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        int: Константа уровня логирования из модуля logging
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return level_map.get(level_name.upper(), logging.INFO)

def setup_logging() -> logging.Logger:
    """
    Настраивает базовое логирование для приложения с использованием настроек из SettingsManager
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Получаем настройки логирования
    settings_manager = config.settings_manager
    log_level_name = settings_manager.get("log_level", "INFO")
    log_to_file = settings_manager.get("log_to_file", True)
    custom_log_dir = settings_manager.get("log_dir", "")
    
    # Преобразуем строковое представление уровня в константу logging
    log_level = get_log_level(log_level_name)
    
    # Настраиваем базовое логирование
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Очищаем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Добавляем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Настройка логирования в файл, если требуется
    if log_to_file:
        try:
            # Определяем директорию для логов
            log_dir = custom_log_dir if custom_log_dir else settings_manager.get_logs_dir()
            
            # Создаем директорию для логов, если не существует
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Создаем файл лога с датой и временем
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"shogun_osc_{timestamp}.log")
            
            # Добавляем обработчик для записи в файл
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
            file_handler.setLevel(log_level)
            root_logger.addHandler(file_handler)
            
            # Логируем информацию о начале логирования в файл
            root_logger.info(f"Логирование в файл включено: {log_file}")
        except Exception as e:
            root_logger.error(f"Не удалось настроить логирование в файл: {e}")
    
    # Настройка логгеров для различных модулей
    loggers = {
        'ShogunOSC': log_level,
        'WebUI': log_level,
        'HyperDeck': log_level,
        'aiohttp': logging.ERROR,  # Внешние библиотеки оставляем на уровне ERROR
    }
    
    for name, level in loggers.items():
        logger = logging.getLogger(name)
        logger.setLevel(level)
    
    # Создаем и возвращаем основной логгер приложения
    app_logger = logging.getLogger('ShogunOSC')
    
    # Добавляем обработчик изменения настроек логирования
    settings_manager.settings_changed.connect(on_log_settings_changed)
    
    return app_logger

def on_log_settings_changed(key: str, value: Any) -> None:
    """
    Обработчик изменения настроек логирования
    
    Args:
        key: Ключ изменённой настройки
        value: Новое значение настройки
    """
    if key in ["log_level", "log_to_file", "log_dir"]:
        # Если изменились настройки логирования, обновляем логгеры
        logger = logging.getLogger('ShogunOSC')
        
        if key == "log_level":
            # Обновляем уровень логирования
            log_level = get_log_level(value)
            logger.setLevel(log_level)
            
            # Обновляем уровень всех обработчиков
            for handler in logger.handlers:
                handler.setLevel(log_level)
            
            logger.info(f"Уровень логирования изменен на {value}")
            
        elif key == "log_to_file" and not value:
            # Отключаем логирование в файл
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    root_logger.removeHandler(handler)
                    handler.close()
            
            logger.info("Логирование в файл отключено")

def add_text_widget_handler(text_widget: QTextEdit, level: Union[str, int] = None) -> QTextEditLogger:
    """
    Добавляет обработчик для вывода логов в текстовый виджет
    
    Args:
        text_widget: Виджет QTextEdit для вывода логов
        level: Уровень логирования (строка или константа из logging)
        
    Returns:
        QTextEditLogger: Созданный обработчик логов
    """
    logger = logging.getLogger('ShogunOSC')
    
    # Определяем уровень логирования
    if level is None:
        # Если уровень не указан, берем из настроек
        level_name = config.settings_manager.get("log_level", "INFO")
        level = get_log_level(level_name)
    elif isinstance(level, str):
        level = get_log_level(level)
    
    # Создаем и настраиваем обработчик
    handler = QTextEditLogger(text_widget)
    handler.setLevel(level)
    logger.addHandler(handler)
    
    return handler

def get_system_info() -> Dict[str, Any]:
    """
    Собирает информацию о системе для диагностики
    
    Returns:
        Dict[str, Any]: Словарь с информацией о системе
    """
    import platform
    
    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "app_version": config.APP_VERSION,
        "os_name": platform.system(),
        "os_version": platform.version()
    }
    
    # Добавляем информацию о PyQt
    try:
        from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
        system_info["qt_version"] = QT_VERSION_STR
        system_info["pyqt_version"] = PYQT_VERSION_STR
    except ImportError:
        system_info["qt_version"] = "unknown"
        system_info["pyqt_version"] = "unknown"
    
    # Добавляем пути к конфигурациям
    system_info["config_dir"] = config.settings_manager.get_config_dir()
    system_info["logs_dir"] = config.settings_manager.get_logs_dir()
    
    return system_info

def log_system_info(logger: logging.Logger) -> None:
    """
    Логирует информацию о системе
    
    Args:
        logger: Логгер для записи информации
    """
    system_info = get_system_info()
    logger.info("=== Информация о системе ===")
    for key, value in system_info.items():
        logger.info(f"{key}: {value}")
    logger.info("===========================")
