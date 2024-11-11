import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import altair as alt
import numpy as np
import pandas as pd
import folium
import random
import branca.colormap as cm
from streamlit_folium import st_folium
from streamlit_folium import folium_static

st.title(":violet[Lab 7: Assignment 7]")
st.header(":rainbow[_Name: Moong Jie Ying, ID: 20001884_]", divider="rainbow")

# Load the Natural Earth dataset (update the path to your downloaded file)
@st.cache_data
def load_data():
    gdf = gpd.read_file("ne_110m_admin_0_countries.shp")
    
    # Check if 'pop_est' column exists; if not, create it with dummy data
    if 'pop_est' not in gdf.columns:
        np.random.seed(0)
        gdf['pop_est'] = np.random.randint(1e6, 1e9, size=len(gdf))  # Random population estimates for demonstration
    return gdf

@st.cache_data
def load_malaysia_population():
    # List of Malaysian states with their approximate coordinates and random populations
    states = [
        "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", "Pahang",
        "Perak", "Perlis", "Pulau Pinang", "Sabah", "Sarawak", "Selangor",
        "Terengganu", "Kuala Lumpur", "Labuan", "Putrajaya"
    ]
    coordinates = [
        [1.4854, 103.7618],   # Johor
        [6.1184, 100.3689],   # Kedah
        [6.1254, 102.2381],   # Kelantan
        [2.1896, 102.2501],   # Melaka
        [2.7258, 101.9378],   # Negeri Sembilan
        [3.8126, 103.3256],   # Pahang
        [4.5975, 101.0901],   # Perak
        [6.4458, 100.2048],   # Perlis
        [5.4141, 100.3288],   # Pulau Pinang
        [5.9788, 116.0753],   # Sabah
        [1.5533, 110.3592],   # Sarawak
        [3.0738, 101.5183],   # Selangor
        [5.3117, 103.1324],   # Terengganu
        [3.1390, 101.6869],   # Kuala Lumpur
        [5.2831, 115.2308],   # Labuan
        [2.9264, 101.6964]    # Putrajaya
    ]
    populations = np.random.randint(500000, 4000000, size=len(states))  # Random population data

    return states, coordinates, populations

# Cache the folium map
@st.cache_data
def create_malaysia_population_map(states, coordinates, populations):
    malaysia_map = folium.Map(location=[4.2105, 101.9758], zoom_start=6)

    for state, coord, population in zip(states, coordinates, populations):
        folium.Marker(
            location=coord,
            popup=f"{state}: {population} people",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(malaysia_map)

    return malaysia_map

@st.cache_data
def load_map():
    malaysia_map = gpd.read_file("malaysia.state.geojson")
    return malaysia_map

# Create a new function to assign parties to states
def assign_party_to_states(malaysia_map):
    # States (matching names in geojson file) and party assignment
    states_party = {
        "Johor": "Najib", "Kedah": "Anwar", "Kelantan": "Anwar", "Melaka": "Najib", 
        "Negeri Sembilan": "Anwar", "Pahang": "Najib", "Penang": "Anwar", 
        "Perak": "Najib", "Perlis": "Anwar", "Sabah": "Najib", "Sarawak": "Anwar", 
        "Selangor": "Anwar", "Terengganu": "Najib", "Kuala Lumpur": "Anwar", 
        "Labuan": "Najib", "Putrajaya": "Anwar"
    }
    
    # Create a new column for party affiliation
    malaysia_map['Party'] = malaysia_map['name'].map(states_party)
    return malaysia_map

# Plot the map with states colored by party affiliation
def plot_map(malaysia_map):
    m = folium.Map(location=[4.2105, 101.9758], zoom_start=6)

    # Assign colors based on party
    def get_color(party):
        return "blue" if party == "Anwar" else "red"

    # Add states to the map with party colors
    folium.GeoJson(
        malaysia_map,
        style_function=lambda feature: {
            "fillColor": get_color(feature['properties']['Party']),
            "fillOpacity": 0.7,
            "color": "black",  # border color
            "weight": 0.5
        },
        tooltip=folium.GeoJsonTooltip(fields=["name", "Party"]),
    ).add_to(m)

    return m

# Load the data
gdf = load_data()
states, coordinates, populations = load_malaysia_population()

st.title("Interactive Map Visualization Examples")

# Sidebar for options
st.sidebar.header("Choose a Map Type")
map_type = st.sidebar.radio("Select Map Type", [
    "Map Cosmetics",
    "Map Visual Hierarchy",
    "Choropleth Map",
    "Geo Projection",
    "My Location",
    "Malaysia Population",
    "Election Result"
])

# 1. Map Cosmetics Example
if map_type == "Map Cosmetics":
    st.header("Map Cosmetics Example")
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax, color='skyblue', edgecolor='black', linewidth=0.5)
    ax.set_title("Styled Map Example", fontsize=15, fontweight="bold")
    ax.set_facecolor("lightgrey")
    st.pyplot(fig)

# 2. Map Visual Hierarchy Example
elif map_type == "Map Visual Hierarchy":
    if 'name' in gdf.columns:
        country_col = 'name'
    elif 'NAME' in gdf.columns:
        country_col = 'NAME'
    elif 'country' in gdf.columns:
        country_col = 'country'
    else:
        st.error("Country name column not found in dataset.")
        country_col = None
    
    if country_col:
        st.header("Interactive Map Visual Hierarchy Example")
        st.write("Highlight selected countries in red and keep the rest in a neutral color (sky blue).")
    
        all_countries = gdf[country_col].unique()
        highlighted_countries = st.multiselect(
            "Select countries to highlight in red",
            all_countries,
            default=["Brazil", "India", "China", "Australia", "South Africa", "Russia"]
        )
    
        gdf['color'] = gdf[country_col].apply(lambda x: 'red' if x in highlighted_countries else 'skyblue')
    
        fig, ax = plt.subplots(figsize=(10, 6))
        gdf.plot(color=gdf['color'], edgecolor='black', linewidth=0.5, ax=ax)
        ax.set_title("Map Visual Hierarchy with Selected Countries Highlighted in Red")
        st.pyplot(fig)

# 3. Interactive Choropleth Map
elif map_type == "Choropleth Map":
    st.header("Interactive Choropleth Map Example")
    st.write("Select a color scheme for the choropleth map and toggle data transformation options.")

    color_options = ['OrRd', 'YlGn', 'Blues', 'Purples', 'Greens']
    color_choice = st.selectbox("Choose Color Scheme", color_options, index=0)
    use_log_scale = st.checkbox("Use Log Transformation", value=True)

    gdf['pop_density'] = gdf['pop_est'] / gdf['geometry'].area

    if use_log_scale:
        gdf['pop_density'] = np.log1p(gdf['pop_density'])

    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(column='pop_density', cmap=color_choice, linewidth=0.5, edgecolor='black', legend=True, ax=ax)
    ax.set_title(f"Population Density by Country (Color Scheme: {color_choice}, {'Log Scale' if use_log_scale else 'Linear Scale'})")
    st.pyplot(fig)

# 4. Interactive Geo Projection Example
elif map_type == "Geo Projection":
    st.header("Interactive Geo Projection Example")
    st.write("Choose a projection and color scheme to see how it affects the map.")

    projection_options = {
        "WGS84 (Geographic)": "EPSG:4326",
        "Mercator": "EPSG:3395",
        "Robinson": "ESRI:54030",
        "Mollweide": "ESRI:54009",
        "Lambert Conformal Conic": "EPSG:3347"
    }
    proj_choice = st.selectbox("Select a Projection", list(projection_options.keys()))

    color_options = ['OrRd', 'YlGn', 'Blues', 'Purples', 'Greens']
    color_choice = st.selectbox("Choose Color Scheme", color_options, index=0)
    use_log_scale = st.checkbox("Use Log Transformation for Population Density", value=True)

    gdf['pop_density'] = gdf['pop_est'] / gdf['geometry'].area

    if use_log_scale:
        gdf['pop_density'] = np.log1p(gdf['pop_density'])

    gdf_proj = gdf.to_crs(projection_options[proj_choice])

    fig, ax = plt.subplots(figsize=(10, 6))
    gdf_proj.plot(column='pop_density', cmap=color_choice, edgecolor='black', legend=True, linewidth=0.5, ax=ax)
    ax.set_title(f"Map in {proj_choice} Projection (Color by Population Density)")
    st.pyplot(fig)

# 5. Plot My Location
elif map_type == "My Location":
    st.header("My Location Example")
    st.write("Plotting your specific location at Village 4, UTP on an interactive map.")

    # Define your specific location (Village 4, UTP)
    my_location = [4.3883553397611035, 100.96435116707825]  # Latitude, Longitude order

    # Create a folium map centered on your location
    m = folium.Map(location=my_location, zoom_start=15)

    # Add a marker for your location
    folium.Marker(
        location=my_location,
        popup="Village 4, UTP",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Display the folium map in Streamlit
    st_folium(m, width=700, height=500)

# 6. Malaysia Population
if map_type == "Malaysia Population":
    st.header("Population of States in Malaysia")
    st.write("Displaying population data for all states in Malaysia.")

    # Display a bar chart
    malaysia_data = {"State": states, "Population": populations}
    st.bar_chart(data=malaysia_data, x="State", y="Population")

    # Create and display the folium map (cached)
    malaysia_map = create_malaysia_population_map(states, coordinates, populations)

    # Display the folium map in Streamlit
    st_folium(malaysia_map, width=700, height=500)

# 7. Election Result
if map_type == "Election Result":
    st.title("Malaysia Election Results Map")
    
    # Load map and population data
    malaysia_map = load_map()
    
    # Assign political parties to each state
    malaysia_map = assign_party_to_states(malaysia_map)
    election_results_filtered = malaysia_map[['name', 'Party']]

    st.dataframe(election_results_filtered)
    
    # Plot the map
    folium_map = plot_map(malaysia_map)
    folium_static(folium_map)