import os
import openai


import os
with open('./openai.key','r') as f:
    openai_api_key = f.read()
os.environ['OPENAI_API_KEY'] = openai_api_key 
# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = "a photo of a small bear, in the forest, looking at the camera and smiling"
#prompt = "A photo of a teddy bear on a skateboard in Times Square"

response = openai.Image.create(
  prompt=prompt,
  n=1,
  size="1024x1024"
)
image_url = response['data'][0]['url']
print(response)
print(image_url)