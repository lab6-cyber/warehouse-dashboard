import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table

# Загрузка данных по умолчанию
df_default = pd.read_csv('data/warehouse_data.csv')
df_default['date'] = pd.to_datetime(df_default['date'])

# Инициализация приложения
app = Dash(__name__)
app.title = 'Складской дашборд'


# Функция для создания линейного графика (временной ряд)
def create_time_series(data):
    fig = px.line(data, x='date', y=['revenue', 'cost', 'profit'],
                  title='Динамика доходов и расходов',
                  labels={'value': 'Сумма (руб)', 'variable': 'Показатель'})
    fig.update_layout(legend=dict(orientation='h', y=1.1))
    return fig


# Функция для создания круговой диаграммы
def create_pie_chart(data):
    category_costs = data.groupby('product_category')['cost'].sum().reset_index()
    fig = px.pie(category_costs, values='cost', names='product_category',
                 title='Структура расходов по категориям')
    return fig


# Функция для создания гистограммы
def create_histogram(data):
    fig = px.histogram(data, x='profit', nbins=30,
                       title='Распределение прибыли по операциям',
                       labels={'profit': 'Прибыль (руб)'})
    return fig


# Функция для агрегации данных по периоду
def aggregate_by_period(data, period):
    data = data.set_index('date')
    aggregated = data.resample(period).agg({
        'revenue': 'sum',
        'cost': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()
    return aggregated


# Макет дашборда
app.layout = html.Div([
    # Заголовок
    html.Div([
        html.H1('Дашборд анализа складских операций'),
        html.P('Интерактивная панель для мониторинга ключевых показателей склада')
    ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px'}),

    # Панель управления
    html.Div([
        html.H3('Панель управления'),

        # Выпадающий список
        html.Label('Выберите период агрегации:'),
        dcc.Dropdown(
            id='period-selector',
            options=[
                {'label': 'День', 'value': 'D'},
                {'label': 'Неделя', 'value': 'W'},
                {'label': 'Месяц', 'value': 'M'},
                {'label': 'Квартал', 'value': 'Q'}
            ],
            value='M',
            clearable=False,
            style={'width': '300px', 'marginBottom': '20px'}
        ),

        # Загрузчик файлов
        html.Label('Загрузите свой CSV-файл:'),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Перетащите файл или ',
                html.A('выберите файл')
            ]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center',
                'marginBottom': '20px', 'backgroundColor': '#f9f9f9'
            },
            multiple=False
        )
    ], style={'padding': '20px'}),

    # Первый ряд графиков
    html.Div([
        html.Div([
            dcc.Graph(id='time-series')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='pie-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    # Второй ряд графиков
    html.Div([
        html.Div([
            dcc.Graph(id='histogram')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.H3('Детальные данные'),
            html.Div(id='data-table')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ])
])

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)