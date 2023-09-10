
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

chat_model = ChatOpenAI(temperature=0.9, openai_api_key=openai_api_key)
entity_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(_DEFAULT_ENTITY_EXTRACTION_TEMPLATE)  
    ],
    input_variables=["history", "input"],
)

_input = entity_prompt.format_prompt(
    history = "NONE", 
    input = statements,
)
output = chat_model(_input.to_messages())
output.content


chat_model = ChatOpenAI(temperature=0.9, openai_api_key=openai_api_key)
kg_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(_DEFAULT_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE)  
    ],
    input_variables=["history", "input"],
)

_input = kg_prompt.format_prompt(
    history = "NONE", 
    input = statements,
)
output = chat_model(_input.to_messages())