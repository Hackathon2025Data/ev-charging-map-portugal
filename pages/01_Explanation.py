import streamlit as st

# Apply custom CSS for black background and white text
st.markdown("""
    <style>
    /* Target the main block container */
    .main .block-container {
        background-color: #000000; /* Black background */
        color: #FFFFFF; /* White text */
    }
    /* Ensure headers and other text elements inherit the color */
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4,
    .main .block-container h5,
    .main .block-container h6,
    .main .block-container p,
    .main .block-container li,
    .main .block-container .stMarkdown {
        color: #FFFFFF !important; /* White text, !important to override defaults */
    }
    /* Style links specifically if needed */
    .main .block-container a {
        color: #00C0F3 !important; /* Use the app's blue color for links */
    }
    </style>
""", unsafe_allow_html=True)

st.title("💡 Application Explanation")

st.header("Map Marker Pop-up Details")
st.markdown("""
When you click on a marker cluster on the map and then on an individual station marker (blue plug icon), a pop-up appears with the following details:

*   **Name:** The official name or designation of the charging station.
*   **Operator:** The company or entity that operates and maintains the charging station. `Not available` if this information is missing.
*   **Address:** The physical street address of the charging station. `Not available` if this information is missing.
*   **City:** The city where the charging station is located. This is normalized to handle variations in naming (e.g., 'Lisbon' becomes 'Lisboa').
*   **Postal Code:** The postal code for the station's location. `Not available` if this information is missing.
*   **Latitude:** The geographic latitude coordinate of the station. Useful for precise location or input into navigation systems.
*   **Longitude:** The geographic longitude coordinate of the station. Useful for precise location or input into navigation systems.
*   **Number of Charging Points:** The total count of individual charging connectors available at this station.
*   **Total Power (kW):** The sum of the power (in kilowatts) of all individual charging points at the station. This indicates the station's overall charging capacity.
*   **Last Update:** The date and time when this application's data source was last updated (Note: This refers to the data *retrieval* time, not necessarily the last update from the operator).
""")

st.header("Statistics Panel Explanation")
st.markdown("""
The panel on the left (below the filters) shows statistics based on the currently selected filters (city, power range, number of points).

*   **General Information:**
    *   **Total Stations:** The total number of charging stations matching the current filters.
    *   **Total Charging Points:** The sum of charging points across all filtered stations.
    *   **Total Available Power:** The sum of the 'Total Power (kW)' for all filtered stations.
    *   **Average Power per Station:** The average 'Total Power (kW)' calculated across the filtered stations.

*   **Top 5 Cities:**
    *   This bar chart displays the top 5 cities with the highest number of charging stations, based on the current filters. If 'All' cities are selected, it shows the overall top 5. If a specific city is selected, this chart will only show that city.

*   **Charging Points Distribution:**
    *   This bar chart shows how the filtered stations are distributed across different categories based on the number of charging points they offer:
        *   `1 point`
        *   `2 points`
        *   `3-4 points`
        *   `5+ points`

*   **Power Distribution:**
    *   This bar chart shows how the filtered stations are distributed across different power range categories:
        *   `0-50` kW
        *   `51-100` kW
        *   `100+` kW
""") 