import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import os

API_HOST = os.getenv("API_HOST")


# Safety Map Front
st.markdown("""
    # Mexico City - Safety Map

    ## Be not part of the statistics

    As much we are loving CDMX we are aware of the fact that it is not the safest place on earth. Therefore we want to provide you
    with a safety map for this amazing city. The intention of our idea is to give you a clear overview of the neighborhoods where you
    eat tacos and drink mezcal tranquilito and where better not to go.

    Our data data includes all registered crimes in Colonias of CDMX from **2019 to 2023**

    To be transparent from the beginning you can find the data for our project public available [here](https://datos.cdmx.gob.mx/dataset/victimas-en-carpetas-de-investigacion-fgj#:~:text=Descargar-,V%C3%ADctimas%20en%20Carpetas%20de%20Investigaci%C3%B3n%20(completa),-CSV)
""")
