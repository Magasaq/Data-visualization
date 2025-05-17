import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from utils.data_preprocess import load_and_clean_data

dash.register_page(__name__, path="/", title="Home", name="Home")

df = load_and_clean_data()

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Welcome to Melbourne Housing Dashboard", className="mb-3"),
            html.P(
                "Dive into Melbourne’s housing market with rich, interactive visualizations. "
                "Filter properties by price to understand market trends, pricing distribution, "
                "and how location and features affect property values."
            ),
            html.P(
                "This dashboard is designed to help buyers, sellers, and analysts gain insights "
                "into Melbourne's diverse real estate landscape."
            ),
            html.Hr(),

            html.Label("Filter by Price Range (Thousands):"),
            dcc.RangeSlider(
                id="price-range-slider",
                min=df["Price"].min() // 10000,
                max=df["Price"].max() // 10000,
                step=10,
                value=[df["Price"].min() // 10000, df["Price"].max() // 10000],
                marks={i: f"${i*10}k" for i in range(0, int(df["Price"].max() // 10000)+100, 100)},
                tooltip={"placement": "bottom", "always_visible": True},
            ),

            dcc.Graph(id="price-histogram", className="mt-4"),

            html.Hr(),

            dcc.Graph(id="price-distance-scatter", className="mt-4"),

            html.Hr(),

            dcc.Graph(id="price-map", className="mt-4"),

            html.Hr(),

            html.Div(id="insights-text", style={"whiteSpace": "pre-line", "fontSize": "1.1rem", "marginTop": "1rem"}),
        ], width=12),
    ])
], fluid=True)

@dash.callback(
    Output("price-histogram", "figure"),
    Output("price-distance-scatter", "figure"),
    Output("price-map", "figure"),
    Output("insights-text", "children"),
    Input("price-range-slider", "value"),
)
def update_visualizations(price_range):
    low, high = price_range
    filtered_df = df[(df["Price"] >= low * 10000) & (df["Price"] <= high * 10000)]

    # Price histogram
    hist_fig = px.histogram(
        filtered_df,
        x="Price",
        nbins=50,
        title="Distribution of Housing Prices in Selected Range",
        template="plotly_white",
    )
    hist_fig.update_layout(yaxis_title="Number of Listings", xaxis_title="Price (AUD)")

    # Scatter Price vs Distance from CBD
    scatter_fig = px.scatter(
        filtered_df,
        x="Distance",
        y="Price",
        color="Rooms",
        title="Relationship Between Price and Distance from CBD",
        template="plotly_white",
        hover_data=["Suburb", "Rooms"]
    )
    scatter_fig.update_layout(yaxis_title="Price (AUD)", xaxis_title="Distance from CBD (km)")

    # Scatter Mapbox of houses
    map_fig = px.scatter_mapbox(
        filtered_df,
        lat="Lattitude",     # <-- Check coordinate column spelling here if needed
        lon="Longtitude",
        color="Price",
        size="Rooms",
        hover_data=["Suburb", "Price", "Rooms"],
        color_continuous_scale=px.colors.sequential.Viridis,
        size_max=15,
        zoom=10,
        mapbox_style="carto-positron",
        title="Geographical Distribution of Housing Prices"
    )

    insight_text = (
        f"You're currently viewing {filtered_df.shape[0]:,} property listings "
        f"priced between ${low * 10000:,} and ${high * 10000:,} AUD.\n\n"
        f"The median price for this segment is ${filtered_df['Price'].median():,.0f} AUD.\n"
        f"Notice how housing prices tend to decrease as the distance from Melbourne's Central Business District (CBD) increases.\n\n"
        f"Use the interactive map above to explore the spatial distribution of homes, "
        f"their prices, and sizes across Melbourne's diverse suburbs."
    )

    return hist_fig, scatter_fig, map_fig, insight_text
