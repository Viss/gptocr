# this is a python3 script. 
# you'll need to get your own API keys for it to work.

import base64
import requests
from io import BytesIO
from mimetypes import guess_type
from mastodon import Mastodon
from openai import OpenAI

# Mastodon setup
mastodon = Mastodon(
    access_token='get-yer-own',  # Your access token
    api_base_url='https://mastodon.social'  # Your instance URL
)

# OpenAI setup
openai_api_key = "also-get-yer-own"  # Your OpenAI API key
OpenAI.api_key = openai_api_key

def encode_image_from_url(image_url):
    response = requests.get(image_url)
    return base64.b64encode(response.content).decode("utf-8")

def analyze_image(base64_image):
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "you're an AI that's used to add alt text to images"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image"},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            },
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content

def reupload_image(image_data, image_url, analysis):
    mime_type = guess_type(image_url)[0] or 'application/octet-stream'
    new_media = mastodon.media_post(BytesIO(base64.b64decode(image_data)), mime_type=mime_type, description=analysis)
    return new_media['id']

def update_post_with_new_images(post_id, new_media_ids):
    headers = {'Authorization': f'Bearer {mastodon.access_token}'}
    data = {'media_ids[]': new_media_ids}
    put_url = f'{mastodon.api_base_url}/api/v1/statuses/{post_id}'
    response = requests.put(put_url, headers=headers, data=data)
    return response

def fetch_and_analyze_images():
    user_account = mastodon.account_verify_credentials()
    user_id = user_account['id']

    print("Fetching posts...")
    posts = mastodon.account_statuses(user_id, limit=20)

    for post in posts:
        new_media_ids = []
        for attachment in post.get('media_attachments', []):
            if attachment['type'] == 'image' and (attachment['description'] is None or attachment['description'].strip() == ''):
                print(f"Found an image in a post: {attachment['url']}")
                base64_image = encode_image_from_url(attachment['url'])
                print("Analyzing image...")
                analysis = analyze_image(base64_image)
                print("Analysis complete.")
                print(analysis)
                new_media_id = reupload_image(base64_image, attachment['url'], analysis)
                new_media_ids.append(new_media_id)
            else:
                print("Image already has alt text or is not an image.")

        if new_media_ids:
            print(f"Updating post ID: {post['id']} with new media.")
            response = update_post_with_new_images(post['id'], new_media_ids)
            if response.status_code == 200:
                print("Post updated successfully.")
            else:
                print(f"Failed to update post. Response: {response.status_code}, {response.text}")

if __name__ == "__main__":
    fetch_and_analyze_images()
