from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
from yt_dlp import YoutubeDL
from pathlib import Path

app = Flask(__name__)

# Dynamically get the Downloads folder path
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")

# Ensure the Downloads folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    # Get the YouTube URL from the form data
    url = request.form.get("youtube_url")
    if not url:
        return redirect(url_for("index"))

    # Configure yt-dlp options
    download_path = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")
    options = {
        'format': 'bestaudio/best',
        'outtmpl': download_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        # Use yt-dlp to download and process the YouTube video
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the output file name (after conversion)
            file_name = f"{info['title']}.mp3"
        
        # Return song details and the file name for the front-end
        return jsonify({
            'file_name': file_name,
            'song_name': info['title'],
            'duration': info.get('duration', 'Unknown Duration'),  # Optional: Add song duration
            'uploader': info.get('uploader', 'Unknown Uploader'),  # Optional: Add uploader name
            'thumbnail': info.get('thumbnail', '')  # Add thumbnail UR
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/download-file/<file_name>")
def download_file(file_name):
    # Construct the file path
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
