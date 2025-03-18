"""
Диалог настроек приложения ShogunOSC.
Позволяет пользователю настраивать различные параметры приложения.
"""

import os
import logging
import traceback
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox, 
                           QPushButton, QGroupBox, QFormLayout, QFileDialog,
                           QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import Qt

import config

class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    
    def __init__(self, parent=None):
        """
        Инициализация диалога настроек
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.logger = logging.getLogger('ShogunOSC')
        self.settings_manager = config.settings_manager
        
        # Копия настроек для отмены изменений
        self.original_settings = self.settings_manager.get_all()
        self.current_settings = self.original_settings.copy()
        
        # Инициализация UI
        try:
            self.init_ui()
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации диалога настроек: {e}\n{traceback.format_exc()}")
            raise
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Настройки приложения")
        self.setMinimumSize(500, 400)
        
        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        
        # Создаем вкладки для разных категорий настроек
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Создаем вкладки для разных групп настроек
        try:
            self.create_general_tab()
            self.create_osc_tab()
            self.create_logging_tab()
        except Exception as e:
            self.logger.error(f"Ошибка при создании вкладок настроек: {e}\n{traceback.format_exc()}")
            raise
        
        # Создаем кнопки "ОК", "Отмена", "Применить"
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        # Добавляем кнопку "Сбросить к значениям по умолчанию"
        reset_button = QPushButton("Сбросить настройки")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_box.addButton(reset_button, QDialogButtonBox.ResetRole)
        
        main_layout.addWidget(button_box)
        
    def create_general_tab(self):
        """Создание вкладки с общими настройками"""
        general_tab = QWidget()
        layout = QVBoxLayout(general_tab)
        
        # Группа "Внешний вид"
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QFormLayout(appearance_group)
        
        # Чекбокс "Темная тема"
        self.dark_mode_checkbox = QCheckBox("Использовать темную тему")
        self.dark_mode_checkbox.setChecked(self.current_settings.get("dark_mode", False))
        appearance_layout.addRow(self.dark_mode_checkbox)
        
        layout.addWidget(appearance_group)
        
        # Добавляем растягивающийся пробел в конец для компактного отображения
        layout.addStretch(1)
        
        self.tab_widget.addTab(general_tab, "Общие")
        
    def create_osc_tab(self):
        """Создание вкладки с настройками OSC"""
        osc_tab = QWidget()
        layout = QVBoxLayout(osc_tab)
        
        # Группа "Настройки OSC-сервера"
        server_group = QGroupBox("OSC-сервер (прием команд)")
        server_layout = QFormLayout(server_group)
        
        # Чекбокс "Включить OSC-сервер при запуске"
        self.osc_enabled_checkbox = QCheckBox("Включить OSC-сервер при запуске")
        self.osc_enabled_checkbox.setChecked(self.current_settings.get("osc_enabled", True))
        server_layout.addRow(self.osc_enabled_checkbox)
        
        # Строка ввода IP-адреса
        self.osc_ip_input = QLineEdit(self.current_settings.get("osc_ip", "0.0.0.0"))
        server_layout.addRow("IP-адрес:", self.osc_ip_input)
        
        # Поле ввода порта
        self.osc_port_input = QSpinBox()
        self.osc_port_input.setRange(1024, 65535)
        self.osc_port_input.setValue(self.current_settings.get("osc_port", 5555))
        server_layout.addRow("Порт:", self.osc_port_input)
        
        layout.addWidget(server_group)
        
        # Группа "Настройки отправки OSC-сообщений"
        broadcast_group = QGroupBox("Отправка OSC-сообщений")
        broadcast_layout = QFormLayout(broadcast_group)
        
        # Строка ввода IP-адреса для отправки
        self.osc_broadcast_ip_input = QLineEdit(self.current_settings.get("osc_broadcast_ip", "255.255.255.255"))
        broadcast_layout.addRow("IP-адрес:", self.osc_broadcast_ip_input)
        
        # Поле ввода порта для отправки
        self.osc_broadcast_port_input = QSpinBox()
        self.osc_broadcast_port_input.setRange(1024, 65535)
        self.osc_broadcast_port_input.setValue(self.current_settings.get("osc_broadcast_port", 9000))
        broadcast_layout.addRow("Порт:", self.osc_broadcast_port_input)
        
        layout.addWidget(broadcast_group)
        
        # Добавляем растягивающийся пробел в конец для компактного отображения
        layout.addStretch(1)
        
        self.tab_widget.addTab(osc_tab, "OSC")
        
    def create_logging_tab(self):
        """Создание вкладки с настройками логирования"""
        logging_tab = QWidget()
        layout = QVBoxLayout(logging_tab)
        
        # Группа "Настройки логирования"
        logging_group = QGroupBox("Настройки логирования")
        logging_layout = QFormLayout(logging_group)
        
        # Выбор уровня логирования
        self.log_level_combo = QComboBox()
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.log_level_combo.addItems(log_levels)
        current_level = self.current_settings.get("log_level", "INFO").upper()
        self.log_level_combo.setCurrentText(current_level if current_level in log_levels else "INFO")
        logging_layout.addRow("Уровень логирования:", self.log_level_combo)
        
        # Чекбокс "Включить логирование в файл"
        self.log_to_file_checkbox = QCheckBox("Включить логирование в файл")
        self.log_to_file_checkbox.setChecked(self.current_settings.get("log_to_file", True))
        logging_layout.addRow(self.log_to_file_checkbox)
        
        # Директория для логов
        log_dir_widget = QWidget()
        self.log_dir_layout = QHBoxLayout(log_dir_widget)
        self.log_dir_layout.setContentsMargins(0, 0, 0, 0)
        
        self.log_dir_input = QLineEdit(self.current_settings.get("log_dir", ""))
        self.log_dir_input.setPlaceholderText("Директория для логов (пусто = по умолчанию)")
        self.log_dir_layout.addWidget(self.log_dir_input)
        
        # Кнопка выбора директории
        select_dir_button = QPushButton("Обзор...")
        select_dir_button.clicked.connect(self.select_log_directory)
        self.log_dir_layout.addWidget(select_dir_button)
        
        logging_layout.addRow("Директория для логов:", log_dir_widget)
        
        # Показываем текущую директорию для логов по умолчанию
        try:
            default_log_dir = self.settings_manager.get_logs_dir()
            log_dir_label = QLabel(f"Текущая директория: {default_log_dir}")
            log_dir_label.setStyleSheet("color: gray;")
            logging_layout.addRow("", log_dir_label)
        except Exception as e:
            self.logger.error(f"Ошибка при получении директории логов: {e}")
        
        layout.addWidget(logging_group)
        
        # Добавляем растягивающийся пробел в конец для компактного отображения
        layout.addStretch(1)
        
        self.tab_widget.addTab(logging_tab, "Логирование")
    
    def select_log_directory(self):
        """Диалог выбора директории для логов"""
        try:
            current_dir = self.log_dir_input.text() or self.settings_manager.get_logs_dir()
            
            directory = QFileDialog.getExistingDirectory(
                self, 
                "Выберите директорию для логов",
                current_dir,
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
            )
            
            if directory:
                self.log_dir_input.setText(directory)
        except Exception as e:
            self.logger.error(f"Ошибка при выборе директории для логов: {e}")
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Не удалось выбрать директорию: {e}"
            )
    
    def collect_settings(self) -> Dict[str, Any]:
        """
        Сбор настроек из интерфейса
        
        Returns:
            Dict[str, Any]: Словарь с настройками из интерфейса
        """
        settings = {}
        
        try:
            # Общие настройки
            settings["dark_mode"] = self.dark_mode_checkbox.isChecked()
            
            # OSC настройки
            settings["osc_enabled"] = self.osc_enabled_checkbox.isChecked()
            settings["osc_ip"] = self.osc_ip_input.text()
            settings["osc_port"] = self.osc_port_input.value()
            settings["osc_broadcast_ip"] = self.osc_broadcast_ip_input.text()
            settings["osc_broadcast_port"] = self.osc_broadcast_port_input.value()
            
            # Настройки логирования
            settings["log_level"] = self.log_level_combo.currentText()
            settings["log_to_file"] = self.log_to_file_checkbox.isChecked()
            settings["log_dir"] = self.log_dir_input.text()
        except Exception as e:
            self.logger.error(f"Ошибка при сборе настроек: {e}\n{traceback.format_exc()}")
        
        return settings
    
    def apply_settings(self):
        """Применение изменений настроек"""
        try:
            new_settings = self.collect_settings()
            
            # Проверяем и создаем директорию для логов если указана и не существует
            log_dir = new_settings.get("log_dir")
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir)
                    self.logger.info(f"Создана директория для логов: {log_dir}")
                except OSError as e:
                    self.logger.error(f"Ошибка создания директории для логов: {e}")
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        f"Не удалось создать директорию для логов: {e}"
                    )
                    return False
            
            # Сохраняем настройки
            self.settings_manager.set_many(new_settings)
            self.logger.info("Настройки применены")
            
            # Обновляем локальную копию настроек
            self.original_settings = self.settings_manager.get_all()
            self.current_settings = self.original_settings.copy()
            
            return True
        except Exception as e:
            error_msg = f"Ошибка при применении настроек: {e}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось применить настройки: {e}"
            )
            return False
    
    def accept(self):
        """Обработка нажатия кнопки "ОК" - применить и закрыть"""
        if self.apply_settings():
            super().accept()
    
    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        try:
            # Запрашиваем подтверждение
            result = QMessageBox.question(
                self,
                "Сброс настроек",
                "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if result != QMessageBox.Yes:
                return
            
            # Сбрасываем настройки к значениям по умолчанию
            self.settings_manager.reset()
            self.logger.info("Настройки сброшены к значениям по умолчанию")
            
            # Обновляем интерфейс
            self.original_settings = self.settings_manager.get_all()
            self.current_settings = self.original_settings.copy()
            
            # Обновляем содержимое виджетов
            self.dark_mode_checkbox.setChecked(self.current_settings.get("dark_mode", False))
            self.osc_enabled_checkbox.setChecked(self.current_settings.get("osc_enabled", True))
            self.osc_ip_input.setText(self.current_settings.get("osc_ip", "0.0.0.0"))
            self.osc_port_input.setValue(self.current_settings.get("osc_port", 5555))
            self.osc_broadcast_ip_input.setText(self.current_settings.get("osc_broadcast_ip", "255.255.255.255"))
            self.osc_broadcast_port_input.setValue(self.current_settings.get("osc_broadcast_port", 9000))
            self.log_level_combo.setCurrentText(self.current_settings.get("log_level", "INFO").upper())
            self.log_to_file_checkbox.setChecked(self.current_settings.get("log_to_file", True))
            self.log_dir_input.setText(self.current_settings.get("log_dir", ""))
        except Exception as e:
            error_msg = f"Ошибка при сбросе настроек: {e}"
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сбросить настройки: {e}"
            )
