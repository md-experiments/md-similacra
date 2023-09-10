
import os, yaml, json
import requests

import io
import base64
from PIL import Image
from src.utils import makedirs, hash_text

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
    try:
        if not os.path.exists(path_image):
            r = requests.post('http://192.168.0.13:7860/sdapi/v1/txt2img', json = params)
            Variable= Image.open(io.BytesIO(base64.b64decode(r.json()['images'][0])))
            Variable.save(path_image, format='jpeg')
            return path_image
        else:
            return path_image
    except:
        return ''

def prepare_txt2img(api_params_path, path_story, seed):
    data = yaml.load(open(api_params_path,'r'), Loader=yaml.FullLoader)
    params = data['defaults']
    params['seed'] = seed
    params['seed_resize_from_h'] = seed
    params['seed_resize_from_w'] = seed

    params['negative_prompt'] = ', '.join(data['negative_prompt'])
    hash_params = hash_text(json.dumps(params))[:6]
    path_images = os.path.join(path_story,'images',hash_params)
    makedirs([path_images])
    return path_images, params, data['style']