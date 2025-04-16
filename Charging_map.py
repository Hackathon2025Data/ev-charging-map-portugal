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

# Apply custom CSS
st.markdown("""
    <style>
    /* --- Main Page Area --- */
    .main .block-container {
        background-color: #000000; /* Black background */
        color: #FFFFFF; /* Default White text for main area */
        padding-top: 2rem; 
    }
    /* General text elements in main area (default white) */
    .main .block-container p,
    .main .block-container li,
    .main .block-container label, 
    .main .block-container .stMarkdown {
        color: #FFFFFF !important; 
    }
    /* Links in main area */
    .main .block-container a {
        color: #00C0F3 !important; 
    }
    /* Main Title H1 - Left Aligned */
    h1 { 
        color: #00C0F3 !important; 
        padding-bottom: 1rem; 
    }
    /* Subheaders H2, H3 in main area - Black Text */
    .main .block-container h2, 
    .main .block-container h3 { 
         color: #000000 !important; /* Black text for subheaders */
         padding-top: 1rem;
    }
    /* Titles for Charts (using st.write("**Title**")) - Black Text */
    .main .block-container p > strong, 
    .main .block-container p > b { 
        color: #000000 !important; 
        font-weight: bold; 
    }
     
    .stButton button {
        background-color: #00C0F3 !important; 
        color: black !important; 
        border: none;
    }
    .stAltairChart {
        background-color: transparent !important;
    }
    
     /* Style st.metric - White background, Black text */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important; /* White background */
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #E0E0E0; /* Light grey border */
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); /* Subtle shadow */
    }
    div[data-testid="stMetric"] label {
        color: #333333 !important; /* Dark grey for metric label */
        font-weight: bold;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #000000 !important; /* Black for metric value */
        font-size: 1.5em; /* Larger value text */
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: #000000 !important; /* Black for metric delta (if used) */
    }

    /* --- Sidebar Area (Keep as is - White background, Black text) --- */
    div[data-testid="stSidebar"] > div:first-child {
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
    }
    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3,
    div[data-testid="stSidebar"] h4,
    div[data-testid="stSidebar"] label { 
         color: #000000 !important; 
    }
    div[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    div[data-testid="stSidebar"] div[data-baseweb="input"],
    div[data-testid="stSidebar"] div[data-baseweb="textarea"] {
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        border: 1px solid #CCCCCC !important; 
    }
    div[data-testid="stSidebar"] div[role="listbox"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
    }
    div[data-testid="stSidebar"] div[role="option"] {
        color: #000000 !important;
    }
    div[data-testid="stSidebar"] div[role="option"]:hover {
        background-color: #EEEEEE !important; 
    }
    div[data-testid="stSidebar"] span[data-baseweb="tag"] {
        background-color: #00C0F3 !important; 
        color: black !important; 
    }
    
    /* --- Folium Map Popups (keep dark) --- */
    .folium-popup .leaflet-popup-content-wrapper {
        background-color: #333333 !important; 
        color: #FFFFFF !important; 
        border-radius: 5px;
    }
    .folium-popup .leaflet-popup-content h4 {
        color: #00C0F3 !important; 
    }
    .folium-popup .leaflet-popup-content b {
        color: #FFFFFF !important; 
    }
        
    </style>
""", unsafe_allow_html=True)

# Custom color scheme (adjusted for dark mode popups / specific elements)
COLORS = {
    'black': '#FFFFFF', # White text for popups
    'blue': '#00C0F3',
    'green': '#96FF46'
}

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

# Function to get power per point category
def get_power_per_point_category(power_per_point):
    if pd.isna(power_per_point) or power_per_point == np.inf:
        return 'N/A'
    elif power_per_point < 7:
        return '< 7 kW'
    elif power_per_point <= 22:
        return '7-22 kW (AC Normal/Fast)'
    elif power_per_point <= 50:
        return '23-50 kW (DC Fast)'
    else:
        return '> 50 kW (DC Ultra-Fast)'

# Function to load data
@st.cache_data
def load_data():
    try:
        # Determine the correct path relative to the script location or workspace root
        # Assuming the script runs from the workspace root and data is in 'data/'
        data_file_path = 'data/postos_carregamento.json'
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame early to calculate Power per Point
        df = pd.DataFrame(data)
        
        # Data Cleaning: Ensure numeric types where necessary
        numeric_cols = ['Número de Pontos', 'Potência Total (kW)', 'Latitude', 'Longitude']
        for col in numeric_cols:
             if col in df.columns:
                 df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate Power per Point, handle division by zero and NaN in Number of Points
        df['Potência por Ponto (kW)'] = (df['Potência Total (kW)'] / df['Número de Pontos']).replace([np.inf, -np.inf], np.nan)
        df.dropna(subset=['Latitude', 'Longitude'], inplace=True) # Drop rows with invalid coordinates

        # Fill NaN operators with 'Unknown' for charting
        df['Operador'] = df['Operador'].fillna('Unknown')

        return df
    
    except FileNotFoundError:
        st.error(f"File '{data_file_path}' not found! Please ensure it's in the 'data' subfolder.")
        return None
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        return None

# Function to create map
def create_map(df, center_lat=39.5, center_lon=-8.0, zoom=7):
    portugal_bounds = [
        [36.8, -9.5],  # Southwest corner
        [42.2, -6.1]   # Northeast corner
    ]
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )
    m.fit_bounds(portugal_bounds)
    
    marker_cluster = MarkerCluster(
        name='Stations',
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
        # Check again for NaN just before creating marker
        if pd.notna(station['Latitude']) and pd.notna(station['Longitude']):
            power_per_point_str = f"{station['Potência por Ponto (kW)']:.2f}" if pd.notna(station['Potência por Ponto (kW)']) else 'N/A'
            num_points_str = f"{int(station['Número de Pontos'])}" if pd.notna(station['Número de Pontos']) else 'N/A'
            total_power_str = f"{station['Potência Total (kW)']}" if pd.notna(station['Potência Total (kW)']) else 'N/A'
            html = f"""
                <div>
                    <h4>{station['Nome']}</h4>
                    <b>Operator:</b> {station['Operador'] or 'Not available'}<br>
                    <b>Address:</b> {station['Endereço'] or 'Not available'}<br>
                    <b>City:</b> {station['Cidade']}<br>
                    <b>Postal Code:</b> {station['Código Postal'] or 'Not available'}<br>
                    <b>Latitude:</b> {station['Latitude']:.5f}<br>
                    <b>Longitude:</b> {station['Longitude']:.5f}<br>
                    <b>Number of Charging Points:</b> {num_points_str}<br>
                    <b>Total Power:</b> {total_power_str} kW<br>
                    <b>Power per Point:</b> {power_per_point_str} kW<br> 
                    <b>Last Update:</b> {station['Data Atualização']}<br>
                </div>
            """
            folium.Marker(
                location=[station['Latitude'], station['Longitude']],
                popup=folium.Popup(html, max_width=350),
                icon=folium.Icon(color='blue', icon_color='#00C0F3', icon='plug', prefix='fa'),
                tooltip=station['Nome']
            ).add_to(marker_cluster)
            
    return m

# --- Main Application Flow ---

df = load_data()

if df is not None and not df.empty:
    
    # --- Data Preprocessing --- 
    df['Cidade'] = df['Cidade'].apply(normalize_city_name)
    df['Power Range'] = df['Potência Total (kW)'].apply(get_power_range)
    df['Charging Points Category'] = df['Número de Pontos'].apply(get_charging_points_label)
    df['Power per Point Category'] = df['Potência por Ponto (kW)'].apply(get_power_per_point_category)
    
    # --- Sidebar Filters --- 
    st.sidebar.header("Filters")
    unique_cities = sorted([city for city in df['Cidade'].unique() if city != 'Not specified'])
    selected_city = st.sidebar.selectbox(
        "Select a city:",
        options=['All'] + unique_cities,
        key='city_selector'
    )
    
    power_ranges = ['0-50', '51-100', '100+']
    selected_power_ranges = st.sidebar.multiselect(
        "Select Total Power ranges (kW):",
        options=power_ranges,
        default=power_ranges
    )
    
    charging_points_options = ['1 point', '2 points', '3-4 points', '5+ points']
    selected_charging_points = st.sidebar.multiselect(
        "Select number of points:",
        options=charging_points_options,
        default=charging_points_options
    )
    
    # --- Apply Filters --- 
    filtered_df = df.copy()
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['Cidade'] == selected_city]
    if selected_power_ranges:
        filtered_df = filtered_df[filtered_df['Power Range'].isin(selected_power_ranges)]
    if selected_charging_points:
        filtered_df = filtered_df[filtered_df['Charging Points Category'].isin(selected_charging_points)]

    # --- Main Layout: Top Section (Stats + Map) --- 
    col1, col2 = st.columns([1, 2]) 

    with col1:
        # --- General Statistics using st.metric --- 
        st.subheader("Overall Statistics")
        if not filtered_df.empty:
            if selected_city != 'All':
                st.write(f"_Showing stats for: {selected_city}_ ")
            else:
                st.write("_Showing overall stats for Portugal_")
            
            total_stations = len(filtered_df)
            total_points = int(filtered_df['Número de Pontos'].sum())
            total_power = filtered_df['Potência Total (kW)'].sum()
            avg_power_station = filtered_df['Potência Total (kW)'].mean()
            avg_power_point = filtered_df['Potência por Ponto (kW)'].mean()
            
            # Add icons (emojis) to labels
            st.metric(label="📍 Total Stations", value=f"{total_stations:,}")
            st.metric(label="⚡ Total Charging Points", value=f"{total_points:,}")
            st.metric(label="💡 Total Available Power (kW)", value=f"{total_power:,.2f}")
            st.metric(label="📊 Average Power per Station (kW)", value=f"{avg_power_station:,.2f}")
            st.metric(label="🚀 Average Power per Point (kW)", value=f"{avg_power_point:,.2f}" if pd.notna(avg_power_point) else "N/A")

        else:
             st.warning("No stations match filters for statistics.")

    with col2:
        # --- Map Display --- 
        # Removed subheader, title is enough
        if not filtered_df.empty:
            if selected_city != 'All':
                center_lat = filtered_df['Latitude'].mean()
                center_lon = filtered_df['Longitude'].mean()
                zoom = 12
            else:
                center_lat = 39.5 
                center_lon = -8.0
                zoom = 7
            
            m = create_map(filtered_df, center_lat, center_lon, zoom)
            folium_static(m, width=None, height=700) # Increased map height
        else:
            # Display empty map centered on Portugal if no results
            m = folium.Map(location=[39.5, -8.0], zoom_start=7, tiles="OpenStreetMap")
            folium_static(m, width=None, height=700)


    # --- Main Layout: Bottom Section (Detailed Charts) --- 
    st.write("--- ") # Separator
    st.subheader("Detailed Charts")

    if not filtered_df.empty:
        chart_col1, chart_col2, chart_col3 = st.columns(3)

        with chart_col1:
            st.write("**Top Cities**")
            top_cities = filtered_df['Cidade'].value_counts().nlargest(5)
            if not top_cities.empty:
                city_chart = alt.Chart(top_cities.reset_index()).mark_bar().encode(
                    x=alt.X('count', title='Stations'),
                    y=alt.Y('Cidade', sort='-x', title=None),
                    tooltip=['Cidade', 'count'],
                    color=alt.value(COLORS['blue'])
                ).properties(height=200)
                st.altair_chart(city_chart, use_container_width=True)
            else:
                st.write("_No data_")

            st.write("**Points Distribution**")
            points_dist = filtered_df['Charging Points Category'].value_counts()
            if not points_dist.empty:
                points_chart = alt.Chart(points_dist.reset_index()).mark_bar().encode(
                    x=alt.X('count', title='Stations'),
                    y=alt.Y('Charging Points Category', sort=['1 point', '2 points', '3-4 points', '5+ points'], title='Points per Station'),
                    tooltip=['Charging Points Category', 'count'],
                    color=alt.value(COLORS['blue'])
                ).properties(height=200)
                st.altair_chart(points_chart, use_container_width=True)
            else:
                 st.write("_No data_")

        with chart_col2:
             st.write("**Average Power per Number of Points**")
             # Calculate average power for each number of points
             avg_power_by_points = filtered_df.groupby('Número de Pontos')['Potência Total (kW)'].mean().reset_index()
             avg_power_by_points.rename(columns={'Potência Total (kW)': 'Average Total Power (kW)'}, inplace=True)
             
             if not avg_power_by_points.empty and avg_power_by_points['Número de Pontos'].nunique() > 1:
                 line = alt.Chart(avg_power_by_points).mark_line(point=True).encode(
                     x=alt.X('Número de Pontos', title='Number of Points', scale=alt.Scale(zero=False)),
                     y=alt.Y('Average Total Power (kW)', title='Avg. Total Power (kW)', scale=alt.Scale(zero=False)),
                     tooltip=['Número de Pontos', alt.Tooltip('Average Total Power (kW)', format='.2f')]
                 ).properties(
                      height=430 # Match height of the column
                 )
                 st.altair_chart(line, use_container_width=True)
             else:
                 st.write("_Not enough distinct points data for line graph_")

        with chart_col3:
            st.write("**Total Power Distribution**")
            power_dist = filtered_df['Power Range'].value_counts().reindex(power_ranges).fillna(0)
            if not power_dist.empty:
                power_chart = alt.Chart(power_dist.reset_index()).mark_bar().encode(
                    x=alt.X('Power Range', title='Total Power (kW)'),
                    y=alt.Y('count', title='Stations'),
                    tooltip=['Power Range', 'count'],
                    color=alt.value(COLORS['blue'])
                ).properties(height=200)
                st.altair_chart(power_chart, use_container_width=True)
            else:
                st.write("_No data_")
                
            st.write("**Power per Point (kW) Distribution**") # Histogram
            ppp_data = filtered_df['Potência por Ponto (kW)'].dropna()
            # ppp_data = ppp_data[ppp_data <= 200] # Optional: Cap at 200 kW for viz
            
            if not ppp_data.empty:
                 ppp_hist = alt.Chart(pd.DataFrame({'Power per Point (kW)': ppp_data})).mark_bar().encode(
                     alt.X("Power per Point (kW)", bin=alt.Bin(maxbins=20), title="Power per Point (kW)"),
                     alt.Y('count()', title='Number of Stations'),
                     tooltip=[alt.Tooltip("count()", title="Stations"), alt.X("Power per Point (kW)", bin=alt.Bin(maxbins=20))],
                     color=alt.value(COLORS['blue']) # Added blue color
                 ).properties(height=200)
                 st.altair_chart(ppp_hist, use_container_width=True)
            else:
                 st.write("_No data for histogram_")

    else:
        st.warning("No stations match the selected filters.")


else:
    st.error("Could not load charging stations data. Please check the 'data' folder and file permissions.") 