import streamlit as st
import folium
from streamlit_folium import folium_static
import json
import pandas as pd
from folium.plugins import MarkerCluster
import numpy as np
import unicodedata
import altair as alt

# Page configuration
st.set_page_config(
    page_title="EV Charging Stations Map",
    page_icon="🔌",
    layout="wide"
)

# Custom color scheme
COLORS = {
    'black': '#000000',
    'blue': '#00C0F3',
    'green': '#96FF46'
}

# Custom CSS
st.markdown(f"""
    <style>
    .stSelectbox, .stMultiSelect {{
        color: {COLORS['black']};
    }}
    .stMarkdown {{
        color: {COLORS['black']};
    }}
    h1 {{
        color: {COLORS['blue']} !important; /* Main title blue */
    }}
    h2, h3, h4 {{
        color: {COLORS['black']} !important; /* Subtitles black */
    }}
    .stButton button {{
        background-color: {COLORS['blue']};
        color: white;
    }}
    .element-container {{
        color: {COLORS['black']};
    }}
    div[data-baseweb="select"] {{
        background-color: white;
    }}
    div[data-baseweb="select"] > div {{
        background-color: white;
    }}
    div[role="listbox"] {{
        background-color: white;
    }}
    span[data-baseweb="tag"] {{
        background-color: {COLORS['green']} !important;
        color: black !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Application title
st.title("🔌 EV Charging Stations Map - Portugal")

# Function to normalize city names
def normalize_city_name(city):
    if pd.isna(city):
        return 'Not specified'
    
    # Dictionary of known variations
    city_variations = {
        'lisbon': 'Lisboa',
        'ponte lima': 'Ponte de Lima',
        'vila real sto antonio': 'Vila Real de Santo António',
        'vr sto antonio': 'Vila Real de Santo António',
        'vrsa': 'Vila Real de Santo António',
        'vfxira': 'Vila Franca de Xira',
        'vila franca xira': 'Vila Franca de Xira',
        'povo': 'Póvoa de Varzim',
        'povoa varzim': 'Póvoa de Varzim',
        'pdv': 'Póvoa de Varzim',
        'vngaia': 'Vila Nova de Gaia',
        'vn gaia': 'Vila Nova de Gaia',
        'gaia': 'Vila Nova de Gaia',
    }
    
    # Convert to string, normalize accents and convert to lowercase
    normalized = str(city).lower()
    normalized = ''.join(c for c in unicodedata.normalize('NFD', normalized)
                        if unicodedata.category(c) != 'Mn')
    
    # Check if the normalized name is in our variations dictionary
    for variant, correct_name in city_variations.items():
        if variant in normalized:
            return correct_name
    
    # If not in variations, capitalize each word
    return ' '.join(word.capitalize() for word in normalized.split())

# Function to get power range label
def get_power_range(power):
    if power <= 50:
        return '0-50'
    elif power <= 100:
        return '51-100'
    else:
        return '100+'

# Function to get charging points label
def get_charging_points_label(points):
    if points == 1:
        return '1 point'
    elif points == 2:
        return '2 points'
    elif points <= 4:
        return '3-4 points'
    else:
        return '5+ points'

# Function to load data
@st.cache_data
def load_data():
    try:
        with open('data/postos_carregamento.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("File 'data/postos_carregamento.json' not found!")
        return None

# Function to create map
def create_map(df, center_lat=39.5, center_lon=-8.0, zoom=7):
    # Define Portugal bounds
    portugal_bounds = [
        [36.8, -9.5],  # Southwest corner
        [42.2, -6.1]   # Northeast corner
    ]
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )
    
    # Set bounds to Portugal
    m.fit_bounds(portugal_bounds)
    
    # Create a MarkerCluster with custom icon color
    marker_cluster = MarkerCluster(
        icon_create_function="""
        function(cluster) {
            return L.divIcon({
                html: '<div style="background-color: #00C0F3; color: black; width: 30px; height: 30px; border-radius: 15px; display: flex; align-items: center; justify-content: center; border: 2px solid white;">' + cluster.getChildCount() + '</div>',
                className: 'marker-cluster-custom',
                iconSize: L.point(30, 30)
            });
        }
        """
    ).add_to(m)
    
    for idx, station in df.iterrows():
        if pd.notna(station['Latitude']) and pd.notna(station['Longitude']):
            html = f"""
                <div style='width: 300px'>
                    <h4 style='color: {COLORS['black']}'>{station['Nome']}</h4>
                    <b style='color: {COLORS['black']}'>Operator:</b> {station['Operador'] or 'Not available'}<br>
                    <b style='color: {COLORS['black']}'>Address:</b> {station['Endereço'] or 'Not available'}<br>
                    <b style='color: {COLORS['black']}'>City:</b> {station['Cidade']}<br>
                    <b style='color: {COLORS['black']}'>Postal Code:</b> {station['Código Postal'] or 'Not available'}<br>
                    <b style='color: {COLORS['black']}'>Number of Charging Points:</b> {station['Número de Pontos']}<br>
                    <b style='color: {COLORS['black']}'>Total Power:</b> {station['Potência Total (kW)']} kW<br>
                    <b style='color: {COLORS['black']}'>Last Update:</b> {station['Data Atualização']}<br>
                </div>
            """
            
            folium.Marker(
                location=[station['Latitude'], station['Longitude']],
                popup=folium.Popup(html, max_width=350),
                icon=folium.Icon(color='lightblue', icon='plug', prefix='fa'),
                tooltip=station['Nome']
            ).add_to(marker_cluster)
    
    return m

# Load data
data = load_data()

if data:
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Normalize city names
    df['Cidade'] = df['Cidade'].apply(normalize_city_name)
    
    # Add power range and charging points categories
    df['Power Range'] = df['Potência Total (kW)'].apply(get_power_range)
    df['Charging Points Category'] = df['Número de Pontos'].apply(get_charging_points_label)
    
    # Create layout with columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("### Filters")
        
        # Region/City filter
        unique_cities = sorted([city for city in df['Cidade'].unique() if city != 'Not specified'])
        selected_city = st.selectbox(
            "Select a city:",
            options=['All'] + unique_cities,
            key='city_selector'
        )
        
        # Power range filter with multiple selection
        st.write("#### Power Range (kW)")
        power_ranges = ['0-50', '51-100', '100+']
        selected_power_ranges = st.multiselect(
            "Select power ranges:",
            options=power_ranges,
            default=power_ranges
        )
        
        # Charging points filter with radio buttons
        st.write("#### Number of Charging Points")
        charging_points_options = ['1 point', '2 points', '3-4 points', '5+ points']
        selected_charging_points = st.multiselect(
            "Select number of points:",
            options=charging_points_options,
            default=charging_points_options
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['Cidade'] == selected_city]
    
    if selected_power_ranges:
        filtered_df = filtered_df[filtered_df['Power Range'].isin(selected_power_ranges)]
        
    if selected_charging_points:
        filtered_df = filtered_df[filtered_df['Charging Points Category'].isin(selected_charging_points)]
    
    with col2:
        # Calculate map center and zoom based on filtered data
        if len(filtered_df) > 0:
            if selected_city != 'All':
                center_lat = filtered_df['Latitude'].mean()
                center_lon = filtered_df['Longitude'].mean()
                zoom = 12
            else:
                center_lat = 39.5
                center_lon = -8.0
                zoom = 7
            
            # Create and display map
            m = create_map(filtered_df, center_lat, center_lon, zoom)
            folium_static(m, width=1000, height=1200)
    
    with col1:
        # Statistics section below the map
        st.write("---")
        if selected_city != 'All':
            st.write(f"### Statistics for {selected_city}")
        else:
            st.write("### Overall Statistics")
        
        # Create three columns for statistics
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.write("#### General Information")
            st.markdown(f"""
                <div style='color: {COLORS['black']}'>
                Total Stations: {len(filtered_df)}<br>
                Total Charging Points: {filtered_df['Número de Pontos'].sum()}<br>
                Total Available Power: {filtered_df['Potência Total (kW)'].sum():.2f} kW<br>
                Average Power per Station: {filtered_df['Potência Total (kW)'].mean():.2f} kW
                </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.write("#### Top 5 Cities")
            top_cities = filtered_df['Cidade'].value_counts().head()
            chart = alt.Chart(pd.DataFrame({
                'City': top_cities.index,
                'Count': top_cities.values
            })).mark_bar().encode(
                x='Count',
                y=alt.Y('City', sort='-x'),
                color=alt.value(COLORS['blue'])
            ).properties(width=300)
            st.altair_chart(chart, use_container_width=True)
        
        with stat_col3:
            st.write("#### Charging Points Distribution")
            points_dist = filtered_df['Charging Points Category'].value_counts()
            chart = alt.Chart(pd.DataFrame({
                'Category': points_dist.index,
                'Count': points_dist.values
            })).mark_bar().encode(
                x='Count',
                y=alt.Y('Category', sort='-x'),
                color=alt.value(COLORS['blue'])
            ).properties(width=300)
            st.altair_chart(chart, use_container_width=True)
        
        # Power distribution chart
        st.write("#### Power Distribution")
        power_dist = filtered_df['Power Range'].value_counts().reindex(power_ranges)
        
        power_df = pd.DataFrame({
            'Range': power_ranges,
            'Count': power_dist.values
        })
        
        power_chart = alt.Chart(power_df).mark_bar().encode(
            x='Range',
            y='Count',
            color=alt.value(COLORS['blue']),
            tooltip=['Range', 'Count']
        ).properties(
            width=800,
            height=400
        )
        
        st.altair_chart(power_chart, use_container_width=True)

else:
    st.error("Could not load charging stations data.") 