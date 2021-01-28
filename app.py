import json
import random
import sys
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State

FRENCH_VERSION = {'app_opens': "Application ouverte",
                  'swipes_likes': "Swipes à droite",
                  'swipes_passes': "Swipes à gauche",
                  'matches': "Matches",
                  'messages_sent': "Message envoyés",
                  'messages_received': "Message reçus",
                  'advertising_id': "advertising_id",
                  'idfa': "idfa"}
COLORS = ["#fd297b", "#ff5864", "#ff655b", "#ff7854"]


def fill_missing_dates(df):
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


def rename_columns(df):
    return df.rename(columns=FRENCH_VERSION)


def process_df(df):
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

df = pd.DataFrame.from_dict(data.get("Usage"), orient="index")
df = process_df(df)
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
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    filtered = df[start:end]
    if value:
        if children:
            children[0]["props"]["figure"] = {
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
