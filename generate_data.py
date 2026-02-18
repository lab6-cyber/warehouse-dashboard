import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Параметры генерации
start_date = datetime(2026, 1, 1)
num_records = 500

# Категории товаров
categories = ['Электроника', 'Мебель', 'Продукты', 'Одежда', 'Книги', 'Бытовая химия']
operations = ['Приемка', 'Отгрузка', 'Возврат']
employees = ['Иванов', 'Петров', 'Сидоров', 'Смирнова', 'Козлов', 'Морозова']
zones = ['Зона А', 'Зона Б', 'Зона В', 'Зона Г']

# Генерация данных
np.random.seed(42)
data = []

for i in range(num_records):
    date = start_date + timedelta(days=np.random.randint(0, 90))
    category = np.random.choice(categories)
    operation = np.random.choice(operations, p=[0.3, 0.6, 0.1])
    quantity = np.random.randint(1, 100)

    if operation == 'Отгрузка':
        revenue = quantity * np.random.randint(500, 5000)
        cost = revenue * np.random.uniform(0.6, 0.8)
    elif operation == 'Приемка':
        revenue = 0
        cost = quantity * np.random.randint(300, 3000)
    else:  # Возврат
        revenue = -quantity * np.random.randint(500, 5000)
        cost = -revenue * np.random.uniform(0.5, 0.7)

    profit = revenue - cost
    employee = np.random.choice(employees)
    zone = np.random.choice(zones)

    data.append([date.strftime('%Y-%m-%d'), category, operation, quantity,
                 revenue, cost, profit, employee, zone])

# Создание DataFrame
df = pd.DataFrame(data, columns=['date', 'product_category', 'operation_type',
                                 'quantity', 'revenue', 'cost', 'profit',
                                 'employee', 'warehouse_zone'])

# Сохранение в CSV
df.to_csv('data/warehouse_data.csv', index=False)
print('Данные успешно сгенерированы и сохранены в data/warehouse_data.csv')
