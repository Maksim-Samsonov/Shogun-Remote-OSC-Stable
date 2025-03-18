"""
Основное окно приложения ShogunOSC.
Собирает и координирует работу всех компонентов интерфейса,
обрабатывает сигналы между компонентами.
"""

import asyncio
import logging
import threading
import os
from datetime import datetime
from typing import Optional

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QTextEdit, QGroupBox, QGridLayout,
                           QLineEdit, QSpinBox, QComboBox, QStatusBar, QCheckBox, QSplitter,
                           QAction, QMenu, QToolBar, QApplication, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QTextCursor, QIcon, QPixmap

from gui.status_panel import StatusPanel
from gui.log_panel import LogPanel
from shogun.shogun_client import ShogunWorker
from osc.osc_server import OSCServer, format_osc_message
from logger.custom_logger import add_text_widget_handler
from styles.app_styles import get_palette, get_stylesheet, set_status_style
import config

class ShogunOSCApp(QMainWindow):
    """Главное окно приложения. Отвечает за организацию 
    интерфейса и координацию работы всех компонентов."""
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('ShogunOSC')

        # Create ShogunWorker before loading UI
        self.shogun_worker = ShogunWorker()
        
        # Initialize the osc_server attribute
        self.osc_server = None
        
        # Load icons from absolute paths
        icons_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "icons"))
        icon_connected = os.path.join(icons_dir, "icon_green.png")
        icon_disconnected = os.path.join(icons_dir, "icon_red.png")
        
        self.icon_connected = QIcon(icon_connected)
        self.icon_disconnected = QIcon(icon_disconnected)
        
        if self.icon_connected.isNull() or self.icon_disconnected.isNull():
            self.logger.warning("Failed to load window icons")
            # Create fallback icons
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.green)
            self.icon_connected = QIcon(pixmap)
            pixmap.fill(Qt.red)
            self.icon_disconnected = QIcon(pixmap)
        
        # Set initial icon
        self.setWindowIcon(self.icon_disconnected)
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Start worker thread
        self.shogun_worker.start()
        
        # Проверка импорта библиотек
        if not config.IMPORT_SUCCESS:
            self.logger.critical(f"Ошибка импорта библиотек: {config.IMPORT_ERROR}")
            self.log_panel.log_text.append(f'<span style="color:red;font-weight:bold;">ОШИБКА ИМПОРТА БИБЛИОТЕК: {config.IMPORT_ERROR}</span>')
            self.log_panel.log_text.append('<span style="color:red;">Убедитесь, что установлены необходимые библиотеки:</span>')
            self.log_panel.log_text.append('<span style="color:blue;">pip install vicon-core-api shogun-live-api python-osc psutil PyQt5</span>')
            
            # Показываем диалог с ошибкой
            self.show_error_dialog("Ошибка импорта библиотек", 
                                  f"Не удалось импортировать необходимые библиотеки: {config.IMPORT_ERROR}\n\n"
                                  "Убедитесь, что установлены все зависимости:\n"
                                  "pip install vicon-core-api shogun-live-api python-osc psutil PyQt5")
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Shogun OSC GUI")
        self.setMinimumSize(800, 600)
        
        # Создаем панель статуса первой, до применения темы
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готов к работе")
        
        # Теперь можно применять тему
        self.apply_theme(config.DARK_MODE)
        
        # Создаем меню и тулбар
        self.create_menu()
        
        # Основные виджеты
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Создаем компоненты интерфейса
        self.status_panel = StatusPanel(self.shogun_worker)
        self.log_panel = LogPanel()
        
        # Добавляем панель логов в систему логирования
        add_text_widget_handler(self.log_panel.log_text)
        
        # Добавляем компоненты в основной лейаут
        main_layout.addWidget(self.status_panel)
        main_layout.addWidget(self.log_panel, 1)  # 1 - коэффициент растяжения
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(central_widget)
        
        # Запускаем OSC сервер
        if self.status_panel.osc_panel.osc_enabled.isChecked():
            self.start_osc_server()
        
        # Настраиваем таймер автосохранения настроек
        self.settings_timer = QTimer(self)
        self.settings_timer.timeout.connect(self.auto_save_settings)
        self.settings_timer.start(60000)  # Автосохранение каждую минуту
    
    def create_menu(self):
        """Создание меню и панели инструментов"""
        # Главное меню
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu("Файл")
        
        save_log_action = QAction("Сохранить лог", self)
        save_log_action.setShortcut("Ctrl+S")
        save_log_action.triggered.connect(self.save_log_to_file)
        file_menu.addAction(save_log_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Настройки"
        settings_menu = menubar.addMenu("Настройки")

        # Подменю "OSC"
        osc_menu = settings_menu.addMenu("OSC")

        self.theme_action = QAction("Тёмная тема", self)
        self.theme_action.setCheckable(True)
        self.theme_action.setChecked(config.DARK_MODE)
        self.theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(self.theme_action)

        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """Подключение сигналов между компонентами"""
        # Сигналы от панели состояния
        self.status_panel.osc_panel.osc_enabled.stateChanged.connect(self.toggle_osc_server)
        
        # Сигналы от Shogun Worker для обновления статусной строки
        self.shogun_worker.connection_signal.connect(self.update_status_bar)
        self.shogun_worker.recording_signal.connect(self.update_recording_status)
        
        # Сигнал изменения имени захвата
        self.shogun_worker.capture_name_changed_signal.connect(self.on_capture_name_changed)
        
        # Сигнал изменения описания захвата
        self.shogun_worker.description_changed_signal.connect(self.on_description_changed)
        
        # Сигнал изменения пути к папке захвата
        self.shogun_worker.capture_folder_changed_signal.connect(self.on_capture_folder_changed)

        # Сигнал изменения статуса OSC-сервера
        self.status_panel.osc_panel.osc_status_changed.connect(self.on_osc_status_changed)

    def on_osc_status_changed(self, running):
        """Обработчик изменения статуса OSC-сервера"""
        self.logger.info(f"OSC server status changed: {running}")
        if running:
            ip = self.status_panel.osc_panel.ip_input.text()
            port = self.status_panel.osc_panel.port_input.value()
            self.start_osc_server()
            self.logger.info(f"OSC server started from signal on {ip}:{port}")
        else:
            self.stop_osc_server()
            self.logger.info("OSC server stopped from signal")
    
    def on_capture_name_changed(self, new_name):
        """Обработчик изменения имени захвата в Shogun Live"""
        self.logger.info(f"Имя захвата изменилось: '{new_name}'")
        
        # Обновляем информацию в интерфейсе
        self.status_panel.shogun_panel.update_capture_name(new_name)
        
        # Отправляем OSC-сообщение об изменении имени захвата только если OSC сервер включен
        if self.osc_server and self.status_panel.osc_panel.osc_enabled.isChecked():
            # Получаем настройки отправки из панели OSC
            broadcast_settings = self.status_panel.osc_panel.get_broadcast_settings()
            
            # Обновляем настройки в конфигурации
            config.app_settings["osc_broadcast_ip"] = broadcast_settings["ip"]
            config.app_settings["osc_broadcast_port"] = broadcast_settings["port"]
            
            # Отправляем сообщение
            success = self.osc_server.send_osc_message(config.OSC_CAPTURE_NAME_CHANGED, new_name)
            if success:
                self.logger.info(f"Отправлено OSC-сообщение: {config.OSC_CAPTURE_NAME_CHANGED} -> '{new_name}'")
                # Добавляем в журнал OSC-сообщений
                self.log_panel.add_osc_message(config.OSC_CAPTURE_NAME_CHANGED, f"'{new_name}'")
    
    def on_description_changed(self, new_description):
        """Обработчик изменения описания захвата в Shogun Live"""
        self.logger.info(f"Описание захвата изменилось: '{new_description}'")
        
        # Обновляем информацию в интерфейсе
        self.status_panel.shogun_panel.update_description(new_description)
        
        # Отправляем OSC-сообщение об изменении описания захвата только если OSC сервер включен
        if self.osc_server and self.status_panel.osc_panel.osc_enabled.isChecked():
            # Получаем настройки отправки из панели OSC
            broadcast_settings = self.status_panel.osc_panel.get_broadcast_settings()
            
            # Обновляем настройки в конфигурации
            config.app_settings["osc_broadcast_ip"] = broadcast_settings["ip"]
            config.app_settings["osc_broadcast_port"] = broadcast_settings["port"]
            
            # Отправляем сообщение
            success = self.osc_server.send_osc_message(config.OSC_DESCRIPTION_CHANGED, new_description)
            if success:
                self.logger.info(f"Отправлено OSC-сообщение: {config.OSC_DESCRIPTION_CHANGED} -> '{new_description}'")
                # Добавляем в журнал OSC-сообщений
                self.log_panel.add_osc_message(config.OSC_DESCRIPTION_CHANGED, f"'{new_description}'")
    
    def on_capture_folder_changed(self, new_folder):
        """Обработчик изменения пути к папке захвата в Shogun Live"""
        self.logger.info(f"Путь к папке захвата изменился: '{new_folder}'")
        
        # Обновляем информацию в интерфейсе, если есть соответствующий метод
        if hasattr(self.status_panel.shogun_panel, 'update_capture_folder'):
            self.status_panel.shogun_panel.update_capture_folder(new_folder)
        
        # Отправляем OSC-сообщение об изменении пути к папке захвата только если OSC сервер включен
        if self.osc_server and self.status_panel.osc_panel.osc_enabled.isChecked():
            # Получаем настройки отправки из панели OSC
            broadcast_settings = self.status_panel.osc_panel.get_broadcast_settings()
            
            # Обновляем настройки в конфигурации
            config.app_settings["osc_broadcast_ip"] = broadcast_settings["ip"]
            config.app_settings["osc_broadcast_port"] = broadcast_settings["port"]
            
            # Отправляем сообщение
            success = self.osc_server.send_osc_message(config.OSC_CAPTURE_FOLDER_CHANGED, new_folder)
            if success:
                self.logger.info(f"Отправлено OSC-сообщение: {config.OSC_CAPTURE_FOLDER_CHANGED} -> '{new_folder}'")
                # Добавляем в журнал OSC-сообщений
                self.log_panel.add_osc_message(config.OSC_CAPTURE_FOLDER_CHANGED, f"'{new_folder}'")
    
    def update_status_bar(self, connected):
        """Обновление статусной строки при изменении состояния подключения"""
        if connected:
            self.status_bar.showMessage("Подключено к Shogun Live")
            # Меняем иконку на зеленую (подключено)
            self.setWindowIcon(self.icon_connected)
        else:
            self.status_bar.showMessage("Нет подключения к Shogun Live")
            # Меняем иконку на красную (отключено)
            self.setWindowIcon(self.icon_disconnected)
    
    def update_recording_status(self, is_recording):
        """Обновление статусной строки при изменении состояния записи"""
        if is_recording:
            self.status_bar.showMessage("Запись активна")
        else:
            # Восстанавливаем предыдущее сообщение о подключении
            self.update_status_bar(self.shogun_worker.connected)
    
    def toggle_osc_server(self, state):
        """Включение/выключение OSC-сервера"""
        if state == Qt.Checked:
            self.start_osc_server()
        else:
            self.stop_osc_server()
    
    def start_osc_server(self):
        """Запуск OSC-сервера"""
        ip = self.status_panel.osc_panel.ip_input.text()
        port = self.status_panel.osc_panel.port_input.value()
        
        # Останавливаем предыдущий сервер, если был
        self.stop_osc_server()
        
        # Создаем и запускаем новый сервер
        self.osc_server = OSCServer(ip, port, self.shogun_worker)
        self.osc_server.message_signal.connect(self.log_panel.add_osc_message)
        self.osc_server.start()
        
        # Блокируем изменение настроек при запущенном сервере
        self.status_panel.osc_panel.ip_input.setEnabled(False)
        self.status_panel.osc_panel.port_input.setEnabled(False)
        
        # Удалено дублирующее сообщение о запуске OSC-сервера
    
    def stop_osc_server(self):
        """Остановка OSC-сервера"""
        if hasattr(self, 'osc_server') and self.osc_server:
            if self.osc_server.isRunning():
                self.osc_server.stop()
                self.osc_server.wait()  # Ждем завершения потока
            self.osc_server = None
            
            # Разблокируем настройки
            self.status_panel.osc_panel.ip_input.setEnabled(True)
            self.status_panel.osc_panel.port_input.setEnabled(True)
            
            self.logger.info("OSC-сервер остановлен")
    
    def apply_theme(self, dark_mode=False):
        """Применяет выбранную тему ко всему приложению"""
        # Обновляем настройку темной темы в конфигурации
        config.DARK_MODE = dark_mode
        config.app_settings['dark_mode'] = dark_mode
        config.save_settings(config.app_settings)
        
        # Применяем палитру и стили
        palette = get_palette(dark_mode)
        stylesheet = get_stylesheet(dark_mode)
        
        # Устанавливаем палитру и стилевую таблицу для приложения
        app = QApplication.instance()
        app.setPalette(palette)
        app.setStyleSheet(stylesheet)
        
        # Уведомляем пользователя о смене темы
        theme_name = "тёмная" if dark_mode else "светлая"
        self.status_bar.showMessage(f"Применена {theme_name} тема", 3000)
        
        # Обновляем состояние чекбокса в меню
        if hasattr(self, 'theme_action'):
            self.theme_action.setChecked(dark_mode)
    
    def toggle_theme(self):
        """Переключение между светлой и тёмной темой"""
        self.apply_theme(not config.DARK_MODE)
    
    def show_about(self):
        """Отображает окно 'О программе'"""
        about_text = (
            "<h2>Shogun OSC GUI</h2>"
            "<p>Приложение для управления Shogun Live через OSC-протокол</p>"
            "<p>Версия: 1.0</p>"
            "<p>Лицензия: MIT</p>"
        )
        
        # Используем QMessageBox для отображения информации
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("О программе")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()
        
        # Также добавляем в лог
        self.logger.info("О программе: Shogun OSC GUI v1.0")
    
    def save_log_to_file(self):
        """Сохраняет журнал логов в файл через диалог выбора файла"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"shogun_osc_log_{timestamp}.html"
            
            # Открываем диалог выбора файла
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Сохранить журнал логов", 
                default_filename, 
                "HTML Files (*.html);;Text Files (*.txt);;All Files (*)"
            )
            
            if not filename:  # Пользователь отменил сохранение
                return
            
            # Определяем формат файла по расширению
            if filename.lower().endswith('.html'):
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("<html><head><meta charset='utf-8'><title>ShogunOSC Log</title></head><body>")
                    f.write(self.log_panel.log_text.toHtml())
                    f.write("</body></html>")
            else:
                # Сохраняем как обычный текст
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_panel.log_text.toPlainText())
            
            self.logger.info(f"Журнал логов сохранен в файл: {filename}")
            self.status_bar.showMessage(f"Журнал сохранен: {filename}", 5000)
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении журнала: {e}")
            self.show_error_dialog("Ошибка сохранения", f"Не удалось сохранить журнал: {e}")
    
    def auto_save_settings(self):
        """Автоматическое сохранение настроек"""
        try:
            self.save_current_settings()
            self.logger.debug("Настройки автоматически сохранены")
        except Exception as e:
            self.logger.error(f"Ошибка при автосохранении настроек: {e}")
    
    def save_current_settings(self):
        """Сохраняет текущие настройки приложения"""
        config.app_settings["osc_ip"] = self.status_panel.osc_panel.ip_input.text()
        config.app_settings["osc_port"] = self.status_panel.osc_panel.port_input.value()
        config.app_settings["osc_enabled"] = self.status_panel.osc_panel.osc_enabled.isChecked()
        
        # Сохраняем настройки отправки OSC-сообщений
        broadcast_settings = self.status_panel.osc_panel.get_broadcast_settings()
        config.app_settings["osc_broadcast_ip"] = broadcast_settings["ip"]
        config.app_settings["osc_broadcast_port"] = broadcast_settings["port"]
        
        config.save_settings(config.app_settings)
    
    def show_error_dialog(self, title, message):
        """Показывает диалоговое окно с ошибкой"""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        try:
            # Сохраняем настройки
            self.save_current_settings()
            
            # Останавливаем рабочие потоки
            if self.shogun_worker:
                self.shogun_worker.stop()
                self.shogun_worker.wait(1000)  # Ждем завершения потока с таймаутом
            
            self.stop_osc_server()
            
            self.logger.info("Приложение закрыто")
            event.accept()
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения: {e}")
            event.accept()  # Все равно закрываем приложение