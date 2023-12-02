# gptocr
a script that uses openai's gpt-4 preview to generate alt-text for images on mastodon.

This script works based on the work of @cbh123's work - specifically his 'narrator' project (https://github.com/cbh123/narrator.

This script is designed to be run after-the-fact, if you're midstream in scramjetting the dankest memes into orbit and moving too fast to add alt-text, or if you're on a mobile and adding alt text means adding 10x more text to your three-word-post, this script is for you. At current, it fetches the most recent 30 statuses, checks them to see if they have images, if they do it checks for alt text. If there is no alt text present, it fetches the image, hands it to gpt-4-preview for a description, then reuploads the image with the new description. 

open to pull requests for stuff like 'handling video' or wiring to make it easy to run as a cronjob somewhere etc.
