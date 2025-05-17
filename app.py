import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc

# Initialize Dash app with Bootstrap theme and multi-page support
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
server = app.server

# Sidebar with page links
sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [html.Div(page["name"], className="ms-2")],
            href=page["path"],
            active="exact"
        )
        for page in dash.page_registry.values()
    ],
    vertical=True,
    pills=True,
    className="bg-light pt-3",
)

# Main layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("🏡 Melbourne Housing Dashboard", className="text-center text-primary mb-4"))
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(
            [sidebar],
            xs=12, sm=3, md=3, lg=2, xl=2, xxl=2
        ),
        dbc.Col(
            [dash.page_container],
            xs=12, sm=9, md=9, lg=10, xl=10, xxl=10
        )
    ])
], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)
