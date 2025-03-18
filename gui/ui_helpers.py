"""
Вспомогательные функции интерфейса для ShogunOSC.
Содержит функции для работы с темами и диалогами.
"""

import logging
import traceback
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

import config
from styles.app_styles import get_palette, get_stylesheet

class UIHelpers:
    """Класс для функций интерфейса"""
    
    def __init__(self, main_window):
        """
        Инициализация помощников интерфейса
        
        Args:
            main_window: Ссылка на главное окно приложения
        """
        self.main_window = main_window
        self.logger = logging.getLogger('ShogunOSC')
        self.settings_manager = config.settings_manager
    
    def apply_theme(self, dark_mode=False):
        """Применяет выбранную тему ко всему приложению"""
        try:
            # Обновляем настройку темной темы в конфигурации
            config.DARK_MODE = dark_mode
            self.settings_manager.set("dark_mode", dark_mode)
            
            # Применяем палитру и стили
            palette = get_palette(dark_mode)
            stylesheet = get_stylesheet(dark_mode)
            
            # Устанавливаем палитру и стилевую таблицу для приложения
            app = QApplication.instance()
            app.setPalette(palette)
            app.setStyleSheet(stylesheet)
            
            # Уведомляем пользователя о смене темы
            theme_name = "тёмная" if dark_mode else "светлая"
            self.main_window.status_bar.showMessage(f"Применена {theme_name} тема", 3000)
            
            # Обновляем состояние радиокнопок
            self.update_theme_buttons()
        except Exception as e:
            self.logger.error(f"Ошибка при применении темы: {e}")
    
    def update_theme_buttons(self):
        """Обновляет состояние радиокнопок темы в соответствии с текущими настройками"""
        dark_mode = self.settings_manager.get("dark_mode")
        self.main_window.light_theme_radio.setChecked(not dark_mode)
        self.main_window.dark_theme_radio.setChecked(dark_mode)
    
    def on_theme_button_clicked(self, button):
        """Обработчик нажатия на кнопки переключения темы"""
        dark_mode = button == self.main_window.dark_theme_radio
        self.apply_theme(dark_mode)
    
    def show_error_dialog(self, title, message):
        """Показывает диалоговое окно с ошибкой"""
        try:
            error_dialog = QMessageBox(self.main_window)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle(title)
            error_dialog.setText(message)
            error_dialog.setStandardButtons(QMessageBox.Ok)
            error_dialog.exec_()
        except Exception as e:
            self.logger.error(f"Ошибка при отображении диалога с ошибкой: {e}")
    
    def show_about(self):
        """Отображает окно 'О программе'"""
        about_text = (
            "<h2>Shogun OSC GUI</h2>"
            "<p>Приложение для управления Shogun Live через OSC-протокол</p>"
            f"<p>Версия: {config.APP_VERSION}</p>"
            "<p>Лицензия: MIT</p>"
        )
        
        # Используем QMessageBox для отображения информации
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("О программе")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()
        
        # Также добавляем в лог
        self.logger.info(f"О программе: Shogun OSC GUI v{config.APP_VERSION}")
