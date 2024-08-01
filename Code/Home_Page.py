# Importing necessary libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Setting page config
st.set_page_config(page_title='DataChat')
                   
# Setting page title along with description
st.title("DataChat :brain: :abacus:")
st.write("## A Data Analytics & Management Platform")
st.write("Just upload your data and talk by using natural language. No coding required!!!")

# Create an uploader widget
uploaded_file = st.sidebar.file_uploader("Choose an Excel file", type="xlsx")

# Check if the session state has already been initialized
if "file" not in st.session_state:
    # Initialize the session state
    st.session_state["file"] = None

if "df" not in st.session_state:
    # Initialize the session state
    st.session_state["df"] = None

# Function to load data and store in cache
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        st.session_state["message_list"] = []
        return data
    
# Function describing the steps performed after clicking submit button
def on_click():
    st.session_state.user_input = ""
    if "message_list" not in st.session_state:
        st.session_state["message_list"] = []
    st.session_state["message_list"].append(txt)
    

# Check if the user has uploaded a file
if uploaded_file is not None:
    # Save the uploaded file to the session state
    st.session_state["file"] = uploaded_file

if st.session_state["file"] is not None:
    # Read the Excel file into a Pandas DataFrame
    df = load_data(st.session_state["file"])

    # Store the dataframe in the session
    st.session_state["df"] = df
    st.write(f"## Data Preview")
    
    # Show the first few rows of the data
    st.dataframe(df.head(),hide_index =True)

    st.write("Summary Statistics:")
    st.write(df.describe())

    # Visualizations
    st.write("Data Visualizations:")

    # Allow users to select specific columns for plotting
    columns = df.columns.tolist()
    selected_columns = st.multiselect("Select columns to visualize", columns)

    if selected_columns:
        st.write(f"Selected Columns: {selected_columns[0]}")

        for col in selected_columns:
            st.write(f"Distribution of {col}:")
            fig=plt.figure(figsize=(10, 6))
            sns.histplot(df[col].transpose(), kde=True)
            plt.title(f'Histogram of {col}')
            plt.xlabel(col)
            plt.xticks(rotation=15)
            plt.ylabel('Frequency')
            st.pyplot(fig)

    # Text input widget for user input
    txt = st.text_area(" Start chatting with Data", key="user_input")
    
    # Radio button widget for selecting type of operation
    t = st.radio('Type',["Perform Analytics", "Perform Data Operation"],horizontal=True,)
    
    # Navigate to respective pages after clicking submit button
    if st.button("Submit", on_click=on_click):
            if t == "Perform Data Operation":
                st.switch_page("pages/Data_Management.py")
            if t == "Perform Analytics":
                st.switch_page("pages/Analytic_Report.py")