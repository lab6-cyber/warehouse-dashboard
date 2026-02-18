import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table, no_update, ctx
import base64
import io

# Загрузка данных по умолчанию
try:
    df_default = pd.read_csv('data/warehouse_data.csv')
    df_default['date'] = pd.to_datetime(df_default['date'])
except FileNotFoundError:
    # Если файл не найден, создаем пустой DataFrame
    df_default = pd.DataFrame(columns=['date', 'product_category', 'operation_type',
                                       'quantity', 'revenue', 'cost', 'profit',
                                       'employee', 'warehouse_zone'])
    print("Предупреждение: файл data/warehouse_data.csv не найден. Используются пустые данные.")

# Инициализация приложения
app = Dash(__name__)
app.title = 'Складской дашборд'


# Функция для создания линейного графика (временной ряд)
def create_time_series(data):
    if data.empty:
        fig = px.line(title='Нет данных для отображения')
    else:
        fig = px.line(data, x='date', y=['revenue', 'cost', 'profit'],
                      title='Динамика доходов и расходов',
                      labels={'value': 'Сумма (руб)', 'variable': 'Показатель'})
        fig.update_layout(legend=dict(orientation='h', y=1.1))
    return fig


# Функция для создания круговой диаграммы
def create_pie_chart(data):
    if data.empty:
        fig = px.pie(title='Нет данных для отображения')
    else:
        category_costs = data.groupby('product_category')['cost'].sum().reset_index()
        fig = px.pie(category_costs, values='cost', names='product_category',
                     title='Структура расходов по категориям')
    return fig


# Функция для создания гистограммы
def create_histogram(data):
    if data.empty:
        fig = px.histogram(title='Нет данных для отображения')
    else:
        fig = px.histogram(data, x='profit', nbins=30,
                           title='Распределение прибыли по операциям',
                           labels={'profit': 'Прибыль (руб)'})
    return fig


# Функция для агрегации данных по периоду - ИСПРАВЛЕНО для новых версий Pandas
def aggregate_by_period(data, period):
    if data.empty:
        return data

    # Словарь для преобразования старых обозначений в новые
    period_mapping = {
        'D': 'D',  # День (без изменений)
        'W': 'W',  # Неделя (без изменений)
        'M': 'ME',  # Месяц -> Month End
        'Q': 'QE'  # Квартал -> Quarter End
    }

    # Получаем правильное обозначение периода
    pandas_period = period_mapping.get(period, period)

    data = data.set_index('date')
    aggregated = data.resample(pandas_period).agg({
        'revenue': 'sum',
        'cost': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()
    return aggregated


# Функция для проверки версии Pandas (для информационных целей)
def get_pandas_version_info():
    import pandas as pd
    version = pd.__version__
    major_version = int(version.split('.')[0])
    return version, major_version


# Макет дашборда
app.layout = html.Div([
    # Заголовок
    html.Div([
        html.H1('Дашборд анализа складских операций'),
        html.P('Интерактивная панель для мониторинга ключевых показателей склада')
    ], style={'textAlign': 'center', 'backgroundColor': '#2c3e50',
              'color': 'white', 'padding': '20px', 'borderRadius': '5px'}),

    # Панель управления
    html.Div([
        html.H3('Панель управления', style={'color': '#2c3e50',
                                            'borderBottom': '2px solid #3498db',
                                            'paddingBottom': '10px'}),

        html.Label('Выберите период агрегации:', style={'fontWeight': 'bold'}),
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

        html.Label('Загрузите свой CSV-файл:', style={'fontWeight': 'bold'}),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Перетащите файл или ',
                html.A('выберите файл', style={'color': '#3498db', 'fontWeight': 'bold'})
            ]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '2px', 'borderStyle': 'dashed',
                'borderRadius': '5px', 'textAlign': 'center',
                'marginBottom': '20px', 'backgroundColor': '#f9f9f9',
                'cursor': 'pointer', 'borderColor': '#3498db'
            },
            multiple=False
        )
    ], style={'padding': '20px', 'margin': '10px', 'backgroundColor': 'white',
              'borderRadius': '5px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

    # Первый ряд графиков
    html.Div([
        html.Div([
            dcc.Graph(id='time-series')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px',
                  'backgroundColor': 'white', 'borderRadius': '5px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '10px'}),

        html.Div([
            dcc.Graph(id='pie-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px',
                  'backgroundColor': 'white', 'borderRadius': '5px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '10px'})
    ]),

    # Второй ряд графиков
    html.Div([
        html.Div([
            dcc.Graph(id='histogram')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px',
                  'backgroundColor': 'white', 'borderRadius': '5px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '10px'}),

        html.Div([
            html.H3('Детальные данные', style={'color': '#2c3e50', 'marginTop': '0'}),
            html.Div(id='data-table')
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px',
                  'backgroundColor': 'white', 'borderRadius': '5px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'margin': '10px'})
    ])
], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'})


# Callback для обновления всех элементов
@app.callback(
    Output('time-series', 'figure'),
    Output('pie-chart', 'figure'),
    Output('histogram', 'figure'),
    Output('data-table', 'children'),
    Input('upload-data', 'contents'),
    Input('period-selector', 'value')
)
def update_dashboard(contents, period):
    # Определяем источник данных
    if not ctx.triggered:
        df = df_default.copy()
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'upload-data' and contents is not None:
            # Загружаем пользовательский файл
            try:
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                df['date'] = pd.to_datetime(df['date'])
            except Exception as e:
                # В случае ошибки показываем сообщение
                error_message = html.Div([
                    html.P('Ошибка загрузки файла. Проверьте формат CSV.',
                           style={'color': 'red', 'fontWeight': 'bold'}),
                    html.P(f'Детали: {str(e)}', style={'color': 'red', 'fontSize': '12px'})
                ])
                return (no_update, no_update, no_update, error_message)
        else:
            df = df_default.copy()

    if df.empty:
        empty_message = html.Div('Нет данных для отображения',
                                 style={'padding': '20px', 'textAlign': 'center'})
        empty_fig = px.line(title='Нет данных')
        return empty_fig, empty_fig, empty_fig, empty_message

    # Агрегация по периоду для линейного графика
    try:
        df_aggregated = aggregate_by_period(df, period)
    except Exception as e:
        # Если ошибка агрегации, показываем сообщение
        error_message = html.Div([
            html.P(f'Ошибка агрегации данных: {str(e)}',
                   style={'color': 'red', 'fontWeight': 'bold'})
        ])
        empty_fig = px.line(title='Ошибка агрегации')
        return empty_fig, empty_fig, empty_fig, error_message

    # Создание графиков
    time_series_fig = create_time_series(df_aggregated)
    pie_chart_fig = create_pie_chart(df)
    histogram_fig = create_histogram(df)

    # Создание таблицы
    table = dash_table.DataTable(
        data=df.head(20).to_dict('records'),
        columns=[{'name': i, 'id': i} for i in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px', 'fontFamily': 'Arial'},
        style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
        style_data={'backgroundColor': 'white'},
        filter_action='native',
        sort_action='native',
        filter_options={'placeholder_text': 'Фильтр...'}
    )

    return time_series_fig, pie_chart_fig, histogram_fig, table


# Запуск приложения
if __name__ == '__main__':
    pandas_version, major_version = get_pandas_version_info()
    print(f"Запуск дашборда")
    print(f"URL: http://127.0.0.1:8050")
    app.run(debug=True)