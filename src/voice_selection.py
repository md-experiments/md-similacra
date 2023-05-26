import random, yaml
from src.utils import flatten_list, pad_integer


def voice_filter(voices_dict, gender_starts_with):
        return set(flatten_list([voices_dict[k] 
                                 for k in voices_dict if k.startswith(gender_starts_with)]))

def voice_assignment(characters,
                     old_threshold = 35,
                     voices_choice_path = './voices.yaml', seed_value = 2023):
    random.seed(seed_value)
    voices_dict = yaml.load(open(voices_choice_path,'r'), Loader=yaml.FullLoader)
    voices_lookup = {
            'male': voice_filter(voices_dict, 'male'),
            'female': voice_filter(voices_dict, 'female'),
            'nonbinary': voice_filter(voices_dict, 'nonbinary'),
            'available_male': voice_filter(voices_dict, 'male'),
            'available_female': voice_filter(voices_dict, 'female'),
            'available_nonbinary': voice_filter(voices_dict, 'nonbinary'),
        }

    voice_choice = random.choice(voices_dict['narrator'])
    voice_assignments = {
        "NARRATOR": voice_choice,
        
    }
    if voice_choice in voices_lookup[f'available_male']:
        voices_lookup[f'available_male'].remove(voice_choice)
    else:
        voices_lookup[f'available_female'].remove(voice_choice)
    #print(voices_lookup)
    for character in characters:
        name = character['character_name']
        gender = character['character_gender'].lower().strip()
        gender = 'female' if 'female' in gender else ('male' if 'male' in gender else 'nonbinary')
        try:
            age = int(character['character_age'])
        except:
            age = 30
            print('Age failed, autoassign 30')
        look_up_key = f'{gender}_{"old" if age > old_threshold else "young"}'
        # Select at random
        available_voices = set(voices_dict[look_up_key]).intersection(voices_lookup[f'available_{gender}'])
        if len(available_voices):
            voice_choice = random.choice(list(available_voices))
            voices_lookup[f'available_{gender}'].remove(voice_choice)
        # If no voices matching profile just pick from the ones remaining by gender
        elif available_voices[f'available_{gender}']:
            print(f'Missing in available for age group {look_up_key}: {name}')
            voice_choice = random.choice(list(available_voices[f'available_{gender}']))
            voices_lookup[f'available_{gender}'].remove(voice_choice)
        # If no voices remaining assign from all available
        else:
            print(f'Missing in available for gender {look_up_key}: {name}')
            voice_choice = random.choice(list(available_voices[gender]))

        voice_assignments[name.upper()] = voice_choice
    return voice_assignments
        

def extract_texts_from_scene(text, voice_assignments: dict, main_path_to_audio: str):
    """
        text: str or list
        path_to_audio: './data/audio/05_02_{audio_key}.mp3'
    """

    if isinstance(text,list):
        text_split = text
    elif isinstance(text,str):
        text_split = text.split('\n')
    result = []
    for i, txt in enumerate(text_split):
        try:
            likely_name = txt.upper().split(':')[0]
            if len(likely_name.split())>2:
                print(f'ERROR: Not sure about {txt}')
            elif (len(likely_name.split())==1) and (likely_name=="NARRATOR"):
                character = 'NARRATOR'
                voice =  voice_assignments[character]
            elif (len(likely_name.split())==1):
                # Likely GPT returned just first name
                print('::',likely_name)
                for k in voice_assignments:
                    if likely_name.upper() in k.upper():
                        character = k.upper()
                        voice = voice_assignments[character]
                        break
            elif (len(likely_name.split())==2) and (voice_assignments.get(likely_name.upper(),'')!=''):
                character = likely_name.upper()
                voice = voice_assignments[character]
            else:
                print(f'ERROR: Could not assign name {txt}')
                voice = ''

            txt_to_read = ':'.join(txt.split(':')[1:])
            audio_key = f"{pad_integer(i)}_{likely_name.split()[0]}__{txt_to_read.replace(' ','_')[:30]}"
            path_to_audio = main_path_to_audio.format(audio_key=audio_key)
            result.append({
                'raw_text': txt,
                'text': txt_to_read,
                'character': character,
                'voice': voice,
                'path_audio': path_to_audio
            })
        except:
            print(txt)
    return result