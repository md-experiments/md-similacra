from src.prompts.storyteller_prompts import character_description_prompt, story_sections_prompt, section_expansion_prompt, scene_prompt
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import json, yaml


import os
with open('openai.key','r') as f:
    openai_api_key = f.read()
os.environ['OPENAI_API_KEY'] = openai_api_key 

chat_model = ChatOpenAI(temperature=0.9, openai_api_key=openai_api_key)

class StoryTeller():
    author_name: str
    author_style: str
    data_storage: str
    existing_story: Optional[str] = ''

    def save_results(self, output, path_result, path_result_safe):
        if "```json" in output.content:
            json_string = output.content.split("```json")[1].replace('```','').strip()
        else:
            json_string = output.content
        try:
            result = json.loads(json_string)
            yaml.dump(result, open(path_result,'w'))
        except:
            yaml.dump(json_string, open(path_result_safe,'w'))
        return result

    def create_story_summary(self):

        if len(self.existing_story):
            path_summary = os.path.join(self.data_storage,self.existing_story,'00_story_summary.txt')
            if os.path.exists(path_summary):
                with open(path_summary,'r') as f:
                    self.story_summary = f.read()
        else:
            # TODO create story summary
            pass

    def create_story_characters(self):
        path_characters = os.path.join(self.data_storage,self.existing_story,'01_characters.yaml')
        path_characters_safe = os.path.join(self.data_storage,self.existing_story,'01_characters_safe.txt')
        if os.path.exists(path_characters) or os.path.exists(path_characters_safe):
            self.character_descriptions = yaml.load(open(path_characters,'r'), Loader=yaml.FullLoader)
        else:
            _input = character_description_prompt.format_prompt(
                author_name = self.author_name, 
                author_style = self.author_style,
                story_summary = self.story_summary
            )
            output = chat_model(_input.to_messages())
            result = self.save_results(output, path_characters, path_characters_safe)
            self.character_descriptions = result
        def character_string_builder(char_dict):
            return f'Name: {char_dict["character_name"]} ({char_dict["character_age"]}), {char_dict["character_gender"]}' \
                f' Role: {char_dict["character_role"]}, Bio: {char_dict["character_traits"]}\n'
        self.character_descriptions_str = '\n'.join([character_string_builder(js) for js in self.character_descriptions ])


    def create_story_plot(self):
        path_story_plot = os.path.join(self.data_storage,self.existing_story,'02_story_plot.yaml')
        path_story_plot_safe = os.path.join(self.data_storage,self.existing_story,'02_story_plot_safe.txt')
        if os.path.exists(path_story_plot) or os.path.exists(path_story_plot_safe):
            self.character_descriptions = yaml.load(open(path_story_plot,'r'), Loader=yaml.FullLoader)
        else:
            _input = story_sections_prompt.format_prompt(
                author_name = self.author_name, 
                author_style = self.author_style,
                story_summary = self.story_summary,
                character_descriptions = self.character_descriptions_str
            )
            output = chat_model(_input.to_messages())
            result = self.save_results(output, path_story_plot, path_story_plot_safe)
            self.story_plot = result


    def create_story_so_far(self):
        """Summary of what is happened in the script so far, as the scriptwriter adds more details an extra summary might help"""
        
        pass
    def create_scenes_for_part():
        """Frome the short description, break the text into a set of scenes"""

        pass
    def create_scripts_from_scenes_for_part(self, section_name, section_description, mentioned_characters, story_so_far, scenes_description):
        """Given a section and its detail as well as actual breakdown by scene, create """
        _input = scene_prompt.format_prompt(
            author_name = self.author_name, 
            author_style = self.author_style,
            story_summary = self.story_summary,
            character_descriptions = self.character_descriptions,
            section_name = section_name,
            section_description = section_description,
            mentioned_characters = mentioned_characters,
            story_so_far = story_so_far,
            scenes_description = scenes_description
        )


        print (f"There are {len(_input.messages)} message(s)")
        print (f"Type: {type(_input.messages[0])}")
        print ("---------------------------")
        print (_input.messages[0].content)
lovecraft0 = StoryTeller(
    author_name = 'H. P. Lovecraft',
    author_style = 'described as atmospheric, dark, and highly descriptive. His works often revolve around cosmic horror and the unknown, incorporating elements of science fiction and supernatural themes. Lovecraft\'s prose is characterized by intricate world-building, richly detailed descriptions of otherworldly creatures and settings, and a sense of foreboding and dread that pervades his stories. He frequently employs a first-person narrative, immersing readers in the unsettling perspectives of his characters as they confront the unfathomable horrors of the Lovecraftian universe.',
    story_summary = 'A small coastal town is plagued by a series of strange disappearances. As the townsfolk investigate, they uncover a cult worshipping an ancient entity that dwells in the depths of the nearby forest. The cult seeks to awaken the deity, intending to bring about the end of the world. The townspeople must unravel the secrets of the cult before it\'s too late.'
)

