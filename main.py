import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import re  # Importing the regex module
import plotly.graph_objects as go  # Importing Plotly for gauge chart
import random  # For generating random success percentages
import numpy as np  # For mathematical operations

# Set the page configuration
st.set_page_config(page_title="SMT Smart Analysis", page_icon="", layout="wide")

# Load the Excel file using openpyxl
def load_excel_file(file_path):
    try:
        wb = load_workbook(file_path, data_only=True)
        sheet = wb.active  # Get the active sheet
        data = sheet.values
        columns = next(data)  # Get the first row as column names
        df = pd.DataFrame(data, columns=columns)
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

# Load the DataFrame from the Xiomi Excel file
df = load_excel_file("smt_68.xlsx")  # Replace with your actual file name

# Check if DataFrame is loaded successfully
if df is not None:
    # Display header
    st.markdown("""<h1 style="color:#002b50;">SMT FA Cook Book</h1>""", unsafe_allow_html=True)

    # Sidebar with logo and date picker
    st.sidebar.image("images/Padget.png") 

    # Search bar for Error Code
    search_code = st.text_input("Enter Error Code to search:")

    # Button to perform the search
    if st.button("Search"):
        # Normalize the search input by removing newlines and extra spaces
        normalized_search_code = re.sub(r'\s+', ' ', search_code.strip())

        # Escape special characters in the normalized search input for regex matching
        escaped_search_code = re.escape(normalized_search_code)

        # Normalize DataFrame values by replacing newlines with spaces for comparison
        df['Error Code'] = df['Error Code'].astype(str).str.replace('\n', ' ', regex=False)

        # Filter DataFrame based on normalized input using regex
        filtered_df = df[df['Error Code'].str.contains(escaped_search_code, na=False, regex=True)]

        # Check if any results were found
        if not filtered_df.empty:
            # Calculate success percentage based on occurrences of error codes
            code_counts = filtered_df['Error Code'].value_counts()
            success_percentages = {}

            for code, count in code_counts.items():
                if count == 1:
                    success_percentages[code] = random.randint(90, 100)  # Random between 90-100%
                else:
                    success_percentages[code] = random.randint(60, 80)   # Random between 60-80%

            # Display Success Percentage Title and Gauge for each error code in parallel layout
            # Display Success Percentage Title and Gauge for each error code in parallel layout
            for code in success_percentages.keys():
                current_value = success_percentages[code]
                color = "red" if current_value <= 50 else "yellow" if current_value <= 80 else "green"

    # Create a gauge chart using Plotly
                # Display Success Percentage Title and Gauge for this failure code occurrence
                        #current_value=80
                plot_bgcolor = "#ffffff" 
                quadrant_colors = [plot_bgcolor, "#2bad4e", "#85e043", "#eff229", "#f2a529", "#f25829"] 
                quadrant_text = ["", "<b>Very high</b>", "<b>High</b>", "<b>Medium</b>", "<b>Low</b>", "<b>Very low</b>"]
                n_quadrants = len(quadrant_colors) - 1

                min_value = 0
                max_value = 100
                hand_length = np.sqrt(2) / 4
                hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

                fig = go.Figure(
                            data=[
                                go.Pie(
                                    values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
                                    rotation=90,
                                    hole=0.5,
                                    marker_colors=quadrant_colors,
                                    text=quadrant_text,
                                    textinfo="text",
                                    hoverinfo="skip",
                                ),
                            ],
                            layout=go.Layout(
                                showlegend=False,
                                margin=dict(b=0,t=10,l=10,r=10),
                                width=450,
                                height=450,
                                paper_bgcolor=plot_bgcolor,
                                annotations=[
                                    go.layout.Annotation(
                                        text=f"<b>Success Rate:</b><br>{current_value} %",
                                        x=0.5, xanchor="center", xref="paper",
                                        y=0.25, yanchor="bottom", yref="paper",
                                        showarrow=False,
                                        font=dict(size=24, color='black')
                                    )
                                ],
                                shapes=[
                                    go.layout.Shape(
                                        type="circle",
                                        x0=0.48, x1=0.52,
                                        y0=0.48, y1=0.52,
                                        fillcolor="#333",
                                        line_color="#333",
                                    ),
                                    go.layout.Shape(
                                        type="line",
                                        x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                                        y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                                        line=dict(color="#333", width=4)
                                    )
                                ]
                            )
                        )

                # Create two columns for displaying results for each error code and its details
                a1, a2 = st.columns(2)

                with a1:
                    st.markdown(
                        f"<div style='background-color: #e7f3fe; padding: 10px; margin-bottom: 10px; border-radius: 5px;'>{code}</div>",
                        unsafe_allow_html=True)
                    
                    st.plotly_chart(fig, use_container_width=True)

                    # Now add the new columns below the Plotly chart
                    # Assuming you want to display details for the first row corresponding to this error code
                    details_df = filtered_df[filtered_df['Error Code'] == code]  # Get details for this error code
                    if not details_df.empty:
                     row = details_df.iloc[0]  # Get the first row of details

                    # Format Risk Station
                    risk_station_text = row['Risk station']  # Assuming 'Risk Station' is in the current row
                    formatted_risk_station = re.sub(r'(\d+\.)', r'<br><b>\1</b>', risk_station_text)
                    formatted_risk_station = formatted_risk_station.lstrip('<br>')  # Remove leading <br>
                    st.markdown(f"<div style='background-color: #d1e7dd; padding: 15px; border-radius: 5px; margin-bottom: 10px;'><b>Risk Station</b><br>{formatted_risk_station}</div>", unsafe_allow_html=True)

                    # Format FA by TRC
                    fa_by_trc_text = row['Symptoms']  # Assuming 'FA by TRC' is in the current row
                    formatted_fa_by_trc = re.sub(r'(\d+\.)', r'<br><b>\1</b>', fa_by_trc_text)
                    formatted_fa_by_trc = formatted_fa_by_trc.lstrip('<br>')  # Remove leading <br>
                    st.markdown(f"<div style='background-color: #cfe2ff; padding: 15px; border-radius: 5px; margin-bottom: 10px;'><b>Repair Action , DRI - TRC</b><br>{formatted_fa_by_trc}</div>", unsafe_allow_html=True)

                with a2:
                    details_df = filtered_df[filtered_df['Error Code'] == code]
                    for index, row in details_df.iterrows():
                        st.subheader("Details:")
                        st.markdown(f"<div style='background-color: #d1e7dd; padding: 15px; border-radius: 5px; margin-bottom: 10px;'><b>Model:</b> {row['Model']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 10px;'><b>Station:</b> {row['Station']}</div>", unsafe_allow_html=True)
                        
                        # Format RCA with line breaks and bold numbers if applicable (assuming RCA is present)
                        rca_text = row['RCA']
                        formatted_rca = re.sub(r'(\d+\.)', r'<br><b>\1</b>', rca_text)
                        formatted_rca = formatted_rca.lstrip('<br>')  # Remove leading <br>
                        st.markdown(f"<div style='background-color: #cfe2ff; padding: 15px; border-radius: 5px; margin-bottom: 10px;'><b>RCA:</b><br>{formatted_rca}</div>", unsafe_allow_html=True)

                        # Format Counter Action with line breaks and bold numbers if applicable (assuming Counter Action is present)
                        counter_action_text = row['Counter Action']
                        formatted_counter_action = re.sub(r'(\d+\.)', r'<br><b>\1</b>', counter_action_text)
                        formatted_counter_action = formatted_counter_action.lstrip('<br>')  # Remove leading <br>
                        st.markdown(f"<div style='background-color: #f9c2c2; padding: 15px; border-radius: 5px; margin-bottom: 10px;'><b>Corrective Action, DRI - PQC</b><br>{formatted_counter_action}</div>", unsafe_allow_html=True)

                        st.markdown("---")  # Add a separator between entries

        else:
            st.warning("No results found for the given Error Code.")
