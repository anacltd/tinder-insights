import json
import random
import sys
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from pandas import DataFrame

FRENCH_VERSION = {'app_opens': "Application ouverte",
                  'swipes_likes': "Swipes à droite",
                  'swipes_passes': "Swipes à gauche",
                  'matches': "Matches",
                  'messages_sent': "Message envoyés",
                  'messages_received': "Message reçus",
                  'advertising_id': "advertising_id",
                  'idfa': "idfa"}
COLORS = ["#fd297b", "#ff5864", "#ff655b", "#ff7854"]


def fill_missing_dates(df: DataFrame) -> DataFrame:
    """
    Generate missing dates and data to avoid weird curve in the graph (happens when the app has been uninstalled or
    hasn't been opened in a while)
    Args:
        df: the original dataframe (having some potentially missing data)

    Returns:
        a dataframe without any missing dates
    """
    df = df.set_index(pd.to_datetime(df.index).date)
    date_from = df.index[0]
    date_to = df.index[-1]
    dates = pd.date_range(date_from, date_to)
    missing_dates = [d for d in list(dates) if d not in list(df.index)]
    missing_data = {col: np.zeros(len(missing_dates)) for col in df.columns}
    sub_df = pd.DataFrame(missing_data, index=missing_dates, columns=df.columns)
    sub_df = sub_df.set_index(pd.to_datetime(pd.Series(sub_df.index.date)))
    new_df = pd.concat([df, sub_df])
    return new_df.sort_index()


def rename_columns(df: DataFrame) -> DataFrame:
    """
    Rename the columns with clean French names
    #TODO: add an English version and a dropdown button to select it
    Args:
        df: the original dataframe

    Returns:
        the dataframe with new columns names
    """
    return df.rename(columns=FRENCH_VERSION)


def process_df(df: DataFrame) -> DataFrame:
    """
    Transpose, rename columns and add potentially missing data in a dataframe
    Args:
        df: the original, "raw" dataframe

    Returns:
        the processed dataframe
    """
    df = df.transpose()
    df.drop(columns=["idfa", "advertising_id"], inplace=True)
    df = fill_missing_dates(df)
    df = rename_columns(df)
    return df


try:
    with open("data.json", encoding="utf-8") as json_file:
        data = json.load(json_file)
except FileNotFoundError as e:
    print("Le fichier data.json n'est pas dans le répertoire")
    sys.exit(1)

df = process_df(pd.DataFrame.from_dict(data.get("Usage"), orient="index"))
drop_down_labels = [{"label": s, "value": s} for s in list(df.columns)]
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Raleway&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Tinder Analytics"

app.layout = html.Div(
    children=[
        html.P(children="🔥", className="fire-emoji"),
        html.H1(children="Tinder Insights",
                className="header-title"),
        html.P(
            children="Analysez vos données Tinder",
            className="header-description",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=drop_down_labels,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Dates",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df.index.min(),
                            max_date_allowed=df.index.max(),
                            start_date=df.index.min(),
                            end_date=df.index.max(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(children=[

        ], id="graph")
    ]
)


@app.callback(
    Output("graph", "children"),
    [Input("type-filter", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date")
     ],
    [State("graph", "children")]
)
def update_graph(value, start_date, end_date, children):
    """
    Based on the callback from the drop-down button, returns the wanted graphs
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    swipes_nb = sum(df["Swipes à droite"] + df["Swipes à gauche"])
    filtered = df[start:end]
    if value:
        val = [swipes_nb - sum(df[value]), sum(df[value])] if 'Matches' not in value else [sum(df["Swipes à droite"]),
                                                                                           sum(df[value])]
        # Tinder-themed CSS colors: salmon fushia indianred lightcoral
        fig = go.Figure(data=[go.Pie(labels=[f"Swipes à {'gauche' if 'droite' in value else 'droite'}", value],
                                     values=val,
                                     pull=[0, 0.25],
                                     textinfo='label+percent',
                                     showlegend=False,
                                     hoverinfo='value',
                                     marker=dict(colors=['coral', 'palevioletred'])
                                     )])
        if children:
            children[0]["props"]["figure"] = fig
            children[1]["props"]["figure"] = {
                "data": [
                        {
                            "x": filtered.index.to_series(),
                            "y": filtered[value],
                            "type": "lines",
                        },
                    ],
                "layout": {"title": value,
                           "colorway": [random.choice(COLORS)]},
                }
        else:
            children.append(
                dcc.Graph(
                    figure=fig
                )
            )
            children.append(
                dcc.Graph(
                    id="matches",
                    figure={
                        "data": [
                            {
                                "x": filtered.index.to_series(),
                                "y": filtered[value],
                                "type": "lines",
                            },
                        ],
                        "layout": {"title": value,
                                   "colorway": [random.choice(COLORS)]},
                    },
                )
            )
    return children


if __name__ == "__main__":
    app.run_server()
