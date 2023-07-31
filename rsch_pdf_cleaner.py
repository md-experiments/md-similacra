from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader

from src.utils import files_in_dir
from tqdm import tqdm

import openai
import json
# Environment Variables
import os

with open('openai.key','r') as f:
    openai_api_key = f.read()
openai.api_key = openai_api_key
os.environ['OPENAI_API_KEY'] = openai_api_key

ls_files = files_in_dir('./data/arxiv/tar/',['.pdf'])

for pdf_path in tqdm(ls_files[:1]):

    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    docs = loader.load()
    ls_text = '\n'.join([d.page_content for d in docs]).split('\n')
    find_ref = [l for l in ls_text if l.lower().startswith('references')]
    if len(find_ref)!=1:
        print(pdf_path, len(find_ref))


# Creating two versions of the model so I can swap between gpt3.5 and gpt4
llm3 = ChatOpenAI(temperature=0,
                  openai_api_key=os.getenv('OPENAI_API_KEY', 'YourAPIKeyIfNotSet'),
                  model_name="gpt-3.5-turbo",
                )
llm3_613 = ChatOpenAI(temperature=0,
                  openai_api_key=os.getenv('OPENAI_API_KEY', 'YourAPIKeyIfNotSet'),
                  model_name="gpt-3.5-turbo-0613",
                )
llm4 = ChatOpenAI(temperature=0,
                  openai_api_key=os.getenv('OPENAI_API_KEY', 'YourAPIKeyIfNotSet'),
                  model_name="gpt-4-0613",
                 )
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, separators=['\n','\n\n'], chunk_overlap=0)

docs_split = text_splitter.create_documents(['\n'.join([d.page_content for d in docs])])


from rsch_prompts.pdf_clean_prompt import pdf_cleaner_prompt
res = []
for d in tqdm(docs_split):
    _input = pdf_cleaner_prompt.format_prompt(
                    input = d.page_content
                )

    output = llm3(_input.to_messages())
    res.append(output.content)

pdf_name = pdf_path.split('/')[-1].replace('.pdf','')

with open(f'./gpt_pp01_{pdf_name}.txt','w') as f:
    f.writelines(res)