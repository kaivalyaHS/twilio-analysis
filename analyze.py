import pandas as pd
import streamlit as st

st.set_page_config(page_title="Campaign Analysis", layout="wide")
st.title("Data Analysis")

uploaded_file = st.file_uploader("Upload your csv file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("Dataset Preview")
    st.dataframe(df.head())
    
    st.subheader("Summary Stats")
    st.dataframe(df.describe(include='all'))
else:
    st.info("Upload a csv file to begin analysis")    
# def read_csv(file):
#     data_df = pd.read_csv(file)
#     return data_df

# def

# if __name__ == "__main__":
#     # file_path = "MMS"
#     data = read_csv("MMSCampaign.csv")