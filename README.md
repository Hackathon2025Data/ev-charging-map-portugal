# EV Charging Stations Map - Portugal

This Streamlit application visualizes electric vehicle charging stations in Portugal on an interactive map.

## Features

*   Displays charging stations on an interactive map using Folium.
*   Uses marker clustering to handle a large number of points.
*   Allows filtering stations by:
    *   City
    *   Power range (kW)
    *   Number of charging points
*   Shows general statistics and charts about the filtered stations:
    *   General information (total stations, points, total and average power)
    *   Top 5 cities with the most stations
    *   Distribution of the number of charging points
    *   Distribution of total power

## Installation

1.  **Clone the repository (or ensure you have the files):**
    ```bash
    # If using git
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv env
    source env/bin/activate  # Linux/macOS
    # or
    .\env\Scripts\activate  # Windows
    ```
    *Alternatively, you can use your Conda `hackathon` environment.* 

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To run the application, use the following command in the terminal, inside the project folder:

```bash
streamlit run Charging_map.py
```

If you are using the Conda `hackathon` environment:

```bash
conda activate hackathon
streamlit run Charging_map.py
```

The application will automatically open in your web browser. 
