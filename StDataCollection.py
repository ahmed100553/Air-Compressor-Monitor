import streamlit as st
import pandas as pd
import plotly.express as px

# Title for the Streamlit app
st.title('Sensor Data Visualization')

# Function to load and prepare the data
def load_data(uploaded_file):
    data = pd.read_csv(uploaded_file)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    return data

# Function to create plot
def create_plot(data, metrics):
    if not data.empty and metrics:
        fig = px.line(data, x='Timestamp', y=metrics, title='Sensor Data over Time', markers=True)
        fig.update_traces(line=dict(width=2.5), mode='markers+lines')
        fig.update_layout(
            xaxis_title='DateTime',
            yaxis_title='Sensor Readings',
            font=dict(family='Arial, sans-serif', size=12, color='RebeccaPurple'),
            hovermode='x unified',
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99)
        )
        fig.update_traces(hovertemplate='<b>Time:</b> %{x}<br><b>Value:</b> %{y}')
        return fig
    elif not metrics:
        return "Please select at least one metric to visualize."
    return None

# Define sidebar for user input
metrics = st.sidebar.multiselect(
    'Select metrics to visualize',
    options=["Motor Temp", "Cooler Temp", "Oil Temp", "Oil Pressure",
             "Air Pressure", "PSI100 Pressure", "Phase_A_Current_(A)", "Phase_B_Current_(A)",
             "Phase_C_Current_(A)", "Phase_A_Voltage_(V)", "Phase_B_Voltage_(V)", "Phase_C_Voltage_(V)",
             "Total Active Power(W)", "Humditiy"],
    default=["Motor Temp", "Oil Pressure"]
)

# Upload the CSV file
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    data = load_data(uploaded_file)
    if not data.empty:
        fig = create_plot(data, metrics)
        if isinstance(fig, str):
            st.write(fig)  # Display message if no metrics are selected
        elif fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("The uploaded file is empty or invalid.")
else:
    st.write("Please upload a CSV file to visualize the data.")
