import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit UI for file upload
st.title('Compressor Data Visualization')
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Reading the uploaded data
    data = pd.read_csv(uploaded_file)
    data['datetime'] = pd.to_datetime(data['datetime'])

    # Data Filtering UI
    compressor_type = st.sidebar.multiselect('Compressor Type', options=data['Compressor_Type'].unique(), default=data['Compressor_Type'].unique())
    location = st.sidebar.multiselect('Location', options=data['Location'].unique(), default=data['Location'].unique())
    trusted = st.sidebar.checkbox('Only Trusted Data', value=True)

    # Applying Filters
    filtered_data = data[data['Compressor_Type'].isin(compressor_type) & data['Location'].isin(location)]
    if trusted:
        filtered_data = filtered_data[filtered_data['Trusted'] == 1]

    # Displaying filtered data
    st.dataframe(filtered_data)

    # Visualization selection
    metric = st.sidebar.selectbox('Select metric to visualize', 
                                  ['All Phase Currents', 'All Phase Voltages'] + 
                                  ['Oil_Temp_(F)', 'Cooler_Temp_(F)', 'Motor_Temp_(F)', 
                                   'Oil_Pressure_(PSI)', 'Air_Pressure_(PSI)', 'Flow_Rate_(L/min)'])

    # Plotting
    if metric in ['All Phase Currents', 'All Phase Voltages']:
        if metric == 'All Phase Currents':
            fig = px.line(filtered_data, x='datetime', 
                          y=['Phase_A_Current_(A)', 'Phase_B_Current_(A)', 'Phase_C_Current_(A)'], 
                          title='Phase Currents over Time')
        else:
            fig = px.line(filtered_data, x='datetime', 
                          y=['Phase_A_Voltage_(V)', 'Phase_B_Voltage_(V)', 'Phase_C_Voltage_(V)'], 
                          title='Phase Voltages over Time')
    else:
        fig = px.line(filtered_data, x='datetime', y=metric, title=f'{metric} over Time', markers=True,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_traces(line=dict(width=2.5), mode='markers+lines')
    
    # Customizing the layout for all plots
    fig.update_layout(
        xaxis_title='DateTime',
        yaxis_title=metric,
        font=dict(family='Arial, sans-serif', size=12, color='RebeccaPurple'),
        hovermode='x unified',
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99)
    )
    
    # Enhancing hover data for all plots
    fig.update_traces(hovertemplate='<b>Time:</b> %{x}<br><b>Value:</b> %{y}')
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please upload a CSV file to proceed.")
