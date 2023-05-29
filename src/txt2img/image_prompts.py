
import os, yaml
import requests

import io
import base64
from PIL import Image


def prepare_prompt(scene, characters_data):
    prompt = scene['SCENE_IMAGE'].lower().strip()
    for character in characters_data:
        char_descr = character['character_appearance']
        gender = character['character_gender'].lower().strip()
        char_pronoun = 'he' if gender == 'male' else 'she'

        char_first_name = character['character_name'].split()[0].lower().strip()
        char_name = character['character_name'].lower().strip()
        char_descr = char_descr.lower().strip().replace(char_name,char_pronoun).replace(char_first_name,char_pronoun)

        prompt = prompt.replace(char_name,char_descr).replace(char_first_name,char_descr)
    return prompt

def create_image_with_sd_api(path_image, params):
    if not os.path.exists(path_image):
        r = requests.post('http://192.168.0.13:7860/sdapi/v1/txt2img', json = params)
        Variable= Image.open(io.BytesIO(base64.b64decode(r.json()['images'][0])))
        Variable.save(path_image, format='jpeg')

