from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Дашборд анализа складских операций'),
    html.P('Тестовое приложение')
])

if __name__ == '__main__':
    app.run_server(debug=True)