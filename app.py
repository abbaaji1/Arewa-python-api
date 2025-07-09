from flask import Flask, request, jsonify
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route("/api/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"success": False, "message": "No URL provided."}), 400

    try:
        command = [
            "yt-dlp",
            "-j",
            "--user-agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        info = eval(result.stdout)

        formats = info.get("formats", [])
        download_links = []

        for f in formats:
            if f.get("url") and f.get("ext") == "mp4":
                download_links.append({
                    "url": f["url"],
                    "quality": f.get("format_note", "unknown")
                })

        if download_links:
            return jsonify({"success": True, "links": download_links})
        else:
            return jsonify({"success": False, "message": "No downloadable MP4 links found."})

    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": "Error fetching video info.", "error": str(e)})
    except Exception as e:
        return jsonify({"success": False, "message": "Server error.", "error": str(e)})

@app.route("/", methods=["GET"])
def home():
    return "Python Video Downloader API is live!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
