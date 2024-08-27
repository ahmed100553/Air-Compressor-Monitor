# Import necessary libraries
import streamlit as st  # Streamlit framework for creating web apps
import pandas as pd  # Pandas for data manipulation
import plotly.express as px  # Plotly Express for interactive plots
import os  # Operating system interfaces
from datetime import date  # Date handling
import time  # Time access and conversions

# Add a title to the Streamlit web app
st.title('Real-Time Sensor Data Visualization')

# Define a function to read sensor data from a CSV file, caching it to improve performance
@st.cache_data(ttl=60)
def get_data(file_path):
    try:
        # Attempt to read the CSV file
        data = pd.read_csv(file_path)
        # Convert 'Timestamp' column to datetime objects
        data['Timestamp'] = pd.to_datetime(data['Timestamp'])
        return data
    except FileNotFoundError:
        # Return an empty DataFrame if the file is not found
        return pd.DataFrame()

# Define a function to create a line plot using the data
def create_plot(data, metrics):
    if not data.empty and metrics:
        # Create a line plot with markers for selected metrics over time
        fig = px.line(data, x='Timestamp', y=metrics, title='Sensor Data over Time', markers=True)
        # Customize line width and mode
        fig.update_traces(line=dict(width=2.5), mode='markers+lines')
        # Update layout with titles, fonts, hovermode, and margins
        fig.update_layout(
            xaxis_title='DateTime',
            yaxis_title='Sensor Readings',
            font=dict(family='Arial, sans-serif', size=12, color='RebeccaPurple'),
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99),
            uirevision=True  # Preserve UI state across updates
        )
        # Define hover text format
        fig.update_traces(hovertemplate='<b>Time:</b> %{x}<br><b>Value:</b> %{y}')
        return fig
    elif not metrics:
        # Return a message if no metrics are selected
        return "Please select at least one metric to visualize."
    return None

# Set up a sidebar in the Streamlit app for user input on metrics to plot
metrics = st.sidebar.multiselect(
    'Select metrics to visualize',
    options=["Temperature1", "Temperature2", "Temperature3", "Oil Pressure",
             "Air Pressure", "PSI100 Pressure", "Phase_A_Current_(A)", "Phase_B_Current_(A)",
             "Phase_C_Current_(A)", "Phase_A_Voltage_(V)", "Phase_B_Voltage_(V)", "Phase_C_Voltage_(V)",
             "Total Active Power(W)", "Humidity"],
    default=["Temperature1", "Oil Pressure"]
)

# Prepare the file path for the CSV file based on today's date
today = date.today()
datafile = f"{today.strftime('%m-%d-%Y')}-data.csv"

# Create containers to display the plot and DataFrame
plot_container = st.empty()
data_container = st.empty()

# Initialize session state to track iterations
if 'iteration' not in st.session_state:
    st.session_state.iteration = 0

# Main loop to update the data and refresh the plot continuously
while True:
    data = get_data(datafile)  # Load data
    if not data.empty:
        # Update the DataFrame display every 10 iterations or the first iteration
        if st.session_state.iteration == 0 or st.session_state.iteration % 10 == 0:
            data_container.write("Sensor Data:")
            data_container.dataframe(data)
        st.session_state.iteration += 1
        
        fig = create_plot(data, metrics)  # Generate the plot
        if isinstance(fig, str):
            plot_container.write(fig)  # Display error message if necessary
        elif fig:
            plot_container.plotly_chart(fig, use_container_width=True)  # Display the plot
    else:
        # Handle cases where no data is available
        data_container.write("Waiting for data... Please ensure the data collection script is running.")
        plot_container.empty()
    time.sleep(1)  # Wait one second before the next update
