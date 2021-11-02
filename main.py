# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# Use a breakpoint in the code line below to debug your script.
# Press ⌘F8 to toggle the breakpoint.
# Imports necesarios
import json

import dash
from dash import html, callback
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from flask import Flask, request
from flask_restful import Resource, Api
import math

#### DATOS
########################################################################################################################
# Data full movies
data = pd.read_csv("data/IMDB_Movies.csv")
data = data.drop_duplicates()
data3 = data.copy()
# Movies - Limpiando
movies = data.loc[:,
         ['budget', 'gross', 'genres', 'duration', 'movie_facebook_likes', 'imdb_score', 'movie_title',
          'title_year',
          'content_rating', 'country', 'color',
          'movie_imdb_link']]  # Agregando country 20-10-21, color y movie_imdb_link 31-10-21
movies.dropna(how="any", inplace=True)
movies[['genre', 'genre_2', 'genre_3', 'genre_4']] = movies['genres'].str.split('|', 3, expand=True)
drop_columnas = ['genre_2', 'genre_3', 'genre_4', 'genres']
cols = [i for i in movies.columns if i not in drop_columnas]
movies = movies[cols]

# movies_budget_clean - Limpiando outliers
IQR = movies["budget"].quantile(.75) - movies["budget"].quantile(.25)
umbral_superior_maximo = movies["budget"].quantile(.75) + 3 * IQR
outliers_index = list(movies[movies['budget'] > umbral_superior_maximo].index)
movies_budget_clean = movies.drop(outliers_index)

IQR = movies_budget_clean["gross"].quantile(.75) - movies_budget_clean["gross"].quantile(.25)
umbral_superior_maximo = movies_budget_clean["gross"].quantile(.75) + 3 * IQR
outliers_index = list(movies_budget_clean[movies_budget_clean['gross'] > umbral_superior_maximo].index)
movies_budget_clean = movies_budget_clean.drop(outliers_index)

# movies_zero_likes - Limpiando outliers y zero likes (irreales)
mov_bak = movies_budget_clean.copy()
outliers_index = list(mov_bak[mov_bak['movie_facebook_likes'] == 0].index)
mov_bak = mov_bak.drop(outliers_index)
IQR = mov_bak["movie_facebook_likes"].quantile(.75) - mov_bak["movie_facebook_likes"].quantile(.25)
umbral_superior_maximo = mov_bak["movie_facebook_likes"].quantile(.75) + 3 * IQR
outliers_index = list(mov_bak[mov_bak['movie_facebook_likes'] > umbral_superior_maximo].index)
mov_bak = mov_bak.drop(outliers_index)

# Lista única de películas
movie_names_unique = list(movies["movie_title"].sort_values().unique())

# Lista única de géneros
genres_unique = list(movies_budget_clean["genre"].sort_values().unique())

# Lista única de categorías
categories_unique = list(movies["content_rating"].sort_values().unique())

# Lista única de países
paises_unique = list(movies["country"].sort_values().unique())

# Para el mapa de películas
data2 = data.copy()
data2[['genre', 'genre_2', 'genre_3', 'genre_4']] = data['genres'].str.split('|', 3, expand=True)
# Eliminando las columnas genre_2, genre_3 y genre_4
drop_columnas = ['genre_2', 'genre_3', 'genre_4', 'genres']
cols = [i for i in data2.columns if i not in drop_columnas]
data2 = data2[cols]
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
df = df.rename(columns={"COUNTRY": "country"})
movies_per_country = data2[["country", "genre", "movie_title"]].groupby(["country", "genre"]).count()
movies_per_country.reset_index(level=0, inplace=True)
movies_per_country.reset_index(level=0, inplace=True)
movies_country_merged = pd.merge(movies_per_country, df, how="left", on="country")
movies_country_merged = movies_country_merged.drop(columns='GDP (BILLIONS)', axis=1)
movies_country_merged[movies_country_merged['CODE'].isna()]
indices_korea = list(movies_country_merged.query("country == 'South Korea'").index)
indices_bahamas = list(movies_country_merged.query("country == 'Bahamas'").index)
indices_usa = list(movies_country_merged.query("country == 'USA'").index)
indices_uk = list(movies_country_merged.query("country == 'UK'").index)
movies_country_merged.iloc[indices_bahamas, 3] = "BHS"
movies_country_merged.iloc[indices_korea, 3] = "KOR"
movies_country_merged.iloc[indices_uk, 3] = "GBR"
movies_country_merged.iloc[indices_usa, 3] = "USA"
movies_country_merged = movies_country_merged.dropna(how="any")

### Para el presupuesto promedio por genero

movies_by_year = movies_budget_clean[["title_year", "genre", "budget"]].sort_values(
    by=["title_year", "genre"]).groupby(
    ["title_year", "genre"])
movies_average_year_genre = movies_by_year.mean(["title_year", "genre"])
movies_average_year_genre_unstack = movies_average_year_genre.unstack(level=-1)
movies_average_year_genre_unstack.columns = movies_average_year_genre_unstack.columns.droplevel()
movies_average_year_genre_unstack.reset_index(level=0, inplace=True)
movies_average_year_genre_unstack.index.names = ['Index']

# Para likes en Facebook vs votos en IMDb
IQR = movies["movie_facebook_likes"].quantile(.75) - movies["movie_facebook_likes"].quantile(.25)
umbral_superior = 110e+06  # Q3 + 1.5 IQR (box plot)
umbral_superior_maximo = movies["movie_facebook_likes"].quantile(.75) + 3 * IQR
outliers_index = list(movies[movies['movie_facebook_likes'] > umbral_superior_maximo].index)
movie_facebook_likes_clean = movies.drop(outliers_index)

IQR = movie_facebook_likes_clean["imdb_score"].quantile(.75) - movie_facebook_likes_clean["imdb_score"].quantile(
    .25)
umbral_superior = 146.405e+06  # Q3 + 1.5 IQR (box plot)
umbral_superior_maximo = movie_facebook_likes_clean["imdb_score"].quantile(.75) + 3 * IQR
outliers_index = list(
    movie_facebook_likes_clean[movie_facebook_likes_clean['imdb_score'] > umbral_superior_maximo].index)
movie_facebook_likes_clean = movie_facebook_likes_clean.drop(outliers_index)


def calcula_porcentaje(val1, val2):
    if val2 == 0:
        return 0
    return round(((val1 - val2) / val2) * 100, 2)


def layout_factory(title, color='#1f2c56'):
    layout = go.Layout(
        title=dict(text=title, y=0.92, x=0.5, xanchor='center', yanchor='top'),
        font=dict(color='white'),
        hovermode='closest',
        margin=dict(r=0),
        titlefont={'color': 'white', 'size': 20},
        paper_bgcolor='#1f2c56',
        plot_bgcolor='#1f2c56',
        legend=dict(orientation='v', bgcolor=color, xanchor='center', x=0.5, y=-0.5)
    )
    return layout


def trace_patch_factory(color='#8cf781'):
    patch = dict(
        marker_color=color
    )
    return patch


# Insertando Dash dentro de Flask


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/assets/s1-plotly.css',
            '/assets/custom-style.css'
        ]
    )

    ########################################################################################################################
    # Figuras estáticas

    fig_gross_budget = px.scatter(movies_budget_clean, x='budget', y='gross', color='genre', symbol='genre',
                                  title="Diagrama de dispersión")
    fig_gross_budget.update_layout(
        title="Diagrama de dispersión: ingreso vs presupuesto",
        xaxis_title="Presupuesto",
        yaxis_title="Ingreso",
        font=dict(
            family="Helvetica",
            size=14,
            color="Black",
        ),
    )

    movies.sort_values(by=["genre"], inplace=True)
    fig_duration_box = px.box(movies, x="genre", y="duration")
    fig_duration_box.update_layout(
        title="Diagrama de caja para los diferentes géneros de las películas",
        xaxis_title="Género",
        yaxis_title="Duración",
        font=dict(
            family="Helvetica",
            size=14,
            color="Black",
        ),
    )

    fig_duration_histogram = px.histogram(movies, x="duration",
                                          title='Histograma de la duración',
                                          opacity=0.8)
    fig_duration_histogram.update_layout(
        title="Histograma de la duración",
        xaxis_title="Duración",
        yaxis_title="Frecuencia",
        font=dict(
            family="Helvetica",
            size=18,
            color="Black"
        )
    )

    fig_gross_likes = px.scatter(mov_bak, x="movie_facebook_likes", y="gross", trendline="ols",
                                 trendline_color_override="red")

    fig_gross_likes.update_layout(
        title="Diagrama de dispersión: Ingresos vs Me gusta en Facebook (Eliminando películas con cero 'Me gusta')",
        xaxis_title="Me gusta en Facebook",
        yaxis_title="Ingresos",
        font=dict(
            family="Helvetica",
            size=18,
            color="Black"
        )
    )

    ######################################################################################################################
    ######################################################################################################################
    ## HTML
    ######################################################################################################################
    ######################################################################################################################

    # Dash
    dash_app = dash.Dash(__name__)

    dash_app.layout = html.Div(children=[

        # Cabecera
        html.Div(children=[
            html.Div(children=[

                html.Img(src="assets/claqueta.png",
                         title="Dashboard de películas",
                         style={
                             "height": "100px",
                             "width": "auto",
                             'marginBottom': "25px"
                         }, id="claqueta"),

            ], className="one-third column"),

            html.Div([
                html.Div([
                    html.H3("Movies Dashboard", style={"marginBottom": '0px', 'color': 'white'}),
                    html.H5('Equipo 12 - Analítica de datos', style={"marginBottom": '0px', 'color': 'white'})
                ])
            ], className="one-third column", id="title"),

            html.Div([
                html.Img(src="assets/uni.png",
                         title="Movies Dashboard",
                         style={
                             "height": "150px",
                             "width": "auto",
                             'marginBottom': "25px",
                             "paddingLeft": "50px",
                             "textAlign": "right"
                         }, id="uni")
            ], className="one-third column", id="title1")

        ], id="header", className="row flex display", style={'marginBottom': '25px'}),

        # Primera fila
        html.Div([
            # Dropdown de películas
            html.Div([
                html.P('Seleccionar película: ', className="fix-label", style={'color': 'white'}),
                dcc.Dropdown(id="dropdown_movies",
                             multi=False,
                             searchable=True,
                             value='The Good, the Bad and the Ugly\xa0',
                             placeholder='Select Country',
                             options=[{'label': c, 'value': c} for c in movie_names_unique],
                             # Lista de diccionarios con los paises
                             className="dcc-compon",
                             clearable=False,
                             ),
                html.H3(children='Género',
                        style={'textAlign': "center",
                               "color": "white",
                               "fontSize": 30,
                               "marginTop": "148px"
                               }
                        ),
                html.P(children="",
                       style={'textAlign': "center",
                              "color": "orange",
                              "fontSize": 40}
                       , id="movie_genre"),
            ], className="create-container three columns"),

            # KPI's rating y likes
            html.Div(children=[
                html.Div(children=[
                    dcc.Graph(id="imdb_score_kpi", config={'displayModeBar': False}, className="dcc-compon",
                              style={'marginTop': '20px'}),
                ])
                ,
                # KPI likes
                html.Div(children=[
                    dcc.Graph(id="likes_kpi", config={'displayModeBar': False}, className="dcc-compon",
                              style={'marginTop': '20px'}),
                ])
            ], className="create-container three columns"),

            # KPI's gross y budget
            html.Div(children=[
                html.Div(children=[
                    dcc.Graph(id="gross_kpi", config={'displayModeBar': False}, className="dcc-compon",
                              style={'marginTop': '20px'}),
                ]),
                html.Div(children=[
                    dcc.Graph(id="budget_kpi", config={'displayModeBar': False}, className="dcc-compon",
                              style={'marginTop': '20px'}),
                ])
            ], className="create-container three columns"),

            # KPI duration
            html.Div(children=[
                dcc.Graph(id="duration_kpi", config={'displayModeBar': False}, className="dcc-compon",
                          style={'marginTop': '20px'})
            ], className="create-container three columns"),

        ], className="row flex display")
        ,

        # Segunda fila
        html.Div([

            html.Div([
                html.P('Seleccionar género: ', className="fix-label", style={'color': 'white'}),
                dcc.Dropdown(id="dropdown_genres",
                             multi=False,
                             searchable=True,
                             value='Action',
                             placeholder='Seleccionar género',
                             options=[{'label': c, 'value': c} for c in genres_unique],
                             className="dcc-compon",
                             clearable=False,
                             ),
            ], className="create-container three columns"),

            html.Div([
                dcc.Graph(figure=fig_gross_budget, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="histogram_duration")
            ], className="card_container five columns"),

            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="box_duration")
            ], className="card_container four columns", style={"marginLeft": "2px"}, ),

        ], className="row flex display"),

        # Tercera fila
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_gross_budget, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="scatter_gross_budget")
            ], className="card_container six columns"),

            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="scatter_gross_likes")
            ], className="card_container six columns", style={"marginLeft": "2px"}),

        ], className="row flex display"),

        # Cuarta fila
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_gross_budget, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="scatter_gross_budget_clean")
            ], className="card_container six columns"),

            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="scatter_gross_likes_clean")
            ], className="card_container six columns", style={"marginLeft": "2px"}),

        ], className="row flex display"),

        # Quinta fila - Scatter Ingreso vs Presupuesto vs Score vs Países
        html.Div([
            html.Div([
                html.P('Seleccionar países: ', className="fix-label", style={'color': 'white'}),
                dcc.Dropdown(id="dropdown_countries",
                             multi=True,
                             searchable=True,
                             value=['USA', 'Canada'],
                             placeholder='Seleccionar país(es)',
                             options=[{'label': c, 'value': c} for c in paises_unique],
                             className="dcc-compon",
                             clearable=False,
                             ),
                dcc.Graph(figure=fig_duration_histogram, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="scatter_gross_budget_score_countries")
            ], className="create-container twelve columns")
        ], className="row flex display"),

        # Cuarta fila - Mapa - Choropleth
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_duration_histogram, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="choropleth")
            ], className="card_container twelve columns"),
        ], className="row flex display"),

        # Quinta fila - Slider - Cantidad de películas por país
        html.Div([
            html.Div([
                html.P('Seleccionar cantidad de países con mayor cantidad de películas: ', className="fix-label",
                       style={'color': 'white'}),
                dcc.Slider(
                    min=1,
                    max=10,
                    step=1,
                    value=5,
                    tooltip={"placement": "bottom", "always_visible": True},
                    id="top_countries_slider"
                    # className="dcc-compon",
                )
            ], className="create-container twelve columns")
        ], className="row flex display"),

        # Sexta fila - Gráficos en 3D
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="3d_score_budget_country")
            ], className="card_container six columns"),

            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="3d_score_likes_country"),
            ], className="card_container six columns"),

        ], className="row flex display"),

        # Septima  fila - Dona
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="pie_movies_country")
            ], className="card_container six columns"),
            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="pie_gross_country")
            ], className="card_container six columns"),
        ], className="row flex display"),

        # Octava  fila - Dona - Duración
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="pie_duration_range")
            ], className="card_container twelve columns"),
        ], className="row flex display"),

        # Octava fila - Presupuesto promedio anual por género y Likes vs Votos en IMDb
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="average_budget_per_genre")
            ], className="card_container six columns"),

            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="likes_votes_per_genre"),
            ], className="card_container six columns"),

        ], className="row flex display"),

        # Novena fila - Calificaciones por IMDb por género y # de películas por año
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="imdb_score_per_genre")
            ], className="card_container six columns"),

            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="movies_per_year_per_genre"),
            ], className="card_container six columns"),

        ], className="row flex display"),

        # Décima fila - Embudo de contenido por género, dropdown de categorías y categoría más rentable por categoría y
        # por género
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="funnel_category_per_genre")
            ], className="card_container four columns"),

            # Dropdown de categorías
            html.Div([
                html.P('Seleccionar categoría: ', className="fix-label", style={'color': 'white'}),
                dcc.Dropdown(id="dropdown_categories",
                             multi=False,
                             searchable=True,
                             value='R',
                             placeholder='Seleccionar género',
                             options=[{'label': c, 'value': c} for c in categories_unique],
                             className="dcc-compon",
                             clearable=False,
                             ),
            ], className="create-container three columns"),

            html.Div([
                dcc.Graph(figure=fig_duration_box, className="dcc-compon", config={'displayModeBar': 'hover'},
                          id="gross_per_category_per_genre"),
            ], className="card_container five columns"),

        ], className="row flex display"),

    ], id="mainContainer", style={'display': 'flex', 'flexDirection': 'column'})
    dash_app.title = "Movies Dashboard"
    init_callbacks(dash_app)

    return dash_app.server


##CALLBACKS
def init_callbacks(app):
    ######################################################################################################################
    ######################################################################################################################
    ## CALLBACKS
    ######################################################################################################################
    ######################################################################################################################
    @app.callback(Output('duration_kpi', 'figure'), Output('gross_kpi', 'figure'), Output('budget_kpi', 'figure'),
                  Output('likes_kpi', 'figure'), Output('imdb_score_kpi', 'figure'), Output('movie_genre', 'children'),
                  Input('dropdown_movies', 'value'))
    def update_movies_kpi(movie_title):
        genre = movies.query("movie_title == @movie_title")["genre"].iloc[0]

        movies_per_genre = movies.query("genre == @genre")

        max_duration = movies_per_genre["duration"].sort_values(ascending=False).iloc[0]
        movie_duration = movies_per_genre.query("movie_title == @movie_title")["duration"].iloc[0]

        max_gross = movies_per_genre["gross"].sort_values(ascending=False).iloc[0]
        movie_gross = movies_per_genre.query("movie_title == @movie_title")["gross"].iloc[0]

        max_budget = movies_per_genre["budget"].sort_values(ascending=False).iloc[0]
        movie_budget = movies_per_genre.query("movie_title == @movie_title")["budget"].iloc[0]

        max_likes = max_duration = movies_per_genre["movie_facebook_likes"].sort_values(ascending=False).iloc[0]
        movie_likes = movies_per_genre.query("movie_title == @movie_title")["movie_facebook_likes"].iloc[0]

        max_imdb_score = movies_per_genre["imdb_score"].sort_values(ascending=False).iloc[0]
        movie_imdb_score = movies_per_genre.query("movie_title == @movie_title")["imdb_score"].iloc[0]

        duration_kpi = go.Figure(data=go.Indicator(
            mode="number",
            delta={
                'reference': max_duration,
                # 'valueformat': '.0f',
                'relative': False,
            },
            value=movie_duration,
            # number={'suffix': " min."},
            number=dict(
                valueformat=',',
                font={'size': 50},
                suffix=' min.',
            ),
            domain={'x': [0, 1], 'y': [0, 1]},
            # title={'text': "Duración"}
        ),
            layout=go.Layout(
                title={
                    'text': 'Duración',
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 40},
                    'pad': {'b': 20}
                },
                font=dict(color='orange'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=330,
            )
        )

        gross_kpi = go.Figure(data=go.Indicator(
            mode="number+delta",
            delta={'reference': max_gross},
            value=movie_gross,
            number=dict(
                prefix='$',
                font={'size': 35}),
            domain={'y': [0, 1], 'x': [0, 1]},
        ),
            layout=go.Layout(
                title={
                    'text': 'Ingresos',
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
                height=150,
            )
        )

        budget_kpi = go.Figure(data=go.Indicator(
            mode="number+delta",
            delta={'reference': max_budget},
            value=movie_budget,
            number=dict(
                prefix='$',
                font={'size': 35}),
            domain={'y': [0, 1], 'x': [0, 1]},
        ),
            layout=go.Layout(
                title={
                    'text': 'Presupuesto',
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
                height=150,
            )
        )

        likes_kpi = go.Figure(data=go.Indicator(
            mode="number+delta",
            delta={'reference': max_likes},
            value=movie_likes,
            number=dict(
                suffix=' Likes',
                font={'size': 35}),
            domain={'y': [0, 1], 'x': [0, 1]},
        ),
            layout=go.Layout(
                title={
                    'text': 'Likes en Facebook',
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 25},
                    'pad': {'b': 20}
                },
                font=dict(color='skyblue'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=150,
            )
        )

        imdb_score_kpi = go.Figure(data=go.Indicator(
            mode="number+delta",
            delta={'reference': max_imdb_score},
            value=movie_imdb_score,
            number=dict(
                suffix=' puntos',
                font={'size': 35}),
            domain={'y': [0, 1], 'x': [0, 1]},
        ),
            layout=go.Layout(
                title={
                    'text': 'Score en IMDb',
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 25},
                    'pad': {'b': 20}
                },
                font=dict(color='skyblue'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=150,
            )
        )

        return duration_kpi, gross_kpi, budget_kpi, likes_kpi, imdb_score_kpi, genre

    @app.callback(Output('scatter_gross_budget', 'figure'), Output('scatter_gross_budget_clean', 'figure'),
                  Output('box_duration', 'figure'),
                  Output('histogram_duration', 'figure'), Output('scatter_gross_likes', 'figure'),
                  Output('scatter_gross_likes_clean', 'figure'),
                  Output('choropleth', 'figure'), Output('average_budget_per_genre', 'figure'),
                  Output('likes_votes_per_genre', 'figure'), Output("imdb_score_per_genre", "figure"),
                  Output('movies_per_year_per_genre', 'figure'), Output('funnel_category_per_genre', 'figure'),
                  Output('top_countries_slider', 'max'), Output('pie_duration_range', 'figure'),
                  Input('dropdown_genres', 'value'))
    def update_genres_charts(genre):
        movies_gross_budget_per_genre = movies.query("genre == @genre")  # movies_budget_clean
        fig_scatter_gross_budget = px.scatter(movies_gross_budget_per_genre, x='budget', y='gross', symbol='genre',
                                              title="Diagrama de dispersión", trendline="ols",
                                              trendline_color_override="red", hover_name="movie_title",
                                              hover_data=["country"])
        # color_discrete_sequence=['green'])
        fig_scatter_gross_budget.update_layout(
            title="Diagrama de dispersión: ingreso vs presupuesto",
            xaxis_title="Presupuesto",
            yaxis_title="Ingreso",
            font=dict(
                family="Helvetica",
                size=14,
                color="Black",
            ),
        )

        fig_scatter_gross_budget.update_traces(patch=trace_patch_factory())

        fig_scatter_gross_budget.update_layout(layout_factory(title="Diagrama de dispersión: ingreso vs presupuesto"))

        movies_gross_budget_per_genre_clean = movies_budget_clean.query("genre == @genre")  # movies_budget_clean
        fig_scatter_gross_budget_clean = px.scatter(movies_gross_budget_per_genre_clean, x='budget', y='gross',
                                                    symbol='genre',
                                                    title="Diagrama de dispersión", trendline="ols",
                                                    trendline_color_override="red", hover_name="movie_title",
                                                    hover_data=["country"])
        # color_discrete_sequence=['green'])
        fig_scatter_gross_budget_clean.update_layout(
            title="Diagrama de dispersión: ingreso vs presupuesto",
            xaxis_title="Presupuesto",
            yaxis_title="Ingreso",
            font=dict(
                family="Helvetica",
                size=14,
                color="Black",
            ),
        )

        fig_scatter_gross_budget_clean.update_traces(patch=trace_patch_factory())

        fig_scatter_gross_budget_clean.update_layout(
            layout_factory(title="Diagrama de dispersión: ingreso vs presupuesto (Sin outliers)"))

        movies_duration_box_genre = movies.query("genre == @genre")
        fig_boxplot_duration = px.box(movies_duration_box_genre, x="genre", y="duration", hover_name="movie_title",
                                      hover_data=["country"])
        # color_discrete_sequence=['blue'])
        fig_boxplot_duration.update_layout(
            title="Boxplot: Duración",
            xaxis_title="Género",
            yaxis_title="Duración",
            font=dict(
                family="Helvetica",
                size=14,
                color="Black",
            ),
        )
        fig_boxplot_duration.update_layout(layout_factory(title="Boxplot: duración"))
        fig_boxplot_duration.update_traces(patch=trace_patch_factory())

        movies_histogram_duration = movies.query("genre==@genre")
        fig_histogram_duration = px.histogram(movies_histogram_duration, x="duration",
                                              title='Histograma de la duración',
                                              opacity=0.8)
        fig_histogram_duration.update_layout(
            title=f"Histograma de la duración: {genre}",
            xaxis_title="Duración",
            yaxis_title="Frecuencia",
            font=dict(
                family="Helvetica",
                size=18,
                color="Black"
            )
        )

        fig_histogram_duration.update_layout(layout_factory(title=f"Histograma de la duración: {genre}"))
        fig_histogram_duration.update_traces(patch=trace_patch_factory())

        movies_scatter_gross_likes = movies.query("genre == @genre")  # mov_bak
        # Graficando la linea de tendencia
        fig_scatter_gross_likes = px.scatter(movies_scatter_gross_likes, x="movie_facebook_likes", y="gross",
                                             trendline="ols",
                                             trendline_color_override="red", hover_name="movie_title",
                                             hover_data=["country"])

        fig_scatter_gross_likes.update_layout(
            title="Diagrama de dispersión: Ingresos vs Me gusta en Facebook (Eliminando películas con cero 'Me gusta')",
            xaxis_title="Me gusta en Facebook",
            yaxis_title="Ingresos",
            font=dict(
                family="Helvetica",
                size=18,
                color="Black"
            )
        )
        fig_scatter_gross_likes.update_layout(layout_factory(title="Diagrama de dispersión: Ingresos vs Likes"))
        fig_scatter_gross_likes.update_traces(patch=trace_patch_factory())

        movies_scatter_gross_likes_clean = mov_bak.query("genre == @genre")  # mov_bak
        # Graficando la linea de tendencia
        fig_scatter_gross_likes_clean = px.scatter(movies_scatter_gross_likes_clean, x="movie_facebook_likes",
                                                   y="gross",
                                                   trendline="ols",
                                                   trendline_color_override="red", hover_name="movie_title",
                                                   hover_data=["country"])

        fig_scatter_gross_likes_clean.update_layout(
            title="Diagrama de dispersión: Ingresos vs Me gusta en Facebook (Eliminando películas con cero 'Me gusta')",
            xaxis_title="Me gusta en Facebook",
            yaxis_title="Ingresos",
            font=dict(
                family="Helvetica",
                size=18,
                color="Black"
            )
        )
        fig_scatter_gross_likes_clean.update_layout(
            layout_factory(title="Diagrama de dispersión: Ingresos vs Likes (Sin outliers)"))
        fig_scatter_gross_likes_clean.update_traces(patch=trace_patch_factory())

        movies_choropleth_genre = movies_country_merged.query("genre == @genre")
        fig_choropleth = go.Figure(data=go.Choropleth(
            locations=movies_choropleth_genre['CODE'],
            z=movies_choropleth_genre['movie_title'],
            text=movies_choropleth_genre['country'],
            colorscale='Blues',
            autocolorscale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            # colorbar_tickprefix='$',
            colorbar_title='Cantidad de películas',
        ))

        fig_choropleth.update_layout(
            title_text='Cantidad de películas por país',
            geo=dict(
                bgcolor="#1f2c56",
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
            width=1400
        )

        fig_choropleth.update_layout(layout_factory(title=f"Cantidad de películas por país, Género: {genre}"))

        fig_average_budget_per_genre = go.Figure(data=go.Bar(x=movies_average_year_genre_unstack["title_year"],
                                                             y=movies_average_year_genre_unstack[genre]))

        fig_average_budget_per_genre.update_layout(layout_factory(title=f"Presupuesto promedio por género {genre}"))

        fig_average_budget_per_genre.update_layout(
            xaxis=dict(title='<b>Años</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
            yaxis=dict(title='<b>Presupuesto promedio</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
        )

        fig_average_budget_per_genre.update_layout(layout_factory(title=f"Presupuesto promedio por género {genre}"))
        fig_average_budget_per_genre.update_traces(patch=trace_patch_factory())

        movie_facebook_likes_clean_per_genre = movie_facebook_likes_clean.query("genre == @genre")
        fig_likes_votes_per_genre = px.scatter(movie_facebook_likes_clean_per_genre, x="movie_facebook_likes",
                                               y="imdb_score", trendline="ols",
                                               trendline_color_override="red", hover_name="movie_title",
                                               hover_data=["country"])

        fig_likes_votes_per_genre.update_layout(
            title="Diagrama de dispersión: Votos de IMDB vs Likes de FB y línea de tendencia",
            xaxis_title="Votos IMDB",
            yaxis_title="Likes FB",
            font=dict(
                family="Helvetica",
                size=14,
                color="Black",
            ),
        )

        fig_likes_votes_per_genre.update_layout(
            layout_factory(title=f"Diagrama de dispersión: Votos de IMDB vs Likes de FB, género: {genre}"))
        fig_likes_votes_per_genre.update_traces(patch=trace_patch_factory())

        movies_per_genre = movies.query("genre == @genre")
        fig_imdb_score_per_genre = px.histogram(movies_per_genre, x="imdb_score",
                                                title='Distribución de calificaciones de IMDB por género',
                                                opacity=0.8)

        fig_imdb_score_per_genre.update_layout(
            layout_factory(title=f"Histograma de calificaciones en IMDB por género: {genre}"))

        fig_imdb_score_per_genre.update_layout(
            xaxis=dict(title='<b>Calificación en IMDb</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
            yaxis=dict(title='<b>Frecuencia</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
        )

        fig_imdb_score_per_genre.update_traces(xbins=dict(  # bins used for histogram
            start=0.0,
            end=10.0,
            size=1
        ))
        fig_imdb_score_per_genre.update_traces(patch=trace_patch_factory())

        number_movies_by_year = movies_per_genre[["title_year"]].sort_values(by=["title_year"]).groupby(["title_year"])
        number_movies_by_year = number_movies_by_year.size().reset_index(name='count')

        fig_movies_per_year_per_genre = go.Figure(data=go.Bar(x=number_movies_by_year["title_year"],
                                                              y=number_movies_by_year["count"]))

        fig_movies_per_year_per_genre.update_layout(
            xaxis=dict(title='<b>Años</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
            yaxis=dict(title='<b>Frecuencia</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
        )

        fig_movies_per_year_per_genre.update_layout(
            layout_factory(title=f"Cantidad de películas por año y por género: {genre}"))

        fig_movies_per_year_per_genre.update_traces(patch=trace_patch_factory())

        movies_funnel = movies_per_genre.copy()
        movies_funnel['counts'] = 1
        movies_funnel = movies_funnel.groupby(['content_rating']).sum()
        movies_funnel = movies_funnel.reset_index()
        movies_funnel = movies_funnel.sort_values('counts', ascending=False)
        fig_funnel_category_per_genre = px.funnel(movies_funnel, x='counts', y='content_rating')
        fig_funnel_category_per_genre.update_layout(
            yaxis=dict(title='<b>Categorías</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
        )

        fig_funnel_category_per_genre.update_layout(
            layout_factory(title=f"Embudo según categoría y por género: {genre}"))

        fig_funnel_category_per_genre.update_traces(patch=trace_patch_factory())

        movies_per_genre_bak = movies.query("genre == @genre")
        movies_per_genre_bak = movies_per_genre_bak.groupby("country")
        movies_per_genre_bak = movies_per_genre_bak.size().reset_index(name='count')
        top_countries_slider = len(movies_per_genre_bak)

        movies_per_genre_bak_1 = movies.query("genre == @genre")

        rango = ['Menos de 50 min', 'Entre 50 y 80 min', 'Entre 80 y 100 min', 'Entre 100 y 120 min',
                 'Entre 120 y 140 min',
                 'Entre 140 y 170 min', 'Entre 170 y 200 min', 'Más de 200 min']
        count = [0, 0, 0, 0, 0, 0, 0, 0]
        d = {'Rangos': rango, 'Cantidad': count}
        dff = pd.DataFrame(d)

        for index, row in movies_per_genre_bak_1.iterrows():
            if row["duration"] <= 50:
                dff.iat[0, 1] = dff.iat[0, 1] + 1
            elif row["duration"] > 50 and row["duration"] <= 80:
                dff.iat[1, 1] = dff.iat[1, 1] + 1
            elif row["duration"] > 80 and row["duration"] <= 100:
                dff.iat[2, 1] = dff.iat[2, 1] + 1
            elif row["duration"] > 100 and row["duration"] <= 120:
                dff.iat[3, 1] = dff.iat[3, 1] + 1
            elif row["duration"] > 120 and row["duration"] <= 140:
                dff.iat[4, 1] = dff.iat[4, 1] + 1
            elif row["duration"] > 140 and row["duration"] <= 170:
                dff.iat[5, 1] = dff.iat[5, 1] + 1
            elif row["duration"] > 170 and row["duration"] <= 200:
                dff.iat[6, 1] = dff.iat[6, 1] + 1
            elif row["duration"] > 200:
                dff.iat[7, 1] = dff.iat[7, 1] + 1

        fig_pie_duration_range = px.pie(dff, values='Cantidad', names='Rangos', title='Porcentaje por Duracion ',
                                        hole=.3)

        fig_pie_duration_range.update_layout(
            layout_factory(title=f"Rangos de duración por porcentajes, género: {genre}"))

        fig_pie_duration_range.update_layout(legend=dict(
            yanchor="top",
            y=0.0,
            xanchor="left",
            x=0.0
        ))

        return fig_scatter_gross_budget, fig_scatter_gross_budget_clean, fig_boxplot_duration, fig_histogram_duration, fig_scatter_gross_likes, \
               fig_scatter_gross_likes_clean, fig_choropleth, fig_average_budget_per_genre, fig_likes_votes_per_genre, fig_imdb_score_per_genre, \
               fig_movies_per_year_per_genre, fig_funnel_category_per_genre, top_countries_slider, fig_pie_duration_range

    @app.callback(Output('3d_score_budget_country', 'figure'), Output('3d_score_likes_country', 'figure'),
                  Output('pie_movies_country', 'figure'), Output('pie_gross_country', 'figure'),
                  Input('dropdown_genres', 'value'),
                  Input('top_countries_slider', 'value'))
    def update_3d_charts(genre, top_countries_slider_n):
        movies_per_genre_bak = movies.query("genre == @genre")
        movies_per_genre_bak = movies_per_genre_bak.groupby("country")
        movies_per_genre_bak = movies_per_genre_bak.size().reset_index(name='count')
        movies_per_genre_bak = movies_per_genre_bak.sort_values(by="count", ascending=False).iloc[
                               :top_countries_slider_n,
                               :]
        list_of_countries = list(movies_per_genre_bak["country"])
        movies_per_genre = movies.query("genre == @genre")
        movies_per_genre = movies_per_genre[movies_per_genre["country"].isin(list_of_countries)]
        fig_3d_country_budget_gross = go.Figure(data=[go.Mesh3d(x=(movies_per_genre['country']),
                                                                y=(movies_per_genre['budget']),
                                                                z=(movies_per_genre['gross']),
                                                                opacity=0.5, )])

        # xaxis.backgroundcolor is used to set background color
        fig_3d_country_budget_gross.update_layout(scene=dict(
            xaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white", ),
            yaxis=dict(
                backgroundcolor="rgb(230, 200,230)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white"),
            zaxis=dict(
                backgroundcolor="rgb(230, 230,200)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white", ), ),
            width=700,
            margin=dict(
                r=10, l=10,
                b=10, t=10)
        )

        fig_3d_country_budget_gross.update_layout(scene=dict(
            xaxis_title='X=Paises',
            yaxis_title='Y=Presupuesto',
            zaxis_title='Z=Ingreso'),
            # width=700,
            margin=dict(r=20, b=10, l=10, t=10))

        fig_3d_country_budget_gross.update_layout(
            layout_factory(title=f"Ingeso vs Presupuesto vs País: {genre} y {top_countries_slider_n} países 'top'"))

        fig_3d_score_likes_country = go.Figure(data=[go.Mesh3d(x=(movies_per_genre['country']),
                                                               y=(movies_per_genre['movie_facebook_likes']),
                                                               z=(movies_per_genre['imdb_score']),
                                                               opacity=0.5, )])

        # xaxis.backgroundcolor is used to set background color
        fig_3d_score_likes_country.update_layout(scene=dict(
            xaxis=dict(
                backgroundcolor="rgb(200, 200, 230)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white", ),
            yaxis=dict(
                backgroundcolor="rgb(230, 200,230)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white"),
            zaxis=dict(
                backgroundcolor="rgb(230, 230,200)",
                gridcolor="white",
                showbackground=True,
                zerolinecolor="white", ), ),
            width=700,
            margin=dict(
                r=10, l=10,
                b=10, t=10)
        )

        fig_3d_score_likes_country.update_layout(scene=dict(
            xaxis_title='Paises',
            yaxis_title='Likes',
            zaxis_title='IMDb Score'),
            # width=700,
            margin=dict(r=20, b=10, l=10, t=10))

        fig_3d_score_likes_country.update_layout(
            layout_factory(title=f"IMDb score vs Likes vs País: {genre} y {top_countries_slider_n} países 'top'"))

        movies_per_genre_bak_1 = movies.query("genre == @genre")
        movies_per_genre_bak_1 = movies_per_genre_bak_1.groupby("country")
        movies_per_genre_bak_1 = movies_per_genre_bak_1.size().reset_index(name='count')
        movies_per_genre_bak_1 = movies_per_genre_bak_1.sort_values(by="count", ascending=False).iloc[
                                 :top_countries_slider_n, :]
        df = movies_per_genre_bak_1
        df.loc[df['count'] < 3, 'country'] = 'Otros Paises'  # Represent only large countries
        fig_pie_movies_country = px.pie(df, values='count', names='country', title='Porcentaje por Genero ' + genre,
                                        hole=.4)
        fig_pie_movies_country.update_layout(
            layout_factory(
                title=f"Porcentaje de películas por países: {genre} y {top_countries_slider_n} países 'top'"))

        fig_pie_movies_country.update_layout(legend=dict(
            yanchor="top",
            y=0.0,
            xanchor="left",
            x=0.0
        ))

        movies_per_genre = movies.query("genre==@genre")
        movies_gross_per_country = movies_per_genre[["country", "gross"]].groupby("country")
        movies_gross_per_country = movies_gross_per_country.sum()
        movies_gross_per_country.reset_index(level=0, inplace=True)
        movies_gross_per_country = movies_gross_per_country.sort_values(by="gross", ascending=False)
        movies_gross_per_country = movies_gross_per_country.iloc[:top_countries_slider_n, :]
        fig_pie_gross_country = px.pie(movies_gross_per_country, values='gross', names='country',
                                       title='Ingreso total por país', hole=.3)

        fig_pie_gross_country.update_layout(
            layout_factory(title=f"Contribución de ingresos: {genre} y {top_countries_slider_n} países 'top'"))

        fig_pie_gross_country.update_layout(legend=dict(
            yanchor="top",
            y=0.0,
            xanchor="left",
            x=0.0
        ))

        return fig_3d_country_budget_gross, fig_3d_score_likes_country, fig_pie_movies_country, fig_pie_gross_country

    @app.callback(Output('scatter_gross_budget_score_countries', 'figure'), Input('dropdown_genres', 'value'), \
                  Input('dropdown_countries', 'value'))
    def update_scatter_budget_gross_score_country(genre, countries):
        movies_scatter_gross = movies.query("genre==@genre")
        if len(countries) == 0:
            countries = ["USA"]
        movies_scatter_gross = movies_scatter_gross[movies_scatter_gross["country"].isin(countries)]

        fig_scatter_gross_budget_score_country = px.scatter(movies_scatter_gross, x="budget", y="gross",
                                                            size="imdb_score", color="country",
                                                            hover_name="movie_title", log_x=True, size_max=60)

        fig_scatter_gross_budget_score_country.update_layout(
            layout_factory(title=f"Ingresos vs presupuesto por IMDb Score y País, Género: {genre}"))

        return fig_scatter_gross_budget_score_country

    @app.callback(Output('gross_per_category_per_genre', 'figure'), Input('dropdown_genres', 'value'), \
                  Input('dropdown_categories', 'value'))
    def update_genres_charts(genre, content_rating):
        movies_per_genre = movies.query("genre == @genre")
        movies_per_genre_per_category = movies_per_genre.query("content_rating == @content_rating")
        fig_gross_per_category_per_genre = px.bar(movies_per_genre_per_category, x="title_year", y="gross",
                                                  title="Distribución de ingresos por categoría a lo largo del tiempo"
                                                  , hover_name="movie_title")
        fig_gross_per_category_per_genre.update_layout(
            layout_factory(title=f"Ingresos por categoría a lo largo del tiempo: {genre}"))

        fig_gross_per_category_per_genre.update_layout(
            xaxis=dict(title='<b>Años</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
            yaxis=dict(title='<b>Ingresos totales</b>',
                       color='white',
                       showline=True,
                       showgrid=True),
        )
        fig_gross_per_category_per_genre.update_traces(patch=trace_patch_factory())
        return fig_gross_per_category_per_genre

    @app.callback(Output("dropdown_countries", "options"), Input("dropdown_genres", "value"))
    def update_dropdown_countries(genre):
        movies_per_genre = movies.query("genre == @genre")
        countries_per_genre = list(movies["country"].sort_values().unique())
        options = [{'label': c, 'value': c} for c in countries_per_genre]

        return options


app = Flask(__name__)
app = init_dashboard(app)
api = Api(app)

# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
# app.run_server(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

## BASE DE DATOS -- MYSQL

import mysql.connector


def conexion():
    cnx = mysql.connector.connect(user='u650849267_chatbot', password='Chatbot1',
                                  host='45.93.101.1',
                                  database='u650849267_chatbot')
    return cnx


def Inserta(json_data):

    #json_data = json.loads(json_text)

    preg = json_data['pregunta']
    resp = json_data["respuesta"]
    intent = json_data["intenciones"]
    entidades = json_data["entidades"]

    entendio = True
    if "No le he entendido. Intente reformular la consulta." in resp:
        entendio = False
    if "¿Puede expresarse con otras palabras? No le he entendido." in resp:
        entendio = False
    if "No entendí el significado." in resp:
        entendio = False
    cnx = conexion()
    cursor = cnx.cursor()
    add_data = ("INSERT INTO dialogo "
                "(pregunta, respuesta, entendio) "
                "VALUES (%s, %s, %s)")
    value_data = (preg, resp, entendio)
    cursor.execute(add_data, value_data)
    dialogo_nro = cursor.lastrowid

    if len(intent) > 0:
        for row in intent:
            cursor = cnx.cursor()
            add_data = ("INSERT INTO intencion "
                        "(intencion_detectada, grado_confianza, id_dialogo) "
                        "VALUES (%s, %s, %s)")
            value_data = (row["intent"], row["confidence"], dialogo_nro)
            cursor.execute(add_data, value_data)

    if len(entidades) > 0:
        for row in entidades:
            cursor = cnx.cursor()
            add_data = ("INSERT INTO entidad "
                        "(entity, valor, grado_confianza, id_dialogo) "
                        "VALUES (%s,%s, %s, %s)")
            value_data = (row["entity"],row["value"], row["confidence"], dialogo_nro)
            cursor.execute(add_data, value_data)

    cnx.commit()
    # cnx.rollback()
    cursor.close()
    cnx.close()


def Lee():
    cnx = conexion()
    cursor = cnx.cursor()
    query = ("SELECT * from data")
    cursor.execute(query)
    result = cursor.fetchall()
    # for row in result:
    #    print (row)
    print(result)
    cnx.close()


def LimpiaData():
    cnx = conexion()
    cursor = cnx.cursor()
    query = ("truncate table data")
    cursor.execute(query)
    cnx.close()


def genre_title_value(df, clasificacion, ascending):
    movie_title = df.sort_values(by=clasificacion, ascending=ascending)["movie_title"].iloc[0][:-1]
    value = df.sort_values(by=clasificacion, ascending=ascending)[clasificacion].iloc[0]
    movie_link = df.sort_values(by=clasificacion, ascending=ascending)["movie_imdb_link"].iloc[0]
    return movie_title, value, movie_link


# Webhook: TODO POST
class movies_genre_likes(Resource):
    def post(self):
        data = request.get_json()
        genre = data["genre"]
        likes = ("likes" in data.keys())
        gross = ("gross" in data.keys())
        duration = ("duration" in data.keys())
        budget = ("budget" in data.keys())
        imdb_score = ("imdb_score" in data.keys())
        ranking = ("ranking" in data.keys())
        if "criterio" in data.keys():
            criterio = data["criterio"]  # en base a que criterio se escoge a las tops

        if "n_top" in data.keys():
            n_top = int(data["n_top"])

        movies_genre_statistics = movies.query("genre == @genre")

        if "ascending" in data.keys():
            ascending = (data["ascending"] == "True")  # True or False

        genre_translated = ["acción", "aventura", "animación", "biografía", "comedia", "crimen", "documental", "drama",
                            "familia", "fantasía", "horror", "musical", "misterio", "romance", "ciencia ficción",
                            "thriller", "western"]
        genre_translate = {}
        for i, j in enumerate(genres_unique):
            genre_translate[j] = genre_translated[i]

        # TODO: FACTORIZAR EL CÓDIGO, EXTRAER FUNCIONALIDAD COMÚN EN UNA FUNCIÓN
        # Película con cantida de likes más alta del género $genre
        if likes:
            # Escogemos la película con más likes, así como el valor de la cantidad de likes
            movie_title, fb_likes, movie_link = genre_title_value(df=movies_genre_statistics,
                                                                  clasificacion="movie_facebook_likes",
                                                                  ascending=ascending)
            # Se tiene que pasar del int64 de numpy al de Python para poder serializar sin problemas
            return {'movie_title': movie_title, 'likes': int(fb_likes), 'genre_translated': genre_translate[genre],
                    'movie_link': movie_link}




        # Película con el ingreso más alto/bajo del género $genre
        elif gross:

            movie_title, mv_gross, movie_link = genre_title_value(df=movies_genre_statistics, clasificacion="gross",
                                                                  ascending=ascending)

            return {'movie_title': movie_title, 'gross': int(mv_gross), 'genre_translated': genre_translate[genre],
                    'movie_link': movie_link}





        # Más/menos larga
        elif duration:

            movie_title, mv_duration, movie_link = genre_title_value(df=movies_genre_statistics,
                                                                     clasificacion="duration", ascending=ascending)

            return {'movie_title': movie_title, 'duration': int(mv_duration),
                    'genre_translated': genre_translate[genre], 'movie_link': movie_link}


        # Con mayor/menor presupuesto
        elif budget:

            movie_title, mv_budget, movie_link = genre_title_value(df=movies_genre_statistics, clasificacion="budget",
                                                                   ascending=ascending)

            return {'movie_title': movie_title, 'budget': float(mv_budget),
                    'genre_translated': genre_translate[genre], 'movie_link': movie_link}




        # Mejor valorada/Peor valorada
        elif imdb_score:
            movie_title, mv_imdb_score, movie_link = genre_title_value(df=movies_genre_statistics,
                                                                       clasificacion="imdb_score", ascending=ascending)

            return {'movie_title': movie_title, 'imdb_score': float(mv_imdb_score),
                    'genre_translated': genre_translate[genre], 'movie_link': movie_link}

        elif ranking:
            movie_ranking = []
            # n_top películas por "clasificacion"
            for i in range(0, n_top):
                movie_place = {}
                movie_title = movies_genre_statistics.sort_values(by=criterio, ascending=False)["movie_title"].iloc[
                                  i][:-1]
                value = int(movies_genre_statistics.sort_values(by=criterio, ascending=False)[criterio].iloc[i])
                movie_place["movie_title"] = movie_title
                movie_place["value"] = value
                movie_ranking.append(movie_place)
            return movie_ranking


        else:
            return {'movie_title': None}


# Webhook: TODO POST
class pregunta_respuesta_chatbot(Resource):
    def post(self):
        data = request.get_json()
        #pregunta = None
        if "pregunta" in data.keys():
            pregunta = data["pregunta"]  # en base a que criterio se escoge a las tops

        respuesta = None
        if "respuesta" in data.keys():
            respuesta = data["respuesta"]

        intenciones = []
        if "intenciones" in data.keys():
            intenciones = data["intenciones"]

        entidades = []
        if "entidades" in data.keys():
            entidades = data["entidades"]

        Inserta(data)
        return {'pregunta': pregunta, 'respuesta': respuesta, "intenciones":intenciones, "entidades": entidades}, 200

# Webhook: TODO POST
class pelicula_estadistica(Resource):
    def post(self):
        data = request.get_json()
        colores = ("colores" in data.keys()) # Para activar: devolver colores, se puede añadir más funcionalidad
        movie_director = ("movie_director" in data.keys())  # Para activar: devolver colores, se puede añadir más funcionalidad
        movie_title = None
        # Carga datos según el nombre de la película
        if "movie_title" in data.keys():
            movie_title = data["movie_title"]  # Nombre de la película, la validación se hace en el chatbot
            movie_title += "\xa0" # Porque se codificó con ANSI, y debería ser con UTF-8
            color = movies.query("movie_title == @movie_title")["color"].values[0]
            year = int(movies.query("movie_title == @movie_title")["title_year"].values[0])
            movie_link = movies.query("movie_title == @movie_title")["movie_imdb_link"].values[0]
            movie_director_data = data3[["movie_title", "director_name"]]
            director = movie_director_data.query("movie_title == @movie_title")["director_name"].values[0]
            if color == " Black and White":
                color = "blanco y negro"
            else:
                color = "colores"
        movie_title = movie_title[:-1]  # Elimina el espacio posterior (trailing spaces)
        if colores:
            return {"movie_title": movie_title, "color":color,"year":year, "movie_link": movie_link}
        if movie_director:
            return {"movie_title": movie_title, "director":director,"year":year, "movie_link": movie_link}


# Responde a la pregunta: "Cuál es la película del genero $genre con más $likes (likes == si está presente o no)"

api.add_resource(movies_genre_likes, '/genre_likes')
api.add_resource(pregunta_respuesta_chatbot, '/estadisticas_chatbot')
api.add_resource(pelicula_estadistica, '/estadisticas_peliculas')

if __name__ == '__main__':
    app.run(debug=True)
