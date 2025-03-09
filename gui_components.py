import tkinter as tk
from tkinter import messagebox, ttk


class ElectricityGUI:
    def __init__(self, root, db_manager, calculator):
        self.root = root
        self.db_manager = db_manager
        self.calculator = calculator

        self.root.geometry("350x325")
        self.root.minsize(350, 325)
        self.root.configure(padx=20, pady=20)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Номер лічильника", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.meter_entry = tk.Entry(self.root, width=20, font=("Arial", 10))
        self.meter_entry.grid(row=0, column=1, sticky="w", pady=5)
        self.meter_entry.bind("<KeyRelease>", lambda event: self.update_previous_readings())
        self.prev_readings_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.prev_readings_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        tk.Label(self.root, text="Новий показник (день)", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.day_entry = tk.Entry(self.root, width=20, font=("Arial", 10))
        self.day_entry.grid(row=2, column=1, sticky="w", pady=5)
        tk.Label(self.root, text="Новий показник (ніч)", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.night_entry = tk.Entry(self.root, width=20, font=("Arial", 10))
        self.night_entry.grid(row=3, column=1, sticky="w", pady=5)
        empty_label = tk.Label(self.root, text="", height=1)
        empty_label.grid(row=4, column=0, columnspan=2, pady=5)
        calc_button = tk.Button(self.root, text="Розрахувати", command=self.calculate_bill,
                                height=1, width=15, font=("Arial", 10))
        calc_button.grid(row=5, column=0, columnspan=2, pady=5)
        history_button = tk.Button(self.root, text="Переглянути історію", command=self.view_history,
                                   height=1, width=15, font=("Arial", 10))
        history_button.grid(row=6, column=0, columnspan=2, pady=5)
        self.result_label = tk.Label(self.root, text="", font=("Arial", 11, "bold"))
        self.result_label.grid(row=7, column=0, columnspan=2, sticky="w", pady=10)

    def update_previous_readings(self):
        meter_id = self.meter_entry.get().strip()
        if not meter_id:
            self.prev_readings_label.config(text="")
            return

        last_reading = self.db_manager.get_last_reading(meter_id)
        if last_reading:
            _, prev_day, prev_night = last_reading
            self.prev_readings_label.config(text=f"Попередні показники. День: {prev_day}, Ніч: {prev_night}")
        else:
            self.prev_readings_label.config(text="Попередні показники відсутні.")

    def show_custom_warning(self, message, adjustment_value, is_day_reading=True):
        dialog = tk.Toplevel(self.root)
        dialog.title("Попередження")
        dialog.geometry("400x150")
        dialog.configure(padx=20, pady=20)
        dialog.grab_set()  # Make the dialog modal
        dialog.resizable(False, False)
        message_label = tk.Label(dialog, text=message, font=("Arial", 10), wraplength=360, justify="left")
        message_label.pack(fill="x", expand=True, pady=10)
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", side="bottom", pady=(10, 0))
        result = [False]

        def on_ok():
            result[0] = True
            dialog.destroy()

        def on_back():
            result[0] = False
            dialog.destroy()

        back_button = tk.Button(button_frame, text="Назад", command=on_back, width=10)
        back_button.pack(side="left", padx=(0, 10))
        ok_button = tk.Button(button_frame, text="OK", command=on_ok, width=10)
        ok_button.pack(side="right")
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        self.root.wait_window(dialog)
        return result[0]

    def calculate_bill(self):
        meter_id = self.meter_entry.get().strip()
        if not meter_id:
            messagebox.showerror("Помилка", "Введіть номер лічильника!")
            return

        try:
            day_kwh = int(self.day_entry.get().strip())
            night_kwh = int(self.night_entry.get().strip())

            if day_kwh < 0 or night_kwh < 0:
                messagebox.showerror("Помилка", "Показники не можуть бути від'ємними!")
                return
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректні числові значення!")
            return

        last_reading = self.db_manager.get_last_reading(meter_id)

        if last_reading is None:
            prev_day, prev_night = 0, 0
            self.db_manager.add_new_meter(meter_id)
        else:
            _, prev_day, prev_night = last_reading

        if day_kwh < prev_day:
            warning_msg = f"Показник 'день' менший за попередній! Додаємо 100 кВт?"
            proceed = self.show_custom_warning(warning_msg, 100, is_day_reading=True)
            if proceed:
                day_kwh += 100
            else:
                self.day_entry.focus_set()
                return

        if night_kwh < prev_night:
            warning_msg = f"Показник 'ніч' менший за попередній! Додаємо 80 кВт?"
            proceed = self.show_custom_warning(warning_msg, 80, is_day_reading=False)
            if proceed:
                night_kwh += 80
            else:
                self.night_entry.focus_set()
                return

        day_rate, night_rate, day_adj, night_adj = self.db_manager.get_tariffs()

        day_usage = day_kwh - prev_day
        night_usage = night_kwh - prev_night
        total_cost = day_usage * day_rate + night_usage * night_rate
        self.db_manager.update_meter_reading(meter_id, day_kwh, night_kwh)
        self.db_manager.add_to_history(meter_id, day_usage, night_usage, total_cost)
        self.result_label.config(text=f"Сума до сплати: {total_cost:.2f} грн.")
        self.update_previous_readings()

    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Історія лічильника")
        history_window.geometry("500x400")
        history_window.configure(padx=20, pady=20)
        top_frame = tk.Frame(history_window)
        top_frame.pack(fill="x", pady=(0, 10))
        tk.Label(top_frame, text="Введіть номер лічильника:", font=("Arial", 10), anchor="w").pack(side="left",
                                                                                                   padx=(0, 10))
        meter_id_entry = tk.Entry(top_frame, width=15, font=("Arial", 10))
        meter_id_entry.pack(side="left")
        table_frame = tk.Frame(history_window)
        table_frame.pack(fill="both", expand=True)
        columns = ("Дата", "КВт (день)", "КВт (ніч)", "Сума (грн)")
        history_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        for col in columns:
            history_tree.heading(col, text=col)

        history_tree.column("Дата", width=120, anchor="center")
        history_tree.column("КВт (день)", width=100, anchor="center")
        history_tree.column("КВт (ніч)", width=100, anchor="center")
        history_tree.column("Сума (грн)", width=120, anchor="center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=scrollbar.set)
        history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        bottom_frame = tk.Frame(history_window)
        bottom_frame.pack(fill="x", side="bottom", pady=(10, 0))

        show_button = tk.Button(
            bottom_frame,
            text="Показати історію",
            command=lambda: show_history(meter_id_entry.get().strip(), history_tree),
            height=1,
            width=20,
            font=("Arial", 10)
        )
        show_button.pack(side="bottom")

        def show_history(meter_id, tree):
            if not meter_id:
                messagebox.showerror("Помилка", "Введіть номер лічильника!")
                return

            records = self.db_manager.get_history(meter_id)
            for row in tree.get_children():
                tree.delete(row)

            if records:
                for record in records:
                    tree.insert("", "end", values=record)
            else:
                messagebox.showinfo("Інформація", "Історія для цього лічильника відсутня.")

        meter_id_entry.bind("<Return>", lambda event: show_history(meter_id_entry.get().strip(), history_tree))
