import subprocess
import os
import configparser

# Load the configuration
config = configparser.ConfigParser()
config.read('config.ini')
FFMPEG = config['DEFAULT']['FFMPEG_PATH']

def convert_video_to_audio(input_video, output_directory):
    output_audio = os.path.join(output_directory, os.path.basename(
        os.path.splitext(input_video)[0]) + '.mp3')
    cmd = [FFMPEG, "-i",
           input_video, "-vn", "-q:a", "0", output_audio]
    subprocess.run(cmd)
    return output_audio
