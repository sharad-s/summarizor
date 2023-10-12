import openai
import argparse
import os
import tiktoken 
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

# Setup your OpenAI API key
openai.api_key = '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'

MAX_TOKENS = 4096
SUMMARY_PREFIX_LENGTH = 150
OVERLAP_SIZE = 500

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
            {"role": "system", "content": "You are a helpful assistant. You will be provided a chunk of text from audio transcription of a video. Break down the text into logical sections, then thoroughly summarize each section, capture all important points and nuances."},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

def main():
    parser = argparse.ArgumentParser(description="Summarize a text file using OpenAI's GPT API")
    parser.add_argument("input_file", metavar="INPUT_TXT", help="Input text file to be summarized")
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        text = f.read()

    logging.info(f"Splitting the text into chunks...")
    chunks = split_text_into_chunks(text)

    logging.info(f"Number of chunks to be summarized: {len(chunks)}")
    
    summarized_chunks = []
    for idx, chunk in enumerate(chunks, 1):
        logging.info(f"Summarizing chunk {idx}/{len(chunks)} (Size: {tokens_in_text(chunk)} tokens)...")
        summarized_chunk = summarize_text_with_openai_gpt(chunk)
        summarized_chunks.append(summarized_chunk)

    combined_summary = summarized_chunks[0]
    for i in range(1, len(summarized_chunks)):
        current_chunk = summarized_chunks[i]
        combined_summary += ' '.join(current_chunk.split()[3:])

    output_filename = os.path.splitext(args.input_file)[0] + "_summary.txt"
    with open(output_filename, "w") as f:
        f.write(combined_summary)

    logging.info(f"Summary written to: {output_filename}")

if __name__ == "__main__":
    main()
