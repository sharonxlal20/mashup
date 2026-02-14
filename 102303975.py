import sys
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment

def validate_inputs(args):
    if len(args) != 5:
        print("Usage: python 102303975.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        print('Example: python 102303975.py "Sharry Maan" 20 20 102303975-output.mp3')
        sys.exit(1)

    singer_name = args[1]
    try:
        num_videos = int(args[2])
    except ValueError:
        print("Error: NumberOfVideos must be a positive integer.")
        sys.exit(1)

    try:
        audio_duration = int(args[3])
    except ValueError:
        print("Error: AudioDuration must be a positive integer.")
        sys.exit(1)

    output_file = args[4]

    if num_videos < 10:
        print("Error: NumberOfVideos must be at least 10.")
        sys.exit(1)

    if audio_duration < 20:
        print("Error: AudioDuration must be at least 20 seconds.")
        sys.exit(1)

    if not output_file.endswith(".mp3"):
        print("Error: OutputFileName must end with .mp3")
        sys.exit(1)

    return singer_name, num_videos, audio_duration, output_file


def download_videos(singer_name, num_videos, download_dir):
    print(f"Searching and downloading {num_videos} videos of '{singer_name}' from YouTube...")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    search_query = f"ytsearch{num_videos}:{singer_name} songs"

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
    except Exception as e:
        print(f"Error downloading videos: {e}")
        sys.exit(1)

    downloaded_files = [
        os.path.join(download_dir, f)
        for f in os.listdir(download_dir)
        if os.path.isfile(os.path.join(download_dir, f)) and not f.startswith("._")
    ]

    if not downloaded_files:
        print("Error: No videos were downloaded. Check the singer name and try again.")
        sys.exit(1)

    print(f"Successfully downloaded {len(downloaded_files)} files.")
    return downloaded_files


def convert_to_audio(downloaded_files, audio_dir):
    print("Converting downloaded files to audio (.mp3)...")
    audio_files = []

    for filepath in downloaded_files:
        try:
            audio = AudioSegment.from_file(filepath)
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            audio_path = os.path.join(audio_dir, f"{base_name}.mp3")
            audio.export(audio_path, format="mp3")
            audio_files.append(audio_path)
            print(f"  Converted: {base_name}.mp3")
        except Exception as e:
            print(f"  Warning: Could not convert {os.path.basename(filepath)}: {e}")

    if not audio_files:
        print("Error: No files could be converted to audio.")
        sys.exit(1)

    print(f"Successfully converted {len(audio_files)} files to audio.")
    return audio_files


def cut_audio(audio_files, duration_sec):
    print(f"Cutting first {duration_sec} seconds from each audio file...")
    duration_ms = duration_sec * 1000
    cut_segments = []

    for filepath in audio_files:
        try:
            audio = AudioSegment.from_mp3(filepath)
            cut_segment = audio[:duration_ms]
            cut_segments.append(cut_segment)
            print(f"  Cut: {os.path.basename(filepath)}")
        except Exception as e:
            print(f"  Warning: Could not cut {os.path.basename(filepath)}: {e}")

    if not cut_segments:
        print("Error: No audio segments could be cut.")
        sys.exit(1)

    print(f"Successfully cut {len(cut_segments)} audio segments.")
    return cut_segments


def merge_audios(cut_segments, output_file):
    print("Merging all audio segments into a single file...")

    try:
        merged = cut_segments[0]
        for segment in cut_segments[1:]:
            merged += segment

        merged.export(output_file, format="mp3")
        print(f"Mashup saved to: {output_file}")
    except Exception as e:
        print(f"Error merging audio files: {e}")
        sys.exit(1)


def main():
    singer_name, num_videos, audio_duration, output_file = validate_inputs(sys.argv)

    download_dir = "downloads"
    audio_dir = "audios"
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    # Step 1: Download videos from YouTube
    downloaded_files = download_videos(singer_name, num_videos, download_dir)

    # Step 2: Convert to audio
    audio_files = convert_to_audio(downloaded_files, audio_dir)

    # Step 3: Cut first Y seconds from each audio
    cut_segments = cut_audio(audio_files, audio_duration)

    # Step 4: Merge all cut segments into one output file
    merge_audios(cut_segments, output_file)

    print("Mashup created successfully!")


if __name__ == "__main__":
    main()