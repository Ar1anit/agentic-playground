import os
import base64
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

invoice_url = "https://likvi.de/assets/img/blog/rechnungsvorlage.jpg"
name = "invoice.jpg"
if not os.path.exists(name):
    print(f"Downloading invoice from {invoice_url}")
    response = requests.get(invoice_url)
    if response.status_code == 200:
        with open(f'{name}', 'wb') as f:
            f.write(response.content)
        print("Downloaded ", name)
    else:
        print(f"Failed to download {invoice_url}")

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


print ("Parse the image and extract the data ")

system_prompt = """
Look at the image attached as input to extract all the invoice information you can find. I want to you extract all the relevant information you can from the image and create a XRechnung Beispiel XML filled with all known values. Replace all existing sample values with either the extracted details from the image or set them to empty."""

template_xml_file = "invoice_template.xml"
# read the file
if os.path.exists(template_xml_file):
    with open(template_xml_file, "r") as file:
        invoice_xml_content = file.read()
else:
    print(f"The file {template_xml_file} does not exist.")

system_prompt = system_prompt + invoice_xml_content

explaination_xml_file = "invoice_explaination.txt"
# read the file
if os.path.exists(explaination_xml_file):
    with open(explaination_xml_file, "r") as file:
        invoice_explaination_content = file.read()
else:
    print(f"The file {explaination_xml_file} does not exist.")

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract all invoice data from this image. Output only the xml an nothing else.:",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_image_data_url("invoice.jpg", "jpg"),
                        "detail": "low"
                    },
                },
            ],
        },
    ],
    model=model_name,
)

print(response.choices[0].message.content)
invoice_xml_parsed = response.choices[0].message.content

with open("invoice_parsed.xml", "w") as file:
    parsed_invoice = invoice_xml_parsed.replace("```xml", "").replace("```", "")
    file.write(parsed_invoice)