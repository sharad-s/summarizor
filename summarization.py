import openai
import tiktoken
import configparser

APIKEY = 'sk-XXX'
MAX_TOKENS = 4096
SUMMARY_PREFIX_LENGTH = 150
OVERLAP_SIZE = 500

# Load the configuration
config = configparser.ConfigParser()
config.read('config.ini')
APIKEY = config['DEFAULT']['APIKEY']

openai.api_key = APIKEY
enc = tiktoken.get_encoding("cl100k_base")

def tokens_in_text(text):
    return len(list(enc.encode(text)))

def split_text_into_chunks(text):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if tokens_in_text(current_chunk + word) <= (MAX_TOKENS - SUMMARY_PREFIX_LENGTH):
            current_chunk += word + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def summarize_text_with_openai_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You will be provided a chunk of text from audio transcription of a video. Break down the text into logical sections, then thoroughly summarize each section, capture all important points and nuances. Reply in in proper markdown."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']
