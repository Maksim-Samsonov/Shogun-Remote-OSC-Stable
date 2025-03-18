"""
Основное окно приложения ShogunOSC.
Собирает и координирует работу всех компонентов интерфейса,
обрабатывает сигналы между компонентами.
"""

import logging
import os
import traceback
from datetime import datetime
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QFileDialog,
                           QAction, QMenu, QApplication, QMessageBox,
                           QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, QTimer

from gui.status_panel import StatusPanel
from gui.log_panel import LogPanel
from gui.settings_dialog import SettingsDialog
from gui.osc_handlers import OSCHandlers
from gui.ui_helpers import UIHelpers
from shogun.shogun_client import ShogunWorker
from logger.custom_logger import add_text_widget_handler
import config

class ShogunOSCApp(QMainWindow):
    """Главное окно приложения. Отвечает за организацию 
    интерфейса и координацию работы всех компонентов."""
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('ShogunOSC')

        # Получаем ссылку на менеджер настроек
        self.settings_manager = config.settings_manager
        
        # Create ShogunWorker before loading UI
        self.shogun_worker = ShogunWorker()
        
        # Создаем вспомогательные классы
        self.ui_helpers = None  # Инициализируем после создания UI
        self.osc_handlers = None  # Инициализируем после создания UI
        
        # Initialize UI
        self.init_ui()
        
        # Теперь инициализируем вспомогательные классы
        self.ui_helpers = UIHelpers(self)
        self.osc_handlers = OSCHandlers(self)
        
        # Подключаемся к сигналу изменения настроек
        self.settings_manager.settings_changed.connect(self.on_settings_changed)
        
        # Connect signals
        self.connect_signals()
        
        # Start worker thread
        self.shogun_worker.start()
        
        # Запускаем OSC сервер, если включен
        if self.settings_manager.get("osc_enabled"):
            self.osc_handlers.start_osc_server()
        
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
    
    def on_settings_changed(self, key: str, value: Any) -> None:
        """
        Обработчик изменения настроек приложения
        
        Args:
            key: Ключ изменённой настройки
            value: Новое значение настройки
        """
        self.logger.debug(f"Настройка изменена: {key} = {value}")
        
        # Обработка изменения темы
        if key == "dark_mode":
            config.DARK_MODE = value
            self.ui_helpers.apply_theme(value)
        
        # Обработка изменений OSC-настроек
        elif key.startswith("osc_"):
            if key == "osc_enabled" and self.status_panel:
                if value != self.status_panel.osc_panel.osc_enabled.isChecked():
                    self.status_panel.osc_panel.osc_enabled.setChecked(value)
            elif key == "osc_ip" and self.status_panel:
                self.status_panel.osc_panel.ip_input.setText(value)
            elif key == "osc_port" and self.status_panel:
                self.status_panel.osc_panel.port_input.setValue(value)
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Shogun OSC GUI")
        self.setMinimumSize(800, 600)
        
        # Создаем панель статуса
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готов к работе")
        
        # Создаем меню и тулбар
        self.create_menu()
        
        # Основные виджеты
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Создаем компоненты интерфейса
        self.status_panel = StatusPanel(self.shogun_worker)
        self.log_panel = LogPanel()
        
        # Создаем переключатель темы
        theme_widget = QWidget()
        theme_layout = QHBoxLayout(theme_widget)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        
        theme_label = QLabel("Тема:")
        theme_layout.addWidget(theme_label)
        
        self.theme_button_group = QButtonGroup(self)
        
        self.light_theme_radio = QRadioButton("Светлая")
        self.dark_theme_radio = QRadioButton("Темная")
        
        self.theme_button_group.addButton(self.light_theme_radio, 0)
        self.theme_button_group.addButton(self.dark_theme_radio, 1)
        
        self.light_theme_radio.setChecked(not self.settings_manager.get("dark_mode"))
        self.dark_theme_radio.setChecked(self.settings_manager.get("dark_mode"))
        
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        
        # Добавляем кнопку настроек
        settings_button = QPushButton("Настройки")
        settings_button.clicked.connect(self.show_settings_dialog)
        theme_layout.addWidget(settings_button)
        
        theme_layout.addStretch(1)
        
        # Добавляем панель логов в систему логирования
        add_text_widget_handler(self.log_panel.log_text)
        
        # Добавляем компоненты в основной лейаут
        main_layout.addWidget(theme_widget)
        main_layout.addWidget(self.status_panel)
        main_layout.addWidget(self.log_panel, 1)  # 1 - коэффициент растяжения
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(central_widget)
        
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
        
        # Меню "Настройки" заменяем на прямой переход к настройкам
        settings_action = menubar.addAction("Настройки")
        settings_action.triggered.connect(self.show_settings_dialog)
        
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_settings_dialog(self):
        """Показывает диалог настроек приложения"""
        try:
            settings_dialog = SettingsDialog(self)
            result = settings_dialog.exec_()
            
            if result == SettingsDialog.Accepted:
                self.logger.info("Настройки применены из диалога настроек")
                # Обновляем радиокнопки темы в соответствии с новыми настройками
                self.ui_helpers.update_theme_buttons()
        except Exception as e:
            # Записываем подробную информацию об ошибке в лог
            error_msg = f"Ошибка при открытии диалога настроек: {e}"
            stack_trace = traceback.format_exc()
            self.logger.error(f"{error_msg}\n{stack_trace}")
            
            # Показываем пользователю сообщение об ошибке
            self.show_error_dialog("Ошибка настроек", 
                                  f"Не удалось открыть диалог настроек:\n{e}")
    
    def connect_signals(self):
        """Подключение сигналов между компонентами"""
        # Сигналы от панели состояния
        self.status_panel.osc_panel.osc_enabled.stateChanged.connect(self.osc_handlers.toggle_osc_server)
        
        # Сигналы от Shogun Worker для обновления статусной строки
        self.shogun_worker.connection_signal.connect(self.update_status_bar)
        self.shogun_worker.recording_signal.connect(self.update_recording_status)
        
        # Сигнал изменения имени захвата
        self.shogun_worker.capture_name_changed_signal.connect(self.osc_handlers.on_capture_name_changed)
        
        # Сигнал изменения описания захвата
        self.shogun_worker.description_changed_signal.connect(self.osc_handlers.on_description_changed)
        
        # Сигнал изменения пути к папке захвата
        self.shogun_worker.capture_folder_changed_signal.connect(self.osc_handlers.on_capture_folder_changed)

        # Сигнал изменения статуса OSC-сервера
        self.status_panel.osc_panel.osc_status_changed.connect(self.osc_handlers.on_osc_status_changed)
        
        # Подключаем сигналы радиокнопок
        self.theme_button_group.buttonClicked.connect(self.ui_helpers.on_theme_button_clicked)
    
    def update_status_bar(self, connected):
        """Обновление статусной строки при изменении состояния подключения"""
        if connected:
            self.status_bar.showMessage("Подключено к Shogun Live")
        else:
            self.status_bar.showMessage("Нет подключения к Shogun Live")
    
    def update_recording_status(self, is_recording):
        """Обновление статусной строки при изменении состояния записи"""
        if is_recording:
            self.status_bar.showMessage("Запись активна")
        else:
            # Восстанавливаем предыдущее сообщение о подключении
            self.update_status_bar(self.shogun_worker.connected)
    
    def show_about(self):
        """Отображает окно 'О программе'"""
        if self.ui_helpers:
            self.ui_helpers.show_about()
    
    def show_error_dialog(self, title, message):
        """Показывает диалоговое окно с ошибкой"""
        if self.ui_helpers:
            self.ui_helpers.show_error_dialog(title, message)
        else:
            # Резервный вариант, если ui_helpers еще не инициализирован
            QMessageBox.critical(self, title, message)
    
    def save_log_to_file(self):
        """Сохраняет журнал логов в файл через диалог выбора файла"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"shogun_osc_log_{timestamp}.html"
            
            # Получаем директорию для логов
            logs_dir = self.settings_manager.get_logs_dir()
            if not os.path.exists(logs_dir):
                try:
                    os.makedirs(logs_dir)
                except OSError as e:
                    self.logger.warning(f"Не удалось создать директорию для логов: {e}")
            
            # Формируем полный путь
            default_path = os.path.join(logs_dir, default_filename)
            
            # Открываем диалог выбора файла
            filename, _ = QFileDialog.getSaveFileName(
                self, 
                "Сохранить журнал логов", 
                default_path, 
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
        try:
            settings_dict = {
                "osc_ip": self.status_panel.osc_panel.ip_input.text(),
                "osc_port": self.status_panel.osc_panel.port_input.value(),
                "osc_enabled": self.status_panel.osc_panel.osc_enabled.isChecked()
            }
            
            # Сохраняем настройки отправки OSC-сообщений
            broadcast_settings = self.status_panel.osc_panel.get_broadcast_settings()
            settings_dict["osc_broadcast_ip"] = broadcast_settings["ip"]
            settings_dict["osc_broadcast_port"] = broadcast_settings["port"]
            
            # Сохраняем все настройки сразу
            self.settings_manager.set_many(settings_dict)
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении настроек: {e}")
    
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        try:
            # Сохраняем настройки
            self.save_current_settings()
            
            # Останавливаем рабочие потоки
            if self.shogun_worker:
                self.shogun_worker.stop()
                self.shogun_worker.wait(1000)  # Ждем завершения потока с таймаутом
            
            # Останавливаем OSC-сервер
            if self.osc_handlers:
                self.osc_handlers.stop_osc_server()
            
            self.logger.info("Приложение закрыто")
            event.accept()
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения: {e}")
            event.accept()  # Все равно закрываем приложение