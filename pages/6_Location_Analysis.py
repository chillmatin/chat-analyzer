"""Location Analysis page - Map visualization of shared locations."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
from ui import create_pie_chart, dict_to_dataframe

# Check if chat data exists
if 'chat' not in st.session_state:
    st.warning("Please upload a chat file from the Home page first.")
    st.stop()

chat = st.session_state.chat

st.header("Location Analysis")

# Get location data
location_count = chat.get_location_count()

if location_count == 0:
    st.info("No location data found in this chat.")
    st.stop()

# Top metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Locations Shared", location_count)
with col2:
    locations_with_coords = chat.get_locations_with_coords()
    st.metric("Locations with Coordinates", len(locations_with_coords))
with col3:
    location_sources = chat.get_location_count_by_source()
    st.metric("Different Sources", len(location_sources))

st.divider()

# Location sources distribution
st.subheader("Location Sources")

col1, col2 = st.columns(2)

with col1:
    df_sources = dict_to_dataframe(location_sources, 'Source', 'Count')
    
    fig = create_pie_chart(
        values=df_sources['Count'].tolist(),
        names=df_sources['Source'].tolist(),
        title="Location Sharing by Source",
        color_scheme='location'
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    st.dataframe(df_sources, hide_index=True, width='stretch')
    
    # Participant breakdown
    participant_counts = chat.get_location_count_by_participant()
    df_participants = dict_to_dataframe(participant_counts, 'Participant', 'Locations')
    st.dataframe(df_participants, hide_index=True, width='stretch')

st.divider()

# Map visualization
st.subheader("Location Map")

if locations_with_coords:
    # Prepare data for map (include message content for hover)
    map_data = []
    for loc in locations_with_coords:
        map_data.append({
            'Latitude': loc['latitude'],
            'Longitude': loc['longitude'],
            'Participant': loc['sender'],
            'Date': loc['timestamp'].strftime('%Y-%m-%d %H:%M'),
            'Source': loc['source'],
            'Place': loc.get('place', 'N/A'),
            'Message': loc.get('content', '')
        })
    
    df_map = pd.DataFrame(map_data)
    
    # Get bounds for map centering (fallback)
    bounds = chat.get_location_bounds()
    
    # Compute preferred center: densest grid cell center, else bounds center, else mean
    def _densest_center(df: pd.DataFrame, cell: float = 0.5):
        if df.empty:
            return None
        bins = {}
        for lat, lon in zip(df['Latitude'], df['Longitude']):
            i = math.floor(lat / cell)
            j = math.floor(lon / cell)
            bins[(i, j)] = bins.get((i, j), 0) + 1
        if not bins:
            return None
        # pick the bin (i,j) with the highest count
        (i, j), _ = max(bins.items(), key=lambda kv: kv[1])
        return (i + 0.5) * cell, (j + 0.5) * cell

    center = _densest_center(df_map)
    if center:
        center_lat, center_lon = center
    elif bounds:
        center_lat, center_lon = bounds['center_lat'], bounds['center_lon']
    else:
        center_lat, center_lon = float(df_map['Latitude'].mean()), float(df_map['Longitude'].mean())

    # Create scatter mapbox
    fig = px.scatter_map(
        df_map,
        lat='Latitude',
        lon='Longitude',
        color='Participant',
        hover_name='Place',
        hover_data={
            'Latitude': ':.6f',
            'Longitude': ':.6f',
            'Date': True,
            'Source': True,
            'Place': True,
            'Message': True
        },
        zoom=10,
        height=600,
        title=f"Shared Locations ({len(locations_with_coords)} points)",
        map_style="open-street-map",
        center={"lat": center_lat, "lon": center_lon}
    )

    # High-contrast dots: add per-participant halo so legend filtering hides both
    fig.update_traces(marker=dict(size=12, opacity=0.95, symbol='circle'))
    if 'Participant' in df_map.columns:
        for participant in df_map['Participant'].unique():
            subset = df_map[df_map['Participant'] == participant]
            fig.add_trace(
                go.Scattermap(
                    lat=subset['Latitude'],
                    lon=subset['Longitude'],
                    mode='markers',
                    marker=dict(size=18, color='black', opacity=0.45, symbol='circle'),
                    showlegend=False,
                    hoverinfo='skip',
                    legendgroup=str(participant),
                    name=f"{participant} halo"
                )
            )

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0}
    )
    
    st.plotly_chart(fig, width='stretch')
    
    st.divider()
    
    # Location details table
    st.subheader("Location Details")
    
    # Show all locations with details
    all_locations = chat.get_all_locations()
    details_data = []
    
    for loc in all_locations:
        details_data.append({
            'Date': loc['timestamp'].strftime('%Y-%m-%d %H:%M'),
            'Participant': loc['sender'],
            'Source': loc['source'],
            'Place': loc.get('place', '-'),
            'Latitude': f"{loc['latitude']:.6f}" if loc['latitude'] is not None else '-',
            'Longitude': f"{loc['longitude']:.6f}" if loc['longitude'] is not None else '-',
            'Link': loc['link']
        })
    
    df_details = pd.DataFrame(details_data)
    st.dataframe(df_details, hide_index=True, width='stretch')

else:
    st.info("No locations with coordinates found. Some location sharing services (like Foursquare) may not include coordinates in the shared link.")
    
    # Show locations without coordinates
    st.subheader("Shared Locations (without coordinates)")
    
    all_locations = chat.get_all_locations()
    no_coords = [loc for loc in all_locations if loc['latitude'] is None or loc['longitude'] is None]
    
    if no_coords:
        details_data = []
        for loc in no_coords:
            details_data.append({
                'Date': loc['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'Participant': loc['sender'],
                'Source': loc['source'],
                'Place': loc.get('place', '-'),
                'Link': loc['link']
            })
        
        df_no_coords = pd.DataFrame(details_data)
        st.dataframe(df_no_coords, hide_index=True, width='stretch')
