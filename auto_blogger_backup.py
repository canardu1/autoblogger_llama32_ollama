import requests
import json

# Configuration
WORDPRESS_URL = input('Enter your WordPress site URL (e.g., https://example.com/wp-json/wp/v2/posts): ')

# Function to generate articles using Ollama
# ... (rest of the code omitted for brevity)

# Function to format content
def format_content(content):
    lines = content.split('\n')
    formatted_lines = []
    in_h1 = False
    in_h2 = False
    in_h3 = False

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
            
            # Handle bold text
            if '**' in line:
                parts = line.split('**')
                formatted_line = ''.join(
                    f'<b>{part}</b>' if i % 2 else part for i, part in enumerate(parts)
                )
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(line)

    # Close any remaining open tags
    if in_h1:
        formatted_lines.append('</h1>')
    if in_h2:
        formatted_lines.append('</h2>')
    if in_h3:
        formatted_lines.append('</h3>')

    content = '<br>'.join(formatted_lines)
    return content

# Function to publish articles to WordPress
# ... (rest of the code omitted for brevity)
