"""
Модуль для взаимодействия с Shogun Live API.
Содержит основной рабочий класс для подключения и управления Shogun Live.
"""

import asyncio
import logging
import time
from typing import Optional, Any, Dict, Tuple
from datetime import datetime

from PyQt5.QtCore import QThread, pyqtSignal

# Импорт необходимых API
from vicon_core_api import Client as ViconClient
from vicon_core_api.result import Result
from shogun_live_api import CaptureServices

import config

class ShogunWorker(QThread):
    """
    Рабочий поток для взаимодействия с Shogun Live API.
    Обеспечивает асинхронное взаимодействие с API и сигнализирует об изменениях.
    """
    # Сигналы для обновления UI
    connection_signal = pyqtSignal(bool)
    connection_error_signal = pyqtSignal(bool)
    recording_signal = pyqtSignal(bool)
    capture_name_changed_signal = pyqtSignal(str)
    description_changed_signal = pyqtSignal(str)
    description_signal = pyqtSignal(str)
    capture_folder_changed_signal = pyqtSignal(str)  # Новый сигнал для изменения папки захвата

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('ShogunOSC')
        self.running = True
        
        # Состояние подключения и записи
        self.connected = False
        self.recording = False
        self.client = None
        self.capture_service = None
        
        # Информация о текущем захвате
        self.current_capture_name = "Нет данных"
        self.current_description = "Нет данных"
        self.current_capture_folder = "Нет данных"  # Текущий путь к папке захвата
        
        # Счетчик попыток подключения
        self.reconnect_attempts = 0
        
        self.logger.info("ShogunWorker инициализирован")

    def run(self):
        """Основной метод потока. Запускает периодическую проверку состояния."""
        self.logger.info("ShogunWorker запущен")
        
        # Попытка первоначального подключения
        asyncio.run(self.connect_shogun())
        
        # Основной цикл работы
        while self.running:
            try:
                if self.connected:
                    # Проверяем состояние подключения и записи
                    asyncio.run(self.check_status())
                else:
                    # Пытаемся переподключиться с нарастающей задержкой
                    if self.reconnect_attempts < config.MAX_RECONNECT_ATTEMPTS:
                        delay = min(
                            config.BASE_RECONNECT_DELAY * (2 ** self.reconnect_attempts), 
                            config.MAX_RECONNECT_DELAY
                        )
                        self.logger.info(f"Попытка переподключения через {delay} сек (попытка {self.reconnect_attempts + 1})")
                        time.sleep(delay)
                        self.reconnect_attempts += 1
                        asyncio.run(self.connect_shogun())
                    else:
                        # Превышено максимальное количество попыток
                        self.logger.warning("Превышено максимальное количество попыток подключения")
                        time.sleep(5)  # Ждем 5 секунд перед следующей серией попыток
                        self.reconnect_attempts = 0
                        
            except Exception as e:
                self.logger.error(f"Ошибка в рабочем цикле ShogunWorker: {e}")
                # При ошибке помечаем как отключено
                self.connected = False
                self.connection_signal.emit(False)
                self.connection_error_signal.emit(True)
                time.sleep(2)  # Задержка перед следующей итерацией при ошибке
                
            # Задержка между итерациями проверки
            time.sleep(1)
            
        self.logger.info("ShogunWorker остановлен")
        
    def check_api_result(self, result: Tuple) -> Tuple[bool, Any]:
        """
        Проверяет результат вызова API и возвращает статус успеха и данные.
        
        Args:
            result: Результат вызова API
            
        Returns:
            Tuple[bool, Any]: Кортеж (успех, данные)
        """
        if result is None:
            return False, None
        
        # В Vicon Core API результат обычно возвращается как кортеж,
        # где первый элемент - это объект Result, а остальные - данные
        if isinstance(result, tuple) and len(result) > 0:
            if isinstance(result[0], Result):
                # Проверяем, что результат успешный (Result.__bool__ определен в API)
                if result[0]:
                    # Возвращаем данные (остальную часть кортежа)
                    return True, result[1:] if len(result) > 1 else None
                else:
                    # Результат содержит ошибку, определяем уровень логирования
                    # NotAvailable - это нормальный код ошибки, когда нет активных записей
                    if str(result[0]) == "NotAvailable: The information requested was not available":
                        self.logger.debug(f"API: {result[0]}")
                    else:
                        self.logger.error(f"API вернул ошибку: {result[0]}")
                    return False, None
        
        # Если формат ответа не соответствует ожидаемому
        self.logger.warning(f"Неожиданный формат ответа API: {result}")
        return False, None

    async def connect_shogun(self) -> bool:
        """
        Подключение к Shogun Live API.
        
        Returns:
            bool: True если подключение успешно, иначе False
        """
        try:
            # Создаем клиент для подключения к Shogun Live
            self.logger.info("Подключение к Shogun Live...")
            
            # В Vicon Core API класс Client выполняет автоматическое подключение при создании
            self.client = ViconClient()
            
            # Проверяем версию сервера для подтверждения подключения
            version = self.client.server_version()
            if version:
                self.logger.info(f"Подключено к Vicon API версии {version}")
                
                # Создаем сервис захвата
                self.capture_service = CaptureServices(self.client)
                
                # Обновляем состояние
                self.connected = True
                self.reconnect_attempts = 0  # Сбрасываем счетчик попыток
                self.connection_signal.emit(True)
                self.connection_error_signal.emit(False)
                
                # Получаем и обновляем начальное состояние
                await self.update_state()
                
                self.logger.info("Успешно подключено к Shogun Live")
                return True
            else:
                self.logger.error("Не удалось получить версию сервера")
                self.connected = False
                self.connection_signal.emit(False)
                self.connection_error_signal.emit(True)
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при подключении к Shogun Live: {e}")
            self.connected = False
            self.connection_signal.emit(False)
            self.connection_error_signal.emit(True)
            return False

    async def reconnect_shogun(self) -> bool:
        """
        Переподключение к Shogun Live API.
        
        Returns:
            bool: True если переподключение успешно, иначе False
        """
        # Сначала отключаемся, если были подключены
        if self.client:
            # В Vicon Core API нет явного метода disconnect
            self.client = None
            self.capture_service = None
            
        self.connected = False
        self.connection_signal.emit(False)
        
        # Сбрасываем счетчик попыток для немедленного переподключения
        self.reconnect_attempts = 0
        
        # Повторно подключаемся
        return await self.connect_shogun()

    async def check_status(self):
        """Проверка текущего состояния подключения и записи."""
        try:
            if not self.client or not self.capture_service:
                self.logger.error("Клиент или сервис захвата не инициализированы")
                self.connected = False
                self.connection_signal.emit(False)
                self.connection_error_signal.emit(True)
                return
            
            # Проверяем, что соединение еще активно
            is_connected = False
            try:
                # Пробуем получить версию сервера
                version = self.client.server_version()
                
                # Если версия получена, попробуем выполнить простую команду
                # для проверки реального соединения
                if version is not None:
                    # Используем простой запрос к API, который не выбрасывает исключений
                    # даже если API недоступен
                    ping_response = self.capture_service.capture_name()
                    success, _ = self.check_api_result(ping_response)
                    is_connected = success
                
            except Exception as conn_error:
                self.logger.debug(f"Ошибка при проверке соединения: {conn_error}")
                is_connected = False
            
            # Проверяем изменение состояния соединения
            if is_connected != self.connected:
                self.connected = is_connected
                self.connection_signal.emit(is_connected)
                self.connection_error_signal.emit(not is_connected)
                
                if is_connected:
                    self.logger.info("Соединение с Shogun Live установлено")
                else:
                    self.logger.warning("Соединение с Shogun Live потеряно")
                    # Сбрасываем состояние записи, т.к. соединение потеряно
                    if self.recording:
                        self.recording = False
                        self.recording_signal.emit(False)
            
            # Обновляем информацию о состоянии только если соединение активно
            if self.connected:
                await self.update_state()
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке статуса: {e}")
            self.connected = False
            self.connection_signal.emit(False)
            self.connection_error_signal.emit(True)

    async def update_state(self):
        """Обновление текущего состояния захвата и записи."""
        try:
            if not self.capture_service or not self.connected:
                return
                
            # Проверяем состояние записи
            try:
                # Получаем текущее состояние записи
                latest_state_response = self.capture_service.latest_capture_state()
                success, data = self.check_api_result(latest_state_response)
                
                if success and data and len(data) >= 2:
                    # Данные содержат id и state
                    capture_id, state = data[0], data[1]
                    
                    # Проверяем состояние записи по state
                    # EStarted = 2 означает активную запись
                    is_recording = (state == CaptureServices.EState.EStarted.value)
                    
                    # Если состояние изменилось, сигнализируем об этом
                    if is_recording != self.recording:
                        self.recording = is_recording
                        self.recording_signal.emit(is_recording)
                        
                        if is_recording:
                            self.logger.info("Запись активна")
                        else:
                            self.logger.info("Запись неактивна")
                else:
                    # Если не удалось получить состояние или нет активных записей
                    if self.recording:
                        self.recording = False
                        self.recording_signal.emit(False)
                        self.logger.info("Запись неактивна")
            except Exception as e:
                # Перехватываем ошибку обращения к API на случай, если соединение потеряно
                # во время выполнения запроса
                if "RPCNotConnected" in str(e):
                    self.connected = False
                    self.connection_signal.emit(False)
                    self.connection_error_signal.emit(True)
                    self.logger.warning(f"Соединение с Shogun Live потеряно при проверке состояния записи")
                    return
                else:
                    self.logger.debug(f"Не удалось получить состояние записи: {e}")
            
            # Получаем имя захвата
            try:
                capture_name_response = self.capture_service.capture_name()
                success, data = self.check_api_result(capture_name_response)
                
                if success and data and len(data) > 0:
                    new_capture_name = data[0]
                    if new_capture_name != self.current_capture_name:
                        self.current_capture_name = new_capture_name
                        self.capture_name_changed_signal.emit(new_capture_name)
            except Exception as e:
                if "RPCNotConnected" in str(e):
                    self.connected = False
                    self.connection_signal.emit(False)
                    self.connection_error_signal.emit(True)
                    self.logger.warning(f"Соединение с Shogun Live потеряно при получении имени захвата")
                    return
                else:
                    self.logger.debug(f"Не удалось получить имя захвата: {e}")
            
            # Получаем описание захвата
            try:
                description_response = self.capture_service.capture_description()
                success, data = self.check_api_result(description_response)
                
                if success and data and len(data) > 0:
                    new_description = data[0]
                    if new_description != self.current_description:
                        self.current_description = new_description
                        self.description_changed_signal.emit(new_description)
            except Exception as e:
                if "RPCNotConnected" in str(e):
                    self.connected = False
                    self.connection_signal.emit(False)
                    self.connection_error_signal.emit(True)
                    self.logger.warning(f"Соединение с Shogun Live потеряно при получении описания захвата")
                    return
                else:
                    self.logger.debug(f"Не удалось получить описание захвата: {e}")
            
            # Получаем путь к папке захвата
            try:
                capture_folder_response = self.capture_service.capture_folder()
                success, data = self.check_api_result(capture_folder_response)
                
                if success and data and len(data) > 0:
                    new_capture_folder = data[0]
                    if new_capture_folder != self.current_capture_folder:
                        self.current_capture_folder = new_capture_folder
                        self.capture_folder_changed_signal.emit(new_capture_folder)
                        self.logger.info(f"Путь к папке захвата изменился: '{new_capture_folder}'")
            except Exception as e:
                if "RPCNotConnected" in str(e):
                    self.connected = False
                    self.connection_signal.emit(False)
                    self.connection_error_signal.emit(True)
                    self.logger.warning(f"Соединение с Shogun Live потеряно при получении пути к папке захвата")
                    return
                else:
                    self.logger.debug(f"Не удалось получить путь к папке захвата: {e}")
        
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении состояния: {e}")

    async def startcapture(self) -> bool:
        """
        Запуск записи в Shogun Live.
        
        Returns:
            bool: True если запись успешно запущена, иначе False
        """
        if not self.connected or not self.capture_service:
            self.logger.warning("Не удалось запустить запись: нет подключения")
            return False
            
        try:
            self.logger.info("Запуск записи...")
            
            # Запускаем запись используя метод API start_capture
            response = self.capture_service.start_capture()
            success, data = self.check_api_result(response)
            
            if success:
                capture_id = data[0] if data and len(data) > 0 else "неизвестно"
                self.logger.info(f"Запись успешно запущена (ID: {capture_id})")
                # Запись запущена, обновим состояние при следующей проверке
                self.recording = True
                self.recording_signal.emit(True)
                return True
            else:
                self.logger.error("Не удалось запустить запись: API вернул ошибку")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при запуске записи: {e}")
            return False

    async def stopcapture(self) -> bool:
        """
        Остановка записи в Shogun Live.
        
        Returns:
            bool: True если запись успешно остановлена, иначе False
        """
        if not self.connected or not self.capture_service:
            self.logger.warning("Не удалось остановить запись: нет подключения")
            return False
            
        try:
            self.logger.info("Остановка записи...")
            
            # Останавливаем запись используя метод API stop_capture с идентификатором 0
            # согласно документации в capture_services.py, id=0 останавливает любую активную запись
            response = self.capture_service.stop_capture(0)
            success, _ = self.check_api_result(response)
            
            if success:
                self.logger.info("Запись успешно остановлена")
                # Запись остановлена, обновим состояние
                self.recording = False
                self.recording_signal.emit(False)
                return True
            else:
                self.logger.error("Не удалось остановить запись: API вернул ошибку")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при остановке записи: {e}")
            return False

    async def set_capture_name(self, name: str) -> bool:
        """
        Установка имени захвата в Shogun Live.
        
        Args:
            name: Новое имя захвата
            
        Returns:
            bool: True если имя успешно установлено, иначе False
        """
        if not self.connected or not self.capture_service:
            self.logger.warning("Не удалось установить имя захвата: нет подключения")
            return False
            
        try:
            self.logger.info(f"Установка имени захвата: {name}")
            
            # Устанавливаем имя захвата используя метод API set_capture_name
            response = self.capture_service.set_capture_name(name)
            success, _ = self.check_api_result(response)
            
            if success:
                self.logger.info(f"Имя захвата успешно установлено: {name}")
                # Обновляем локальное значение и отправляем сигнал
                self.current_capture_name = name
                self.capture_name_changed_signal.emit(name)
                return True
            else:
                self.logger.error("Не удалось установить имя захвата: API вернул ошибку")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при установке имени захвата: {e}")
            return False

    async def set_capture_description(self, description: str) -> bool:
        """
        Установка описания захвата в Shogun Live.
        
        Args:
            description: Новое описание захвата
            
        Returns:
            bool: True если описание успешно установлено, иначе False
        """
        if not self.connected or not self.capture_service:
            self.logger.warning("Не удалось установить описание захвата: нет подключения")
            return False
            
        try:
            self.logger.info(f"Установка описания захвата: {description}")
            
            # Устанавливаем описание захвата используя метод API set_capture_description
            response = self.capture_service.set_capture_description(description)
            success, _ = self.check_api_result(response)
            
            if success:
                self.logger.info("Описание захвата успешно установлено")
                # Обновляем локальное значение и отправляем сигнал
                self.current_description = description
                self.description_changed_signal.emit(description)
                return True
            else:
                self.logger.error("Не удалось установить описание захвата: API вернул ошибку")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при установке описания захвата: {e}")
            return False

    async def set_capture_folder(self, folder: str) -> bool:
        """
        Установка пути к папке захвата в Shogun Live.
        
        Args:
            folder: Новый путь к папке захвата
            
        Returns:
            bool: True если путь успешно установлен, иначе False
        """
        if not self.connected or not self.capture_service:
            self.logger.warning("Не удалось установить путь к папке захвата: нет подключения")
            return False
            
        try:
            self.logger.info(f"Установка пути к папке захвата: {folder}")
            
            # Устанавливаем путь к папке захвата используя метод API set_capture_folder
            response = self.capture_service.set_capture_folder(folder)
            success, _ = self.check_api_result(response)
            
            if success:
                self.logger.info(f"Путь к папке захвата успешно установлен: {folder}")
                # Обновляем локальное значение и отправляем сигнал
                self.current_capture_folder = folder
                self.capture_folder_changed_signal.emit(folder)
                return True
            else:
                self.logger.error("Не удалось установить путь к папке захвата: API вернул ошибку")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при установке пути к папке захвата: {e}")
            return False

    def stop(self):
        """Остановка рабочего потока."""
        self.logger.info("Останавливаем ShogunWorker...")
        self.running = False