# DataChat

The DataChat Application is designed to communicate with data by using natural language. This application is capable of performing data analytics and management operations.

## Live Application

[![Application link]](https://datachat-hack-6vojjx9gaovskyedhfe66k.streamlit.app/)


## Demo Video

[![Watch the Video](https://img.youtube.com/vi/DFACoJQSdsg/0.jpg)](https://www.youtube.com/watch?v=DFACoJQSdsg)


## Installation

To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```
## Running the App

To run the app, use the following command:
```bash
streamlit run Code/Home_Page.py --server.enableXsrfProtection false
```

## Configuration

Before running the app, you need to configure your API key in the Analytic_Report.py and Data_Management.py files. Replace st.secrets["api"] with your actual API key to enable the AI functionalities.
