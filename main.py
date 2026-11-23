import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

url = "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Monterrey/airbnb.csv"
df = pd.read_csv(url)

req_col = ['latitude', 'longitude', 'price', 'minimum_nights']
for col in req_col:
    if col == 'price':
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce'
        )
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=req_col)

df = df[
    (df['price'] > 0) &
    (df['latitude'].abs() > 1) &
    (df['longitude'].abs() > 1)
]

app = Dash(__name__)
server = app.server

max_price_val = int(df['price'].max())
slider_max = ((max_price_val + 99) // 100) * 100

app.layout = html.Div(
    style={'fontFamily': 'sans-serif', 'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'},
    children=[
        html.H1('Monterrey Airbnb Spatial Distribution', style={'textAlign': 'center'}),

        html.H3("Select maximum minimum-nights allowed"),
        dcc.Slider(
            id='slider', min=1, max=30, step=1, value=7,
            marks={i: str(i) for i in range(1, 31, 5)}
        ),

        html.Br(),
        html.H3('Select price range', style={'marginBottom': '30px'}),
        dcc.RangeSlider(
            id='slider2',
            min=0,
            max=slider_max,
            value=[0, slider_max],
            step=100,
            marks=None,
            tooltip={'placement': 'top', 'always_visible': True}
        ),

        html.Br(),
        html.Div(id='count', style={'textAlign': 'center', 'fontWeight': 'bold', 'marginBottom': '10px'}),
        dcc.Graph(id='spatial-plot', style={'height': '700px'})
    ]
)


@app.callback(
    Output('spatial-plot', 'figure'),
    Output('count', 'children'),
    Input('slider', 'value'),
    Input('slider2', 'value')
)
def update_plot(min_nights, price_range):
    min_price, max_price = price_range

    filtered_df = df[
        (df['minimum_nights'] <= min_nights) &
        (df['price'] >= min_price) &
        (df['price'] <= max_price)
    ]

    if filtered_df.empty:
        fig = px.scatter(title="No properties match the selected filters")
    else:
        hover_col = 'name' if 'name' in filtered_df.columns else None
        fig = px.scatter(
            filtered_df,
            x='longitude',
            y='latitude',
            color='price',
            hover_name=hover_col,
            hover_data={'minimum_nights': True, 'price': ':,.0f'},
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Geographic Coordinate Distribution (No Map Tiles)'
        )
        fig.update_traces(marker={'size': 7, 'opacity': 0.8})
        fig.update_yaxes(scaleanchor='x', scaleratio=1)

    return fig, f"Properties shown: {len(filtered_df):,}"


if __name__ == '__main__':
    app.run(debug=True)
