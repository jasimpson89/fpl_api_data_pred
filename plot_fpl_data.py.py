import plotly.graph_objects as go
import pandas as pd
from get_fpl_data import main as get_fpl_data

# Load data
player_dataframes = get_fpl_data()

# Create figure
fig = go.Figure()

# Add a trace per player
for player_name, df in player_dataframes.items():
    # Create custom hover text
    hover_text = df.apply(
        lambda row: f"Opponent: {row['opponent_team']}<br>"
                    f"Home: {row['was_home']}<br>"
                    f"FDR: {row['team_difficulty']}", axis=1)

    fig.add_trace(go.Scatter(
        x=df["gameweek"],
        y=df["points"],
        mode='lines+markers',
        name=player_name,
        text=hover_text,
        hoverinfo='text+y+name'
    ))

# Layout
fig.update_layout(
    title="FPL Points per Gameweek by Player",
    xaxis_title="Gameweek",
    yaxis_title="FPL Points",
    hovermode="closest",
    template="plotly_dark",
    legend_title="Player",
    width=1000,
    height=600
)

# Show the plot
fig.show()
