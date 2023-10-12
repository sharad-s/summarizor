import logging
import time
import os
import subprocess
import openai

import configparser

# Load the configuration
config = configparser.ConfigParser()
config.read('config.ini')
FFMPEG = config['DEFAULT']['FFMPEG_PATH']

def split_audio_into_chunks(audio_file, uuid_str):
    logging.info(f"Splitting {audio_file} into chunks using ffmpeg...")
    start_time = time.time()

    chunk_duration_seconds = 600
    chunk_directory = os.path.join("tmp", uuid_str, "chunks")
    os.makedirs(chunk_directory, exist_ok=True)
    chunk_filename_template = os.path.join(chunk_directory, "chunk_%03d.mp3")
    cmd = [FFMPEG, "-i", audio_file, "-f", "segment",
           "-segment_time", str(chunk_duration_seconds), "-c", "copy", chunk_filename_template]
    subprocess.run(cmd)
    chunks = [os.path.join(chunk_directory, f) for f in os.listdir(
        chunk_directory) if f.startswith("chunk_")]

    logging.info(
        f"Finished splitting in {time.time() - start_time:.2f} seconds.")
    return sorted(chunks)


def transcribe_audio_with_openai_whisper_api(audio_file):
    logging.info(f"Transcribing {audio_file} using Whisper API...")
    start_time = time.time()

    with open(audio_file, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)

    logging.info(
        f"Finished transcribing in {time.time() - start_time:.2f} seconds.")
    return transcript["text"]
