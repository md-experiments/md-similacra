from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

character_response_schemas = [
    ResponseSchema(name="character_name", description="This is the name of the character"),
    ResponseSchema(name="character_age", description="integer, This is the age of the character, as a positive integer"),
    ResponseSchema(name="character_gender", description="Character gender: male or female"),
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

Please imagine a set of characters to take part in the story and add their descritions

{format_instructions}

Wrap your final output with closed and open brackets (a list of json objects)

YOUR RESPONSE:
"""

character_description_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(template)  
    ],
    input_variables=["author_name", "author_style", "story_summary"],
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

These are the characters in the story:
{character_descriptions}

Please create a plot for this story by describing a series of sections relevant.

{format_instructions}

Wrap your final output with closed and open brackets (a list of json objects)

YOUR RESPONSE:
"""

story_sections_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(template)  
    ],
    input_variables=["author_name", "author_style", "story_summary", "character_descriptions"],
    partial_variables={"format_instructions": story_sections_instructions}
)



section_expansion_template = """
You are a storyteller who writes and is inspired by {author_name} and you write stories in their style. 
Their style is typically described as {author_style}. 

This is the story summary: 
{story_summary}

These are the characters in the story:
{character_descriptions}

{story_so_far}

Write part of the story titled: {section_name}, with the description: {section_description}
This part also mentions these characters {mentioned_characters}

YOUR RESPONSE:
"""

section_detail_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(section_expansion_template)  
    ],
    input_variables=["author_name", "author_style", "story_summary", "character_descriptions",
                     "section_name","section_description","mentioned_characters"],
)

"""
ResponseSchema(
        name="speaker_name", 
        description="The name of the speaker. will be either the movie/story narrator speaking or one of the characters speaking. Narrator lines will start with NARRATOR: and story character lines will start with the full name of the character speaking, for instance if a character is named John Smith, the line will start with JOHN SMITH: followed by what they say."),
ResponseSchema(
        name="speaker_text", 
        description="The content of what the speaker is saying"),
"""

# How you would like your reponse structured. This is basically a fancy prompt template
scene_response_schemas = [
    ResponseSchema(
        name="SCENE_CONTENT", 
        description="The detail of the content of this scene, this will be in movie script format. This means it will be a list of dialogue or description lines, each line will be either the movie/story narrator speaking or one of the characters speaking. There can be multiple speakers, for example a dialogue between speakers. The narrator can also make multiple statements in each scene. Meaning there will likely be multiple lines for each scene. Narrator lines will start with NARRATOR: and story character lines will start with the full name of the character speaking, for instance if a character is named John Smith, the line will start with JOHN SMITH: followed by what they say."),
    ResponseSchema(
        name="SCENE_IMAGE", 
        description="A description of the image used for the scene, it will link to the content of the scene and will be sent to a AI model that can create images based on a description. Use descriptive language for the background, objects and people in the scene. Mention relevant details to the scene: how and where are objects and people placed in reltion to each other, what they are doing, any actions taking place. When mentioning characters, refer to them with their full names"),
    ResponseSchema(
        name="SCENE_AUDIO",  
        description="A description of the audio, this will fit the content of the scene and will be sent to a AI model that can create audio music based on a description")
]

# How you would like to parse your output
scene_output_parser = StructuredOutputParser.from_response_schemas(scene_response_schemas)

scene_instructions = scene_output_parser.get_format_instructions()

template = """
You are a scriptwriter who writes and is inspired by {author_name} and you write stories in their style. 
Their style is typically described as {author_style}. 

This is the story summary: 
{story_summary}

This is FULL LIST OF CHARACTERS in the story:
{character_descriptions}

{story_so_far}

This section is titled: {section_name}, with the description: {section_description}
These are the CHARACTERS MENTIONED in this scene {mentioned_characters}.
Only only mention characters from the list of CHARACTERS MENTIONED in this scene. Rely on their descriptions per the FULL LIST OF CHARACTERS in the story. If needed, there can be references to other characters as part of the dialogue or narration.

You are writing the script for the scenes within this part of the story. 
This is the list of SCENE_DESCRIPTION to write
{scenes_description}

Please write the detailed description for the script of each scene
Refer to the story so far, previous scenes and character descriptions when writing this, do not contradict things mentioned already.
However, you can be creative with what happens in this scene. Try to insert dynamic and excited conversation between characters where possible.
Where possible, try to tell the story with dialogue between the charaters instead of the NARRATOR speaking.

{format_instructions}

Here is an example of what scene_content will look like for an example scene:

EXAMPLE INPUT: 

SCENE DESCRIPTION: 
Scene 0: John saw Marry in the school hallway and walked over to her. 'Hello Marry, how are you?' John said. 'I am good, thanks!' Marry responded. They both stood there for a moment, not speaking.
CHARACTERS MENTIONED: John Smith, Marry Jones

EXAMPLE OUTPUT for Scene 0:

```json
[
    {{
    "SCENE_CONTENT": "NARRATOR: John saw Marry in the school hallway and walked over to her.\nJOHN SMITH: Hello Marry, how are you? I thought you were having lunch.\nMARRY JONES: I am good, thanks! I already had lunch.\nNARRATOR: They both stood there for a moment, not speaking. It felt like time had stood still",
    "SCENE_IMAGE": "Bustling high school hallway, teeming with students hurrying to their classes. John is seen in the foreground walking toward marry, staning in a dimly lit hallway. Marry is looking at him smiling. The look content and happy to see each other"
    "SCENE_AUDIO": "a gentle and melodic background music begins to play, seamlessly blending with the atmosphere of the high school hallway. The music, a delicate combination of piano and strings, creates an emotional undercurrent that heightens the significance of the encounter."
    }},
    ...
    ]
```
EXPLANATION of OUTPUT: 
SCENE_CONTENT: The structure of the SCENE_CONTENT will always have narrator and character names in the beginning. The final output can embellish and add additional additional detail if needed, like the discussion about lunch. You can drop detail like: "Marry responded" because this is now clear from the script.

Wrap your final output with closed and open brackets (a list of json objects)

YOUR RESPONSE:
"""

scene_prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template(template)  
    ],
    input_variables=["author_name", "author_style", "story_summary", "character_descriptions",
                     "section_name","section_description","mentioned_characters",
                     "story_so_far", 'scenes_description'],
    partial_variables={"format_instructions": scene_instructions}
)
