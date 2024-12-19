import requests
import json
import re
import os
from PIL import Image

# Configuration
WORDPRESS_BASE_URL = input('Enter your WordPress site base URL (e.g., https://example.com/): ')
WORDPRESS_USER = input('Enter your WordPress username: ')
WORDPRESS_PASSWORD = input('Enter your WordPress application password: ')

# Pexels API Configuration
PEXELS_API_KEY = 'f9JmLdm656RDtK3ChU2yWvhWFAlcZx17L71Jbh7aDzdOG42gysNIvur3'
PEXELS_API_URL = 'https://api.pexels.com/v1/search'

# Function to translate text using Ollama API
def translate_with_ollama(text):
    llama_version = '3.2'
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={'prompt': f'Translate the following text to English: {text}', 'model': f'llama{llama_version}'},
        stream=True
    )
    translation_parts = []
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                part = json.loads(line.decode('utf-8'))
                translation_parts.append(part['response'])
        return ''.join(translation_parts).strip()  # Combine all parts
    else:
        print(f'Error translating text: {response.status_code} - {response.text}')
        return text  # Return original text if translation fails

# Generalized prompt for article generation
PROMPT = """
Using markdown formatting, act as an Expert Article Writer. Write a detailed, long-form, 100% unique, and creative SEO article based on the provided niche, article title, and description. Follow these guidelines:

1. Article Structure:
   - Start with a compelling introduction that outlines the main topic and its relevance to the audience.
   - Use clear and engaging headings and subheadings to organize the content logically.
   - Avoid creating multiple sections with the same title, such as 'Conclusion'. Instead, ensure that each section has a unique title.
   - Don't use "introductions" or "conclusions" as section titles.
   - When prompted to expand the article, continue the story from where it left off.
   - Do not create FAQs
   - Don't repeat the same information multiple times in the article.
   - Don't repeat the same image multiple times in the article.

2. Content Requirements:
   - Each section should provide valuable insights, practical tips, and relevant examples.
   - Aim for a word count of at least 3000 words, with each section being informative and engaging.
   - Incorporate relevant keywords naturally throughout the article to enhance SEO.

3. Readability and Engagement:
   - Write in a formal yet engaging tone that resonates with the target audience.
   - Use short paragraphs, bullet points, and lists to improve readability.

4. SEO Best Practices:
   - Ensure that the article is optimized for search engines by using appropriate keywords in headings, subheadings, and throughout the content.
   - Avoid keyword stuffing; maintain a natural flow of language.
   - Use small paragraphs, bullet points, and lists to improve readability.
   - Use relevant images to enhance the article's visual appeal and improve user engagement.
   - Use transition phrases, such as 'In this article,' to guide the reader's attention to different sections.
   - Use clear and concise language to avoid long sentences.
   - Use simple terms and avoid complex jargon.
   - Use a clear call-to-action at the end of the article to encourage readers to take action.
   - Use small phrases and avoid long sentences.
   - Use active forms and avoid passive forms.

Make sure the content is plagiarism-free and can easily pass AI detection tools. Focus on providing accurate, relevant, and helpful information to readers while showcasing expertise in the niche.
"""

# Function to search for images on Pexels
def search_images(query):
    # Translate the query to English using Ollama
    english_query = translate_with_ollama(query)
    headers = {'Authorization': PEXELS_API_KEY}
    params = {'query': english_query, 'per_page': 5}  # Adjust the number of images as needed
    response = requests.get(PEXELS_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        photos = response.json()['photos']  # Return the list of photos
        print(f'Fetched {len(photos)} images from Pexels for query: {english_query}.')  # Message showing number of images fetched
        return photos
    else:
        print(f'Error fetching images from Pexels: {response.status_code} - {response.text}')
        return []

# Function to download an image
def download_image(image_url, title, index):
    response = requests.get(image_url)
    if response.status_code == 200:
        # Extract the image extension from the URL
        file_extension = image_url.split('.')[-1]
        file_name = f'{title}_{index}.{file_extension}'  # Append index for uniqueness
        file_path = os.path.join('images', file_name)
        with open(file_path, 'wb') as img_file:
            img_file.write(response.content)
        print(f'Downloaded image: {file_name}')  # Log the downloaded image file name
        compress_image(file_path)  # Compress the image after downloading
        return file_path
    else:
        print(f'Error downloading image: {response.status_code} - {response.text}')
        return None

# Function to compress images
def compress_image(image_path):
    max_size = 500 * 1024  # 500 KB
    with Image.open(image_path) as img:
        # Check the original size
        if os.path.getsize(image_path) > max_size:
            quality = 85  # Start with a quality of 85
            while True:
                # Save the image with the specified quality
                img.save(image_path, format='JPEG', quality=quality)
                if os.path.getsize(image_path) <= max_size or quality <= 10:
                    break
                quality -= 5  # Decrease quality in steps of 5
            print(f'Compressed image: {image_path} to {os.path.getsize(image_path) / 1024:.2f} KB')
        else:
            print(f'Image {image_path} is already under 500 KB.')

# Function to process and download all images
def process_images(images, title):
    downloaded_images = []
    for index, img in enumerate(images):
        image_url = img['src']['original']
        downloaded_image_path = download_image(image_url, title, index)
        if downloaded_image_path:
            downloaded_images.append(downloaded_image_path)
    return downloaded_images

# Function to upload an image to WordPress
def upload_image_to_wordpress(image_path, title):
    with open(image_path, 'rb') as img:
        response = requests.post(
            WORDPRESS_MEDIA_URL,
            auth=(WORDPRESS_USER, WORDPRESS_PASSWORD),
            headers={
                'Content-Type': 'image/jpeg',
                'Content-Disposition': f'attachment; filename="{os.path.basename(image_path)}"'
            },
            files={'file': (title, img)}
        )
    if response.status_code == 201:
        return response.json()['id']  # Return the attachment ID
    else:
        return None

# Function to generate an article using Ollama
def generate_article_with_ollama(niche, word_count, title, meta_description):
    llama_version = '3.2'
    keywords = generate_keywords_from_niche(niche)
    context = ''  # Set context to an empty string since we're not fetching existing posts
    prompt = PROMPT + f'\n\nNiche: {niche}\nTitle: {title}\nDescription: {meta_description}'
    response = requests.post('http://localhost:11434/api/generate', json={'prompt': prompt, 'model': f'llama{llama_version}'}, stream=True)

    if response.status_code == 200:
        full_content = ""
        for line in response.iter_lines():
            if line:  # Filter out empty lines
                data = json.loads(line.decode('utf-8'))
                full_content += data['response']  # Concatenate the generated text

        # Check if the generated content meets the word count requirement
        while len(full_content.split()) < word_count:
            print(f"Generated article is too short ({len(full_content.split())} words). Expanding...")
            last_generated_content = full_content
            expansion_prompt = f'Continue the following article:\n\n{last_generated_content}'
            response = requests.post('http://localhost:11434/api/generate', json={'prompt': expansion_prompt, 'model': f'llama{llama_version}'}, stream=True)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:  # Filter out empty lines
                        data = json.loads(line)
                        full_content = full_content + data['response']  # Expand the existing content
            else:
                print(f"Error during expansion: {response.status_code} - {response.text}")
                break

        return {
            'content': full_content,  # Use the full concatenated content
            'title': title,
            'meta_description': meta_description,
            'keywords': keywords
        }
    else:
        # Print the response for debugging
        print(f"Error: {response.status_code} - {response.text}")
        # Handle error response
        return {
            'content': 'Non è stato possibile generare l\'articolo.',  # Escaped single quote
            'title': f'Errore nella generazione dell\'articolo su {niche}',  # Escaped single quote
            'meta_description': 'Errore nella generazione del contenuto.',
            'keywords': []
        }

def generate_keywords_from_niche(niche):
    llama_version = '3.2'
    # Call Ollama API to generate relevant keywords based on the niche
    response = requests.post('http://localhost:11434/api/generate', json={'prompt': f'Generate keywords for the niche: {niche}', 'model': f'llama{llama_version}'}, stream=True)
    keywords = []
    print('Response from Ollama:')  # Debugging line to print raw response
    for line in response.iter_lines():
        if line:  # Filter out empty lines
            data = json.loads(line)
            keywords.append(data['response'])
            if data.get('done'):
                break
    return ' '.join(keywords).strip().split(',')

# Function to set up WordPress URLs
def setup_wordpress_urls(base_url):
    global WORDPRESS_URL, WORDPRESS_MEDIA_URL
    WORDPRESS_URL = f'{base_url}wp-json/wp/v2/posts'
    WORDPRESS_MEDIA_URL = f'{base_url}wp-json/wp/v2/media'

# Call this function with the base URL
setup_wordpress_urls(WORDPRESS_BASE_URL)

# Function to format content
def format_content(content):
    lines = content.split('\n')
    formatted_lines = []
    in_h1 = False
    in_h2 = False
    in_h3 = False
    in_list = False

    for line in lines:
        # Check for heading levels
        if line.startswith('# '):
            if in_h2:
                formatted_lines.append('</h2>')
            if in_h3:
                formatted_lines.append('</h3>')
            formatted_lines.append('<h1>' + line[2:] + '</h1>')
            in_h1 = True
            in_h2 = False
            in_h3 = False
        elif line.startswith('## '):
            if in_h1:
                formatted_lines.append('</h1>')
            if in_h3:
                formatted_lines.append('</h3>')
            formatted_lines.append('<h2>' + line[3:] + '</h2>')
            in_h1 = False
            in_h2 = True
            in_h3 = False
        elif line.startswith('### '):
            if in_h1:
                formatted_lines.append('</h1>')
            if in_h2:
                formatted_lines.append('</h2>')
            formatted_lines.append('<h3>' + line[4:] + '</h3>')
            in_h1 = False
            in_h2 = False
            in_h3 = True
        elif line.startswith('* '):
            if not in_list:
                formatted_lines.append('<ul>')  # Start an unordered list
                in_list = True
            formatted_lines.append('<li>' + line[2:].strip() + '</li>')  # Add list item
        else:
            # Close any open heading tags
            if in_h1:
                formatted_lines.append('</h1>')
                in_h1 = False
            if in_h2:
                formatted_lines.append('</h2>')
                in_h2 = False
            if in_h3:
                formatted_lines.append('</h3>')
                in_h3 = False
            
            # Close the list if it was open
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            
            # Handle bold text
            if '**' in line:
                parts = line.split('**')
                formatted_line = ''.join(
                    f'<b>{part}</b>' if i % 2 else part for i, part in enumerate(parts)
                )
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(line.strip())  # Remove leading/trailing whitespace

    # Close any remaining open tags
    if in_h1:
        formatted_lines.append('</h1>')
    if in_h2:
        formatted_lines.append('</h2>')
    if in_h3:
        formatted_lines.append('</h3>')
    if in_list:
        formatted_lines.append('</ul>')  # Close the list if it was open

    content = '<br>'.join(formatted_lines)
    return content

# Function to publish articles to WordPress
def publish_to_wordpress(title, content, meta_description, attachment_ids=None):
    content = format_content(content)
    post = {
        'title': title,
        'content': content,
        'status': 'draft',  # Change this to 'draft' to save as draft
        'format': 'standard',
        'meta': {
            '_yoast_wpseo_metadesc': meta_description  # Updated key for Yoast SEO
        }
    }
    if attachment_ids:
        post['featured_media'] = attachment_ids[0]  # Attach the first image if available
        for attachment_id in attachment_ids[1:]:
            post[f'media[{attachment_id}]'] = attachment_id  # Add additional images

    response = requests.post(WORDPRESS_URL, auth=(WORDPRESS_USER, WORDPRESS_PASSWORD), json=post)
    return response.status_code, response.json()

# Main function
if __name__ == '__main__':
    niche = input('Enter the niche for the articles: ')
    word_count = int(input('Enter the desired word count for all articles: '))
    print('Enter the titles and descriptions (format: Title|Description). Press Enter twice to finish input:')
    input_data = []
    while True:
        line = input()  # Read lines until an empty line is entered
        if line:
            input_data.append(line)
        else:
            break

    for line in input_data:
        parts = line.split('|')  # Split by pipe character
        if len(parts) >= 2:
            title = parts[0].strip()
            meta_description = parts[1].strip()

            # Search for relevant images
            images = search_images(title)
            if images:
                # Process and download all images
                downloaded_images = process_images(images, title)
                # Upload all downloaded images
                attachment_ids = []
                for image_path in downloaded_images:
                    attachment_id = upload_image_to_wordpress(image_path, title)
                    if attachment_id:
                        attachment_ids.append(attachment_id)

            article = generate_article_with_ollama(niche, word_count, title, meta_description)
            print(f'Generated article for title: {title}')

            # Publish the article immediately after generation
            status_code, response = publish_to_wordpress(article['title'], article['content'], article['meta_description'], attachment_ids)
            if status_code == 201:
                print(f'Article published successfully: {article["title"]}')
            else:
                print(f'Error publishing article: {article["title"]}, Status Code: {status_code}')
        else:
            print('Invalid input format. Please provide Title and Description separated by pipes.')

