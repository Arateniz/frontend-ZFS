import pandas as pd
import numpy as np
import glob

import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash import Dash, html, dcc, Input, Output

files = sorted(glob.glob("data/*.csv"))

def read_data(file):
	df = pd.read_csv(
		file,
		sep="\t",
		header=None,
		usecols=[0, 1, 2, 3, 4, 5, 7],
		names=["year", "month", "day", "hour", "minute", "CH4", "CO2"]
	)

	df["datetime"] = pd.to_datetime(df[["year", "month", "day", "hour", "minute"]])
	df = df.drop(columns=["year", "month", "day", "hour", "minute"]).set_index("datetime")

	return df

df = read_data(files[1])

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Analiza gazów śladowych"

app.layout = dbc.Container([
	dbc.Row([
		dbc.Col([
			html.H3("Ustawienia"),
			html.Label("Plik danych:"),
			dcc.Dropdown(
				id="file-select",
				options=[{"label": f.split("/")[-1], "value": f} for f in files],
				value=files[0],
				clearable=False
			),

			html.Br(),
			html.Label("Zanieczyszczenie:"),
			dcc.Dropdown(
				id="pollutant-select",
				options=[
					{"label": "Dwutlenek węgla (CO₂)", "value": "CO2"},
					{"label": "Metan (CH₄)", "value": "CH4"},
				],
				value="CO2",
				clearable=False
			),

			html.Br(),
			html.Label("Zakres dat:"),
			dcc.DatePickerRange(
				id="date-range",
				display_format="YYYY-MM-DD",
				start_date=None,
				end_date=None,
				min_date_allowed=None,
				max_date_allowed=None
			)
		], width=4, style={"backgroundColor": "#f8f9fa", "padding": "20px", "height": "100vh"}),

		dbc.Col([
			html.H3("Wykres pomiarów"),
			dcc.Graph(id="main-graph", style={"height": "80vh"}),
		], width=8)
	])
], fluid=True)

@app.callback(
	Output("date-range", "min_date_allowed"),
	Output("date-range", "max_date_allowed"),
	Output("date-range", "start_date"),
	Output("date-range", "end_date"),
	Input("file-select", "value")
)
def update_datepicker_limits(filename):
	df = read_data(filename)
	df = df.sort_index()
	min_date = df.index.min().date()
	max_date = df.index.max().date()
	return min_date, max_date, min_date, max_date

@app.callback(
	Output("main-graph", "figure"),
	Input("file-select", "value"),
	Input("pollutant-select", "value"),
	Input("date-range", "start_date"),
	Input("date-range", "end_date")
)
def update_graph(filename, pollutant, start_date, end_date):
	df = read_data(filename)
	df = df.sort_index()
	if start_date and end_date:
		df = df.loc[(df.index >= pd.to_datetime(start_date)) &
					(df.index <= pd.to_datetime(end_date))]
	fig = px.line(df, y=pollutant)
	return fig

if __name__ == "__main__":
	app.run(debug=True)
