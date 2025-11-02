import logging
import tkinter as tk

class GUILogger(logging.Handler):
    """
    Выводит логи в поле для логов на окне tkinter
    """
    def __init__(self, text_widget = None):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
    
    def set_text_widget(self, text_widget: tk.Text):
        """Установка текстового виджета для вывода логов"""
        self.text_widget = text_widget
    
    def emit(self, record):
        """Вывод сообщения в виджет"""
        try:
            msg = self.format(record)
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.update_idletasks()
        except Exception as e:
            print(f"Ошибка при попытке вывести сообщение на виджет: {e}")

logger = logging.getLogger('Logger')
logger.setLevel(logging.INFO)
handler = GUILogger()
logger.addHandler(handler)

def setup_widget(text_widget: tk.Text):
    """Настройка логгера с текстовым виджетом"""
    handler.set_text_widget(text_widget)
