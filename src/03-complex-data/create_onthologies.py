import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"


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


client = OpenAI(
    base_url=endpoint,
    api_key=token,
)


print ("Creating structure from these image contents")

system_prompt = """
Look at the images below and use them as input. Generate a response based on the images.
You are an expert in ontology engineering. Generate an OWL ontology based on the following domain description:
Define classes, data properties, and object properties with their term designation, the norm name, a description of what it is, and the range and domain while also group them by domain.
Include domain and range for each property.
When a term has one or more synonyms, they follow the preferred term. The synonyms are listed in alphabetical order and need to be carried over to the OWL ontology.
The numerical values in the definitions should be use to create a hierarchy of classes and properties.
Add the numeric value to the label of the class or property and be specific. Add the most amount of details possible to the ontology.
Add descriptions to the classes and properties so that they are self-explanatory and can be used to classify images based on the descriptions.
Provide the output in OWL (XML) format and only output the ontology and nothing else"""

response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": system_prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("screen_1.png", "png"),
                        "detail": "low"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("screen_2.png", "png"),
                        "detail": "low"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("screen_3.png", "png"),
                        "detail": "low"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("screen_4.png", "png"),
                        "detail": "low"
                    },
                }
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)
content_owl = response.choices[0].message.content

with open("screws.xml", "w") as file:
    new_ontology = content_owl.replace("```xml", "").replace("```", "")
    file.write(new_ontology)