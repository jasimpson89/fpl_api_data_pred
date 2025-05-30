import dash
from dash import dcc, html
import plotly.express as px
from get_fpl_data import main as get_fpl_data

# Get data
player_dataframes = get_fpl_data()

# Start Dash app
app = dash.Dash(__name__)
app.title = "FPL Points vs Fixture Difficulty"

# Create a tab for each player
tabs = []
for player_name, df in player_dataframes.items():
    fig = px.scatter(
        df,
        x="team_difficulty",
        y="points",
        color=df["was_home"].map({True: "Home", False: "Away"}),
        title=f"{player_name} - Points vs Fixture Difficulty Rating",
        labels={"team_difficulty": "Fixture Difficulty Rating (FDR)", "points": "FPL Points"},
        hover_data=["opponent_team", "gameweek"]
    )
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))

    tab = dcc.Tab(label=player_name, children=[
        dcc.Graph(figure=fig)
    ])
    tabs.append(tab)

# Define app layout
app.layout = html.Div([
    html.H1("FPL Points vs Fixture Difficulty Rating", style={"textAlign": "center"}),
    dcc.Tabs(children=tabs)
])

# Run app
if __name__ == "__main__":
    app.run(debug=True)
