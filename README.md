# autoblogger_llama32_ollama
# Autoblogger
This project is an autoblogger that uses Ollama to automatically create and publish articles on a WordPress blog using a Flask interface.

## Setup

1. Clone the repository.
2. Install the required packages:
   pip install -r requirements.txt

The prompt for the creation of the article is in the main file auto_blogger.py, you can modify the prompt and now is set to create the articles in Italian (i will add an option for language in a later update).
The app will ask for your wordpress site URL (e.g., https://example.com/)
For your wordpress username and for your wordpress application password (you'll need to create one in wordpress under profile)
Then it will ask for the niche you want your articles to be and the number of words every article should contain.

After this it will ask for the list of articles you want to create in a form like this: title | description

Once you double press enter the app will start to download the images and compress them from pexels.com
You can use these dowloaded images in your articles.

The script will start to write the articles and will expand them until the desired word count is reached.

Since the AI is not perfect the articles will need to be reviewed, but they represent a good starting point.
There are still some issues with the FAQs (too many) and with the expansion feature.
