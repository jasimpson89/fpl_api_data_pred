import plotly.graph_objects as go
import pandas as pd
from get_fpl_data import main as get_fpl_data

def plot_player_form():
    player_dataframes = get_fpl_data()
    fig = go.Figure()

    for player, df in player_dataframes.items():
        if 'form' in df.columns and 'gameweek' in df.columns:
            # Convert form and gameweek to numeric and replace missing values with 0
            form_series = pd.to_numeric(df['form'], errors='coerce').fillna(0)
            gameweeks = pd.to_numeric(df['gameweek'], errors='coerce').fillna(0)

            if not form_series.empty and not gameweeks.empty:
                fig.add_trace(go.Scatter(
                    x=gameweeks,
                    y=form_series,
                    mode='lines+markers',
                    name=player
                ))

    fig.update_layout(
        title="Player Form vs Gameweek",
        xaxis_title="Gameweek",
        yaxis_title="Form (Rolling Avg Points)",
        template='plotly_white',
        legend_title="Player",
        width=1000,
        height=600
    )

    fig.show()

if __name__ == "__main__":
    plot_player_form()
