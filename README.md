# AI Story Teller

AI tool that creates a complete video story from a simple description. 
For some sample seed descriptions, see ./scripts

## How it works
1. The tool uses your description to create an extensive plot outline
2. Next, it generates character profiles basedon the plot expanding them with descriptions like: age, personality, role, etc.
3. It breaks down the plot into a series of scenes complete with a signifcance to overall story and actions taken by the characters
4. For each scene, it writes the specific lines both narrative and character dialogue
5. Now it selects a voice using Amazon Polly or Eleven Labs and assigning voices based on profile (age and gender) and creates the audio dubbing
6. Finally, uses the description of each scene to create an image using DallE or Stability AI
7. loops through each scene and stitches together inages and voice

## Samples 
Some sample videos coming soon

## Success and Challenges 
- The stiry is consistently sequential and providing a summary back to the AI creates a relatively long and complex plot with good consistency. This is very hard to achieve in simpler setups
- As will be apparent from the samples, the results are still very generic in terms of story line as the AI struggles to speak about specific events and actions by the characters
- Image generation does not produce consistent characters, despite attempts to inject consistent character descriptions. This is the case aith all image AI
