# Importing necessary libraries
import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns

# Setting page title
st.title("Forecast")

# Check if the session state has already been initialized
if "message_list" not in st.session_state:
        # Initialize the session state
        st.session_state["message_list"] = []

# Check if the session state has already been initialized
if "disabled" not in st.session_state:
        # Initialize the session state
        st.session_state.disabled = False

# Import df from Home_Page.py
df = st.session_state.df

# Storing the query/instruction from Home Page into a variable
if st.session_state["message_list"] != []:
    instruction = st.session_state["message_list"][-1]

# Gen AI model config
genai.configure(api_key='AIzaSyDNKtbzCAuDTUC6HIrbVDOH2fDnEphpDME')

# Function to create prompt
@st.cache_data
def prompt_maker(dataframe,text):
    p = '\nTable description: '

    for i in list(dataframe.columns.values):
        d = df[i].dtypes
        if d == 'O':
            p += '\n\nColumn ' + i +  ' has following categories \n'
            for j in list(df[i].unique()):
                if type(j) == float:
                    pass 
                else:
                    p += str(j) + ' ,'

        else:
            p += '\n\nColumn ' + i +  ' has ' + str(d) + ' datatype'
    
    p += '\n\nBy using the table description, which column is mentioned in instruction. Only return the name of the column. Also return for how many steps to be forecasted. \n\n'
    p += 'instruction : ' + text
    return p

# Defining parameters for Gen AI model
parameters = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1500,
    "response_mime_type": "text/plain",
}

# Loading the Gen AI model
@st.cache_resource
def load_models():
    llm =  genai.GenerativeModel(model_name="models/gemini-1.5-flash",generation_config=parameters)
    return llm 

@st.cache_data
def pro_make(l):
    a = df[l[0]][int(l[1])*-2:].to_list()
    p = 'complete next '+ l[1] +' sequence. only provide the numbers only.\n'
    for i in a:
        p += str(i) + '\n'

    return p

if "message_list" in st.session_state and "df" in st.session_state and st.session_state["message_list"] != []:

    llm = load_models()
    p = prompt_maker(df,instruction)   
    
    a = llm.generate_content(p)
    
    l = a.text.strip().split('\n')
    
    
    p = pro_make(l)
    a = llm.generate_content(p)
    L = a.text.strip().split('\n')

    st.write('Your Instruction is : ' + instruction)
    
    forecast_df =  pd.DataFrame({'Forecast':L, 'Time Step' :range(1,int(l[1])+1)})
    t = 'Here is your forcast for next ' + l[1] + ' time steps.'
    st.write(t)
    st.dataframe(forecast_df)
    #final_df = df[l[0]][int(l[1])*-2:].append(forecast_df.squeeze()).to_frame().reset_index()
    st.line_chart(forecast_df['Forecast'] )
    
    
    
else:
    st.markdown("### Please Insert Instruction to Perform Forecasting")