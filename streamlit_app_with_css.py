#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

from functions.pop_func import *
#######################
# Page configuration
st.set_page_config(
                    page_title="US Population Dashboard",
                    page_icon="images/usa.ico",
                    layout="wide",
                    initial_sidebar_state="expanded"
                    )

alt.themes.enable("dark")
#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

#######################
# Load data
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
#######################
# Sidebar
with st.sidebar:
    title_container = st.container()
    col1, col2 = st.columns((0.1,25), gap = 'medium')
    with title_container:
        with col1:
            st.logo('images/usa_pop.png')
        with col2:
            st.markdown('<h2 style="color: lightblue;">US Population Dashboard</h1>',
                        unsafe_allow_html=True)

    year_list = list(df_reshaped.year.unique())[::-1]
    
    selected_year = st.selectbox('Select Year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)
    earliest = min(df_reshaped.year.unique())

    if selected_year != earliest:    
        year_list.remove(selected_year)
        year_list.insert(0, selected_year - 1)
        selected_year2 = st.selectbox('Select Year to Compare', year_list)
    else:  
        selected_year2 = earliest

    sel_yr_list = [selected_year, selected_year2]
    sel_yr_list = sorted(sel_yr_list,  reverse=True)
    selected_year, selected_year2 = sel_yr_list
    
    total_us_populationprev = df_reshaped[df_reshaped.year == selected_year2].population.sum()
    total_us_population = df_reshaped[df_reshaped.year == selected_year].population.sum()   

    state_list = sorted(list(df_reshaped.states.unique())[::-1])
    # state_list.insert(0, 'All')
    selected_state = st.multiselect('Select States', state_list)
 
#######################
# Dashboard Main Panel
if selected_state != []:
    df_reshaped = df_reshaped[df_reshaped.states.isin(selected_state)]
    df_selected_year= df_selected_year[df_selected_year.states.isin(selected_state)]

info_cols = st.columns(3, gap = 'medium')
with info_cols[0]:
    st.metric(f"Total US Population ({selected_year})", format_number(total_us_population))
with info_cols[1]:
    st.metric(f"Total US Population ({selected_year2})", format_number(total_us_populationprev))
with info_cols[2]:
    diff = total_us_population - total_us_populationprev
    st.metric(f"US Population change between {selected_year2} and {selected_year}", format_number(diff))

col = st.columns((1.5, 4.5, 2), gap='medium')
with col[0]:
    st.markdown('#### Gains/Losses')

    df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year, selected_year2)

    if selected_year > 2010:
        first_state_name = df_population_difference_sorted.states.iloc[0]
        first_state_population = format_number(df_population_difference_sorted.population.iloc[0])
        first_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[0])
    else:
        first_state_name = '---'
        first_state_population = '---'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2010:
        last_state_name = df_population_difference_sorted.states.iloc[-1]
        last_state_population = format_number(df_population_difference_sorted.population.iloc[-1])   
        last_state_delta = format_number(df_population_difference_sorted.population_difference.iloc[-1])   
    else:
        last_state_name = '---'
        last_state_population = '---'
        last_state_delta = ''

    # if selected_state != [] and len(selected_state) ==1: #selected_state == []:
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    st.markdown('#### States Migration')

    if selected_year > 2010:
        # Filter states with population difference > 50000
        # df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference_absolute > 50000]
        df_greater_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference > 50000]
        df_less_50000 = df_population_difference_sorted[df_population_difference_sorted.population_difference < -50000]
        
        # % of States with population difference > 50000
        states_migration_greater = round((len(df_greater_50000)/df_population_difference_sorted.states.nunique())*100)
        states_migration_less = round((len(df_less_50000)/df_population_difference_sorted.states.nunique())*100)
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')
    else:
        states_migration_greater = 0
        states_migration_less = 0
        donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
        donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown('#### Total Population')
    
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

    choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme, max(df_selected_year.population))
    st.plotly_chart(choropleth, use_container_width=True)
    heatmap = make_heatmap(df_reshaped, 'year', 'states', 'population', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

with col[2]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("states", "population"),
                 hide_index=True,
                #  width=500,
                 use_container_width=True,
                 column_config={
                    "states": st.column_config.TextColumn(
                        "States",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.population),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: 
                 - [U.S. Census Bureau 2010-2019](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html)
                 - [U.S. Census Bureau 2020-2023](https://www.census.gov/data/datasets/time-series/demo/popest/2020s-state-total.html)
            - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
            - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000
            ''')
