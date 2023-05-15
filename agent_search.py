#from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain.utilities import GoogleSearchAPIWrapper

import os
with open('./openai.key','r') as f:
    openai_api_key = f.read()
os.environ['OPENAI_API_KEY'] = openai_api_key 
with open('./gcp_key.txt','r') as f:
    search_key = f.read()
with open('./gcp_cse.txt','r') as f:
    search_id = f.read()
os.environ["GOOGLE_CSE_ID"] = search_id
os.environ["GOOGLE_API_KEY"] = search_key

llm = OpenAI(temperature=0)
#tools = load_tools(["serpapi", "llm-math"], llm=llm)
from langchain.tools import Tool
from langchain.utilities import GoogleSearchAPIWrapper

search = GoogleSearchAPIWrapper()
tools = [
    Tool(
        name = "Google Search",
        description="Search Google for recent results.",
        func=search.run
    )
]
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
agent.run("Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?")