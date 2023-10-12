import subprocess
import os
import glob
import hashlib

import configparser

# Load the configuration
config = configparser.ConfigParser()
config.read('config.ini')
YT_DLP_PATH = config['DEFAULT']['YT_DLP_PATH']

def download_youtube_audio(url, output_directory):
    temp_audio = os.path.join(output_directory, "temp_audio.%(ext)s")
    cmd = [YT_DLP_PATH, url, "--extract-audio", "--audio-format", "mp3", "-o", temp_audio]
    subprocess.run(cmd)
    
    # Rename the downloaded file to its title
    downloaded_files = glob.glob(os.path.join(output_directory, "temp_audio.*"))
    if downloaded_files:
        final_audio_path = os.path.join(output_directory, os.path.basename(os.path.splitext(downloaded_files[0])[0]) + '.mp3')
        os.rename(downloaded_files[0], final_audio_path)
        return final_audio_path
    else:
        raise Exception("Failed to download audio from YouTube.")
    

def is_youtube_url(url):
    # Simple check to determine if the input is a YouTube URL
    return "youtube.com" in url or "youtu.be" in url



def get_video_id_from_url(url):
    # Extract video ID from YouTube URL
    if "youtu.be" in url:
        return url.split('/')[-1]
    elif "youtube.com" in url:
        return url.split('v=')[-1].split('&')[0]
    else:
        return None

def get_sanitized_filename_from_url(url):
    video_id = get_video_id_from_url(url)
    if video_id:
        return video_id + ".mp3"
    else:
        # If we can't extract the video ID, use a hash of the URL
        return hashlib.md5(url.encode()).hexdigest() + ".mp3"
