import os
import base64
from openai import OpenAI

from imagelibrary import VectorDatabase

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

database = VectorDatabase()
database.download_images()

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

print ("Comparing two images: f1_car_url_1.jpg and f1_car_url_2.jpg")
response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that describes images in details.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Look at these two pictures. Image 1 and Image 2. Are they similar List all the differences according to category, color, position and size.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("f1_car_url_1.jpg", "jpg"),
                        "detail": "low"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("f1_car_url_2.jpg", "jpg"),
                        "detail": "low"
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)