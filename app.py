from flask import Flask, request, jsonify
from ollama_service import generate_article
from wordpress_service import publish_article

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    num_articles = data.get('num_articles', 1)
    articles = []
    for _ in range(num_articles):
        article = generate_article()
        articles.append(article)
        publish_article(article)
    return jsonify({'status': 'success', 'articles': articles})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
