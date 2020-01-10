import pandas as pd
import streamlit as st
import plotly.express as px

def is_authenticated(password):
    return password == "DSAdemo"

# st.empty is a placeholder to 'save' a
# slot in your app that you can use later.
def generate_login_block():
    block1 = st.empty()
    block2 = st.empty()

    return block1, block2

# clear the password and text input box
def clean_blocks(blocks):
    for block in blocks:
        block.empty()


def login(blocks):
    # grab the first block, which will be the input text,
    # but only display **** to mask the password
    blocks[0].markdown("""
            <style>
                input {
                    -webkit-text-security: disc;
                }
            </style>
        """, unsafe_allow_html=True)
    # print out the text input box
    return blocks[1].text_input('Please input password to load the demo.')


def main():
    
    @st.cache
    def get_data():
        return pd.read_csv("http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv")

    df = get_data()

    st.title("Streamlit 101: An in-depth introduction")
    st.dataframe(df)
    #st.markdown("The following map shows the top 1% most expensive Airbnbs priced at $800 and above.")

    #st.map(df.query("price>=800")[["latitude", "longitude"]].dropna(how="any"))
    defaultcols = ["name", "host_name", "neighbourhood", "room_type", "price"]
    cols = st.multiselect("Columns", df.columns.tolist(), default=defaultcols)
    st.dataframe(df[cols])
    
    values = st.slider("Price range", float(df.price.min()), float(df.price.clip(upper=1000.).max()), (50., 300.))
    # the inclusion of {values[0]} and {values[1]} is what connects the slider to the histogram
    f = px.histogram(df.query(f"{values[0]} <= price <= {values[1]}"), x="price", nbins=15, title="Price distribution")
    f.update_xaxes(title="Price")
    f.update_yaxes(title="No. of listings")
    st.plotly_chart(f)

    neighborhood = st.radio("Neighborhood", df.neighbourhood_group.unique())
    show_exp = st.checkbox("Include expensive listings")
    show_exp = " and price<200" if not show_exp else ""

    @st.cache
    def get_availability(show_exp, neighborhood):
        # 'describe' returns a Series. 
        # need to convert Series to Data Frame before we can transpose
        
        # @ is a feature of query which converts a variable into a string
        # so that it fits nicely into our conditional. E.g. if we pass in Brooklyn,
        # @ will convert it to "Brooklyn" so that when we evaluate the condition,
        # neighbourhood_group == "Brooklyn" it's a valid syntax. 
        # If we had used {neighborhood}, we would have gotten
        # the query f""" neighbourhood_group == Brooklyn """" which is invalid syntax,
        #  when we would have wanted f""" neighbourhood_group == 'Brooklyn' """" . 
        # "{neighborhood}" is equivalent to @neighborhood
        # We use {} for show_exp because {} is a placeholder
        # for a string to our query. {} does not convert the variable into a string.
        # i.e. when we pass in {neighborhood}, we don't get something like
        # f"""neighbourhood_group=='Brooklyn', because Brooklyn will be integrated
        # into the string without the ' ' .
        return df.query(f"""neighbourhood_group==@neighborhood{show_exp}\
        and availability_365>0""").availability_365.describe(\
            percentiles=[.1, .25, .5, .75, .9, .99]).to_frame().T

    st.table(get_availability(show_exp, neighborhood))

login_blocks = generate_login_block()
password = login(login_blocks)

if is_authenticated(password):
   main()
elif password:
   st.info("Please enter a valid password")
    

    

