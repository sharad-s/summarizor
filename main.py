import argparse
import os
import uuid
import logging
import configparser

from video_processing import convert_video_to_audio
from transcription import split_audio_into_chunks, transcribe_audio_with_openai_whisper_api
from summarization import split_text_into_chunks, summarize_text_with_openai_gpt, tokens_in_text
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s')

# Load the configuration
config = configparser.ConfigParser()
config.read('config.ini')

APIKEY = config['DEFAULT']['APIKEY']
FFMPEG_PATH = config['DEFAULT']['FFMPEG_PATH']

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Full combined process")
    parser.add_argument("input_file", metavar="INPUT_VIDEO",
                        help="Input video file to be processed")
    args = parser.parse_args()

    unique_id = str(uuid.uuid4())
    output_directory = os.path.join("out", unique_id)
    os.makedirs(output_directory, exist_ok=True)

    audio_file = convert_video_to_audio(args.input_file, output_directory)

    # Transcribe the audio
    chunks = split_audio_into_chunks(audio_file, unique_id)
    combined_transcription = ""
    for chunk in chunks:
        transcript = transcribe_audio_with_openai_whisper_api(chunk)
        combined_transcription += transcript + "\n\n"

    with open(os.path.join(output_directory, "transcription.txt"), "w") as f:
        f.write(combined_transcription)

    # Summarize
    logging.info(f"Splitting the text into chunks...")
    chunks = split_text_into_chunks(combined_transcription)

    logging.info(f"Number of chunks to be summarized: {len(chunks)}")
    summarized_chunks = []
    for idx, chunk in enumerate(chunks, 1):
        logging.info(
            f"Summarizing chunk {idx}/{len(chunks)} (Size: {tokens_in_text(chunk)} tokens)...")
        summarized_chunk = summarize_text_with_openai_gpt(chunk)
        summarized_chunks.append(summarized_chunk)

    # Combine the summarized chunks
    combined_summary = summarized_chunks[0]
    for i in range(1, len(summarized_chunks)):
        current_chunk = summarized_chunks[i]
        combined_summary += ' '.join(current_chunk.split()[3:])

    output_filename = os.path.join(
        output_directory,  os.path.splitext(args.input_file)[0] + "_summary.txt")

    with open(output_filename, "w") as f:
        f.write(combined_summary)
        logging.info(f"Summary written to: {output_filename}")


if __name__ == "__main__":
    main()
