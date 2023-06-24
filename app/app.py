import streamlit as st
import folium
from google.cloud import bigquery
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os

load_dotenv()

# Create a BigQuery client
client = bigquery.Client()

# Define BigQuery project ID, dataset ID, and table ID
project_id = os.getenv("GCP_PROJECT")
dataset_id = os.getenv("BQ_DATASET")
table_id = os.getenv("TABLE_ID")

# Construct the BigQuery table reference
table_ref = client.dataset(dataset_id).table(table_id)
# Query to retrieve the column data

# safety_map front

st.markdown("""
    # Mexico City - Safety Map

    ## Be not part of the statistics

    As much we are loving CDMX we are aware of the fact that it is not the safest place on earth. Therefore we want to provide you
    with a safety map for this amazing city. The intention of our idea is to give you a clear overview of the neighborhoods where you
    eat tacos and trink mezcal tranquilito and where better not to go.

    Our data data includes all registered crimes in Colonias of CDMX from  **2019 to 2023**

    To be transparent from the beginning you can find the data for our project public available [here](https://datos.cdmx.gob.mx/dataset/victimas-en-carpetas-de-investigacion-fgj#:~:text=Descargar-,V%C3%ADctimas%20en%20Carpetas%20de%20Investigaci%C3%B3n%20(completa),-CSV)
""")

###add map

st.title("Historical crime data")

map = folium.Map(location=[19.4326, -99.1332], zoom_start=11, tiles='Stamen Toner')

##select colonia (names queried from Big Query)
query = f"SELECT DISTINCT Neighborhood FROM `{project_id}.{dataset_id}.{table_id}`"
# Execute the query and fetch the results
query_job = client.query(query)
rows = query_job.result()
# Extract the column values into a Python list
colonias = [row['Neighborhood'] for row in rows]

###add drop downs
dropdown_values = {
    'Neighborhood': colonias,
    'Year': ['ALL', 2019, 2020, 2021, 2022, 2023],
    'Month': ['ALL'] + list(range(1, 13)),
    'Category': ['ALL', 'fraud', 'threats', 'threats', 'burglary', 'homicide',
                  'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
                  'robbery with violence', 'robbery without violence']
}

# Collect selected values from the dropdown menus
selected_values = {}
for dropdown_label, dropdown_options in dropdown_values.items():
    selected_values[dropdown_label] = st.selectbox(dropdown_label, dropdown_options)

# Fetch the relevant data from BigQuery based on the selected values
where_clauses = []
for dropdown_label, selected_value in selected_values.items():
    if selected_value != 'ALL':
        if isinstance(selected_value, str):
            where_clauses.append(f"{dropdown_label} = '{selected_value}'")
        else:
            where_clauses.append(f"{dropdown_label} = {selected_value}")

if where_clauses:
    where_clause = " AND ".join(where_clauses)
else:
    where_clause = "1 = 1"  # Condition to select all values

# Prepare the query
query = f"""
    SELECT Latitude, Longitude
    FROM `{dataset_id}.{table_id}`
    WHERE {where_clause}
"""


# Run the query
query_job = client.query(query)
dataframe = query_job.to_dataframe()

dataframe_shape = dataframe.shape

# Create a Folium map
if dataframe_shape[0] > 0:
    map_center = [dataframe['Latitude'].iloc[0], dataframe['Longitude'].iloc[0]]
else:
    map_center = [19.4326, -99.1332]  # Default center if no data is available

map = folium.Map(location=map_center, zoom_start=11, tiles='Stamen Toner')

# Add markers to the map
if dataframe_shape[0] > 0:
    for _, row in dataframe.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(map)
else:
    st.markdown(""" ## NO CRIME WAS COMMITTED """)

# Display the map
st_folium(map, width=700)
