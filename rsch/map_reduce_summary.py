

from langchain import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain import PromptTemplate

def map_reduce_summary(
        llm,
        ls_texts,
        map_prompt = """
        Write a concise summary of the following:
        "{text}"
        CONCISE SUMMARY:
        """,
        combine_prompt = """
        Write a concise summary of the following text delimited by triple backquotes.
        Return your response in bullet points which covers the key points of the text.
        ```{text}```
        BULLET POINT SUMMARY:
        """
    ):
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)

    docs = text_splitter.create_documents(ls_texts)


    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])




    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])



    summary_chain = load_summarize_chain(llm=llm,
                                        chain_type='map_reduce',
                                        map_prompt=map_prompt_template,
                                        combine_prompt=combine_prompt_template,
    #                                      verbose=True
                                        )
    output = summary_chain.run(docs)
    return output
