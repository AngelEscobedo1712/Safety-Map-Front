import streamlit as st
import requests
import pandas as pd
import os
import altair as alt

API_HOST = os.getenv("API_HOST")

#Setting the page to wide mode
st.set_page_config(layout='wide')

margins_css = """
    <style>
        .main > div {
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 2rem;
        }
    </style>
"""
st.markdown(margins_css, unsafe_allow_html=True)

#Define the number of tabs and its names

tab1, tab2 = st.tabs(["⏪ Historical", "Forecasting ⏩"])

with tab1:
    col1, col2 = st.columns([1,3])

    with col1:
        #Title of the page
        st.title("📈Historical Plots 📉")
        st.subheader("Here you can play with some plots for the historical data")

        # Fetch neighborhoods from the backend
        if 'neighborhoods' not in st.session_state:
            response = requests.get(API_HOST + "/neighborhoods")
            neighborhoods = response.json()["neighborhoods"]
            st.session_state.neighborhoods = neighborhoods
        else:
            neighborhoods = st.session_state.neighborhoods

        month_mapping = {
            "January": "Enero",
            "February": "Febrero",
            "March": "Marzo",
            "April": "Abril",
            "May": "Mayo",
            "June": "Junio",
            "July": "Julio",
            "August": "Agosto",
            "September": "Septiembre",
            "October": "Octubre",
            "November": "Noviembre",
            "December": "Diciembre"
        }

        month_mapping_swapped = {value: key for key, value in month_mapping.items()}

        # Add checkboxes
        checkbox_values = {
            'Neighborhood': neighborhoods,
            'Year': ['ALL', 2019, 2020, 2021, 2022, 2023],
            'Category': ['ALL', 'fraud', 'threats', 'threats', 'burglary', 'homicide',
                        'sexual crime', 'property damage', 'domestic violence', 'danger of well-being',
                        'robbery with violence', 'robbery without violence']
        }

        selected_values = {}
        for checkbox_label, checkbox_options in checkbox_values.items():
            selected_values[checkbox_label] = st.multiselect(checkbox_label, checkbox_options)

        # Initialize the plot_search flag
        if 'plot_search' not in st.session_state:
            st.session_state.plot_search = False
            st.session_state.data = []

        # Check if values were selected
        if all(selected_values.values()):
            if st.button('Plot'):
                st.session_state.plot_search = True


                # Make API request to the backend to get_plot_historical_data
                api_url = API_HOST + "/get_plot_historical_data"

                year = selected_values['Year'] if 'ALL' not in selected_values['Year'] else None
                params = {
                    'neighborhoods': selected_values['Neighborhood'],
                    'years': year,
                    'categories': selected_values['Category']
                }

                with st.spinner('Calculating plot...'):
                    response = requests.post(api_url, json=params)
                    if response.status_code == 200:
                        st.session_state.data = response.json()["data"]
                        st.session_state.search_executed = True

            else:
                st.write('No plot yet')
                st.empty()

        else:
            st.write('Please select values in all dropdown menus to execute the plot.')
            st.session_state.plot_search = False

    with col2:
        if st.session_state.plot_search:
            data = st.session_state.data
            dataframe = pd.DataFrame(data)
            dataframe['Month'] = dataframe['Month'].replace(month_mapping_swapped)
            dataframe['datetime'] = pd.to_datetime(dataframe['Year'].astype(int).astype(str) + ' ' + dataframe['Month'], format='%Y %B')
            # Create the Altair chart
            selection = alt.selection_interval(bind='scales')
            chart = alt.Chart(dataframe).mark_line().encode(
                x='datetime:T',
                y=alt.Y('TotalCrimes', scale=alt.Scale(domain=(1,10)), axis=alt.Axis(tickMinStep=1, labelOverlap=True)),
                    color='Category'
            ).add_params(
                selection
            )

            st.altair_chart(chart, use_container_width=True)


with tab2:
    # Title of the page
    st.title("Forecasting Plots 📉")
    st.subheader("Here you can play with some plots for the Forecasting data")

    # Initialize the plot_search flag
    if 'predictions_search' not in st.session_state:
        st.session_state.predictions_search = False
        st.session_state.prediction_data = None  # Initialize prediction_data as None

    month_mapping_two = {
        "July": '07',
        "August": '08',
        "September": '09',
        "October": '10',
        "November": '11',
        "December": '12'
    }

    month_mapping_two_swapped = {value: key for key, value in month_mapping_two.items()}

    checkbox_values_predict = {
        'Category': ['fraud', 'threats', 'burglary', 'homicide',
                     'sexual_crime', 'property_damage', 'domestic_violence', 'danger_of_well_being',
                     'robbery_with_violence', 'robbery_without_violence', 'score'],
    }

    selected_values_predict = {}
    for checkbox_label_predict, checkbox_options_predict in checkbox_values_predict.items():
        selected_values_predict[checkbox_label_predict] = st.multiselect(checkbox_label_predict,
                                                                         checkbox_options_predict)

        selected_category = selected_values_predict.get('Category')

    if st.session_state.prediction_data is None:
        response_predict = requests.get(API_HOST + "/get_plot_prediction_data")
        prediction_data = response_predict.json()["data"]
        st.session_state.prediction_data = pd.DataFrame(prediction_data)
    else:
        if selected_category == []:
            st.warning("Please select at least one crime Category")
            st.empty()

    # Get the selected value from selected_values_predict
    if selected_category:
        selected_value = [f"total_{category}" for category in selected_category] + ["year_month"]

        df = st.session_state.prediction_data[selected_value].melt(id_vars='year_month', value_name='Crimes')

        # Create the Altair chart
        selection_new = alt.selection_interval(bind='scales')
        chart_predict = alt.Chart(df).mark_line().encode(
            x='year_month',
            y='Crimes', color='variable'
        ).add_params(
            selection_new
        )


        st.altair_chart(chart_predict, use_container_width=True)
