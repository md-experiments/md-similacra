from elevenlabs import generate


def create_tts_11labs(text, save_to_path, voice = 'Bella', api_key_path = './elevenlabs.key'):
  # set_api_key("<YOUR_API_KEY>") 
  e11labs_key = open(api_key_path,'r').read()
  audio = generate( 
      text=text,
      voice=voice,
      api_key=e11labs_key
  )
  with open(save_to_path, "wb") as out:
      # Write the response to the output file.
      out.write(audio)
  return save_to_path