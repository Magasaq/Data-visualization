import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_preprocess import load_and_clean_data

dash.register_page(__name__, path="/analysis", title="Analysis", name="Analysis")

df = load_and_clean_data()

# Mapping property type codes to readable names
type_map = {
    "h": "House",
    "t": "Townhouse",
    "u": "Unit"
}

# Reverse map for filtering
reverse_type_map = {v: k for k, v in type_map.items()}

# Precompute some KPIs
avg_price = df["Price"].mean()
median_price = df["Price"].median()
avg_rooms = df["Rooms"].mean()
total_properties = df.shape[0]

# Calculate Price per Square Meter
df["Price_per_sqm"] = df["Price"] / df["Landsize"].replace(0, np.nan)  # avoid division by zero
df["Price_per_sqm"].fillna(0, inplace=True)

layout = dbc.Container([
    html.H2("Melbourne Housing Market Analysis", className="mb-4"),
    
    # KPIs Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Average Price", className="card-title"),
                html.H3(f"${avg_price:,.0f}", className="card-text text-success"),
            ])
        ]), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Median Price", className="card-title"),
                html.H3(f"${median_price:,.0f}", className="card-text text-info"),
            ])
        ]), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Average Number of Rooms", className="card-title"),
                html.H3(f"{avg_rooms:.1f}", className="card-text text-warning"),
            ])
        ]), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Properties", className="card-title"),
                html.H3(f"{total_properties:,}", className="card-text text-primary"),
            ])
        ]), width=3),
    ], className="mb-5"),
    
    # Filters for interactive charts
    dbc.Row([
        dbc.Col([
            html.Label("Select Region:"),
            dcc.Dropdown(
                id="region-filter",
                options=[{"label": r, "value": r} for r in sorted(df["Regionname"].unique())],
                value=None,
                placeholder="All Regions",
                clearable=True
            ),
        ], width=4),
        dbc.Col([
            html.Label("Select Property Type:"),
            dcc.Dropdown(
                id="type-filter",
                options=[{"label": name, "value": name} for name in sorted(type_map.values())],
                value=None,
                placeholder="All Types",
                clearable=True
            ),
        ], width=4),
    ], className="mb-4"),
    
    # Existing interactive charts
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="price-by-region"),
            html.P(
                "This bar chart shows the average property price for each suburb in Melbourne, "
                "based on your selected filters. It helps identify which suburbs are more expensive "
                "and which offer more affordable options."
            )
        ], width=6),
        
        dbc.Col([
            dcc.Graph(id="rooms-vs-price-scatter"),
            html.P(
                "The scatter plot visualizes the relationship between the number of rooms and property prices, "
                "with colors indicating the property type (House, Townhouse, Unit). This reveals how size and type "
                "impact pricing."
            )
        ], width=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="price-over-time"),
            html.P(
                "This line chart illustrates the trend of average property prices over time (monthly), "
                "helping to understand the market’s temporal dynamics and seasonality."
            )
        ], width=12),
    ]),
    
    # New: Price per Square Meter chart
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="price-per-sqm"),
            html.P(
                "Average price per square meter by suburb, useful for comparing property value relative to size."
            )
        ], width=12),
    ]),
    
    # New: Correlation matrix heatmap
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="correlation-matrix"),
            html.P(
                "Correlation matrix of key numerical features, indicating relationships between variables."
            )
        ], width=12),
    ]),
    
    # New: Outlier detection (Boxplot for Price and Price per sqm)
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="outlier-detection"),
            html.P(
                "Boxplots showing distribution and potential outliers for Price and Price per Square Meter."
            )
        ], width=12),
    ]),
    
    # Descriptive insights at the bottom
    dbc.Row([
        dbc.Col([
            html.H4("Insights & Analysis", className="mt-5"),
            html.P(
                """
                The Melbourne housing market exhibits diverse price levels across suburbs and property types.
                Inner-city suburbs generally have higher prices but fewer rooms, while outer suburbs tend to offer
                larger homes at lower prices. Over time, property prices have shown an upward trend, reflecting
                sustained demand and market growth. The dashboard provides interactive tools to explore these
                patterns and gain deeper market insights, useful for buyers, sellers, and investors.
                """
            )
        ])
    ]),
], fluid=True)


@dash.callback(
    Output("price-by-region", "figure"),
    Output("rooms-vs-price-scatter", "figure"),
    Output("price-over-time", "figure"),
    Output("price-per-sqm", "figure"),
    Output("correlation-matrix", "figure"),
    Output("outlier-detection", "figure"),
    Input("region-filter", "value"),
    Input("type-filter", "value"),
)
def update_analysis(region, property_type):
    filtered = df.copy()

    if region:
        filtered = filtered[filtered["Regionname"] == region]
    if property_type:
        # Map readable type name back to code for filtering
        code = reverse_type_map.get(property_type)
        if code:
            filtered = filtered[filtered["Type"] == code]

    # Map codes to readable names for plots
    filtered["TypeName"] = filtered["Type"].map(type_map)

    # Price by Region - Bar Chart (average price per suburb)
    price_region_fig = px.bar(
        filtered.groupby("Suburb")["Price"].mean().reset_index().sort_values("Price", ascending=False),
        x="Suburb", y="Price",
        title="Average Price by Suburb",
        labels={"Price": "Avg Price ($)", "Suburb": "Suburb"},
        template="plotly_white",
    )
    price_region_fig.update_layout(xaxis_tickangle=-45)

    # Scatter: Rooms vs Price colored by Property TypeName
    scatter_fig = px.scatter(
        filtered,
        x="Rooms", y="Price",
        color="TypeName",
        hover_data=["Suburb", "Price", "Rooms", "Regionname"],
        title="Rooms vs Price by Property Type",
        template="plotly_white",
    )

    # Price over time - Line chart of average price per month
    df_date = filtered.copy()
    df_date["Date"] = pd.to_datetime(df_date["Date"])
    price_time_df = df_date.groupby(df_date["Date"].dt.to_period("M"))["Price"].mean().reset_index()
    price_time_df["Date"] = price_time_df["Date"].dt.to_timestamp()

    price_time_fig = px.line(
        price_time_df,
        x="Date", y="Price",
        title="Average Price Over Time",
        labels={"Price": "Avg Price ($)", "Date": "Date"},
        template="plotly_white",
    )

    # Price per sqm by Suburb bar chart
    price_sqm_fig = px.bar(
        filtered.groupby("Suburb")["Price_per_sqm"].mean().reset_index().sort_values("Price_per_sqm", ascending=False),
        x="Suburb", y="Price_per_sqm",
        title="Average Price per Square Meter by Suburb",
        labels={"Price_per_sqm": "Avg Price per sqm ($)", "Suburb": "Suburb"},
        template="plotly_white",
    )
    price_sqm_fig.update_layout(xaxis_tickangle=-45)

    # Correlation matrix heatmap
    numeric_cols = ["Price", "Rooms", "Distance", "Bedroom2", "Bathroom", "Car", "Landsize", "Landsize", "Price_per_sqm"]
    corr_df = filtered[numeric_cols].corr()
    corr_fig = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Matrix of Numerical Features",
        template="plotly_white"
    )

    # Outlier detection boxplots
    outlier_fig = px.box(
        filtered,
        y=["Price", "Price_per_sqm"],
        title="Outlier Detection: Price and Price per Square Meter",
        labels={"value": "Value ($)", "variable": "Feature"},
        template="plotly_white"
    )

    return price_region_fig, scatter_fig, price_time_fig, price_sqm_fig, corr_fig, outlier_fig
