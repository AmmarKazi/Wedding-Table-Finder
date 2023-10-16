import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType, create_csv_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from langchain.sql_database import SQLDatabase
from dotenv import load_dotenv
load_dotenv()

#os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
#OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

dburi = "sqlite:///seating.db"
db = SQLDatabase.from_uri(dburi)

llm = ChatOpenAI(temperature = 0, model_name = "gpt-3.5-turbo")
#toolkit = SQLDatabaseToolkit(llm = llm, db = db)

custom_suffix = """
I am a CSV agent that queries the CSV to help users find their table number. I always have access to the CSV.
I am given the users first name defined as {firstName}
I am given the users last name defined as {lastName}
I will find the table number defined as {tableNumber}
I will run a query on the CSV using the first name and last name to find the table number.

An example query to find the table number looks like the following:
SELECT Table Number from SeatingTable WHERE First Name LIKE %{firstName}% AND Last Name LIKE %{lastName}%

An example query to find other people at the table looks like the following:
SELECT First Name, Last Name from SeatingTable WHERE Table Number = {tableNumber}

If the query returns the table number, I will always respond with the following structure:
Hello {firstName}!, We are delighted for you to have joined us today. You are seated at table number: {table number}

I will then find all names that are at the same table. If there are other names, I will return them all to the user in a list.
Otherwise If there is only this one person at this table, I will say:
You are currently the only person at this table!.

If I cannot find the table number for the given first name and last name, I will always respond with the following:
Unfortunately I am unable to find your table number. Please make your way to the entrance doors where the hosts will gladly help you find your seats!.

"""

custom_suffix_1 = """
I am a CSV agent that searches the CSV to help users find their table number. I always have access to the CSV.
I am given the users first name defined as {firstName}. Before I make any search, I will always capitalize the first letter of this.
I am given the users last name defined as {lastName}. Before I make any search, I will always capitalize the first letter of this.
I will find the table number defined as {tableNumber}
I will run a search on the CSV using the first name and last name to find the table number.

I will do two queries in order.

The first is: df[(df['First Name']=='{firstName}') & (df['Last Name'] == '{lastName}')]['Table Number'].
This will give me the {tableNumber} of the given first name and last name.
If the search returns the table number, I will always respond with the following structure:
Hello {firstName}!, We are delighted for you to have joined us today. You are seated at table number: {table number}

The second is: df[(df['Table Number']=='{tableNumber}')]['First Name', 'Last Name'].
This will tell me all other first names and last names at the same table.
If this search returns other names, I will list them out.
Otherwise If there is only this one person at this table, I will say:
You are currently the only person at this table!.

If I cannot find the table number for the given first name and last name, I will always respond with the following:
Unfortunately I am unable to find your table number. Please make your way to the entrance doors where the hosts will gladly help you find your seats!.
"""

agent = create_csv_agent(
    agent_type=AgentType.OPENAI_FUNCTIONS,
    path = "Seating Sample List.csv",
    llm=llm,
    #verbose= True,
    #extra_tools= custom_tool_list,
    suffix= custom_suffix_1,
    include_df_in_prompt=None
    #toolkit = toolkit
)


def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''

    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url("https://cdn.pixabay.com/photo/2020/02/20/17/57/flower-4865379_1280.png");
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True
    )
set_bg_hack_url()


st.markdown("<h1 style='text-align: center; color: black;'>Umer and Ayesha's Wedding Table Finder</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: black;'>Please enter your FIRST and LAST Name below to find your table number</h3>", unsafe_allow_html=True)

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(prompt, callbacks=[st_callback])
        st.write(response)
