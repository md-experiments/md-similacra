# flake8: noqa
from langchain.prompts.prompt import PromptTemplate

_DEFAULT_ENTITY_EXTRACTION_TEMPLATE = """You are an AI assistant analysing a series of statements. 
Extract all of the proper nouns from the text and use the text as much as possible to provide a description of the text. 
As a guideline, a proper noun is generally capitalized. You should definitely extract all names, entities, organisations and places.

A series of statemets is provided just in case of a coreference (e.g. "What do you know about him" where "him" is defined in a previous line) -- ignore items mentioned, they are just provided as reference.

Return the output as a single comma-separated list, or NONE if there is nothing of note to return.

EXAMPLE
Reference statements:
Statement: We propose the GFlowNets with Human Feedback (GFlowHF) framework to improve the exploration ability when training AI models
Statement: We use RLHF results as baseline
Statements for extraction:
Statement: The goal of GFlowHF is to learn a policy that is strictly proportional to human ratings
Statement: Experiments show that it can achieve better exploration ability than the baseline.
Output: GFlowHF, RLHF
END OF EXAMPLE

EXAMPLE
Reference statements:
Statement: Researchers have been using Neural Networks and other related machine-learning techniques to price options since the early 1990s. 
Statement: This paper is able to provide a comparison of using TensorFlow, and XGBoost for pricing European Options.
Statement: XGBoost has performed best.
Statements for extraction:
Statement: The model was able to outperform the Black Scholes Model in terms of mean absolute error. 
Output: XGBoost, Black Scholes Model
END OF EXAMPLE

Reference statements:
{history}
Statements for extraction:
{input}

Output:"""

ENTITY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_ENTITY_EXTRACTION_TEMPLATE
)

KG_TRIPLE_DELIMITER = "<|>"
_DEFAULT_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE = (
    "You are a networked intelligence helping a human track knowledge triples"
    " about all relevant people, things, concepts."
    " Extract all of the knowledge triples from the statements for extraction. "
    'A series of statemets may be provided just in case of a coreference. If no statements for reference we will state "Statements for reference: NONE"'
    '(e.g. "What do you know about him" where "him" is defined in a previous line) -- ignore items mentioned, they are just provided as reference.\n'
    "A knowledge triple is a clause that contains a subject, a predicate,"
    " and an object. The subject is the entity being described,"
    " the predicate is the property of the subject that is being"
    " described, and the object is the value of the property.\n\n"
    "When extracting triplets rely purely on knowledge from the statements, if there is no knoledge triplets to be returned, simply respond with NONE.\n\n"
    "EXAMPLE\n"
    "Statements for reference:\n"
    "NONE\n\n"
    "Statements for extraction:\n"
    "Statement: Nevada is a state in the US:\n"
    "Statement: It's also the number 1 producer of gold in the US.\n\n"
    f"Output: (Nevada, is a, state){KG_TRIPLE_DELIMITER}(Nevada, is in, US)"
    f"{KG_TRIPLE_DELIMITER}(Nevada, is the number 1 producer of, gold)\n"
    "END OF EXAMPLE\n\n"
    "EXAMPLE\n"
    "Statements for reference:\n"
    "Statement: Descartes I'm referring to is a standup comedian and interior designer from Montreal.\n"
    "Statement: He is a comedian and an interior designer. He has been in the industry for 30 years. His favorite food is baked bean pie.\n\n"
    "Statements for extraction:\n"
    "Statement: I know he likes to drive antique scooters and play the mandolin.\n"
    f"Output: (Descartes, likes to drive, antique scooters){KG_TRIPLE_DELIMITER}(Descartes, plays, mandolin)\n"
    "END OF EXAMPLE\n\n"
    "Statements for reference:\n"
    "{history}"
    "Statements for extraction:\n"
    "{input}\n\n"
    "Output:"
)

KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=_DEFAULT_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE,
)