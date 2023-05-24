from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

character_response_schemas = [
    ResponseSchema(name="character_name", description="This is the name of the character"),
    ResponseSchema(name="character_age", description="This is the age of the character"),
    ResponseSchema(name="character_gender", description="Character gender: male, female, non-binary"),
    ResponseSchema(name="character_appearance", description="This is the visual appearance of the character: their face, build, details of how they dress and how they appear to others"),
    ResponseSchema(name="character_traits", description="This briefly describes the character profile, their background, traits, habits and goals"),
    ResponseSchema(name="character_role",  description="Consider the story summary. This is the role the character plays in the story: are they central or secondary, helping the protagonist, ignoring, thwarting or deceiving them, do they grow and how")
]

# How you would like to parse your output
character_response_parser = StructuredOutputParser.from_response_schemas(character_response_schemas)

# See the prompt template you created for formatting
character_format_instructions = character_response_parser.get_format_instructions()

template = """
You are a storyteller who writes and is inspired by {author_name} and you write stories in their style. 
Their style is typically described as {author_style}. 

This is the story summary: 
{story_summary}

These are the characters in the story:
{character_descriptions}

Please imagine a set of characters to take part in the story and add their descritions

{format_instructions}

Wrap your final output with closed and open brackets (a list of json objects)

YOUR RESPONSE:
"""

character_description_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(template)  
    ],
    input_variables=["author_name", "author_style", "story_summary", "character_descriptions"],
    partial_variables={"format_instructions": character_format_instructions}
)


story_sections_response_schemas = [
    ResponseSchema(name="section_name", description="This is the name of the section of the story"),
    ResponseSchema(name="section_description", description="This is a short one sentence description of what happens in this section of the story"),
    ResponseSchema(name="characters",  description="This is a comma separated list of the characters who take part in each section of the story")
]

# How you would like to parse your output
story_sections_output_parser = StructuredOutputParser.from_response_schemas(story_sections_response_schemas)
story_sections_instructions = story_sections_output_parser.get_format_instructions()

template = """
You are a storyteller who writes and is inspired by {author_name} and you write stories in their style. 
Their style is typically described as {author_style}. 

This is the story summary: 
{story_summary}

Please create a plot for this story by describing a series of sections relevant.

{story_sections_instructions}

Wrap your final output with closed and open brackets (a list of json objects)

YOUR RESPONSE:
"""

story_sections_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(template)  
    ],
    input_variables=["author_name", "author_style", "story_summary"],
    partial_variables={"format_instructions": story_sections_instructions}
)



template = """
You are a storyteller who writes and is inspired by {author_name} and you write stories in their style. 
Their style is typically described as {author_style}. 

This is the story summary: 
{story_summary}

These are the characters in the story:
{character_descriptions}

Write part of the story titled: {section_name}, with the description: {section_description}
This part also mentions these characters {mentioned_characters}

YOUR RESPONSE:
"""

prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(template)  
    ],
    input_variables=["author_name", "author_style", "story_summary", "character_descriptions",
                     "section_name","section_description","mentioned_characters"],
)

