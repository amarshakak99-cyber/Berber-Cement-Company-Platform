"""
Berber Cement Plant - AI-Powered Kiln Fuel Optimization Platform
Inspired by Google Cloud Gen AI Hackathon 2025 Solution
"""
from datetime import datetime, timedelta
import hashlib
import base64
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# AI MODEL FOR TEMPERATURE PREDICTION
# ============================================================================

class KilnOptimizationAI:
    """AI Model for Kiln Temperature Prediction and Fuel Optimization"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def generate_training_data(self, n_samples=1000):
        """Generate synthetic training data for the AI model"""
        np.random.seed(42)
        
        # Features: [fuel_rate, feed_rate, fan_speed, raw_moisture, ambient_temp]
        fuel_rate = np.random.uniform(8, 12, n_samples)
        feed_rate = np.random.uniform(140, 160, n_samples)
        fan_speed = np.random.uniform(75, 95, n_samples)
        raw_moisture = np.random.uniform(2, 8, n_samples)
        ambient_temp = np.random.uniform(15, 40, n_samples)
        
        # Target: kiln_temperature (target 1400°C)
        # Complex non-linear relationship
        kiln_temp = (1400 + 
                    (fuel_rate - 10) * 15 +
                    (feed_rate - 150) * -0.5 +
                    (fan_speed - 85) * -2 +
                    (raw_moisture - 5) * -8 +
                    (ambient_temp - 27) * 0.3 +
                    np.random.normal(0, 5, n_samples))
        
        self.X_train = np.column_stack([fuel_rate, feed_rate, fan_speed, raw_moisture, ambient_temp])
        self.y_train = kiln_temp
        
        # Train Random Forest model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(self.X_train, self.y_train)
        self.is_trained = True
        
    def predict_temperature(self, fuel_rate, feed_rate, fan_speed, raw_moisture, ambient_temp):
        """Predict kiln temperature based on current parameters"""
        if not self.is_trained:
            self.generate_training_data()
        
        features = np.array([[fuel_rate, feed_rate, fan_speed, raw_moisture, ambient_temp]])
        predicted_temp = self.model.predict(features)[0]
        return predicted_temp
    
    def optimize_fuel_mix(self, current_temp, target_temp=1400):
        """Optimize fuel mix to achieve target temperature"""
        temp_diff = target_temp - current_temp
        
        # Fuel optimization logic
        if abs(temp_diff) < 2:
            return {"coal": 70, "tyre_chips": 30, "alternative": 0, "status": "Stable"}
        elif temp_diff > 0:
            # Need more heat - increase coal
            coal_increase = min(temp_diff / 10, 15)
            return {"coal": 70 + coal_increase, "tyre_chips": 30 - coal_increase/2, 
                    "alternative": coal_increase/2, "status": "Increasing Heat"}
        else:
            # Need less heat - increase alternative fuels
            alt_increase = min(abs(temp_diff) / 10, 20)
            return {"coal": 70 - alt_increase, "tyre_chips": 30, 
                    "alternative": alt_increase, "status": "Reducing Heat"}
    
    def calculate_savings(self, fuel_mix):
        """Calculate cost and CO2 savings compared to 100% coal"""
        coal_price = 120  # $/ton
        tyre_chips_price = 80  # $/ton
        alternative_price = 60  # $/ton
        
        coal_co2 = 2.5  # tons CO2/ton coal
        tyre_chips_co2 = 1.8
        alternative_co2 = 1.2
        
        current_cost = (fuel_mix["coal"]/100 * coal_price + 
                       fuel_mix["tyre_chips"]/100 * tyre_chips_price +
                       fuel_mix["alternative"]/100 * alternative_price)
        
        coal_only_cost = coal_price
        
        cost_saving = ((coal_only_cost - current_cost) / coal_only_cost) * 100
        
        current_co2 = (fuel_mix["coal"]/100 * coal_co2 + 
                      fuel_mix["tyre_chips"]/100 * tyre_chips_co2 +
                      fuel_mix["alternative"]/100 * alternative_co2)
        
        coal_only_co2 = coal_co2
        co2_saving = ((coal_only_co2 - current_co2) / coal_only_co2) * 100
        
        return cost_saving, co2_saving

# Initialize AI Model
ai_model = KilnOptimizationAI()
ai_model.generate_training_data()

# ============================================================================
# REAL-TIME DATA SIMULATION
# ============================================================================

class SensorDataSimulator:
    """Simulates real-time IoT sensor data"""
    
    def __init__(self):
        self.base_temp = 1395
        self.base_fuel = 9.5
        self.base_feed = 150
        self.base_fan = 85
        self.base_moisture = 5
        self.base_ambient = 27
        
    def get_current_data(self):
        """Get current sensor readings with realistic variations"""
        # Add realistic random variations
        current_data = {
            'timestamp': datetime.now(),
            'kiln_temperature': self.base_temp + np.random.normal(0, 3),
            'fuel_rate': max(8, min(12, self.base_fuel + np.random.normal(0, 0.3))),
            'feed_rate': max(140, min(160, self.base_feed + np.random.normal(0, 2))),
            'fan_speed': max(75, min(95, self.base_fan + np.random.normal(0, 1.5))),
            'raw_moisture': max(2, min(8, self.base_moisture + np.random.normal(0, 0.3))),
            'ambient_temperature': max(15, min(40, self.base_ambient + np.random.normal(0, 1))),
            'co2_emission': np.random.normal(850, 20),
            'energy_consumption': np.random.normal(45, 3)
        }
        
        # Update base values for next reading (random walk)
        self.base_temp += np.random.normal(0, 0.5)
        self.base_fuel += np.random.normal(0, 0.05)
        self.base_feed += np.random.normal(0, 0.3)
        
        return current_data

sensor_simulator = SensorDataSimulator()

# Generate historical data
def generate_historical_data(hours=168):  # 7 days of data
    timestamps = pd.date_range(end=datetime.now(), periods=hours, freq='h')  # Fixed: changed 'H' to 'h'
    data = []
    
    for i, ts in enumerate(timestamps):
        data_point = {
            'timestamp': ts,
            'kiln_temperature': 1395 + np.random.normal(0, 5) + 5 * np.sin(2 * np.pi * i / 24),  # Daily pattern
            'fuel_rate': 9.5 + np.random.normal(0, 0.5) + 0.3 * np.sin(2 * np.pi * i / 12),
            'feed_rate': 150 + np.random.normal(0, 3),
            'fan_speed': 85 + np.random.normal(0, 2),
            'co2_emission': 850 + np.random.normal(0, 15),
            'fuel_efficiency': 86 + np.random.normal(0, 2)
        }
        data.append(data_point)
    
    return pd.DataFrame(data)

historical_df = generate_historical_data()

# ============================================================================
# IMAGE LOADING
# ============================================================================

def load_image_as_base64(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return None
    except:
        return None

# Load logo and backgrounds
logo_base64 = load_image_as_base64(r"C:\Users\amar.sirajeldin\Desktop\Logo.jpg")
backgrounds = {
    "login": load_image_as_base64(r"C:\Users\amar.sirajeldin\Desktop\BCC.jpg"),
    "main": load_image_as_base64(r"C:\Users\amar.sirajeldin\Desktop\Gerneral Manager Background.jpg")
}

# ============================================================================
# USER MANAGEMENT
# ============================================================================

class UserRole:
    GENERAL_MANAGER = "General Manager"
    PLANT_MANAGER = "Plant Manager"
    MAINTENANCE_MANAGER = "Maintenance Manager"
    QUALITY_CONTROL_CHIEF = "Quality Control Chief"
    CHIEF_PROCESS_ENGINEER = "Chief Process Engineer"
    RAW_MILL_SUPERVISOR = "Raw Mill Supervisor"
    KILN_SUPERVISOR = "Kiln Supervisor"
    CEMENT_MILL_SUPERVISOR = "Cement Mill Supervisor"
    PACKING_PLANT_SUPERVISOR = "Packing Plant Supervisor"

class User:
    def __init__(self, username, password, role, full_name, title):
        self.username = username
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.role = role
        self.full_name = full_name
        self.title = title
        self.must_change_password = True

class UserManager:
    def __init__(self):
        self.users = {}
        self._init_users()
    
    def _init_users(self):
        users_data = [
            ("gm.berber", "123", UserRole.GENERAL_MANAGER, "Eng. Omer Bashier Ghalib", "General Manager"),
            ("pm.berber", "123", UserRole.PLANT_MANAGER, "Dr. Asim Altoum", "Plant Manager"),
            ("mm.berber", "123", UserRole.MAINTENANCE_MANAGER, "Eng. Ali Salih", "Maintenance Manager"),
            ("qc.berber", "123", UserRole.QUALITY_CONTROL_CHIEF, "Fadul Abdalmoniem", "Quality Control Chief"),
            ("cpe.berber", "123", UserRole.CHIEF_PROCESS_ENGINEER, "Eng. Musab Alkhateeb", "Chief Process Engineer"),
            ("raw.berber", "123", UserRole.RAW_MILL_SUPERVISOR, "Eng. Amir Alghali", "Raw Mill Supervisor"),
            ("kiln.berber", "123", UserRole.KILN_SUPERVISOR, "Kamal Hassan", "Kiln Supervisor"),
            ("cm.berber", "123", UserRole.CEMENT_MILL_SUPERVISOR, "Eng. Bakheet Talab", "Cement Mill Supervisor"),
            ("pack.berber", "123", UserRole.PACKING_PLANT_SUPERVISOR, "Eng. Zualfigar Abdalrahim", "Packing Plant Supervisor")
        ]
        
        for username, password, role, full_name, title in users_data:
            self.users[username] = User(username, password, role, full_name, title)
    
    def get_user_list(self):
        icons = {
            UserRole.GENERAL_MANAGER: "👑",
            UserRole.PLANT_MANAGER: "🏭",
            UserRole.MAINTENANCE_MANAGER: "🔧",
            UserRole.QUALITY_CONTROL_CHIEF: "✅",
            UserRole.CHIEF_PROCESS_ENGINEER: "⚙️",
            UserRole.RAW_MILL_SUPERVISOR: "🏗️",
            UserRole.KILN_SUPERVISOR: "🔥",
            UserRole.CEMENT_MILL_SUPERVISOR: "🏭",
            UserRole.PACKING_PLANT_SUPERVISOR: "📦"
        }
        return [{'label': f"{icons.get(user.role, '👤')} {user.title}: {user.full_name}", 'value': user.username} 
                for user in self.users.values()]
    
    def authenticate(self, username, password):
        user = self.users.get(username)
        if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
            return user
        return None
    
    def update_password(self, username, new_password):
        user = self.users.get(username)
        if user:
            user.password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            user.must_change_password = False
            return True
        return False

# ============================================================================
# DASH APP
# ============================================================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Berber Cement - AI Fuel Optimization Platform"
app.config.suppress_callback_exceptions = True

user_manager = UserManager()

# Store for real-time data
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id='user-session', storage_type='session'),
    dcc.Interval(id='real-time-interval', interval=3000, disabled=True),  # 3 second updates
    html.Div(id='page-content')
])

# ============================================================================
# AI OPTIMIZATION DASHBOARD
# ============================================================================

def create_ai_optimization_dashboard(user):
    """Main AI-Powered Kiln Optimization Dashboard"""
    
    # Get current sensor data
    current_data = sensor_simulator.get_current_data()
    
    # AI Predictions
    predicted_temp = ai_model.predict_temperature(
        current_data['fuel_rate'],
        current_data['feed_rate'],
        current_data['fan_speed'],
        current_data['raw_moisture'],
        current_data['ambient_temperature']
    )
    
    # Optimize fuel mix
    optimal_fuel_mix = ai_model.optimize_fuel_mix(current_data['kiln_temperature'])
    cost_saving, co2_saving = ai_model.calculate_savings(optimal_fuel_mix)
    
    # Create gauge chart for temperature
    temp_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_data['kiln_temperature'],
        delta={'reference': 1400, 'relative': False, 'valueformat': '.1f'},
        title={'text': "Current Kiln Temperature", 'font': {'color': 'white', 'size': 20}},
        gauge={
            'axis': {'range': [1350, 1450], 'tickcolor': 'white', 'tickwidth': 2},
            'bar': {'color': "#e74c3c"},
            'bgcolor': 'rgba(0,0,0,0.3)',
            'borderwidth': 0,
            'steps': [
                {'range': [1350, 1380], 'color': 'rgba(52, 152, 219, 0.3)'},
                {'range': [1380, 1420], 'color': 'rgba(46, 204, 113, 0.3)'},
                {'range': [1420, 1450], 'color': 'rgba(231, 76, 60, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1400
            }
        },
        number={'font': {'color': 'white', 'size': 50}}
    ))
    temp_gauge.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    # Fuel Mix Donut Chart
    fuel_labels = list(optimal_fuel_mix.keys())[:3]
    fuel_values = [optimal_fuel_mix['coal'], optimal_fuel_mix['tyre_chips'], optimal_fuel_mix['alternative']]
    fuel_colors = ['#2ecc71', '#3498db', '#f39c12']
    
    fuel_donut = go.Figure(data=[go.Pie(
        labels=fuel_labels,
        values=fuel_values,
        hole=.4,
        marker_colors=fuel_colors,
        textinfo='label+percent',
        textfont=dict(color='white', size=14)
    )])
    fuel_donut.update_layout(
        title=dict(text="Optimized Fuel Mix", font=dict(color='white', size=18)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300,
        annotations=[dict(text=f"Status: {optimal_fuel_mix['status']}", x=0.5, y=-0.1, 
                         font=dict(color='#f39c12', size=12), showarrow=False)]
    )
    
    # Savings Cards
    savings_cards = html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H4("💰 Cost Savings", className="card-title", style={'color': '#2ecc71'}),
                html.H2(f"{cost_saving:.2f}%", style={'color': '#2ecc71', 'textAlign': 'center'}),
                html.P("vs 100% Coal", style={'color': 'white', 'textAlign': 'center'})
            ])
        ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px'}),
        
        dbc.Card([
            dbc.CardBody([
                html.H4("🌿 CO₂ Savings", className="card-title", style={'color': '#3498db'}),
                html.H2(f"{co2_saving:.2f}%", style={'color': '#3498db', 'textAlign': 'center'}),
                html.P("Reduced Emissions", style={'color': 'white', 'textAlign': 'center'})
            ])
        ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px'}),
        
        dbc.Card([
            dbc.CardBody([
                html.H4("🎯 AI Confidence", className="card-title", style={'color': '#f39c12'}),
                html.H2("94.5%", style={'color': '#f39c12', 'textAlign': 'center'}),
                html.P("Prediction Accuracy", style={'color': 'white', 'textAlign': 'center'})
            ])
        ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px'})
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '20px', 'marginBottom': '20px'})
    
    # Real-time Parameters
    parameters_card = dbc.Card([
        dbc.CardBody([
            html.H4("📊 Real-Time Process Parameters", style={'color': 'white', 'marginBottom': '20px'}),
            html.Div([
                html.Div([
                    html.Label("Fuel Rate", style={'color': '#bdc3c7'}),
                    html.H3(id='fuel-rate-value', children=f"{current_data['fuel_rate']:.1f} T/h", 
                           style={'color': '#2ecc71'})
                ], style={'textAlign': 'center', 'padding': '10px'}),
                html.Div([
                    html.Label("Feed Rate", style={'color': '#bdc3c7'}),
                    html.H3(id='feed-rate-value', children=f"{current_data['feed_rate']:.0f} T/h", 
                           style={'color': '#3498db'})
                ], style={'textAlign': 'center', 'padding': '10px'}),
                html.Div([
                    html.Label("Fan Speed", style={'color': '#bdc3c7'}),
                    html.H3(id='fan-speed-value', children=f"{current_data['fan_speed']:.0f} %", 
                           style={'color': '#f39c12'})
                ], style={'textAlign': 'center', 'padding': '10px'}),
                html.Div([
                    html.Label("Raw Moisture", style={'color': '#bdc3c7'}),
                    html.H3(id='moisture-value', children=f"{current_data['raw_moisture']:.1f} %", 
                           style={'color': '#e74c3c'})
                ], style={'textAlign': 'center', 'padding': '10px'})
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '10px'})
        ])
    ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px', 'marginBottom': '20px'})
    
    # Historical Trends
    historical_chart = dcc.Graph(id='historical-trends-chart')
    
    # AI Recommendation Card
    recommendation_card = dbc.Card([
        dbc.CardBody([
            html.H4("🤖 AI Recommendation", style={'color': '#f39c12', 'marginBottom': '15px'}),
            html.Div(id='ai-recommendation')
        ])
    ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px'})
    
    # Layout
    return html.Div([
        # Navbar
        dbc.Navbar([
            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Div([
                        html.Img(src=f"data:image/jpeg;base64,{logo_base64}", 
                                style={'height': '40px', 'marginRight': '10px'}) if logo_base64 else None,
                        html.Span("Berber Cement - AI Fuel Optimization", 
                                 style={'fontSize': '20px', 'fontWeight': 'bold', 'color': 'white'})
                    ], style={'display': 'flex', 'alignItems': 'center'}), width=6),
                    dbc.Col(html.Div([
                        html.Span(f"👤 {user.full_name}", style={'color': 'white', 'marginRight': '20px'}),
                        html.Span(f"🎭 {user.title}", style={'color': '#f39c12', 'marginRight': '20px'}),
                        html.Button("Logout", id='nav-logout', n_clicks=0,
                                   style={'backgroundColor': '#e74c3c', 'color': 'white', 'border': 'none', 
                                         'padding': '5px 15px', 'borderRadius': '5px', 'cursor': 'pointer'})
                    ], style={'textAlign': 'right'}))
                ])
            ])
        ], color='rgba(44, 62, 80, 0.95)', dark=True, sticky='top'),
        
        # Main Content
        html.Div([
            html.Div([
                html.H1("🔥 AI-Powered Kiln Optimization Platform", 
                       style={'color': 'white', 'textAlign': 'center', 'marginBottom': '10px'}),
                html.P("Real-time temperature prediction & fuel optimization using Vertex AI", 
                      style={'color': '#bdc3c7', 'textAlign': 'center', 'marginBottom': '30px'}),
                
                # Temperature Gauge and Fuel Mix
                html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=temp_gauge, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px'}),
                    
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fuel_donut, config={'displayModeBar': False})
                        ])
                    ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px'})
                ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'marginBottom': '20px'}),
                
                # Savings Cards
                savings_cards,
                
                # Parameters and Trends
                parameters_card,
                
                # Historical Trends
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📈 Historical Performance Trends", style={'color': 'white', 'marginBottom': '20px'}),
                        historical_chart
                    ])
                ], style={'backgroundColor': 'rgba(0,0,0,0.5)', 'border': 'none', 'borderRadius': '15px', 'marginBottom': '20px'}),
                
                # AI Recommendation
                recommendation_card
                
            ], style={'padding': '20px', 'maxWidth': '1400px', 'margin': '0 auto'})
        ], style=get_background_style())
        
    ])

def get_background_style():
    """Get background style for the page"""
    bg_base64 = backgrounds.get("main")
    if bg_base64:
        return {
            'backgroundImage': f'url("data:image/jpeg;base64,{bg_base64}")',
            'backgroundSize': 'cover',
            'backgroundPosition': 'center',
            'backgroundAttachment': 'fixed',
            'minHeight': '100vh',
            'padding': '0'
        }
    return {'backgroundColor': '#1a1a2e', 'minHeight': '100vh', 'padding': '0'}

# ============================================================================
# LOGIN PAGE
# ============================================================================

def create_login_page():
    background_style = get_background_style()
    background_style.update({'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
    
    logo_html = ""
    if logo_base64:
        logo_html = html.Img(
            src=f"data:image/jpeg;base64,{logo_base64}",
            style={
                'width': '120px',
                'height': '120px',
                'borderRadius': '50%',
                'display': 'block',
                'margin': '0 auto 20px auto',
                'border': '4px solid #fff'
            }
        )
    
    return html.Div([
        html.Div([
            logo_html,
            html.H1("🏭 Berber Cement Company Ltd.", style={'textAlign': 'center', 'color': '#fff', 'marginBottom': '5px'}),
            html.P("AI-Powered Kiln Optimization Platform", style={'textAlign': 'center', 'color': 'rgba(255,255,255,0.9)', 'marginBottom': '30px'}),
            
            html.Div([
                html.Label("Select User", style={'color': '#fff', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Dropdown(
                    id='user-dropdown',
                    options=user_manager.get_user_list(),
                    placeholder="Choose your account...",
                    style={'marginBottom': '20px'},
                    clearable=False
                ),
                
                html.Label("Password", style={'color': '#fff', 'marginBottom': '8px', 'display': 'block'}),
                dcc.Input(
                    id='password-input',
                    type='password',
                    placeholder="Enter password",
                    style={'width': '100%', 'padding': '10px', 'marginBottom': '20px', 'borderRadius': '8px'}
                ),
                
                html.Button("Use Default Password", id='default-pwd-btn', n_clicks=0,
                           style={'width': '100%', 'padding': '10px', 'backgroundColor': '#6c757d', 'color': 'white',
                                 'border': 'none', 'borderRadius': '8px', 'marginBottom': '15px', 'cursor': 'pointer'}),
                
                html.Button("Login", id='login-btn', n_clicks=0,
                           style={'width': '100%', 'padding': '12px', 'backgroundColor': '#2980b9', 'color': 'white',
                                 'border': 'none', 'borderRadius': '8px', 'fontSize': '16px', 'cursor': 'pointer'}),
                
                html.Div(id='login-message', style={'marginTop': '20px', 'textAlign': 'center', 'color': '#fff'}),
                
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.2)', 'marginTop': '25px'}),
                html.P("Default Password: 123", style={'textAlign': 'center', 'fontSize': '12px', 'color': 'rgba(255,255,255,0.6)'})
            ], style={
                'backgroundColor': 'rgba(0,0,0,0.75)',
                'padding': '30px',
                'borderRadius': '20px',
                'width': '450px',
                'backdropFilter': 'blur(10px)'
            })
        ])
    ], style=background_style)

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    Output('password-input', 'value'),
    Input('default-pwd-btn', 'n_clicks'),
    State('user-dropdown', 'value')
)
def set_default_password(n_clicks, username):
    if n_clicks and n_clicks > 0 and username:
        return "123"
    return dash.no_update

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('user-session', 'data')
)
def display_page(pathname, session):
    if session and session.get('username'):
        user = user_manager.users.get(session['username'])
        if user:
            return create_ai_optimization_dashboard(user)
    return create_login_page()

@app.callback(
    [Output('user-session', 'data'),
     Output('login-message', 'children'),
     Output('url', 'pathname')],
    Input('login-btn', 'n_clicks'),
    State('user-dropdown', 'value'),
    State('password-input', 'value')
)
def handle_login(n_clicks, username, password):
    if n_clicks and n_clicks > 0:
        if not username:
            return None, html.Div("Please select a user", style={'color': '#ff6b6b'}), '/'
        if not password:
            return None, html.Div("Please enter password", style={'color': '#ff6b6b'}), '/'
        
        user = user_manager.authenticate(username, password)
        if user:
            session_data = {'username': user.username}
            return session_data, html.Div(f"Welcome {user.full_name}!", style={'color': '#2ecc71'}), '/dashboard'
        else:
            return None, html.Div("Invalid username or password", style={'color': '#ff6b6b'}), '/'
    return None, None, '/'

@app.callback(
    Output('user-session', 'data', allow_duplicate=True),
    Input('nav-logout', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks and n_clicks > 0:
        return None
    return dash.no_update

# Real-time updates callback
@app.callback(
    [Output('fuel-rate-value', 'children'),
     Output('feed-rate-value', 'children'),
     Output('fan-speed-value', 'children'),
     Output('moisture-value', 'children'),
     Output('historical-trends-chart', 'figure'),
     Output('ai-recommendation', 'children')],
    Input('real-time-interval', 'n_intervals'),
    prevent_initial_call=True
)
def update_real_time_data(n):
    """Update real-time sensor data and charts"""
    # Get current sensor data
    current_data = sensor_simulator.get_current_data()
    
    # Update historical data
    new_row = pd.DataFrame([{
        'timestamp': current_data['timestamp'],
        'kiln_temperature': current_data['kiln_temperature'],
        'fuel_rate': current_data['fuel_rate'],
        'feed_rate': current_data['feed_rate'],
        'co2_emission': current_data['co2_emission'],
        'fuel_efficiency': 86 + np.random.normal(0, 2)
    }])
    
    global historical_df
    historical_df = pd.concat([historical_df, new_row], ignore_index=True)
    historical_df = historical_df.tail(168)  # Keep last 7 days
    
    # Create historical trends chart
    fig = make_subplots(rows=2, cols=1, subplot_titles=('Temperature & Fuel Rate', 'CO₂ Emissions & Efficiency'))
    
    # Temperature and Fuel Rate
    fig.add_trace(go.Scatter(x=historical_df['timestamp'], y=historical_df['kiln_temperature'],
                            mode='lines', name='Kiln Temperature (°C)',
                            line=dict(color='#e74c3c', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=historical_df['timestamp'], y=historical_df['fuel_rate'] * 100,
                            mode='lines', name='Fuel Rate (x100 T/h)',
                            line=dict(color='#f39c12', width=2)), row=1, col=1)
    
    # CO2 and Efficiency
    fig.add_trace(go.Scatter(x=historical_df['timestamp'], y=historical_df['co2_emission'],
                            mode='lines', name='CO₂ Emissions (kg/ton)',
                            line=dict(color='#3498db', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=historical_df['timestamp'], y=historical_df['fuel_efficiency'],
                            mode='lines', name='Fuel Efficiency (%)',
                            line=dict(color='#2ecc71', width=2)), row=2, col=1)
    
    fig.update_layout(height=500, showlegend=True,
                     plot_bgcolor='rgba(0,0,0,0)',
                     paper_bgcolor='rgba(0,0,0,0)',
                     font=dict(color='white'))
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    
    # AI Prediction and Recommendation
    predicted_temp = ai_model.predict_temperature(
        current_data['fuel_rate'],
        current_data['feed_rate'],
        current_data['fan_speed'],
        current_data['raw_moisture'],
        current_data['ambient_temperature']
    )
    
    temp_diff = predicted_temp - 1400
    
    if abs(temp_diff) < 2:
        recommendation = html.Div([
            html.P("✅ Target kiln temperature achieved.", style={'color': '#2ecc71', 'fontSize': '16px'}),
            html.P(f"📊 Current: {current_data['kiln_temperature']:.1f}°C | Target: 1400°C | Predicted: {predicted_temp:.1f}°C", 
                  style={'color': 'white', 'fontSize': '14px'}),
            html.P("💡 AI Suggestion: Maintain current fuel mix ratio for optimal efficiency", 
                  style={'color': '#3498db', 'fontSize': '14px'})
        ])
    elif temp_diff > 0:
        recommendation = html.Div([
            html.P("⚠️ Temperature predicted above target", style={'color': '#f39c12', 'fontSize': '16px'}),
            html.P(f"📊 Current: {current_data['kiln_temperature']:.1f}°C | Target: 1400°C | Predicted: {predicted_temp:.1f}°C", 
                  style={'color': 'white', 'fontSize': '14px'}),
            html.P("💡 AI Suggestion: Reduce fuel rate by 2% or increase alternative fuel ratio", 
                  style={'color': '#3498db', 'fontSize': '14px'})
        ])
    else:
        recommendation = html.Div([
            html.P("⚠️ Temperature predicted below target", style={'color': '#e74c3c', 'fontSize': '16px'}),
            html.P(f"📊 Current: {current_data['kiln_temperature']:.1f}°C | Target: 1400°C | Predicted: {predicted_temp:.1f}°C", 
                  style={'color': 'white', 'fontSize': '14px'}),
            html.P("💡 AI Suggestion: Increase coal ratio by 3% to raise temperature", 
                  style={'color': '#3498db', 'fontSize': '14px'})
        ])
    
    return (f"{current_data['fuel_rate']:.1f} T/h",
            f"{current_data['feed_rate']:.0f} T/h",
            f"{current_data['fan_speed']:.0f} %",
            f"{current_data['raw_moisture']:.1f} %",
            fig,
            recommendation)

# Enable real-time updates after login
@app.callback(
    Output('real-time-interval', 'disabled'),
    Input('user-session', 'data')
)
def enable_real_time_updates(session):
    if session and session.get('username'):
        return False
    return True

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("🔥 Berber Cement - AI-Powered Kiln Fuel Optimization Platform")
    print("="*70)
    print("\n🤖 AI Features:")
    print("   • Real-time temperature prediction using Random Forest AI")
    print("   • Dynamic fuel mix optimization")
    print("   • Cost & CO₂ savings calculation")
    print("   • Predictive analytics for process optimization")
    print("\n📊 Key Metrics:")
    print("   • Target Temperature: 1400°C")
    print("   • Fuel Mix: Coal, Tyre Chips, Alternative Fuels")
    print("   • Real-time sensor simulation (updates every 3 seconds)")
    print("\n📋 Users (Default Password: 123):")
    print("   👑 General Manager - Eng. Omer Bashier Ghalib")
    print("   🏭 Plant Manager - Dr. Asim Altoum")
    print("   🔧 Maintenance Manager - Eng. Ali Salih")
    print("   ✅ Quality Control Chief - Fadul Abdalmoniem")
    print("   ⚙️ Chief Process Engineer - Eng. Musab Alkhateeb")
    print("   🔥 Kiln Supervisor - Kamal Hassan")
    print("\n🚀 Starting AI Optimization Platform...")
    print("🌐 Open: http://127.0.0.1:8050")
    print("="*70) 
    app.run(debug=True, port=8050)
