from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

_PDF_CLEANER_PROMPT_TEMPLATE = """
You will receive a text extracted from exactly one page of a PDF file, most of the text will be extracted correctly.
However, there will be parts of the text which will be incorrectly extracted or have missing spaces or line breaks.
Your task is to correct such issues from the PDF extraction process and return clean text. 
Respond only with the corrected text. 
Do not add or change the meaning or words in any way except to fix issues from the 

I would expect you to correct issues like:
- Remove line breaks due to PDF formatting where there is no new paragraph
EXAMPLE INPUT: 
Consequently, all these methods adopt an\noff-the-shelf metric for retrieval, leading to sub-\noptimal performance.
EXAMPLE OUTPUT:
Consequently, all these methods adopt an off-the-shelf metric for retrieval, leading to sub-optimal performance.

- Keep consistent line breaks. Keep new lines or add missing new line when a paragraph ends. Add double line breaks for new sections: 

EXAMPLE INPUT: 
some text\nnext line of the text\nNew Section\nFirst line of new section.\nSecond line of new section.\nNew paragraph
EXAMPLE OUTPUT:
some text next line of the text.\n\nNew Section\n\nFirst line of new section. Second line of new section.\nNew paragraph

EXAMPLE INPUT: 
system performance.\n4.2 Translation Memory in NMT\nTranslation memory has been widely explored in\nNeural Machine learning
EXAMPLE OUTPUT:
system performance.\n\n4.2 Translation Memory in NMT\n\nTranslation memory has been widely explored in Neural Machine learning

EXAMPLE INPUT: 
system performance.4.2 Translation Memory in NMTTranslation memory has been widely explored in\nNeural Machine learning
EXAMPLE OUTPUT:
system performance.\n\n4.2 Translation Memory in NMT\n\nTranslation memory has been widely explored in Neural Machine learning

- Restore missing spaces between words. 
EXAMPLE INPUT: 
methodsintegratetheretrievedexamplesintoa
EXAMPLE OUTPUT:
methods integrate the retrieved examples in to a

EXAMPLE INPUT: 
wehavenofear
EXAMPLE OUTPUT:
we have no fear

- Remove hyphenation at the end of a line and merge into one word. 
EXAMPLE INPUT: 
to-\ngether we are strong
EXAMPLE OUTPUT:
together we are strong

- Remove left over text, in coherent snippets like page numbers or headers, footers.
EXAMPLE INPUT: 
Figure 1. Recall@1000 of the 4 query sets.\nNo entities\n0.87\nHashed entities\n0.67\nSecondly, these\nmethods integrate the retrieved examples into a module of SMT
EXAMPLE OUTPUT:
Secondly, these methods integrate the retrieved examples into a module of SMT

Here is a full end to end example:
EXAMPLE INPUT:
Figure 1. Recall@1000 of the 4 query sets.\nNo entities\n0.87\nHashed entities\n0.67\nSecondly, these\nmethodsintegratetheretrievedexamplesintoa\nmoduleofSMTinthewayswhichcannotmake\nfull use of the knowledge in retrieved examples.Consequently, all these methods adopt an\noff-the-shelf metric for retrieval, leading to sub-\noptimal performance.\n4.2 Translation Memory in NMT\nTranslation memory has been widely explored in\nNeural Machine Translation (NMT).

EXAMPLE OUTPUT:
Secondly, these methods integrate the retrieved examples into a module of SMT in the ways which can not make full use of the knowledge in retrieved examples. Consequently, all these methods adopt an off-the-shelf metric for retrieval, leading to sub-optimal performance.\n\n4.2 Translation Memory in NMT\n\nTranslation memory has been widely explored in Neural Machine Translation (NMT).

INPUT:
{input}

OUTPUT:
"""


pdf_cleaner_prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(_PDF_CLEANER_PROMPT_TEMPLATE),
    ],
    input_variables=["input"]
)