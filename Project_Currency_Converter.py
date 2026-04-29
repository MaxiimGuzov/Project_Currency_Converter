import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import datetime

API_KEY = 'ВАШ_API_КЛЮЧ'  # замените на ваш API-ключ
HISTORY_FILE = 'history.json'

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        
        self.currencies = ['USD', 'EUR', 'RUB', 'GBP', 'JPY']  # список валют
        self.create_widgets()
        self.load_history()
        
    def create_widgets(self):
        # Валюты "от" и "куда"
        ttk.Label(self.root, text="Из:").grid(row=0, column=0, padx=5, pady=5)
        self.from_currency = ttk.Combobox(self.root, values=self.currencies)
        self.from_currency.current(0)
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.root, text="В:").grid(row=0, column=2, padx=5, pady=5)
        self.to_currency = ttk.Combobox(self.root, values=self.currencies)
        self.to_currency.current(1)
        self.to_currency.grid(row=0, column=3, padx=5, pady=5)
        
        # Поле суммы
        ttk.Label(self.root, text="Сумма:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Кнопка конвертации
        self.convert_button = ttk.Button(self.root, text="Конвертировать", command=self.convert)
        self.convert_button.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        # Таблица истории
        self.tree = ttk.Treeview(self.root, columns=('from', 'to', 'amount', 'result', 'date'), show='headings')
        self.tree.heading('from', text='Из')
        self.tree.heading('to', text='В')
        self.tree.heading('amount', text='Сумма')
        self.tree.heading('result', text='Результат')
        self.tree.heading('date', text='Дата')
        self.tree.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        
    def load_history(self):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
            for item in history:
                self.tree.insert('', 'end', values=(item['from'], item['to'], item['amount'], item['result'], item['date']))
        except FileNotFoundError:
            pass
    
    def save_history(self, record):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
        history.append(record)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
    
    def get_exchange_rate(self, base, target):
        url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}'
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200 or 'conversion_rates' not in data:
            messagebox.showerror("Ошибка", "Не удалось получить курсы валют.")
            return None
        return data['conversion_rates'].get(target)
    
    def convert(self):
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        amount_str = self.amount_entry.get()
        
        # Проверка ввода
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Введите положительное число.")
            return
        
        # Получение курса
        rate = self.get_exchange_rate(from_curr, to_curr)
        if rate is None:
            return
        result = amount * rate
        
        # Обновление таблицы истории
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            'from': from_curr,
            'to': to_curr,
            'amount': amount,
            'result': result,
            'date': date_str
        }
        self.tree.insert('', 'end', values=(from_curr, to_curr, amount, result, date_str))
        self.save_history(record)

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
