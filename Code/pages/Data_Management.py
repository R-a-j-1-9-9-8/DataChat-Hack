# Importing necessary libraries
import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import logging
import functools
import traceback

# Retry decorator with exponential backoff
# This decorator will used with a function for re-executing the function if any error is raised
def retry(retry_num, retry_sleep_sec):
    """
    retry help decorator.
    :param retry_num: the retry num; retry sleep sec
    :return: decorator
    """
    def decorator(func):
        """decorator"""
        # preserve information about the original function, or the func name will be "wrapper" not "func"
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper"""
            for attempt in range(retry_num):
                try:
                    return func(*args, **kwargs)  # should return the raw function's return value
                except Exception as err:   # pylint: disable=broad-except
                    logging.error(err)
                    logging.error(traceback.format_exc())
                    time.sleep(retry_sleep_sec)
                logging.error("Trying attempt %s of %s.", attempt + 1, retry_num)
            logging.error("func %s retry failed", func)
            raise Exception('Exceed max retry num: {} failed'.format(retry_num))

        return wrapper

    return decorator

# Setting page title
st.title("Data Management")

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
genai.configure(api_key=st.secrets["api"])

# Function to create prompt
@st.cache_data
def prompt_maker(dataframe,text):
    """
    Create prompt to generate python function code to extract result data according to dataframe and query/instruction.

    dataframe: dataframe from which result is to be extracted
    text: query/instruction provided by user
    p: prompt text
    """
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
    
    p += '\n\nBy using the table description, create a python code function which takes dataframe as input and '+ text + ' and returns all the records. Keep the name of function short. Don\'t use reset index. \n '
    
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
    code_llm =  genai.GenerativeModel(model_name="models/gemini-1.5-flash",generation_config=parameters)
    return code_llm 

# Function for formatting the code generated by Gen AI model
@st.cache_data
def func(value):
    """
    Formats generated code for execution. Returns formatted code and function name.

    value: generated code 
    var: function name
    """
    # Remove specific strings from generated code
    if '`' in value:
        value=value[:value.rindex('`')+1]
        value=value.replace("`", "")
    if 'python' in value:
        value=value.replace("python", "")
    
    value=value.replace("Answer:", "")

    # Extracting function name
    var = value[value.index('def')+3:value.index(':')]
    return value , var.strip()

@st.cache_data
@retry(10, 1)
def run_code(p,df):
    """
    
    """
    p_df = df.copy()
    a = code_llm.generate_content(p)
    b = a.text
    code_text , var = func(b)    
    exec(code_text)
    data = eval(var)

    if p_df.equals(data):
            return 0 , pd.DataFrame(),data
            
    elif len(p_df) == len(data):
            differences = p_df.compare(data)
            modified_indices = differences.index.unique()
            diff = p_df.loc[modified_indices]
            row = len(diff)
            updated_data = p_df
            return row , diff, updated_data
    else:
            diff = pd.concat([p_df,data]).drop_duplicates(keep=False)
            row = len(diff)
            updated_data = data
            return row , diff, updated_data


if "message_list" in st.session_state and "df" in st.session_state and st.session_state["message_list"] != []:

    if "dmessages" not in st.session_state:
        st.session_state.dmessages = [{"role": "assistant", "content": 'Please verify the Affected records and confirm for execution with YES or NO.'}]

    code_llm = load_models()
    p = prompt_maker(df,instruction)   
    row , diff, updated_data = run_code(p,df)
    
    st.write('Your Instruction is : ' + instruction)
    st.write('Execution of Instruction will affect ' + str(row) + ' out of ' + str(len(df)) + ' records.')
    st.write('Affected Records :')
    st.dataframe(diff)

    for message in st.session_state.dmessages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("YES or NO ?" ):

        if prompt.lower().strip() == 'yes':
            st.success('Execution Successful ' )
            st.session_state.dmessages.append({"role": "assistant", "content": 'Click \'Download\' button to download updated data.'})
            updated_data = updated_data.to_csv(index=False).encode("utf-8")
            st.download_button("Download", updated_data, "benchmark-tools.csv","text/csv",key="download-tools-csv",)
        elif prompt.lower().strip() == 'no':
            st.session_state.dmessages.append({"role": "assistant", "content": 'Please give detailed instruction in Home Page for better accuracy.'})
            st.rerun()
        else:
            st.session_state.dmessages.append({"role": "assistant", "content": 'Please answer only in YES or NO'})
            st.rerun()
else:
    st.markdown("### Please Insert Instruction to Perform Data Management Operations")