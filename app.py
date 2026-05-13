import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the Excel file (works both locally and on Plotly Cloud)
try:
    # Find any Excel file in the current directory
    excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]
    
    if excel_files:
        excel_file = excel_files[0]
        df = pd.read_excel(excel_file)
        print(f"✅ Loaded {excel_file} successfully. Shape: {df.shape}")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Create a bar chart using the first two columns
        # Replace column names with your actual column names if needed
        if len(df.columns) >= 2:
            fig = px.bar(
                df.head(20), 
                x=df.columns[0], 
                y=df.columns[1],
                title=f"Dashboard - {excel_file}",
                labels={df.columns[0]: df.columns[0], df.columns[1]: df.columns[1]},
                color_discrete_sequence=['#2E86AB']
            )
        else:
            fig = px.line(df, title="Data Overview")
            
        # Create a data table preview
        table_preview = html.Div([
            html.H3("📋 Data Preview (First 10 rows)", style={'marginTop': 30}),
            html.Div([
                html.Table([
                    html.Thead(html.Tr([html.Th(col, style={'padding': '8px', 'textAlign': 'left'}) 
                                       for col in df.columns])),
                    html.Tbody([
                        html.Tr([html.Td(str(df.iloc[row][col]), style={'padding': '8px'}) 
                                for col in df.columns])
                        for row in range(min(10, len(df)))
                    ])
                ], style={'border': '1px solid #ddd', 'borderCollapse': 'collapse', 'width': '100%'})
            ])
        ])
        
        # Statistics section
        stats = html.Div([
            html.H3("📊 Dataset Information", style={'marginTop': 30}),
            html.Div([
                html.P(f"📈 Total rows: {len(df)}", style={'fontSize': '16px'}),
                html.P(f"📊 Total columns: {len(df.columns)}", style={'fontSize': '16px'}),
                html.P(f"📝 Column names: {', '.join(df.columns)}", style={'fontSize': '14px'}),
                html.P(f"💾 File: {excel_file}", style={'fontSize': '14px', 'color': '#666'})
            ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
        ])
        
    else:
        df = pd.DataFrame()
        fig = {}
        table_preview = html.Div("❌ No Excel file found. Please upload your data file.")
        stats = html.Div("No data available")
        print("❌ No Excel file found in directory")
        
except Exception as e:
    print(f"❌ Error loading data: {e}")
    df = pd.DataFrame()
    fig = {}
    table_preview = html.Div(f"⚠️ Error loading data: {str(e)}")
    stats = html.Div("Error loading data")

# Create the app layout
app.layout = html.Div([
    html.H1("📊 Berber Cement - Sales Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10, 'marginTop': 20}),
    
    html.Hr(),
    
    # Main chart
    dcc.Graph(figure=fig),
    
    # Data preview and stats
    table_preview,
    stats
    
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)
