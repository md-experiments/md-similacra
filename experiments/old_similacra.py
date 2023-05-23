from src.agents.memory import MDGenerativeAgentMemory
from src.agents.generative_agent import MDGenerativeAgent

from datetime import datetime, timedelta
from typing import List
from termcolor import colored


from langchain.chat_models import ChatOpenAI
from langchain.docstore import InMemoryDocstore
#from langchain.embeddings import OpenAIEmbeddings
from langchain.retrievers import TimeWeightedVectorStoreRetriever
#from langchain.vectorstores import FAISS

from langchain.vectorstores.weaviate import Weaviate
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain
import weaviate

from src.weaviate_schemas import WeaviateEmbeddings, text2vec_schema

import os
with open('openai.key','r') as f:
    openai_api_key = f.read()
os.environ['OPENAI_API_KEY'] = openai_api_key 

USER_NAME = "Misho" # The name you want to use when interviewing the agent.
LLM = ChatOpenAI(
    model_name = 'gpt-3.5-turbo',
    temperature = 0.7,
    max_tokens = 1500) # Can be any LLM you want.


client = weaviate.Client("http://localhost:8080",     
    #additional_headers={
    #    "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
    #}
                        )
#embeddings_model = OpenAIEmbeddings(openai_api_key = openai_api_key)
    
embeddings = WeaviateEmbeddings(pooling_strategy = 'masked_mean',
                                url='http://localhost:8081/vectors')

client.schema.delete_all()
client.schema.get()

client.schema.create(text2vec_schema)

vectorstore = Weaviate(client, "Paragraph", "page_content", embedding=embeddings)

def create_new_memory_retriever():
    """Create a new vector store retriever unique to the agent."""
    # Define your embedding model
    return TimeWeightedVectorStoreRetriever(vectorstore=vectorstore, other_score_keys=["importance"], k=15) 

tommies_memory = MDGenerativeAgentMemory(
    llm=LLM,
    memory_retriever=create_new_memory_retriever(),
    verbose=False,
    reflection_threshold=8 # we will give this a relatively low number to show how reflection works
)

tommie = MDGenerativeAgent(name="Tommie", 
              age=25,
              traits="anxious, likes design, talkative", # You can add more persistent traits here 
              status="looking for a job", # When connected to a virtual world, we can have the characters update their status
              memory_retriever=create_new_memory_retriever(),
              llm=LLM,
              memory=tommies_memory
             )

# We can add memories directly to the memory object
tommie_observations = [
    "Tommie remembers his dog, Bruno, from when he was a kid",
    "Tommie feels tired from driving so far",
    "Tommie sees the new home",
    "The new neighbors have a cat",
    "The road is noisy at night",
    "Tommie is hungry",
    "Tommie tries to get some rest.",
]
for observation in tommie_observations:
    tommie.memory.add_memory(observation)

print(tommie.get_summary(force_refresh=True))

def interview_agent(agent: MDGenerativeAgent, message: str) -> str:
    """Help the notebook user interact with the agent."""
    new_message = f"{USER_NAME} says {message}"
    return agent.generate_dialogue_response(new_message)[1]

print(interview_agent(tommie, "What do you like to do?"))