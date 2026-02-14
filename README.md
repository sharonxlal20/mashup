# YouTube Mashup Generator

**Name:** Vansh Singla  
**Roll No:** 102303975  

This project implements a complete Mashup system consisting of:

- Command Line Mashup Program
- Web Service Mashup Generator with Email Delivery

Live Website:  
https://mashup-xwsv.onrender.com/

The system downloads multiple YouTube songs of a given singer, extracts audio, trims them, merges them into a single mashup file, and delivers the final output.

---

## Program 1 – Command Line Mashup

**File:** `102303975.py`

### Features
- Downloads N videos of a given singer from YouTube
- Converts videos to MP3 audio
- Cuts first Y seconds from each audio
- Merges all trimmed audios into one final mashup file
- Validates user inputs
- Handles exceptions properly

### Usage

### Input Constraints
- NumberOfVideos ≥ 10
- AudioDuration ≥ 20 seconds
- Output file must end with `.mp3`
- Correct number of parameters required

If invalid input is provided, appropriate error messages are displayed.

### Required Packages


FFmpeg must be installed for audio conversion.

---

## Program 2 – Web Service Mashup Generator

**File:** `app.py`  
**Frontend:** `templates/index.html`

Built using Flask and deployed on Render.

Production URL:  
https://mashup-xwsv.onrender.com/

### Features
User inputs:
- Singer Name
- Number of Videos
- Duration (seconds)
- Email ID

System capabilities:
- Validates integer inputs and email format
- Generates mashup
- Creates ZIP file
- Sends ZIP file via email
- Allows direct download from browser

---

## Running Locally

### Install Dependencies


### Install FFmpeg
https://ffmpeg.org/download.html

Verify installation:

---

## Email Configuration

Create a `.env` file in the project root:


For Gmail, use an **App Password**.

---

## Run Web Application


Server runs at: http://127.0.0.1:5000


---

## Processing Flow

1. Download videos
2. Convert to MP3
3. Cut first Y seconds
4. Merge into single mashup
5. Create ZIP file
6. Send email
7. Provide download link

---

## Technologies Used

- Python
- Flask
- yt-dlp
- pydub
- SMTP
- FFmpeg
- Render (Cloud Deployment)

---

## Notes

- CLI minimum videos: 10
- Web minimum videos: 2
- Minimum duration: 20 seconds
- Internet connection required
- FFmpeg required for audio processing

---

## Author

**Vansh Singla**  
**Roll No:** 102303975
