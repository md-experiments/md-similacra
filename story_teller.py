from src.prompts.storyteller_prompts import character_description_prompt, story_sections_prompt, section_detail_prompt, scene_prompt
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import json, yaml
from tqdm import tqdm

import os
with open('openai.key','r') as f:
    openai_api_key = f.read()
os.environ['OPENAI_API_KEY'] = openai_api_key 

chat_model = ChatOpenAI(temperature=0.9, openai_api_key=openai_api_key)

class StoryTeller():
    def __init__(self, author_name: str, author_style: str, data_storage: str, story_key: Optional[str] = '') -> None:
        self.author_name = author_name
        self.author_style = author_style
        self.data_storage = data_storage
        self.story_key = story_key

    def save_results(self, output, path_result = '', path_result_safe = ''):
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
        path_summary = os.path.join(self.data_storage,self.story_key,'00_story_summary.txt')
        if os.path.exists(path_summary):
            with open(path_summary,'r') as f:
                self.story_summary = f.read()
        else:
            # TODO create story summary
            pass

    def create_story_characters(self):
        path_characters = os.path.join(self.data_storage,self.story_key,'01_characters.yaml')
        path_characters_safe = os.path.join(self.data_storage,self.story_key,'01_characters_safe.txt')
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
        path_story_plot = os.path.join(self.data_storage,self.story_key,'02_story_plot.yaml')
        path_story_plot_safe = os.path.join(self.data_storage,self.story_key,'02_story_plot_safe.txt')
        if os.path.exists(path_story_plot) or os.path.exists(path_story_plot_safe):
            self.story_plot = yaml.load(open(path_story_plot,'r'), Loader=yaml.FullLoader)
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
        self.story_so_far = ''
        pass

    def create_scenes_for_part(self, scenes_description):
        """Frome the short description, break the text into a set of scenes"""
        # TODO: This can be more sophisticated in how we create scenes for a section
        this_scene = [f"Scene {i}: {s}\n\n" for i, s in enumerate(scenes_description.split('\n\n'))]

        scenes = ''.join(this_scene)
        return scenes

    def create_section_detail(self, section_id, section_name, section_description, mentioned_characters):

        path_section_detail = os.path.join(self.data_storage,self.story_key,f'03_section_detail_{section_id}.yaml')
        path_section_detail_safe = os.path.join(self.data_storage,self.story_key,f'03_section_detail_{section_id}_safe.txt')
        if os.path.exists(path_section_detail) or os.path.exists(path_section_detail_safe):
            section_detail = yaml.load(open(path_section_detail,'r'), Loader=yaml.FullLoader)
        else:
            _input = section_detail_prompt.format_prompt(
                author_name = self.author_name, 
                author_style = self.author_style,
                story_summary = self.story_summary,
                character_descriptions = self.character_descriptions,
                section_name = section_name,
                section_description = section_description,
                mentioned_characters = mentioned_characters,
            )
            output = chat_model(_input.to_messages())
            section_detail = self.save_results(output, path_section_detail, path_section_detail_safe)
        return section_detail
    
    def create_scripts_from_scenes_for_part(self, 
                                            section_id, section_name, section_description, 
                                            mentioned_characters, story_so_far, scenes_description):
        """Given a section and its detail as well as actual breakdown by scene, create """
        
        if len(story_so_far)==0:
            story_so_far = f''
        else:
            story_so_far = f'This is the story so far {story_so_far}.\n'

        path_story_plot = os.path.join(self.data_storage,self.story_key,f'03_section_plot_{section_id}.yaml')
        path_story_plot_safe = os.path.join(self.data_storage,self.story_key,f'03_section_plot_{section_id}_safe.txt')
        if os.path.exists(path_story_plot) or os.path.exists(path_story_plot_safe):
            self.story_plot = yaml.load(open(path_story_plot,'r'), Loader=yaml.FullLoader)
        else:
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
            output = chat_model(_input.to_messages())
            result = self.save_results(output, path_story_plot, path_story_plot_safe)
            self.story_plot = result

lovecraft0 = StoryTeller(
    author_name = 'H. P. Lovecraft',
    author_style = 'described as atmospheric, dark, and highly descriptive. His works often revolve around cosmic horror and the unknown, incorporating elements of science fiction and supernatural themes. Lovecraft\'s prose is characterized by intricate world-building, richly detailed descriptions of otherworldly creatures and settings, and a sense of foreboding and dread that pervades his stories. He frequently employs a first-person narrative, immersing readers in the unsettling perspectives of his characters as they confront the unfathomable horrors of the Lovecraftian universe.',
    data_storage = './data/stories',
    story_key = 'lovecraft0'
)
lovecraft0.create_story_summary()
lovecraft0.create_story_characters()
lovecraft0.create_story_plot()

story_so_far = []

for section_id, section in enumerate(tqdm(lovecraft0.story_plot[:2])):
    section_detail = lovecraft0.create_section_detail(section_id, section['section_name'], section['section_description'],
                                     section['characters'])
    scenes_detail = lovecraft0.create_scenes_for_part(section_detail)
    lovecraft0.create_scripts_from_scenes_for_part(section_id, section['section_name'], section['section_description'],
                                     section['characters'], story_so_far, scenes_detail)