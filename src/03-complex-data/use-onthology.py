import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

def get_image_data_url(image_file: str, image_format: str) -> str:
    """
    Helper function to converts an image file to a data URL string.

    Args:
        image_file (str): The path to the image file.
        image_format (str): The format of the image file.

    Returns:
        str: The data URL of the image.
    """
    try:
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Could not read '{image_file}'.")
        exit()
    return f"data:image/{image_format};base64,{image_data}"

onthology_file="screws.xml"
# read the file
if os.path.exists(onthology_file):
    with open(onthology_file, "r") as file:
        ontology_content = file.read()
    print("Ontology file content:")
    print(ontology_content)
else:
    print(f"The file {onthology_file} does not exist.")


client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

print ("Use onthology to describe image")
response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that describes images in details. Make use of the onology provided to describe the image.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": ontology_content,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("reference.png", "png"),
                        "detail": "low"
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)
