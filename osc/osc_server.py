"""
Модуль OSC-сервера для приема и обработки OSC-сообщений.
"""

import asyncio
import logging
import socket
from datetime import datetime
from typing import Callable, Any, Optional
from PyQt5.QtCore import QThread, pyqtSignal, QRunnable, QThreadPool, QObject

from pythonosc import dispatcher, osc_server, udp_client
import config

class ShogunTaskSignals(QObject):
    """Сигналы для задач Shogun."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class ShogunTask(QRunnable):
    """Рабочая задача для выполнения асинхронных операций Shogun в пуле потоков."""
    
    def __init__(self, coro_func: Callable):
        """
        Инициализирует новую задачу.
        
        Args:
            coro_func: Корутина для выполнения
        """
        super().__init__()
        self.coro_func = coro_func
        self.signals = ShogunTaskSignals()
        self.logger = logging.getLogger('ShogunOSC')
        
    def run(self):
        """Запускает асинхронную функцию в отдельном цикле событий."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.coro_func())
                self.signals.finished.emit(result)
            finally:
                loop.close()
        except Exception as e:
            self.logger.error(f"Ошибка в ShogunTask: {e}")
            self.signals.error.emit(str(e))

class OSCServer(QThread):
    """Поток OSC-сервера для приема и обработки OSC-сообщений"""
    message_signal = pyqtSignal(str, str)  # Сигнал для полученного OSC-сообщения (адрес, значение)
    
    def __init__(self, ip: str = "0.0.0.0", port: int = 5555, shogun_worker = None):
        super().__init__()
        self.logger = logging.getLogger('ShogunOSC')
        self.ip = ip
        self.port = port
        self.shogun_worker = shogun_worker
        self.running = True
        self.dispatcher = dispatcher.Dispatcher()
        self.server = None
        self._socket = None
        self.osc_client = None
        self.thread_pool = QThreadPool.globalInstance()
        
        # Настройка обработчиков OSC-сообщений
        self.setup_dispatcher()
        
    def setup_dispatcher(self) -> None:
        """Настройка обработчиков OSC-сообщений"""
        self.dispatcher.map(config.OSC_START_RECORDING, self.start_recording)
        self.dispatcher.map(config.OSC_STOP_RECORDING, self.stop_recording)
        self.dispatcher.map("/SetCaptureName", self.set_capture_name)
        self.dispatcher.map("/SetCaptureDescription", self.set_capture_description)
        self.dispatcher.map(config.OSC_SET_CAPTURE_FOLDER, self.set_capture_folder)  # Новый обработчик для установки папки захвата
        self.dispatcher.set_default_handler(self.default_handler)
    
    def _run_task(self, coro_func: Callable, finished_callback=None, error_callback=None) -> None:
        """
        Запускает асинхронную задачу в пуле потоков.
        
        Args:
            coro_func: Асинхронная функция для выполнения
            finished_callback: Callback для обработки завершения задачи
            error_callback: Callback для обработки ошибки
        """
        task = ShogunTask(coro_func)
        
        if finished_callback:
            task.signals.finished.connect(finished_callback)
        
        if error_callback:
            task.signals.error.connect(error_callback)
        else:
            # Стандартный обработчик ошибок
            task.signals.error.connect(lambda error: self.logger.error(f"Ошибка задачи: {error}"))
            
        self.thread_pool.start(task)
    
    def start_recording(self, address: str, *args: Any) -> None:
        """
        Обработчик команды запуска записи
        
        Args:
            address: OSC-адрес сообщения
            *args: Аргументы OSC-сообщения
        """
        self.logger.info(f"Получена команда OSC: {address} -> Запуск записи")
        self.message_signal.emit(address, "Запуск записи")
        
        if self.shogun_worker and self.shogun_worker.connected:
            def on_finished(result):
                self.logger.info("Запись успешно запущена" if result else "Не удалось запустить запись")
                
            self._run_task(
                self.shogun_worker.startcapture,
                finished_callback=on_finished
            )
        else:
            self.logger.warning("Не удалось запустить запись: нет подключения к Shogun Live")
    
    def stop_recording(self, address: str, *args: Any) -> None:
        """
        Обработчик команды остановки записи
        
        Args:
            address: OSC-адрес сообщения
            *args: Аргументы OSC-сообщения
        """
        self.logger.info(f"Получена команда OSC: {address} -> Остановка записи")
        self.message_signal.emit(address, "Остановка записи")
        
        if self.shogun_worker and self.shogun_worker.connected:
            def on_finished(result):
                self.logger.info("Запись успешно остановлена" if result else "Не удалось остановить запись")
                
            self._run_task(
                self.shogun_worker.stopcapture,
                finished_callback=on_finished
            )
        else:
            self.logger.warning("Не удалось остановить запись: нет подключения к Shogun Live")
    
    def set_capture_name(self, address: str, *args: Any) -> None:
        """
        Обработчик команды установки имени захвата
        
        Args:
            address: OSC-адрес сообщения
            *args: Аргументы OSC-сообщения (первый аргумент - новое имя)
        """
        if not args:
            self.logger.warning(f"Получена команда OSC: {address} -> Отсутствует имя захвата")
            self.message_signal.emit(address, "Ошибка: отсутствует имя захвата")
            return
            
        # Преобразуем аргумент в строку и проверяем, что он не пустой
        new_name = str(args[0]).strip()
        if not new_name:
            self.logger.warning(f"Получена команда OSC: {address} -> Пустое имя захвата")
            self.message_signal.emit(address, "Ошибка: пустое имя захвата")
            return
            
        self.logger.info(f"Получена команда OSC: {address} -> Установка имени захвата: '{new_name}'")
        self.message_signal.emit(address, f"Установка имени захвата: '{new_name}'")
        
        if self.shogun_worker and self.shogun_worker.connected:
            async def set_name_task():
                return await self.shogun_worker.set_capture_name(new_name)
                
            def on_finished(result):
                if result:
                    self.logger.info(f"Имя захвата успешно установлено: '{new_name}'")
                else:
                    self.logger.warning(f"Не удалось установить имя захвата: '{new_name}'")
                
            self._run_task(
                set_name_task,
                finished_callback=on_finished
            )
        else:
            self.logger.warning("Не удалось установить имя захвата: нет подключения к Shogun Live")
    
    def set_capture_description(self, address: str, *args: Any) -> None:
        """
        Обработчик команды установки описания захвата
        
        Args:
            address: OSC-адрес сообщения
            *args: Аргументы OSC-сообщения (первый аргумент - новое описание)
        """
        if not args:
            self.logger.warning(f"Получена команда OSC: {address} -> Отсутствует описание захвата")
            self.message_signal.emit(address, "Ошибка: отсутствует описание захвата")
            return
            
        # Преобразуем аргумент в строку
        new_description = str(args[0])
        
        self.logger.info(f"Получена команда OSC: {address} -> Установка описания захвата: '{new_description}'")
        self.message_signal.emit(address, f"Установка описания захвата: '{new_description}'")
        
        if self.shogun_worker and self.shogun_worker.connected:
            async def set_description_task():
                return await self.shogun_worker.set_capture_description(new_description)
                
            def on_finished(result):
                if result:
                    self.logger.info(f"Описание захвата успешно установлено")
                else:
                    self.logger.warning(f"Не удалось установить описание захвата")
                
            self._run_task(
                set_description_task,
                finished_callback=on_finished
            )
        else:
            self.logger.warning("Не удалось установить описание захвата: нет подключения к Shogun Live")
    
    def set_capture_folder(self, address: str, *args: Any) -> None:
        """
        Обработчик команды установки пути к папке захвата
        
        Args:
            address: OSC-адрес сообщения
            *args: Аргументы OSC-сообщения (первый аргумент - новый путь к папке)
        """
        if not args:
            self.logger.warning(f"Получена команда OSC: {address} -> Отсутствует путь к папке захвата")
            self.message_signal.emit(address, "Ошибка: отсутствует путь к папке захвата")
            return
            
        # Преобразуем аргумент в строку и проверяем, что он не пустой
        new_folder_path = str(args[0]).strip()
        if not new_folder_path:
            self.logger.warning(f"Получена команда OSC: {address} -> Пустой путь к папке захвата")
            self.message_signal.emit(address, "Ошибка: пустой путь к папке захвата")
            return
            
        self.logger.info(f"Получена команда OSC: {address} -> Установка пути к папке захвата: '{new_folder_path}'")
        self.message_signal.emit(address, f"Установка пути к папке захвата: '{new_folder_path}'")
        
        if self.shogun_worker and self.shogun_worker.connected:
            async def set_folder_task():
                return await self.shogun_worker.set_capture_folder(new_folder_path)
                
            def on_finished(result):
                if result:
                    self.logger.info(f"Путь к папке захвата успешно установлен: '{new_folder_path}'")
                else:
                    self.logger.warning(f"Не удалось установить путь к папке захвата: '{new_folder_path}'")
                
            self._run_task(
                set_folder_task,
                finished_callback=on_finished
            )
        else:
            self.logger.warning("Не удалось установить путь к папке захвата: нет подключения к Shogun Live")
    
    def default_handler(self, address: str, *args: Any) -> None:
        """
        Обработчик для неизвестных OSC-сообщений
        
        Args:
            address: OSC-адрес сообщения
            *args: Аргументы OSC-сообщения
        """
        args_str = ", ".join(str(arg) for arg in args) if args else "нет аргументов"
        self.logger.debug(f"Получено неизвестное OSC-сообщение: {address} -> {args_str}")
        self.message_signal.emit(address, args_str)
    
    def send_osc_message(self, address: str, value: Any) -> bool:
        """
        Отправляет OSC-сообщение
        
        Args:
            address: OSC-адрес сообщения
            value: Значение для отправки
            
        Returns:
            bool: True если сообщение отправлено успешно, иначе False
        """
        try:
            # Проверяем, что адрес не пустой
            if not address:
                self.logger.error("Попытка отправить OSC-сообщение с пустым адресом")
                return False
                
            # Создаем клиент для отправки, если еще не создан
            if not self.osc_client:
                # Используем настройки из конфигурации
                target_ip = config.DEFAULT_OSC_BROADCAST_IP
                target_port = config.DEFAULT_OSC_BROADCAST_PORT
                
                # Создаем клиент с обычным сокетом вместо широковещательного
                # для избежания ошибок доступа
                if target_ip == "255.255.255.255":
                    # Создаем собственный сокет с поддержкой широковещательных сообщений
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    # Привязываем к любому доступному порту
                    sock.bind(('', 0))
                    # Создаем клиент с нашим сокетом
                    self.osc_client = udp_client.SimpleUDPClient(target_ip, target_port, sock)
                else:
                    # Для обычного IP используем стандартный клиент
                    self.osc_client = udp_client.SimpleUDPClient(target_ip, target_port)
                
                self.logger.info(f"Создан OSC-клиент для отправки сообщений на {target_ip}:{target_port}")
                
            # Отправляем сообщение
            self.osc_client.send_message(address, value)
            self.logger.debug(f"Отправлено OSC-сообщение: {address} -> {value}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки OSC-сообщения: {e}")
            return False
    
    def run(self) -> None:
        """Запуск OSC-сервера"""
        try:
            self.logger.info(f"OSC-сервер запущен на {self.ip}:{self.port}")
            
            # Создаем сервер с обработкой ошибок
            try:
                self.server = osc_server.ThreadingOSCUDPServer((self.ip, self.port), self.dispatcher)
                self._socket = self.server.socket
            except socket.error as e:
                self.logger.error(f"Не удалось создать OSC-сервер: {e}")
                # Сигнализируем об ошибке
                self.message_signal.emit("ERROR", f"Не удалось запустить OSC-сервер: {e}")
                return
            
            # Устанавливаем таймаут для сокета, чтобы можно было корректно остановить сервер
            self._socket.settimeout(0.5)
            
            # Запускаем сервер с возможностью остановки
            while self.running:
                try:
                    self.server.handle_request()
                except socket.timeout:
                    # Таймаут сокета - нормальная ситуация, продолжаем работу
                    continue
                except Exception as e:
                    if self.running:  # Логируем ошибку только если сервер должен работать
                        self.logger.error(f"Ошибка при обработке OSC-запроса: {e}")
        except Exception as e:
            self.logger.error(f"Критическая ошибка OSC-сервера: {e}")
    
    def stop(self) -> None:
        """Остановка OSC-сервера"""
        self.running = False
        # Закрываем сервер если он создан
        if self.server:
            try:
                self.server.server_close()
            except Exception as e:
                self.logger.error(f"Ошибка при закрытии OSC-сервера: {e}")
        
        # Закрываем клиент для отправки сообщений
        if self.osc_client and hasattr(self.osc_client, '_sock'):
            try:
                self.osc_client._sock.close()
            except Exception as e:
                self.logger.error(f"Ошибка при закрытии OSC-клиента: {e}")
                
        self.logger.info("OSC-сервер остановлен")

def format_osc_message(address: str, value: Any, with_timestamp: bool = True) -> str:
    """
    Форматирует OSC-сообщение для отображения
    
    Args:
        address: OSC-адрес сообщения
        value: Значение сообщения
        with_timestamp: Добавлять ли временную метку
        
    Returns:
        str: Отформатированное сообщение
    """
    if with_timestamp:
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"<b>[{timestamp}]</b> {address} → {value}"
    else:
        return f"{address} → {value}"