import os
import re
import sys
import shutil
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory
from yt_dlp import YoutubeDL
from pydub import AudioSegment

load_dotenv()

app = Flask(__name__)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── SMTP Configuration (loaded from .env) ───────────────────────────
SMTP_EMAIL = os.environ.get("SENDER_EMAIL", "")
SMTP_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))


def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)


def download_videos(singer_name, num_videos, download_dir):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(download_dir, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    search_query = f"ytsearch{num_videos}:{singer_name} songs"
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([search_query])

    files = [
        os.path.join(download_dir, f)
        for f in os.listdir(download_dir)
        if os.path.isfile(os.path.join(download_dir, f)) and not f.startswith("._")
    ]
    return files


def convert_to_audio(downloaded_files, audio_dir):
    audio_files = []
    for filepath in downloaded_files:
        try:
            audio = AudioSegment.from_file(filepath)
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            audio_path = os.path.join(audio_dir, f"{base_name}.mp3")
            audio.export(audio_path, format="mp3")
            audio_files.append(audio_path)
        except Exception:
            continue
    return audio_files


def cut_audio(audio_files, duration_sec):
    duration_ms = duration_sec * 1000
    segments = []
    for filepath in audio_files:
        try:
            audio = AudioSegment.from_mp3(filepath)
            segments.append(audio[:duration_ms])
        except Exception:
            continue
    return segments


def merge_audios(segments, output_path):
    merged = segments[0]
    for seg in segments[1:]:
        merged += seg
    merged.export(output_path, format="mp3")


def create_zip(mp3_path, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(mp3_path, os.path.basename(mp3_path))


def send_email(to_email, zip_path):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "SMTP credentials not configured on the server."

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Your Mashup is Ready!"

    with open(zip_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(zip_path)}")
    msg.attach(part)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mashup", methods=["POST"])
def mashup():
    singer_name = request.form.get("singer_name", "").strip()
    email = request.form.get("email", "").strip()

    try:
        num_videos = int(request.form.get("num_videos", 0))
        duration = int(request.form.get("duration", 0))
    except ValueError:
        return render_template("index.html", error="Number of videos and duration must be integers.")

    if not singer_name:
        return render_template("index.html", error="Singer name is required.")
    if num_videos < 2:
        return render_template("index.html", error="Number of videos must be at least 2.")
    if duration < 20:
        return render_template("index.html", error="Duration must be at least 20 seconds.")
    if not is_valid_email(email):
        return render_template("index.html", error="Please enter a valid email address.")

    # Create unique working dirs
    import uuid
    job_id = uuid.uuid4().hex[:8]
    download_dir = os.path.join(OUTPUT_DIR, f"{job_id}_downloads")
    audio_dir = os.path.join(OUTPUT_DIR, f"{job_id}_audios")
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    mp3_filename = f"{job_id}-mashup.mp3"
    zip_filename = f"{job_id}-mashup.zip"
    mp3_path = os.path.join(OUTPUT_DIR, mp3_filename)
    zip_path = os.path.join(OUTPUT_DIR, zip_filename)

    try:
        # Step 1: Download
        downloaded = download_videos(singer_name, num_videos, download_dir)
        if not downloaded:
            return render_template("result.html", success=False, error="No videos found. Check the singer name.")

        # Step 2: Convert to audio
        audio_files = convert_to_audio(downloaded, audio_dir)
        if not audio_files:
            return render_template("result.html", success=False, error="Failed to convert videos to audio.")

        # Step 3: Cut
        segments = cut_audio(audio_files, duration)
        if not segments:
            return render_template("result.html", success=False, error="Failed to cut audio files.")

        # Step 4: Merge
        merge_audios(segments, mp3_path)

        # Step 5: Zip
        create_zip(mp3_path, zip_path)

        # Step 6: Send email
        email_sent, email_error = send_email(email, zip_path)

        # Cleanup temp dirs
        shutil.rmtree(download_dir, ignore_errors=True)
        shutil.rmtree(audio_dir, ignore_errors=True)

        return render_template(
            "result.html",
            success=True,
            singer_name=singer_name,
            num_videos=num_videos,
            duration=duration,
            email=email,
            email_sent=email_sent,
            email_error=email_error,
            audio_url=f"/output/{mp3_filename}",
            zip_url=f"/output/{zip_filename}",
        )

    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        shutil.rmtree(audio_dir, ignore_errors=True)
        return render_template("result.html", success=False, error=str(e))


@app.route("/output/<filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
