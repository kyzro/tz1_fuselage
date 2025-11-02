import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from stl_processor import load_stl, calc_xyz_len
from logger import logger, setup_widget

class FuselageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Фюзерезка 1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        
        self.create_widgets()
        
        setup_widget(self.log_text)
        
        self.log_text.config(state=tk.NORMAL)
        self.make_logs_readonly()
    
    def make_logs_readonly(self):
        """Делает поле логов только для чтения (кроме программной вставки)"""
        def deny_write(event):
            if event.state & 0x4 and event.keysym in ['c', 'C']:
                return None
            return "break"
        
        self.log_text.bind('<Key>', deny_write)
        self.create_context_menu()
    
    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        header_label = ttk.Label(main_frame, text="Обработка STL фюзеляжа", style='Header.TLabel')
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 1. Поле для выбора STL файла
        ttk.Label(main_frame, text="STL файл:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.stl_path = tk.StringVar()
        stl_frame = ttk.Frame(main_frame)
        stl_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        stl_frame.columnconfigure(0, weight=1)
        
        stl_entry = ttk.Entry(stl_frame, textvariable=self.stl_path)
        stl_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        stl_button = ttk.Button(stl_frame, text="Обзор", command=self.browse_stl_file)
        stl_button.grid(row=0, column=1)
        
        # 2. Поле для выбора файла вывода
        ttk.Label(main_frame, text="Выходной файл:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar(value="result.data")
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        output_button = ttk.Button(output_frame, text="Обзор", command=self.browse_output_file)
        output_button.grid(row=0, column=1)
        
        # 3. Параметры обработки
        params_frame = ttk.LabelFrame(main_frame, text="Параметры обработки", padding="10")
        params_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        params_frame.columnconfigure(1, weight=1)
        
        # Количество сечений
        ttk.Label(params_frame, text="Количество сечений:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sections_count = tk.IntVar(value=10)
        sections_spin = ttk.Spinbox(params_frame, from_=2, to=100, textvariable=self.sections_count, width=10)
        sections_spin.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Количество точек
        ttk.Label(params_frame, text="Точек на сечение:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.points_count = tk.IntVar(value=30)
        points_spin = ttk.Spinbox(params_frame, from_=10, to=500, textvariable=self.points_count, width=10)
        points_spin.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 4. Кнопка запуска
        self.process_button = ttk.Button(main_frame, text="Запустить обработку", command=self.process_stl)
        self.process_button.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 5. Поле для логов
        log_frame = ttk.LabelFrame(main_frame, text="Логи выполнения", padding="5")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 6. Кнопки управления логами
        log_buttons_frame = ttk.Frame(main_frame)
        log_buttons_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        log_buttons_frame.columnconfigure(0, weight=1)

        # Кнопка копирования логов
        copy_button = ttk.Button(log_buttons_frame, text="Скопировать логи", command=self.copy_all_logs)
        copy_button.grid(row=0, column=0, sticky=tk.W)

        # Кнопка очистки логов
        clear_button = ttk.Button(log_buttons_frame, text="Очистить логи", command=self.clear_logs)
        clear_button.grid(row=0, column=1, sticky=tk.E)
    
    def create_context_menu(self):
        """Создает контекстное меню для поля логов"""
        self.context_menu = tk.Menu(self.log_text, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_selected_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Копировать все логи", command=self.copy_all_logs)
        
        # Привязываем контекстное меню к правой кнопке мыши
        self.log_text.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Показывает контекстное меню"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_selected_text(self):
        """Копирует выделенный текст в буфер обмена"""
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                logger.info("Выделенный текст скопирован в буфер обмена")
        except tk.TclError:
            # Если ничего не выделено
            logger.warning("Не выделен текст для копирования")

    def copy_all_logs(self):
        """Копирует все логи в буфер обмена"""
        all_text = self.log_text.get(1.0, tk.END)
        if all_text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(all_text)
            logger.info("Все логи скопированы в буфер обмена")
        else:
            logger.warning("Нет логов для копирования")
    
    def browse_stl_file(self):
        """Выбор STL файла"""
        filename = filedialog.askopenfilename(
            title="Выберите STL файл",
            filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
        )
        if filename:
            self.stl_path.set(filename)
            logger.info(f"Выбран STL файл: {filename}")
    
    def browse_output_file(self):
        """Выбор файла вывода"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить result.data",
            defaultextension=".data",
            filetypes=[("Data files", "*.data"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            logger.info(f"Выходной файл: {filename}")
    
    def process_stl(self):
        """Обработка STL файла"""
        if not self.stl_path.get():
            logger.error("Необходимо выбрать STL файл!")
            return
        
        if not self.output_path.get():
            logger.error("Не указан выходной файл для данных!")
            return
        
        try:
            logger.info("=" * 50)
            logger.info(f"Обработка файла: {self.stl_path.get()}")
            logger.info(f"{self.sections_count.get()} сечений по {self.sections_count.get()} точек")
            logger.info(f"Выходной файл: {self.output_path.get()}")
            
            # Загрузка STL
            mesh = load_stl(self.stl_path.get())
            
            # Вычисление размеров
            dimensions = calc_xyz_len(mesh)
            
            # Нарезка на сечения
            from make_sections import slice_fuselage, visualize_sections
            sections_data = slice_fuselage(mesh, self.sections_count.get(), 
                                           self.points_count.get())
            
            if not sections_data:
                logger.error("Сечения не были получены!")
                return
            
            # Визуализация сечений
            visualize_sections(sections_data)
            
            # Экспорт в файл
            from exporter import export_to_data
            export_to_data(sections_data, self.output_path.get())
            
            logger.info(f"Успешно было получено {len(sections_data)} сечений!")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке: {str(e)}")

    def clear_logs(self):
        """Очистка логов"""
        self.log_text.delete(1.0, tk.END)
        logger.info("Логи очищены")
