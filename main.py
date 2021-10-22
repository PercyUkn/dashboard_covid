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
import plotly.express as px
import math

# url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
#              "/csse_covid_19_time_series/time_series_covid19_deaths_global.csv "
# url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
#                 "/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv "
# url_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data" \
#                 "/csse_covid_19_time_series/time_series_covid19_recovered_global.csv "

#### DATOS
########################################################################################################################
# confirmed = pd.read_csv(url_confirmed)
# deaths = pd.read_csv(url_deaths)
# recovered = pd.read_csv(url_recovered)

# Data full movies
data = pd.read_csv("data/IMDB_Movies.csv")
data = data.drop_duplicates()

# Movies - Limpiando
movies = data.loc[:,
         ['budget', 'gross', 'genres', 'duration', 'movie_facebook_likes', 'imdb_score', 'movie_title', 'title_year',
          'content_rating', 'country']]  # Agregando country 20-10-21
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

movies_by_year = movies_budget_clean[["title_year", "genre", "budget"]].sort_values(by=["title_year", "genre"]).groupby(
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

IQR = movie_facebook_likes_clean["imdb_score"].quantile(.75) - movie_facebook_likes_clean["imdb_score"].quantile(.25)
umbral_superior = 146.405e+06  # Q3 + 1.5 IQR (box plot)
umbral_superior_maximo = movie_facebook_likes_clean["imdb_score"].quantile(.75) + 3 * IQR
outliers_index = list(
    movie_facebook_likes_clean[movie_facebook_likes_clean['imdb_score'] > umbral_superior_maximo].index)
movie_facebook_likes_clean = movie_facebook_likes_clean.drop(outliers_index)

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

########################################################################################################################


# # confirmed unpivot
# columnas_quedan = confirmed.columns[:4]
# date1 = confirmed.columns[4:]
# total_confirmed = confirmed.melt(id_vars=columnas_quedan, value_vars=date1, var_name="date", value_name="confirmed")
# # deaths unpivot
# columnas_quedan2 = deaths.columns[:4]
# date2 = deaths.columns[4:]
# total_deaths = deaths.melt(id_vars=columnas_quedan2, value_vars=date2, var_name="date", value_name="death")
# # recovered unpivot
# columnas_quedan3 = recovered.columns[:4]
# date3 = recovered.columns[4:]
# total_recovered = recovered.melt(id_vars=columnas_quedan3, value_vars=date3, var_name="date", value_name="recovered")
#
# # Combinando todos los datos
# covid_data = total_confirmed.merge(right=total_recovered, how="left",
#                                    on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'])
# covid_data = covid_data.merge(right=total_deaths, how="left",
#                               on=['Province/State', 'Country/Region', 'Lat', 'Long', 'date'])
# # Convirtiendo la fecha de string a datetime
# covid_data["date"] = pd.to_datetime(covid_data["date"])
#
# # Llenando con valores los na
# covid_data["recovered"] = covid_data["recovered"].fillna(0)
# # Convertir de float a int
# covid_data["recovered"] = covid_data["recovered"].astype(int)
#
# # Calculando los casos activos
# covid_data["active"] = covid_data["confirmed"] - covid_data["recovered"] - covid_data["death"]
#
# # Calculando los confirmados, recuperados y muertos actualmente
# covid_data1 = covid_data.groupby("date")[["date", "confirmed", "recovered", "death", "active"]].sum().reset_index()
#
# countries = list(covid_data["Country/Region"].sort_values().unique())
#
# # Agrupando por país y fecha, para los KPI's por país
# covid_data2 = covid_data.groupby(["date", "Country/Region"])[
#     ["confirmed", "recovered", "death", "active"]].sum().reset_index()


########################################################################################################################

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

    # # Undécima fila
    # html.Div([
    #     html.Div([
    #         html.H6(children='Global cases',
    #                 style={'textAlign': "center",
    #                        "color": "white",
    #                        "fontSize": 30}
    #                 ),
    #         html.P(f"{covid_data1['confirmed'].iloc[-1]:,.0f}",
    #                style={'textAlign': "center",
    #                       "color": "orange",
    #                       "fontSize": 40}
    #                ),
    #         html.P(children='new: ' + f'{covid_data1["confirmed"].iloc[-1] - covid_data1["confirmed"].iloc[-2]:,.0f}' +
    #                         " (" + str(round(((covid_data1["confirmed"].iloc[-1] - covid_data1["confirmed"].iloc[-2])
    #                                           / covid_data1["confirmed"].iloc[-2]) * 100, 2)) + "%)",
    #                style={
    #                    'textAlign': 'center',
    #                    'color': 'orange',
    #                    'fontSize': 18,
    #                    'marginTop': '-10px'
    #                }
    #                )
    #     ], className="card_container three columns"),
    #
    #     html.Div([
    #         html.H6(children='Global deaths',
    #                 style={'textAlign': "center",
    #                        "color": "white",
    #                        "fontSize": 30}
    #                 ),
    #         html.P(f"{covid_data1['confirmed'].iloc[-1]:,.0f}",
    #                style={'textAlign': "center",
    #                       "color": "red",
    #                       "fontSize": 40}
    #                ),
    #         html.P('new: ' + f'{covid_data1["death"].iloc[-1] - covid_data1["death"].iloc[-2]:,.0f}' +
    #                " (" + str(
    #             calcula_porcentaje(val1=covid_data1["death"].iloc[-1], val2=covid_data1["death"].iloc[-2])) + "%)",
    #                style={
    #                    'textAlign': 'center',
    #                    'color': 'red',
    #                    'fontSize': 18,
    #                    'marginTop': '-10px'
    #                }
    #                )
    #     ], className="card_container three columns"),
    #
    #     html.Div([
    #         html.H6(children='Global recovered',
    #                 style={'textAlign': "center",
    #                        "color": "white",
    #                        "fontSize": 30}
    #                 ),
    #         html.P(f"{covid_data1['recovered'].iloc[-1]:,.0f}",
    #                style={'textAlign': "center",
    #                       "color": "green",
    #                       "fontSize": 40}
    #                ),
    #         html.P('new: ' + f'{covid_data1["recovered"].iloc[-1] - covid_data1["recovered"].iloc[-2]:,.0f}' +
    #                " (" + str(calcula_porcentaje(val1=covid_data1["recovered"].iloc[-1],
    #                                              val2=covid_data1["recovered"].iloc[-2])) + "%)",
    #                style={
    #                    'textAlign': 'center',
    #                    'color': 'green',
    #                    'fontSize': 18,
    #                    'marginTop': '-10px'
    #                }
    #                )
    #     ], className="card_container three columns"),
    #
    #     html.Div([
    #         html.H6(children='Global active',
    #                 style={'textAlign': "center",
    #                        "color": "white",
    #                        "fontSize": 30}
    #                 ),
    #         html.P(f"{covid_data1['active'].iloc[-1]:,.0f}",
    #                style={'textAlign': "center",
    #                       "color": "yellow",
    #                       "fontSize": 40}
    #                ),
    #         html.P('new: ' + f'{covid_data1["active"].iloc[-1] - covid_data1["active"].iloc[-2]:,.0f}' +
    #                " (" + str(
    #             calcula_porcentaje(val1=covid_data1["active"].iloc[-1], val2=covid_data1["active"].iloc[-2])) + "%)",
    #                style={
    #                    'textAlign': 'center',
    #                    'color': 'yellow',
    #                    'fontSize': 18,
    #                    'marginTop': '-10px'
    #                }
    #                )
    #     ], className="card_container three columns")
    #
    # ], className="row flex display"),
    #
    # # Décima fila
    # html.Div([
    #     # Dropdown + 4 KPI's por país
    #     html.Div([
    #         html.P('Select country: ', className="fix-label", style={'color': 'white'}),
    #         dcc.Dropdown(id="w_countries",
    #                      multi=False,
    #                      searchable=True,
    #                      value='Peru',
    #                      placeholder='Select Country',
    #                      options=[{'label': c, 'value': c} for c in countries],  # Lista de diccionarios con los paises
    #                      className="dcc-compon",
    #                      clearable=False
    #                      ),
    #         html.P('New Cases: ' + str(covid_data["date"].iloc[-1].strftime("%d/%m/%y")),
    #                style={'textAlign': "center",
    #                       "color": "white",
    #                       "fontSize": 25}
    #                ),
    #         dcc.Graph(id="confirmed", config={'displayModeBar': False}, className="dcc-compon",
    #                   style={'marginTop': '20px'}),
    #         dcc.Graph(id="death", config={'displayModeBar': False}, className="dcc-compon",
    #                   style={'marginTop': '20px'}),
    #         dcc.Graph(id="recovered", config={'displayModeBar': False}, className="dcc-compon",
    #                   style={'marginTop': '20px'}),
    #         dcc.Graph(id="active", config={'displayModeBar': False}, className="dcc-compon",
    #                   style={'marginTop': '20px'})
    #     ], className="create-container three columns"),
    #
    #     # Donut chart con Confirmados = Activos + Muertos + Recuperados (por país)
    #     html.Div(children=[
    #         dcc.Graph(id="donut_chart", className="dcc-compon", config={'displayModeBar': 'hover'})
    #     ], className="create-container four columns"),
    #
    #     # Line Chart (30 días de incremento, y en barra los totales)
    #     html.Div(children=[
    #         dcc.Graph(id="line_chart", className="dcc-compon", config={'displayModeBar': 'hover'})
    #     ], className="create-container five columns")
    #
    # ], className="row flex display")

], id="mainContainer", style={'display': 'flex', 'flexDirection': 'column'})


######################################################################################################################
######################################################################################################################
## CALLBACKS
######################################################################################################################
######################################################################################################################
@app.callback(Output('duration_kpi', 'figure'), Output('gross_kpi', 'figure'), Output('budget_kpi', 'figure'),
              Output('likes_kpi', 'figure'), Output('imdb_score_kpi', 'figure'), Output('movie_genre', 'children'),
              Input('dropdown_movies', 'value'))
def update_movies_kpi(movie_title):
    max_duration = movies["duration"].sort_values(ascending=False).iloc[0]
    movie_duration = movies.query("movie_title == @movie_title")["duration"].iloc[0]

    max_gross = movies["gross"].sort_values(ascending=False).iloc[0]
    movie_gross = movies.query("movie_title == @movie_title")["gross"].iloc[0]

    max_budget = movies["budget"].sort_values(ascending=False).iloc[0]
    movie_budget = movies.query("movie_title == @movie_title")["budget"].iloc[0]

    max_likes = max_duration = movies["movie_facebook_likes"].sort_values(ascending=False).iloc[0]
    movie_likes = movies.query("movie_title == @movie_title")["movie_facebook_likes"].iloc[0]

    max_imdb_score = movies["imdb_score"].sort_values(ascending=False).iloc[0]
    movie_imdb_score = movies.query("movie_title == @movie_title")["imdb_score"].iloc[0]

    genre = movies.query("movie_title == @movie_title")["genre"].iloc[0]

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


@app.callback(Output('scatter_gross_budget', 'figure'), Output('box_duration', 'figure'),
              Output('histogram_duration', 'figure'), Output('scatter_gross_likes', 'figure'),
              Output('choropleth', 'figure'), Output('average_budget_per_genre', 'figure'),
              Output('likes_votes_per_genre', 'figure'), Output("imdb_score_per_genre", "figure"),
              Output('movies_per_year_per_genre', 'figure'), Output('funnel_category_per_genre', 'figure'),
              Output('top_countries_slider', 'max'), Input('dropdown_genres', 'value'))
def update_genres_charts(genre):
    movies_gross_budget_per_genre = movies_budget_clean.query("genre == @genre")
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

    movies_scatter_gross_likes = mov_bak.query("genre == @genre")
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

    return fig_scatter_gross_budget, fig_boxplot_duration, fig_histogram_duration, fig_scatter_gross_likes, \
           fig_choropleth, fig_average_budget_per_genre, fig_likes_votes_per_genre, fig_imdb_score_per_genre, \
           fig_movies_per_year_per_genre, fig_funnel_category_per_genre, top_countries_slider


@app.callback(Output('3d_score_budget_country', 'figure'), Output('3d_score_likes_country','figure'),
              Output('pie_movies_country','figure'),Input('dropdown_genres', 'value'),
              Input('top_countries_slider', 'value'))
def update_3d_charts(genre, top_countries_slider_n):
    movies_per_genre_bak = movies.query("genre == @genre")
    movies_per_genre_bak = movies_per_genre_bak.groupby("country")
    movies_per_genre_bak = movies_per_genre_bak.size().reset_index(name='count')
    movies_per_genre_bak = movies_per_genre_bak.sort_values(by="count", ascending=False).iloc[:top_countries_slider_n, :]
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
        xaxis_title='Paises',
        yaxis_title='Presupuesto',
        zaxis_title='Ingreso'),
        #width=700,
        margin=dict(r=20, b=10, l=10, t=10))

    fig_3d_country_budget_gross.update_layout(layout_factory(title=f"Ingeso vs Presupuesto vs País: {genre} y {top_countries_slider_n} países 'top'"))

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
    movies_per_genre_bak_1 = movies_per_genre_bak_1.sort_values(by="count", ascending=False).iloc[:top_countries_slider_n, :]
    df = movies_per_genre_bak_1
    df.loc[df['count'] < 3, 'country'] = 'Otros Paises'  # Represent only large countries
    fig_pie_movies_country = px.pie(df, values='count', names='country', title='Porcentaje por Genero ' + genre, hole=.4)
    fig_pie_movies_country.update_layout(
        layout_factory(title=f"Porcentaje de películas por países: {genre} y {top_countries_slider_n} países 'top'"))

    fig_pie_movies_country.update_layout(legend=dict(
        yanchor="top",
        y=0.0,
        xanchor="left",
        x=0.0
    ))


    return fig_3d_country_budget_gross, fig_3d_score_likes_country, fig_pie_movies_country


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


# @app.callback(Output('confirmed', 'figure'), Output('death', 'figure'), Output('recovered', 'figure'),
#               Output('active', 'figure'), Output(component_id="donut_chart", component_property="figure"),
#               Output('line_chart', 'figure'), [Input('w_countries', 'value')])
# def update_confirmed(w_country):
#     value_confirmed = covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-1] - \
#                       covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-2]
#     delta_confirmed = covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-2] - \
#                       covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-3]
#
#     value_death = covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-1] - \
#                   covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-2]
#     delta_death = covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-2] - \
#                   covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-3]
#
#     value_recovered = covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-1] - \
#                       covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-2]
#     delta_recovered = covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-2] - \
#                       covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-3]
#
#     value_active = covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-1] - \
#                    covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-2]
#     delta_active = covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-2] - \
#                    covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-3]
#
#     figs = []
#     fig_confirmed = go.Figure(
#         data=go.Indicator(
#             mode="number+delta",
#             value=value_confirmed,
#             delta=dict(
#                 position="right",
#                 reference=delta_confirmed,
#                 valueformat='.0f',
#                 relative=False,
#                 font={'size': 20}),
#             number=dict(
#                 valueformat=',',
#                 font={'size': 25}),
#             domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
#         ),
#         layout=go.Layout(
#             title={
#                 'text': 'New confirmed',
#                 'y': 0.9,
#                 'x': 0.5,
#                 'xanchor': 'center',
#                 'yanchor': 'top',
#                 'font': {'size': 25},
#                 'pad': {'b': 20}
#             },
#             font=dict(color='orange'),
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             height=100,
#         )
#
#     )
#
#     fig_death = go.Figure(
#         data=go.Indicator(
#             mode="number+delta",
#             value=value_death,
#             delta=dict(
#                 position="right",
#                 reference=delta_death,
#                 valueformat='.0f',
#                 relative=False,
#                 font={'size': 20}),
#             number=dict(
#                 valueformat=',',
#                 font={'size': 25}),
#             domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
#         ),
#         layout=go.Layout(
#             title={
#                 'text': 'New deaths',
#                 'y': 0.9,
#                 'x': 0.5,
#                 'xanchor': 'center',
#                 'yanchor': 'top',
#                 'font': {'size': 25},
#                 'pad': {'b': 20}
#             },
#             font=dict(color='red'),
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             height=100,
#         )
#
#     )
#
#     fig_recovered = go.Figure(
#         data=go.Indicator(
#             mode="number+delta",
#             value=value_recovered,
#             delta=dict(
#                 position="right",
#                 reference=delta_recovered,
#                 valueformat='.0f',
#                 relative=False,
#                 font={'size': 20}),
#             number=dict(
#                 valueformat=',',
#                 font={'size': 25}),
#             domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
#         ),
#         layout=go.Layout(
#             title={
#                 'text': 'New recovered',
#                 'y': 0.9,
#                 'x': 0.5,
#                 'xanchor': 'center',
#                 'yanchor': 'top',
#                 'font': {'size': 25},
#                 'pad': {'b': 20}
#             },
#             font=dict(color='green'),
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             height=100,
#         )
#
#     )
#
#     fig_active = go.Figure(
#         data=go.Indicator(
#             mode="number+delta",
#             value=value_active,
#             delta=dict(
#                 position="right",
#                 reference=delta_active,
#                 valueformat='.0f',
#                 relative=False,
#                 font={'size': 20}),
#             number=dict(
#                 valueformat=',',
#                 font={'size': 25}),
#             domain={'y': [0, 1], 'x': [0, 1]}  ### Se relaciona con la posición de los valores delta y value
#         ),
#         layout=go.Layout(
#             title={
#                 'text': 'New active',
#                 'y': 0.9,
#                 'x': 0.5,
#                 'xanchor': 'center',
#                 'yanchor': 'top',
#                 'font': {'size': 25},
#                 'pad': {'b': 20}
#             },
#             font=dict(color='yellow'),
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             height=100,
#         )
#
#     )
#
#     figs.append([fig_confirmed, fig_death, fig_recovered])
#
#     confirmed = covid_data2[covid_data2["Country/Region"] == w_country]["confirmed"].iloc[-1]
#     death = covid_data2[covid_data2["Country/Region"] == w_country]["death"].iloc[-1]
#     recovered = covid_data2[covid_data2["Country/Region"] == w_country]["recovered"].iloc[-1]
#     active = covid_data2[covid_data2["Country/Region"] == w_country]["active"].iloc[-1]
#     values = [active, recovered, death]
#     dict_pasa = {}
#     for i, v in enumerate(values):
#         if v != 0:
#             if i == 0:
#                 dict_pasa["Actives"] = (values[i], "yellow")
#             if i == 1:
#                 dict_pasa["Recovered"] = (values[i], "green")
#             if i == 2:
#                 dict_pasa["Death"] = (values[i], "red")
#     labels = list(dict_pasa.keys())
#     values = []
#     colors = []
#     for v, c in dict_pasa.values():
#         values.append(v)
#         colors.append(c)
#
#     fig_donut = go.Figure(
#         data=go.Pie(
#             labels=labels,
#             values=values,
#             hoverinfo='label+value+percent',
#             marker=dict(colors=colors),
#             textinfo='label+value',
#             hole=.7,
#             rotation=90,
#             # insidetextorientation='radial'
#         ),
#         layout=go.Layout(
#             title={'text': f'Confirmed Cases: {confirmed}',
#                    'y': 0.92,
#                    'x': 0.5,
#                    'xanchor': 'center',
#                    'yanchor': 'top'},
#             font=dict(color='white'),
#             hovermode='closest',
#             margin=dict(r=0),
#             titlefont={'color': 'white', 'size': 20},
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             legend={
#                 'orientation': 'v',
#                 'bgcolor': '#1f2c56',
#                 'xanchor': 'center',
#                 'x': 0.5,
#                 'y': -0.5
#             }
#         )
#     )
#
#     covid_data3 = covid_data2[covid_data2["Country/Region"] == w_country][["Country/Region", "date", "confirmed"]]
#     # Usando shift para desplazar una fila
#     covid_data3["daily increase"] = covid_data3["confirmed"] - covid_data3["confirmed"].shift(1)
#
#     fig_line = go.Figure(
#         data=go.Bar(
#             x=covid_data3['date'].tail(30),
#             y=covid_data3['daily increase'].tail(30),
#             name='Daily Confirmed Cases',
#             marker=dict(color='orange'),
#             hoverinfo='text',
#             hovertext=
#             '<b>Date</b>' + covid_data3['date'].tail(30).astype(str) + '<br>' +
#             '<b>Daily Confirmed Cases</b>' + [f'{x:0f}' for x in covid_data3['daily increase'].tail(30)] + '<br>' +
#             '<b>Country</b>' + covid_data3['Country/Region'].tail(30).astype(str) + '<br>'
#         ),
#         layout=go.Layout(
#             title={'text': f'Last Daily Confirmed Cases',
#                    'y': 0.92,
#                    'x': 0.5,
#                    'xanchor': 'center',
#                    'yanchor': 'top'},
#             font=dict(color='white'),
#             hovermode='closest',
#             titlefont={'color': 'white', 'size': 20},
#             paper_bgcolor='#1f2c56',
#             plot_bgcolor='#1f2c56',
#             legend={
#                 'orientation': 'v',
#                 'bgcolor': '#1f2c56',
#                 'xanchor': 'center',
#                 'x': 0.5,
#                 'y': -0.5
#             },
#             margin=dict(r=1),
#             xaxis=dict(title='<b>Date</b>',
#                        color='white',
#                        showline=True,
#                        showgrid=True),
#             yaxis=dict(title='<b>Daily Confirmed Cases</b>',
#                        color='white',
#                        showline=True,
#                        showgrid=True),
#         ),
#     )
#
#     return fig_confirmed, fig_death, fig_recovered, fig_active, fig_donut, fig_line


app.title = "Movies Dashboard"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
