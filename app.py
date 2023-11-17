import eel
import json
from playwright.sync_api import sync_playwright
import openai
import os

eel.init('web')
openai.api_key = os.getenv('OPENAI_API_KEY')

with open('prompts.json', 'r') as file:
    prompts = json.load(file)

def get_prompt(task_name):
    return prompts.get(task_name, {}).get('prompt', '')

def analyze_image_with_gpt4_vision(image_url, task_name):
    prompt = get_prompt(task_name)
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

@eel.expose
def perform_automated_tasks():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto('https://www.linkedin.com/login')
        page.fill('input[name="session_key"]', 'YOUR_USERNAME')
        page.fill('input[name="session_password"]', 'YOUR_PASSWORD')
        page.click('button[type="submit"]')
        page.wait_for_navigation()

        page.goto('https://www.linkedin.com/jobs')
        page.fill('input[aria-label="Search by title, skill, or company"]', 'Software Engineer')
        page.fill('input[aria-label="City, state, or zip code"]', 'New York')
        page.click('button[aria-label="Search"]')
        page.wait_for_selector('div.jobs-search-results')

        page.click('div.jobs-search-results a.job-card-container--clickable')
        page.wait_for_selector('div.jobs-details-top-card')

        page.screenshot(path='job_listing.png')
        analysis_result = analyze_image_with_gpt4_vision('job_listing.png', 'analyze_job_listing')
        eel.display_analysis_result(analysis_result)

        browser.close()

eel.start('index.html', size=(1920, 1080))
