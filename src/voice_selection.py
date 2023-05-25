import random, yaml
from src.utils import flatten_list


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
    print(voices_lookup)
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

        voice_assignments[name] = voice_choice
    return voice_assignments
        
