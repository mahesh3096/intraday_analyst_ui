# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 10:10:50 2024

@author: mahe
"""
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# Get the current date
current_date = datetime.now()

# Format the date as DDYYMM
formatted_date = current_date.strftime("%d-%m-%Y")


def draw_line_chart(X,Y):
    chart_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <canvas id="myChart" style="width: 100%; height: 400px;"></canvas>
        <script>
            const ctx = document.getElementById('myChart').getContext('2d');
            const myChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {list(X)}, // X-Axis labels
                    datasets: [{{
                        label: 'Profit / loss Chart - {formatted_date}',
                        data: {list(Y)}, // Y-Axis data
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        tension: 0.4 // Smoothing
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'Number of trades'
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'Profit/loss points'
                            }},
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return chart_html


def draw_bar_chart(df,st):
    df = df.apply(pd.Series.value_counts).fillna(0)
        # Create a grouped bar chart using Plotly
    fig = go.Figure(data=[
        go.Bar(name='Yes', x=df.columns, y=df.loc['Yes'], marker_color='rgba(60, 179, 113, 0.6)'),
        go.Bar(name='No', x=df.columns, y=df.loc['No'], marker_color='rgba(255, 99, 132, 0.6)')
    ])
    
    # Update layout for better presentation
    fig.update_layout(
        barmode='group',
        xaxis_title="Features",
        yaxis_title="Count",
        yaxis=dict(range=[0, max(df.max()) + 1]),  # Ensure y-axis starts from 0
    )
    
    # Display the plot in Streamlit
    st.plotly_chart(fig)
