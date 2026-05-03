import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define color scheme
colors = {
    'primary': '#1F4E79',
    'secondary': '#2E75B6',
    'success': '#28A745',
    'warning': '#FFC107',
    'danger': '#DC3545',
    'info': '#17A2B8',
    'light': '#F8F9FA',
    'dark': '#343A40'
}

# Define all KPIs for each department
KPI_DATA = {
    'Production': {
        'Clinker Production (tons/day)': {'target': 5000, 'actual': 4850, 'unit': 'tons/day', 'lower_better': False},
        'Cement Production (tons/day)': {'target': 6000, 'actual': 6100, 'unit': 'tons/day', 'lower_better': False},
        'Kiln Feed Rate (tph)': {'target': 400, 'actual': 395, 'unit': 'tph', 'lower_better': False},
        'Specific Heat Consumption (kcal/kg)': {'target': 720, 'actual': 730, 'unit': 'kcal/kg', 'lower_better': True},
        'Specific Power Consumption (kWh/ton)': {'target': 85, 'actual': 87, 'unit': 'kWh/ton', 'lower_better': True},
        'Kiln Availability (%)': {'target': 92, 'actual': 91, 'unit': '%', 'lower_better': False},
        'Mill Availability (%)': {'target': 90, 'actual': 88, 'unit': '%', 'lower_better': False},
        'Production Efficiency (%)': {'target': 95, 'actual': 93, 'unit': '%', 'lower_better': False},
        'OEE (%)': {'target': 85, 'actual': 83, 'unit': '%', 'lower_better': False},
        'Packing Plant Throughput (bags/hour)': {'target': 2400, 'actual': 2350, 'unit': 'bags/hour', 'lower_better': False},
        'Despatch Volume (tons/day)': {'target': 5800, 'actual': 5900, 'unit': 'tons/day', 'lower_better': False},
        'Inventory Turnover Ratio': {'target': 8, 'actual': 7.5, 'unit': 'ratio', 'lower_better': False}
    },
    'Maintenance - Mechanical': {
        'MTBF (hours)': {'target': 720, 'actual': 680, 'unit': 'hours', 'lower_better': False},
        'MTTR (hours)': {'target': 4, 'actual': 4.5, 'unit': 'hours', 'lower_better': True},
        'Preventive Maintenance Compliance (%)': {'target': 95, 'actual': 92, 'unit': '%', 'lower_better': False},
        'Equipment Reliability (%)': {'target': 98, 'actual': 96, 'unit': '%', 'lower_better': False},
        'Spare Parts Availability (%)': {'target': 90, 'actual': 85, 'unit': '%', 'lower_better': False},
        'Vibration Levels (mm/s)': {'target': 4.5, 'actual': 5.2, 'unit': 'mm/s', 'lower_better': True},
        'Lubrication Compliance (%)': {'target': 98, 'actual': 95, 'unit': '%', 'lower_better': False}
    },
    'Maintenance - Electrical': {
        'Power Factor': {'target': 0.95, 'actual': 0.92, 'unit': 'PF', 'lower_better': False},
        'Voltage Stability Index (%)': {'target': 98, 'actual': 95, 'unit': '%', 'lower_better': False},
        'Motor Efficiency (%)': {'target': 94, 'actual': 92, 'unit': '%', 'lower_better': False},
        'Transformer Loading (%)': {'target': 85, 'actual': 88, 'unit': '%', 'lower_better': True},
        'UPS Availability (%)': {'target': 99.5, 'actual': 99, 'unit': '%', 'lower_better': False},
        'Electrical Downtime (hours)': {'target': 20, 'actual': 25, 'unit': 'hours', 'lower_better': True},
        'Cable Insulation Resistance (MΩ)': {'target': 100, 'actual': 95, 'unit': 'MΩ', 'lower_better': False}
    },
    'Maintenance - DCS & Instrument': {
        'Control System Availability (%)': {'target': 99.5, 'actual': 99.2, 'unit': '%', 'lower_better': False},
        'Sensor Calibration Accuracy (%)': {'target': 98, 'actual': 97, 'unit': '%', 'lower_better': False},
        'Data Acquisition Rate (%)': {'target': 99, 'actual': 98.5, 'unit': '%', 'lower_better': False},
        'Loop Performance Index (%)': {'target': 95, 'actual': 93, 'unit': '%', 'lower_better': False},
        'Alarm Management Score (%)': {'target': 90, 'actual': 87, 'unit': '%', 'lower_better': False},
        'Network Uptime (%)': {'target': 99.9, 'actual': 99.8, 'unit': '%', 'lower_better': False},
        'Controller Health Index (%)': {'target': 98, 'actual': 96, 'unit': '%', 'lower_better': False}
    },
    'Maintenance - Heavy Equipment': {
        'Excavator Availability (%)': {'target': 85, 'actual': 83, 'unit': '%', 'lower_better': False},
        'Loader Availability (%)': {'target': 88, 'actual': 86, 'unit': '%', 'lower_better': False},
        'Dump Truck Availability (%)': {'target': 82, 'actual': 80, 'unit': '%', 'lower_better': False},
        'Fuel Efficiency (L/ton)': {'target': 0.85, 'actual': 0.90, 'unit': 'L/ton', 'lower_better': True},
        'Tire Life (hours)': {'target': 2000, 'actual': 1850, 'unit': 'hours', 'lower_better': False},
        'Hydraulic System Pressure (bar)': {'target': 250, 'actual': 245, 'unit': 'bar', 'lower_better': False},
        'Equipment Utilization (%)': {'target': 75, 'actual': 72, 'unit': '%', 'lower_better': False}
    },
    'Utility - Civil': {
        'Building Structural Health (%)': {'target': 95, 'actual': 93, 'unit': '%', 'lower_better': False},
        'Road Condition Index (1-10)': {'target': 8, 'actual': 7.5, 'unit': '1-10', 'lower_better': False},
        'Water Management Efficiency (%)': {'target': 90, 'actual': 88, 'unit': '%', 'lower_better': False},
        'Waste Treatment Compliance (%)': {'target': 100, 'actual': 98, 'unit': '%', 'lower_better': False},
        'Dust Suppression Efficiency (%)': {'target': 95, 'actual': 92, 'unit': '%', 'lower_better': False},
        'Green Belt Coverage (%)': {'target': 30, 'actual': 28, 'unit': '%', 'lower_better': False},
        'Infrastructure Maintenance Cost ($/m²)': {'target': 5, 'actual': 5.5, 'unit': '$/m²', 'lower_better': True}
    },
    'Utility - Industrial Services': {
        'Compressed Air Quality (ppm)': {'target': 5, 'actual': 7, 'unit': 'ppm', 'lower_better': True},
        'Water Treatment Efficiency (%)': {'target': 95, 'actual': 92, 'unit': '%', 'lower_better': False},
        'Waste Heat Recovery (kW)': {'target': 5000, 'actual': 4800, 'unit': 'kW', 'lower_better': False},
        'HVAC Efficiency (%)': {'target': 88, 'actual': 85, 'unit': '%', 'lower_better': False},
        'Lighting Efficiency (lux/W)': {'target': 120, 'actual': 115, 'unit': 'lux/W', 'lower_better': False},
        'Housekeeping Score (%)': {'target': 90, 'actual': 87, 'unit': '%', 'lower_better': False},
        'Utility Cost per ton ($)': {'target': 3.5, 'actual': 3.8, 'unit': '$/ton', 'lower_better': True}
    },
    'HSE': {
        'Lost Time Injury Frequency': {'target': 0.5, 'actual': 0.8, 'unit': 'per million hrs', 'lower_better': True},
        'Total Recordable Cases': {'target': 2, 'actual': 3, 'unit': 'cases', 'lower_better': True},
        'Safety Training Hours/Employee': {'target': 40, 'actual': 35, 'unit': 'hours', 'lower_better': False},
        'Environmental Compliance Rate (%)': {'target': 100, 'actual': 98, 'unit': '%', 'lower_better': False},
        'Air Quality Index (PM2.5)': {'target': 50, 'actual': 65, 'unit': 'µg/m³', 'lower_better': True},
        'Noise Levels (dB)': {'target': 85, 'actual': 88, 'unit': 'dB', 'lower_better': True},
        'PPE Compliance (%)': {'target': 100, 'actual': 97, 'unit': '%', 'lower_better': False}
    },
    'Power Generation': {
        'Power Generation (MW)': {'target': 25, 'actual': 24, 'unit': 'MW', 'lower_better': False},
        'WHR Generation (MW)': {'target': 8, 'actual': 7.5, 'unit': 'MW', 'lower_better': False},
        'Grid Import (MW)': {'target': 15, 'actual': 16, 'unit': 'MW', 'lower_better': True},
        'Specific Fuel Consumption (L/kWh)': {'target': 0.28, 'actual': 0.30, 'unit': 'L/kWh', 'lower_better': True},
        'Generator Efficiency (%)': {'target': 92, 'actual': 90, 'unit': '%', 'lower_better': False},
        'CO2 Emissions (tons/MWh)': {'target': 0.85, 'actual': 0.88, 'unit': 'tons/MWh', 'lower_better': True},
        'Auxiliary Power Consumption (%)': {'target': 8, 'actual': 8.5, 'unit': '%', 'lower_better': True}
    },
    'Quality Control': {
        'Cement Strength (MPa)': {'target': 42.5, 'actual': 42.0, 'unit': 'MPa', 'lower_better': False},
        'Fineness (Blaine cm²/g)': {'target': 3200, 'actual': 3150, 'unit': 'cm²/g', 'lower_better': False},
        'SO3 Content (%)': {'target': 2.8, 'actual': 2.9, 'unit': '%', 'lower_better': False},
        'MgO Content (%)': {'target': 2.0, 'actual': 2.1, 'unit': '%', 'lower_better': True},
        'Clinker Free Lime (%)': {'target': 1.2, 'actual': 1.3, 'unit': '%', 'lower_better': True},
        'Sampling Frequency Compliance (%)': {'target': 100, 'actual': 98, 'unit': '%', 'lower_better': False},
        'Lab Test Accuracy (%)': {'target': 99, 'actual': 98, 'unit': '%', 'lower_better': False}
    },
    'Quarry & Crusher': {
        'Limestone Production (tons/day)': {'target': 10000, 'actual': 9800, 'unit': 'tons/day', 'lower_better': False},
        'Crusher Throughput (tph)': {'target': 800, 'actual': 780, 'unit': 'tph', 'lower_better': False},
        'Crusher Availability (%)': {'target': 90, 'actual': 88, 'unit': '%', 'lower_better': False},
        'Blasting Efficiency (tons/kg)': {'target': 5.5, 'actual': 5.2, 'unit': 'tons/kg', 'lower_better': False},
        'Material Size Distribution (mm)': {'target': 50, 'actual': 52, 'unit': 'mm', 'lower_better': True},
        'Stockpile Inventory (tons)': {'target': 50000, 'actual': 48000, 'unit': 'tons', 'lower_better': False},
        'Hauling Distance (km)': {'target': 2.5, 'actual': 2.7, 'unit': 'km', 'lower_better': True}
    }
}

def calculate_department_score(dept_data):
    """Calculate performance score for a department"""
    scores = []
    for kpi, data in dept_data.items():
        target = data['target']
        actual = data['actual']
        lower_better = data.get('lower_better', False)
        
        if target > 0:
            if lower_better:
                score = max(0, min(100, (target / actual) * 100)) if actual > 0 else 0
            else:
                score = max(0, min(100, (actual / target) * 100))
            scores.append(score)
    
    return np.mean(scores) if scores else 0

def create_kpi_table(dept_name, dept_data):
    """Create an HTML table for KPIs"""
    rows = []
    for kpi, data in dept_data.items():
        target = data['target']
        actual = data['actual']
        unit = data['unit']
        lower_better = data.get('lower_better', False)
        
        # Calculate achievement
        if lower_better:
            achievement = (target / actual * 100) if actual > 0 else 0
            on_track = actual <= target
        else:
            achievement = (actual / target * 100) if target > 0 else 0
            on_track = actual >= target
        
        status_color = colors['success'] if on_track else colors['danger']
        status_text = "✅ On Track" if on_track else "❌ Needs Improvement"
        
        row = html.Tr([
            html.Td(kpi, style={'padding': '8px', 'border': '1px solid #ddd'}),
            html.Td(f"{target:.2f}" if isinstance(target, float) else str(target), 
                   style={'padding': '8px', 'border': '1px solid #ddd', 'text-align': 'center'}),
            html.Td(f"{actual:.2f}" if isinstance(actual, float) else str(actual), 
                   style={'padding': '8px', 'border': '1px solid #ddd', 'text-align': 'center'}),
            html.Td(unit, style={'padding': '8px', 'border': '1px solid #ddd', 'text-align': 'center'}),
            html.Td(f"{achievement:.1f}%", 
                   style={'padding': '8px', 'border': '1px solid #ddd', 'text-align': 'center'}),
            html.Td(status_text, 
                   style={'padding': '8px', 'border': '1px solid #ddd', 'text-align': 'center', 'color': status_color})
        ])
        rows.append(row)
    
    table = html.Table([
        html.Thead(html.Tr([
            html.Th("KPI", style={'padding': '10px', 'background-color': colors['primary'], 'color': 'white'}),
            html.Th("Target", style={'padding': '10px', 'background-color': colors['primary'], 'color': 'white'}),
            html.Th("Actual", style={'padding': '10px', 'background-color': colors['primary'], 'color': 'white'}),
            html.Th("Unit", style={'padding': '10px', 'background-color': colors['primary'], 'color': 'white'}),
            html.Th("Achievement", style={'padding': '10px', 'background-color': colors['primary'], 'color': 'white'}),
            html.Th("Status", style={'padding': '10px', 'background-color': colors['primary'], 'color': 'white'})
        ])),
        html.Tbody(rows)
    ], style={'width': '100%', 'border-collapse': 'collapse', 'margin-top': '20px'})
    
    return table

# Create navigation tabs
tabs = []
dept_list = list(KPI_DATA.keys())

# Add Overall tab first
tabs.append(dbc.Tab(label="📊 Overall Dashboard", tab_id="overall", children=[
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Overall Plant Performance", className="card-title"),
                    html.H2(f"{np.mean([calculate_department_score(KPI_DATA[dept]) for dept in dept_list]):.1f}%", 
                           style={'color': colors['primary'], 'font-size': '48px'}),
                    html.P("Overall Performance Score", className="card-text")
                ])
            ], color="primary", inverse=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total KPIs Tracked", className="card-title"),
                    html.H2(f"{sum(len(KPI_DATA[dept]) for dept in dept_list)}", 
                           style={'color': colors['success'], 'font-size': '48px'}),
                    html.P("Across All Departments", className="card-text")
                ])
            ], color="success", inverse=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Departments", className="card-title"),
                    html.H2(f"{len(dept_list)}", 
                           style={'color': colors['warning'], 'font-size': '48px'}),
                    html.P("Active Monitoring", className="card-text")
                ])
            ], color="warning", inverse=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("On-Track KPIs", className="card-title"),
                    html.H2(f"{sum(1 for dept in dept_list for k,v in KPI_DATA[dept].items() if (v['actual'] >= v['target'] if not v.get('lower_better', False) else v['actual'] <= v['target']))}", 
                           style={'color': colors['success'], 'font-size': '48px'}),
                    html.P("Meeting or Exceeding Targets", className="card-text")
                ])
            ], color="info", inverse=True)
        ], width=3)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Department Performance Summary", style={'text-align': 'center'})),
                dbc.CardBody([
                    dcc.Graph(
                        id='dept-performance-graph',
                        figure=px.bar(
                            x=dept_list,
                            y=[calculate_department_score(KPI_DATA[dept]) for dept in dept_list],
                            title="Department Performance Scores (%)",
                            labels={'x': 'Department', 'y': 'Performance Score (%)'},
                            color=[calculate_department_score(KPI_DATA[dept]) for dept in dept_list],
                            color_continuous_scale='Viridis'
                        ).update_layout(height=500, showlegend=False)
                    )
                ])
            ])
        ], width=12)
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("⚠️ Recent Alerts & Action Items", style={'color': colors['danger']})),
                dbc.CardBody([
                    html.Ul([
                        html.Li("⚠️ Specific Heat Consumption above target - Production Dept", style={'margin': '10px 0'}),
                        html.Li("⚠️ High vibration levels detected - Mechanical Section", style={'margin': '10px 0'}),
                        html.Li("⚠️ LTIF rate exceeded target - HSE Department", style={'margin': '10px 0'}),
                        html.Li("⚠️ Power factor below optimum - Electrical Section", style={'margin': '10px 0'}),
                        html.Li("ℹ️ Crusher throughput below target - Quarry Section", style={'margin': '10px 0'})
                    ], style={'font-size': '16px'})
                ])
            ])
        ], width=12)
    ])
]))

# Add department tabs
for dept_name in dept_list:
    dept_data = KPI_DATA[dept_name]
    score = calculate_department_score(dept_data)
    
    # Determine color based on score
    score_color = colors['success'] if score >= 80 else colors['warning'] if score >= 60 else colors['danger']
    
    tabs.append(dbc.Tab(label=dept_name[:20], tab_id=dept_name, children=[
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H3(f"{dept_name} KPI Dashboard", style={'text-align': 'center', 'color': colors['primary']})),
                    dbc.CardBody([
                        # Score Cards
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Department Performance", className="card-title"),
                                        html.H2(f"{score:.1f}%", style={'color': score_color, 'font-size': '36px'}),
                                        html.P("Overall Score", className="card-text")
                                    ])
                                ], color="light")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("KPIs Tracked", className="card-title"),
                                        html.H2(f"{len(dept_data)}", style={'color': colors['primary'], 'font-size': '36px'}),
                                        html.P("Active Metrics", className="card-text")
                                    ])
                                ], color="light")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("On-Track KPIs", className="card-title"),
                                        html.H2(f"{sum(1 for k,v in dept_data.items() if (v['actual'] >= v['target'] if not v.get('lower_better', False) else v['actual'] <= v['target']))}", 
                                               style={'color': colors['success'], 'font-size': '36px'}),
                                        html.P("Meeting Target", className="card-text")
                                    ])
                                ], color="light")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Critical KPIs", className="card-title"),
                                        html.H2(f"{sum(1 for k,v in dept_data.items() if (v['actual'] < v['target'] * 0.9 if not v.get('lower_better', False) else v['actual'] > v['target'] * 1.1))}", 
                                               style={'color': colors['danger'], 'font-size': '36px'}),
                                        html.P("Need Attention", className="card-text")
                                    ])
                                ], color="light")
                            ], width=3)
                        ]),
                        
                        html.Br(),
                        
                        # Target vs Actual Bar Chart
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        dcc.Graph(
                                            figure=px.bar(
                                                x=list(dept_data.keys()),
                                                y=[[v['target'] for v in dept_data.values()], [v['actual'] for v in dept_data.values()]],
                                                title="Target vs Actual Performance",
                                                labels={'x': 'KPI', 'y': 'Value', 'value': 'Value', 'variable': 'Type'},
                                                barmode='group'
                                            ).update_layout(height=400, showlegend=True, xaxis={'tickangle': 45})
                                        )
                                    ])
                                ])
                            ], width=12)
                        ]),
                        
                        html.Br(),
                        
                        # KPI Table
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(html.H5("Detailed KPI Performance Table", style={'text-align': 'center'})),
                                    dbc.CardBody([
                                        create_kpi_table(dept_name, dept_data)
                                    ])
                                ])
                            ], width=12)
                        ])
                    ])
                ])
            ], width=12)
        ])
    ]))

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🏭 Berber Cement Plant - KPI Dashboard", 
                style={'text-align': 'center', 'color': colors['primary'], 'padding': '20px', 'margin': '0'}),
        html.P("Real-time Performance Monitoring Platform", 
               style={'text-align': 'center', 'color': colors['secondary'], 'font-size': '18px', 'margin-bottom': '20px'})
    ], style={'background-color': colors['light'], 'border-radius': '5px'}),
    
    # Tabs
    dbc.Tabs(tabs, active_tab="overall"),
    
    # Footer
    html.Br(),
    html.Hr(),
    html.Footer(
        html.P(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Berber Cement Plant - KPI Dashboard v2.0",
               style={'text-align': 'center', 'color': 'gray', 'font-size': '12px', 'padding': '20px'})
    )
], style={'padding': '20px', 'font-family': 'Arial, sans-serif', 'background-color': '#f8f9fa'})

# Run the app
if __name__ == '__main__':
    print("="*80)
    print("🏭 BERBER CEMENT PLANT - KPI DASHBOARD")
    print("="*80)
    print("\n🚀 Starting Dashboard Server...")
    print("📊 Dashboard includes:")
    print(f"   • {len(KPI_DATA)} Department Dashboards")
    print(f"   • {sum(len(KPI_DATA[dept]) for dept in KPI_DATA)} KPIs with real-time tracking")
    print("   • Interactive visualizations")
    print("   • Performance scoring system")
    print("\n🌐 Access the dashboard at: http://127.0.0.1:8050")
    print("📱 Dashboard is responsive and works on desktop & tablet")
    print("\n💡 Features:")
    print("   • Department performance scores")
    print("   • Target vs actual comparisons")
    print("   • Color-coded status indicators")
    print("   • Automatic calculations")
    print("\n⚠️ Press Ctrl+C to stop the server")
    print("="*80)
    
    app.run_server(debug=True, port=8050)
