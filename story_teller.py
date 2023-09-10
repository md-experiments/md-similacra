from src.prompts.storyteller_prompts import character_description_prompt, story_sections_prompt, section_detail_prompt, scene_prompt
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import json, yaml
from tqdm import tqdm
from src.utils import pad_integer, flatten_list, makedirs
#from tts.tts import create_tts_11labs
from src.tts.polly import create_tts_polly
from src.voice_selection import voice_assignment, extract_texts_from_scene
import requests
from src.txt2img.image_prompts import prepare_prompt, create_image_with_sd_api, prepare_txt2img

import os
with open('openai.key','r') as f:
    openai_api_key = f.read()
os.environ['OPENAI_API_KEY'] = openai_api_key 

chat_model = ChatOpenAI(temperature=0.9, openai_api_key=openai_api_key)

class StoryTeller():
    def __init__(self, author_name: str, author_style: str, data_storage: str, seed: int, 
                 bg_audio: str, story_summary: str = '', story_key: Optional[str] = '') -> None:
        self.author_name = author_name
        self.author_style = author_style
        self.data_storage = data_storage
        self.story_key = story_key
        self.seed = seed
        self.bg_audio = bg_audio
        self.path_story = os.path.join(data_storage, story_key)
        self.path_audio = os.path.join(self.path_story,'audio')
        self.story_summary = story_summary
        makedirs([self.path_story, self.path_audio])
        

    def save_results(self, output, path_result, path_result_safe, save_as_text = False):
        if "```json" in output.content:
            json_string = output.content.split("```json")[1].replace('```','').strip()
        else:
            json_string = output.content
        if save_as_text:
            result = json_string
            yaml.dump(json_string, open(path_result_safe,'w'))
        else:
            try:
                result = json.loads(json_string)
                yaml.dump(result, open(path_result,'w'))
            except:
                yaml.dump(json_string, open(path_result_safe,'w'))
        return result

    def create_story_summary(self):
        path_summary = os.path.join(self.data_storage,self.story_key,'00_story_summary.txt')
        if os.path.exists(path_summary) and (self.story_summary == ''):
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

    def assign_voices(self, path_voices = './voices_polly.yaml'):
        voice_assignments = voice_assignment(self.character_descriptions, old_threshold = 35, child_threshold=14,
                voices_choice_path = path_voices, seed_value = 2023)
        path_voice_assignments = os.path.join(self.data_storage,self.story_key,'01_voice_assignments.yaml')
        yaml.dump(voice_assignments,open(path_voice_assignments,'w'))
        self.voice_assignments = voice_assignments

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

    def create_section_detail(self, section_id, section_name, section_description, mentioned_characters, story_so_far):

        path_section_prompt = os.path.join(self.data_storage,self.story_key,f'03_{section_id}_section_detail_prompt.txt')
        path_section_detail = os.path.join(self.data_storage,self.story_key,f'03_{section_id}_section_detail.yaml')
        path_section_detail_safe = os.path.join(self.data_storage,self.story_key,f'03_{section_id}_section_detail_safe.txt')
        if os.path.exists(path_section_detail_safe):
            section_detail = yaml.load(open(path_section_detail_safe,'r'), Loader=yaml.FullLoader)
        else:
            _input = section_detail_prompt.format_prompt(
                author_name = self.author_name, 
                author_style = self.author_style,
                story_summary = self.story_summary,
                character_descriptions = self.character_descriptions_str,
                section_name = section_name,
                section_description = section_description,
                mentioned_characters = mentioned_characters,
                story_so_far = story_so_far
            )
            with open(path_section_prompt,'w') as f:
                f.write(_input.messages[0].content)
            output = chat_model(_input.to_messages())
            section_detail = self.save_results(output, path_section_detail, path_section_detail_safe, save_as_text=True)
        return section_detail
    
    def create_scripts_from_scenes_for_part(self, 
                                            section_id, section_name, section_description, 
                                            mentioned_characters, story_so_far, scenes_description):
        """Given a section and its detail as well as actual breakdown by scene, create """
        
        if len(story_so_far)==0:
            story_so_far = f''
        else:
            story_so_far = f'This is the story so far {story_so_far}.\n'

        path_story_plot_prompt = os.path.join(self.data_storage,self.story_key,f'04_{section_id}_section_plot_prompt.txt')
        path_story_plot = os.path.join(self.data_storage,self.story_key,f'04_{section_id}_section_plot.yaml')
        path_story_plot_safe = os.path.join(self.data_storage,self.story_key,f'04_{section_id}_section_plot_safe.txt')
        if os.path.exists(path_story_plot):
            scene_script = yaml.load(open(path_story_plot,'r'), Loader=yaml.FullLoader)
        elif os.path.exists(path_story_plot_safe):
            try:
                txt = open(path_story_plot_safe,'r').read()
                txt = txt.replace('\\n', '').replace('\\', '').replace('\n', '').replace('  ', '').replace(',]', ']')
                if txt.startswith('"') and txt.endswith('"'):
                    txt = txt[1:-1]
                scene_script = json.loads(txt.strip())
            except:
                pass
        else:
            _input = scene_prompt.format_prompt(
                author_name = self.author_name, 
                author_style = self.author_style,
                story_summary = self.story_summary,
                character_descriptions = self.character_descriptions_str,
                section_name = section_name,
                section_description = section_description,
                mentioned_characters = mentioned_characters,
                story_so_far = story_so_far,
                scenes_description = scenes_description
            )
            with open(path_story_plot_prompt,'w') as f:
                f.write(_input.messages[0].content)

            output = chat_model(_input.to_messages())
            scene_script = self.save_results(output, path_story_plot, path_story_plot_safe)
        return scene_script

    def make_video(self):
        all_vids = []
        nr_sections = len(self.story_plot)
        for section_id in range(nr_sections):
            ls_screens = yaml.load(open(f'./data/stories/{self.story_key}/05_0{section_id}_aud_img_scripts.yaml','r'),Loader = yaml.FullLoader)
            all_screens = []
            for screen in tqdm(ls_screens, desc = f'{self.story_key}:::Section {section_id}'):
                full_path = screen['txt2img_image'].replace('./data/','../../../md-similacra/data/')
                image_path = '/'.join(full_path.split('/')[:-1])
                image_name = full_path.split('/')[-1]
                data = {
                "user_id": "user1234",
                "file_name": image_name,
                "input_path": image_path,
                "output_path": "../data/video_summary/assets",
                "text": "Some non-empty text",
                "video_effects": "img",
                "video_fade_in": "0.0",
                "video_fade_out": "0.0",
                "video_post_stt_buffer": "0.5",
                "resolution": [
                    1280,
                    720
                ],
                "vox": screen['path_audio'].replace('./data/','../../../md-similacra/data/'),
                "text_position": "no_text"
                }

                r = requests.post('http://localhost:8000/byo_vox_video/', json = data)
                all_screens.append(r.json())

            all_vids.append(all_screens)
        data = {
        "user_id": "user1234",
        "files_list": [f['output_file'] for f in flatten_list(all_vids)],
        "video_summary_name": f"{self.story_key}.mp4",
        "input_path": "../data/video_summary/assets",
        "output_path": "../data/video_summary/summaries",
        "bg_audio_file": f"../data/bg_sounds/{self.bg_audio}",
        "bg_audio_volume_frac": "0.1",
        "bg_audio_start_sec": "0"
        }

        r = requests.post('http://localhost:8000/list_files_summary_video/', json = data)


api_params_path = './scripts/txt2img_lovecraft.yaml'
api_params_path = './scripts/txt2img_donaldson.yaml'
params_story = yaml.load(open('./scripts/donaldson1.yaml','r'),Loader=yaml.FullLoader)
st = StoryTeller(
    **params_story
)


"""api_params_path = './scripts/txt2img_donaldson.yaml'
st = StoryTeller(
    author_name = 'Julia Donaldson',
    author_style = "Engages young readers and captures their imaginations. Her writing is known for its rhythmic and rhyming patterns, enchanting storytelling, and memorable characters. She often introduces protagonists who face challenges or embark on quests, making her books both entertaining and educational. Her stories are often written in lively and catchy verse, which creates a musical quality that children find captivating.",
    data_storage = './data/stories',
    seed = 1,
    bg_audio = 'Organic Guitar House - Dyalla.mp3',
    story_summary = "When Sammy the Squirrel finds a mysterious key in the forest, he embarks on a thrilling adventure to discover what it unlocks. Along the way, he encounters a cast of animal friends who each have a clue to help him on his quest. Through teamwork and problem-solving, they navigate through obstacles and unravel the secret behind the lost key.",
    story_key = 'donaldson0',
    )
"""
st.create_story_summary()
st.create_story_characters()
st.assign_voices(path_voices = './voices_polly.yaml')

st.create_story_plot()

path_images, params, image_style = prepare_txt2img(api_params_path, st.path_story, st.seed)

print(f'Path images {path_images}')

for section_id, section in enumerate(tqdm(st.story_plot)):

    story_so_far = ''.join([t['section_description']+'\n' for t in st.story_plot[:section_id]])
    section_detail = st.create_section_detail(section_id, section['section_name'], section['section_description'],
                                     section['characters'], story_so_far)
    scenes_detail = st.create_scenes_for_part(section_detail)
    scene_script = st.create_scripts_from_scenes_for_part(section_id, section['section_name'], section['section_description'],
                                     section['characters'], story_so_far, scenes_detail)
    
    path_to_aud_img_script = os.path.join(st.data_storage,st.story_key,f'05_{pad_integer(section_id)}_aud_img_scripts.yaml')

    all_voice_scripts = []
    for scene_id, scene in enumerate(scene_script):
        # Extract text from scene
        path_to_audio = os.path.join(st.path_audio,f'audio_{pad_integer(section_id)}_{pad_integer(scene_id)}_')
        path_to_audio = path_to_audio + '{audio_key}.mp3'
        voice_script = extract_texts_from_scene(scene['SCENE_CONTENT'], st.voice_assignments, path_to_audio)
        # Each scene here can have a combination of speakers while still part of the same scene
        # For all of them the picture is always the same but multiple voices may be needed
        # Hence the image will keep repeating
        for v in voice_script:
            # Make audio
            if not os.path.exists(v['path_audio']):
                #create_tts_11labs(v['text'], v['path_audio'], v['voice'], api_key_path = './tts/elevenlabs.key')
                create_tts_polly(v['text'], v['path_audio'], v['voice'], api_key_path = './aws_key.yaml')
            # Make image
            path_image = os.path.join(path_images,f'img_{pad_integer(section_id)}_{pad_integer(scene_id)}.jpeg')
            prompt = prepare_prompt(scene, st.character_descriptions)
            params['prompt'] = f"{prompt}, {image_style}"
            path_image_res = create_image_with_sd_api(path_image, params)
            if path_image_res != '':
                v['txt2img_prompt'] = prompt
                v['txt2img_image'] = path_image
        all_voice_scripts.append(voice_script)
    all_voice_scripts = flatten_list(all_voice_scripts)
    yaml.dump(all_voice_scripts, open(path_to_aud_img_script,'w'))

st.make_video()