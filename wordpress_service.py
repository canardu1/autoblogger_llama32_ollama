import requests

WORDPRESS_URL = 'https://your-wordpress-site.com/wp-json/wp/v2/posts'
WORDPRESS_USER = 'your_username'
WORDPRESS_PASSWORD = 'your_application_password'

def publish_article(article):
    headers = {'Content-Type': 'application/json'}
    data = {
        'title': 'Auto-generated Article',
        'content': article,
        'status': 'publish'
    }
    response = requests.post(WORDPRESS_URL, json=data, headers=headers, auth=(WORDPRESS_USER, WORDPRESS_PASSWORD))
    return response.json()
