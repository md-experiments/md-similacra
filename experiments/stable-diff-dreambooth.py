from diffusers import DiffusionPipeline

from PIL.Image import Image


# Load the HF pipeline

model = DiffusionPipeline.from_pretrained("sd-dreambooth-library/herge-style")


# The input prompt

prompt = "Mountain winds and babbling springs and moonlight seas, herge_style."


# Generate an image from the prompt

output_image: Image = model(prompt).images[0]


# Save the image to a local file

with open("image.jpeg", "w") as f:

    output_image.save(f, format="JPEG")