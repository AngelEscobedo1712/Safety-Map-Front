import streamlit as st
import os
from PIL import Image

API_HOST = os.getenv("API_HOST")

# Setting the wide config for the page
st.set_page_config(layout="wide")
#adding marging specs for the main page with css inyection
margins_css = """
    <style>
        .main > div {
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 0rem;
        }
    </style>
"""

st.markdown(margins_css, unsafe_allow_html=True)

#Title
st.markdown("""
        # 🇲🇽 Mexico City - Safety Map
    ## Don't Become a Statistic""")

col1, col2 = st.columns([1,1])

with col1:

    ## Safety Map Front
    st.markdown("""

    Despite our love for CDMX, we cannot ignore the fact that it is not the safest place on earth.\n
    However, we are here to empower you with amazing knowledge and provide a safety map for this incredible city.\n
    Our aim is to offer a comprehensive overview of neighborhoods where you can enjoy tacos and mezcal without worries,
    as well as areas where caution is advised.""")

    st.video("https://www.youtube.com/watch?v=2zavTsqaAiw",start_time=0)


with col2:
    st.markdown("""

    Our data encompasses all registered crimes in the Colonias of CDMX from **2019 to 2023**. By sharing this information, we hope to help you make informed decisions and navigate the city with confidence.

    Remember, being aware is the first step towards safety. Let us guide you through the vibrant streets of CDMX, ensuring that you won't become just another statistic.
    ###

    To be transparent from the beginning, you can find the data for our project publicly available [here](https://datos.cdmx.gob.mx/dataset/victimas-en-carpetas-de-investigacion-fgj#:~:text=Descargar-,V%C3%ADctimas%20en%20Carpetas%20de%20Investigaci%C3%B3n%20(completa),-CSV)
    """)
