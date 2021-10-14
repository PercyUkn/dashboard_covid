# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# Use a breakpoint in the code line below to debug your script.
# Press ⌘F8 to toggle the breakpoint.
# Imports necesarios
import dash
from dash import html, callback
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import math

url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
             "/csse_covid_19_time_series/time_series_covid19_deaths_global.csv "
url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
                "/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv "
url_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
                "/csse_covid_19_time_series/time_series_covid19_recovered_global.csv "

#### DATOS
########################################################################################################################
confirmed = pd.read_csv(url_confirmed)
deaths = pd.read_csv(url_deaths)
recovered = pd.read_csv(url_recovered)

# confirmed unpivot
columnas_quedan = confirmed.columns[:4]
date1 = confirmed.columns[4:]
total_confirmed = confirmed.melt(id_vars=columnas_quedan, value_vars=date1, var_name="date", value_name="confirmed")
# deaths unpivot
columnas_quedan2 = deaths.columns[:4]
date2 = deaths.columns[4:]
total_deaths = deaths.melt(id_vars=columnas_quedan2, value_vars=date2, var_name="date", value_name="death")
# recovered unpivot
columnas_quedan3 = recovered.columns[:4]
date3 = recovered.columns[4:]
total_recovered = recovered.melt(id_vars=columnas_quedan3, value_vars=date3, var_name="date", value_name="recovered")

# Combinando todos los datos
covid_data = total_confirmed.merge(right=total_recovered, how="left",
                                   on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'])
covid_data = covid_data.merge(right=total_deaths, how="left",
                              on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'])
# Convirtiendo la fecha de string a datetime
covid_data["date"] = pd.to_datetime(covid_data["date"])

# Llenando con valores los na
covid_data["recovered"] = covid_data["recovered"].fillna(0)
# Convertir de float a int
covid_data["recovered"] = covid_data["recovered"].astype(int)

# Calculando los casos activos
covid_data["active"] = covid_data["confirmed"] - covid_data["recovered"] - covid_data["death"]

# Calculando los confirmados, recuperados y muertos actualmente
covid_data1 = covid_data.groupby("date")[["date", "confirmed", "recovered", "death", "active"]].sum().reset_index()

countries = list(covid_data["Country/Region"].sort_values().unique())

# Agrupando por país y fecha, para los KPI's por país
covid_data2 = covid_data.groupby(["date", "Country/Region"])[
    ["confirmed", "recovered", "death", "active"]].sum().reset_index()


def calcula_porcentaje(val1, val2):
    if val2 == 0:
        return 0
    return round(((val1 - val2) / val2) * 100, 2)


######################################################################################################################
######################################################################################################################
## HTML
######################################################################################################################
######################################################################################################################

# Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[

    # Cabecera
    html.Div(children=[
        html.Div(children=[

            html.Img(src="assets/covid_logo.png",
                     title="Covid Dashboard",
                     style={
                         "height": "60px",
                         "width": "auto",
                         'marginBottom': "25px"
                     }, id="covid_logo"),

        ], className="one-third column"),

        html.Div([
            html.Div([
                html.H3("Covid -19", style={"marginBottom": '0px', 'color': 'white'}),
                html.H5('Track Covid -19 Cases', style={"marginBottom": '0px', 'color': 'white'})
            ])
        ], className="one-third column", id="title"),

        html.Div([
            html.H6('Last updated: ' + str(covid_data["date"].iloc[-1].strftime("%d/%m/%y")),
                    style={'color': 'orange', "textAlign": "right"})
        ], className="one-third column", id="title1")

    ], id="header", className="row flex display", style={'marginBottom': '25px'}),

    # Primera fila
    html.Div([
        html.Div([
            html.H6(children='Global cases',
                    style={'textAlign': "center",
                           "color": "white",
                           "fontSize": 30}
                    ),
            html.P(f"{covid_data1['confirmed'].iloc[-1]:,.0f}",
                   style={'textAlign': "center",
                          "color": "orange",
                          "fontSize": 40}
                   ),
            html.P('new: ' + f'{covid_data1["confirmed"].iloc[-1] - covid_data1["confirmed"].iloc[-2]:,.0f}' +
                   " (" + str(round(((covid_data1["confirmed"].iloc[-1] - covid_data1["confirmed"].iloc[-2])
                                     / covid_data1["confirmed"].iloc[-2]) * 100, 2)) + "%)",
                   style={
                       'textAlign': 'center',
                       'color': 'orange',
                       'fontSize': 18,
                       'marginTop': '-10px'
                   }
                   )
        ], className="card_container three columns"),

        html.Div([
            html.H6(children='Global deaths',
                    style={'textAlign': "center",
                           "color": "white",
                           "fontSize": 30}
                    ),
            html.P(f"{covid_data1['confirmed'].iloc[-1]:,.0f}",
                   style={'textAlign': "center",
                          "color": "red",
                          "fontSize": 40}
                   ),
            html.P('new: ' + f'{covid_data1["death"].iloc[-1] - covid_data1["death"].iloc[-2]:,.0f}' +
                   " (" + str(
                calcula_porcentaje(val1=covid_data1["death"].iloc[-1], val2=covid_data1["death"].iloc[-2])) + "%)",
                   style={
                       'textAlign': 'center',
                       'color': 'red',
                       'fontSize': 18,
                       'marginTop': '-10px'
                   }
                   )
        ], className="card_container three columns"),

        html.Div([
            html.H6(children='Global recovered',
                    style={'textAlign': "center",
                           "color": "white",
                           "fontSize": 30}
                    ),
            html.P(f"{covid_data1['recovered'].iloc[-1]:,.0f}",
                   style={'textAlign': "center",
                          "color": "green",
                          "fontSize": 40}
                   ),
            html.P('new: ' + f'{covid_data1["recovered"].iloc[-1] - covid_data1["recovered"].iloc[-2]:,.0f}' +
                   " (" + str(calcula_porcentaje(val1=covid_data1["recovered"].iloc[-1],
                                                 val2=covid_data1["recovered"].iloc[-2])) + "%)",
                   style={
                       'textAlign': 'center',
                       'color': 'green',
                       'fontSize': 18,
                       'marginTop': '-10px'
                   }
                   )
        ], className="card_container three columns"),

        html.Div([
            html.H6(children='Global active',
                    style={'textAlign': "center",
                           "color": "white",
                           "fontSize": 30}
                    ),
            html.P(f"{covid_data1['active'].iloc[-1]:,.0f}",
                   style={'textAlign': "center",
                          "color": "yellow",
                          "fontSize": 40}
                   ),
            html.P('new: ' + f'{covid_data1["active"].iloc[-1] - covid_data1["active"].iloc[-2]:,.0f}' +
                   " (" + str(
                calcula_porcentaje(val1=covid_data1["active"].iloc[-1], val2=covid_data1["active"].iloc[-2])) + "%)",
                   style={
                       'textAlign': 'center',
                       'color': 'yellow',
                       'fontSize': 18,
                       'marginTop': '-10px'
                   }
                   )
        ], className="card_container three columns")

    ], className="row flex display"),

    # Segunda fila
    html.Div([
        # Dropdown + 4 KPI's por país
        html.Div([
            html.P('Select country: ', className="fix-label", style={'color': 'white'}),
            dcc.Dropdown(id="w_countries",
                         multi=False,
                         searchable=True,
                         value='Peru',
                         placeholder='Select Country',
                         options=[{'label': c, 'value': c} for c in countries],  # Lista de diccionarios con los paises
                         className="dcc-compon",
                         clearable=False
                         ),
            html.P('New Cases: ' + str(covid_data["date"].iloc[-1].strftime("%d/%m/%y")),
                   style={'textAlign': "center",
                          "color": "white",
                          "fontSize": 25}
                   ),
            dcc.Graph(id="confirmed", config={'displayModeBar': False}, className="dcc-compon",
                      style={'marginTop': '20px'}),
            dcc.Graph(id="death", config={'displayModeBar': False}, className="dcc-compon",
                      style={'marginTop': '20px'}),
            dcc.Graph(id="recovered", config={'displayModeBar': False}, className="dcc-compon",
                      style={'marginTop': '20px'}),
            dcc.Graph(id="active", config={'displayModeBar': False}, className="dcc-compon",
                      style={'marginTop': '20px'})
        ], className="create-container three columns"),

        # Donut chart con Confirmados = Activos + Muertos + Recuperados (por país)
        html.Div(children=[
            dcc.Graph(id="donut_chart", className="dcc-compon", config={'displayModeBar': 'hover'})
        ], className="create-container four columns"),

        # Line Chart (30 días de incremento, y en barra los totales)
        html.Div(children=[
            dcc.Graph(id="line_chart", className="dcc-compon", config={'displayModeBar': 'hover'})
        ], className="create-container five columns")

    ], className="row flex display")

], id="mainContainer", style={'display': 'flex', 'flexDirection': 'column'})


######################################################################################################################
######################################################################################################################
## CALLBACKS
######################################################################################################################
######################################################################################################################
@app.callback(Output('confirmed', 'figure'), Output('death', 'figure'), Output('recovered', 'figure'),
              Output('active', 'figure'), Output(component_id="donut_chart", component_property="figure"),
              Output('line_chart', 'figure'), [Input('w_countries', 'value')])
def update_confirmed(w_country):
    value_confirmed = covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-1] - \
                      covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-2]
    delta_confirmed = covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-2] - \
                      covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-3]

    value_death = covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-1] - \
                  covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-2]
    delta_death = covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-2] - \
                  covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-3]

    value_recovered = covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-1] - \
                      covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-2]
    delta_recovered = covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-2] - \
                      covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-3]

    value_active = covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-1] - \
                   covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-2]
    delta_active = covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-2] - \
                   covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-3]

    figs = []
    fig_confirmed = go.Figure(
        data=go.Indicator(
            mode="number+delta",
            value=value_confirmed,
            delta=dict(
                position="right",
                reference=delta_confirmed,
                valueformat='.0f',
                relative=False,
                font={'size': 20}),
            number=dict(
                valueformat=',',
                font={'size': 25}),
            domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
        ),
        layout=go.Layout(
            title={
                'text': 'New confirmed',
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 25},
                'pad': {'b': 20}
            },
            font=dict(color='orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=100,
        )

    )

    fig_death = go.Figure(
        data=go.Indicator(
            mode="number+delta",
            value=value_death,
            delta=dict(
                position="right",
                reference=delta_death,
                valueformat='.0f',
                relative=False,
                font={'size': 20}),
            number=dict(
                valueformat=',',
                font={'size': 25}),
            domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
        ),
        layout=go.Layout(
            title={
                'text': 'New deaths',
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 25},
                'pad': {'b': 20}
            },
            font=dict(color='red'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=100,
        )

    )

    fig_recovered = go.Figure(
        data=go.Indicator(
            mode="number+delta",
            value=value_recovered,
            delta=dict(
                position="right",
                reference=delta_recovered,
                valueformat='.0f',
                relative=False,
                font={'size': 20}),
            number=dict(
                valueformat=',',
                font={'size': 25}),
            domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
        ),
        layout=go.Layout(
            title={
                'text': 'New recovered',
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 25},
                'pad': {'b': 20}
            },
            font=dict(color='green'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=100,
        )

    )

    fig_active = go.Figure(
        data=go.Indicator(
            mode="number+delta",
            value=value_active,
            delta=dict(
                position="right",
                reference=delta_active,
                valueformat='.0f',
                relative=False,
                font={'size': 20}),
            number=dict(
                valueformat=',',
                font={'size': 25}),
            domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
        ),
        layout=go.Layout(
            title={
                'text': 'New active',
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 25},
                'pad': {'b': 20}
            },
            font=dict(color='yellow'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=100,
        )

    )

    figs.append([fig_confirmed, fig_death, fig_recovered])

    confirmed = covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-1]
    death = covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-1]
    recovered = covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-1]
    active = covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-1]
    values = [active, recovered, death]
    dict_pasa = {}
    for i, v in enumerate(values):
        if v != 0:
            if i == 0:
                dict_pasa["Actives"] = (values[i], "yellow")
            if i == 1:
                dict_pasa["Recovered"] = (values[i], "green")
            if i == 2:
                dict_pasa["Death"] = (values[i], "red")
    labels = list(dict_pasa.keys())
    values = []
    colors = []
    for v, c in dict_pasa.values():
        values.append(v)
        colors.append(c)

    fig_donut = go.Figure(
        data=go.Pie(
            labels=labels,
            values=values,
            hoverinfo='label+value+percent',
            marker=dict(colors=colors),
            textinfo='label+value',
            hole=.7,
            rotation=90,
            #insidetextorientation='radial'
        ),
        layout=go.Layout(
            title={'text': f'Confirmed Cases: {confirmed}',
                   'y': 0.92,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='white'),
            hovermode='closest',
            margin=dict(r=0),
            titlefont={'color': 'white', 'size': 20},
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={
                'orientation': 'v',
                'bgcolor': '#1f2c56',
                'xanchor': 'center',
                'x': 0.5,
                'y': -0.5
            }
        )
    )

    covid_data3 = covid_data2[covid_data2["Country/Region"] == w_country][["Country/Region", "date", "confirmed"]]
    # Usando shift para desplazar una fila
    covid_data3["daily increase"] = covid_data3["confirmed"] - covid_data3["confirmed"].shift(1)

    # Calculando el promedio móvil de 7 días
    covid_data3["Rolling Ave"] = covid_data3['daily increase'].rolling(window=7).mean()

    fig_line = go.Figure(
        data=[
            go.Bar(
                x=covid_data3['date'].tail(30),
                y=covid_data3['daily increase'].tail(30),
                name='Daily Confirmed Cases',
                marker=dict(color='orange'),
                hoverinfo='text',
                hovertext=
                '<b>Date: </b>' + covid_data3['date'].tail(30).astype(str) + '<br>' +
                '<b>Daily Confirmed Cases: </b>' + [f'{x: .0f}' for x in
                                                    covid_data3['daily increase'].tail(30)] + '<br>' +
                '<b>Country: </b>' + covid_data3['Country/Region'].tail(30).astype(str) + '<br>'
            ),
            go.Scatter(
                x=covid_data3['date'].tail(30),
                y=covid_data3['Rolling Ave'].tail(30),
                mode='lines',
                name='Rolling Average of the last 7 days - daily confirmed cases',
                marker=dict(color='#FF00FF'),
                hoverinfo='text',
                hovertext=
                '<b>Date: </b>' + covid_data3['date'].tail(30).astype(str) + '<br>' +
                '<b>Average of last 7 days: </b>' + [f'{x: .0f}' for x in
                                                    covid_data3['Rolling Ave'].tail(30)] + '<br>'
            )
        ],
        layout=go.Layout(
            title={'text': f'Last Daily Confirmed Cases',
                   'y': 0.92,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='white'),
            hovermode='closest',
            titlefont={'color': 'white', 'size': 20},
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={
                'orientation': 'v',
                'bgcolor': '#1f2c56',
                'xanchor': 'center',
                'x': 0.5,
                'y': -0.5
            },
            margin=dict(r=1),
            xaxis=dict(title='<b>Date</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='white',
                       linewidth=1,
                       gridwidth=0.1,
                       gridcolor='#fff',
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
            yaxis=dict(title='<b>Daily Confirmed Cases</b>',
                       color='white',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       gridwidth=0.1,
                       linecolor='white',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='white',
                           size=12
                       )),
        ),
    )

    return fig_confirmed, fig_death, fig_recovered, fig_active, fig_donut, fig_line


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
