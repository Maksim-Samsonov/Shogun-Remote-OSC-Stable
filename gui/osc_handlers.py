"""
Обработчики OSC-сообщений для ShogunOSC.
Отвечают за передачу данных через OSC-протокол.
"""

import logging
import traceback
from typing import Dict, Any, Optional

import config
from osc.osc_server import OSCServer

class OSCHandlers:
    """Класс для обработки OSC-сообщений"""
    
    def __init__(self, main_window):
        """
        Инициализация обработчиков OSC-сообщений
        
        Args:
            main_window: Ссылка на главное окно приложения
        """
        self.main_window = main_window
        self.logger = logging.getLogger('ShogunOSC')
        self.settings_manager = config.settings_manager
        self.osc_server = None
    
    def on_osc_status_changed(self, running):
        """Обработчик изменения статуса OSC-сервера"""
        self.logger.info(f"OSC server status changed: {running}")
        if running:
            ip = self.main_window.status_panel.osc_panel.ip_input.text()
            port = self.main_window.status_panel.osc_panel.port_input.value()
            self.start_osc_server()
            self.logger.info(f"OSC server started from signal on {ip}:{port}")
        else:
            self.stop_osc_server()
            self.logger.info("OSC server stopped from signal")
    
    def on_capture_name_changed(self, new_name):
        """Обработчик изменения имени захвата в Shogun Live"""
        self.logger.info(f"Имя захвата изменилось: '{new_name}'")
        
        # Обновляем информацию в интерфейсе
        self.main_window.status_panel.shogun_panel.update_capture_name(new_name)
        
        # Отправляем OSC-сообщение об изменении имени захвата только если OSC сервер включен
        if self.osc_server and self.main_window.status_panel.osc_panel.osc_enabled.isChecked():
            try:
                # Получаем настройки отправки из панели OSC
                broadcast_settings = self.main_window.status_panel.osc_panel.get_broadcast_settings()
                
                # Обновляем настройки в конфигурации
                self.settings_manager.set("osc_broadcast_ip", broadcast_settings["ip"])
                self.settings_manager.set("osc_broadcast_port", broadcast_settings["port"])
                
                # Отправляем сообщение
                success = self.osc_server.send_osc_message(config.OSC_CAPTURE_NAME_CHANGED, new_name)
                if success:
                    self.logger.info(f"Отправлено OSC-сообщение: {config.OSC_CAPTURE_NAME_CHANGED} -> '{new_name}'")
                    # Добавляем в журнал OSC-сообщений
                    self.main_window.log_panel.add_osc_message(config.OSC_CAPTURE_NAME_CHANGED, f"'{new_name}'")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке OSC-сообщения об изменении имени захвата: {e}")
    
    def on_description_changed(self, new_description):
        """Обработчик изменения описания захвата в Shogun Live"""
        self.logger.info(f"Описание захвата изменилось: '{new_description}'")
        
        # Обновляем информацию в интерфейсе
        self.main_window.status_panel.shogun_panel.update_description(new_description)
        
        # Отправляем OSC-сообщение об изменении описания захвата только если OSC сервер включен
        if self.osc_server and self.main_window.status_panel.osc_panel.osc_enabled.isChecked():
            try:
                # Получаем настройки отправки из панели OSC
                broadcast_settings = self.main_window.status_panel.osc_panel.get_broadcast_settings()
                
                # Обновляем настройки в конфигурации
                self.settings_manager.set("osc_broadcast_ip", broadcast_settings["ip"])
                self.settings_manager.set("osc_broadcast_port", broadcast_settings["port"])
                
                # Отправляем сообщение
                success = self.osc_server.send_osc_message(config.OSC_DESCRIPTION_CHANGED, new_description)
                if success:
                    self.logger.info(f"Отправлено OSC-сообщение: {config.OSC_DESCRIPTION_CHANGED} -> '{new_description}'")
                    # Добавляем в журнал OSC-сообщений
                    self.main_window.log_panel.add_osc_message(config.OSC_DESCRIPTION_CHANGED, f"'{new_description}'")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке OSC-сообщения об изменении описания захвата: {e}")
    
    def on_capture_folder_changed(self, new_folder):
        """Обработчик изменения пути к папке захвата в Shogun Live"""
        self.logger.info(f"Путь к папке захвата изменился: '{new_folder}'")
        
        # Обновляем информацию в интерфейсе, если есть соответствующий метод
        if hasattr(self.main_window.status_panel.shogun_panel, 'update_capture_folder'):
            self.main_window.status_panel.shogun_panel.update_capture_folder(new_folder)
        
        # Отправляем OSC-сообщение об изменении пути к папке захвата только если OSC сервер включен
        if self.osc_server and self.main_window.status_panel.osc_panel.osc_enabled.isChecked():
            try:
                # Получаем настройки отправки из панели OSC
                broadcast_settings = self.main_window.status_panel.osc_panel.get_broadcast_settings()
                
                # Обновляем настройки в конфигурации
                self.settings_manager.set("osc_broadcast_ip", broadcast_settings["ip"])
                self.settings_manager.set("osc_broadcast_port", broadcast_settings["port"])
                
                # Отправляем сообщение
                success = self.osc_server.send_osc_message(config.OSC_CAPTURE_FOLDER_CHANGED, new_folder)
                if success:
                    self.logger.info(f"Отправлено OSC-сообщение: {config.OSC_CAPTURE_FOLDER_CHANGED} -> '{new_folder}'")
                    # Добавляем в журнал OSC-сообщений
                    self.main_window.log_panel.add_osc_message(config.OSC_CAPTURE_FOLDER_CHANGED, f"'{new_folder}'")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке OSC-сообщения об изменении пути к папке захвата: {e}")
    
    def toggle_osc_server(self, state):
        """Включение/выключение OSC-сервера"""
        if state == 2:  # Qt.Checked
            self.start_osc_server()
            # Обновляем настройку
            self.settings_manager.set("osc_enabled", True)
        else:
            self.stop_osc_server()
            # Обновляем настройку
            self.settings_manager.set("osc_enabled", False)
    
    def start_osc_server(self):
        """Запуск OSC-сервера"""
        try:
            ip = self.main_window.status_panel.osc_panel.ip_input.text()
            port = self.main_window.status_panel.osc_panel.port_input.value()
            
            # Сохраняем настройки
            self.settings_manager.set("osc_ip", ip)
            self.settings_manager.set("osc_port", port)
            
            # Сохраняем настройки отправки
            broadcast_settings = self.main_window.status_panel.osc_panel.get_broadcast_settings()
            self.settings_manager.set("osc_broadcast_ip", broadcast_settings["ip"])
            self.settings_manager.set("osc_broadcast_port", broadcast_settings["port"])
            
            # Останавливаем предыдущий сервер, если был
            self.stop_osc_server()
            
            # Создаем и запускаем новый сервер
            self.osc_server = OSCServer(ip, port, self.main_window.shogun_worker)
            self.osc_server.message_signal.connect(self.main_window.log_panel.add_osc_message)
            self.osc_server.start()
            
            # Блокируем изменение настроек при запущенном сервере
            self.main_window.status_panel.osc_panel.ip_input.setEnabled(False)
            self.main_window.status_panel.osc_panel.port_input.setEnabled(False)
            
            self.logger.info(f"OSC-сервер запущен на {ip}:{port}")
        except Exception as e:
            error_msg = f"Ошибка при запуске OSC-сервера: {e}"
            self.logger.error(error_msg)
            self.main_window.show_error_dialog("Ошибка OSC-сервера", error_msg)
    
    def stop_osc_server(self):
        """Остановка OSC-сервера"""
        try:
            if hasattr(self, 'osc_server') and self.osc_server:
                if self.osc_server.isRunning():
                    self.osc_server.stop()
                    self.osc_server.wait()  # Ждем завершения потока
                self.osc_server = None
                
                # Разблокируем настройки
                self.main_window.status_panel.osc_panel.ip_input.setEnabled(True)
                self.main_window.status_panel.osc_panel.port_input.setEnabled(True)
                
                self.logger.info("OSC-сервер остановлен")
        except Exception as e:
            error_msg = f"Ошибка при остановке OSC-сервера: {e}"
            self.logger.error(error_msg)
