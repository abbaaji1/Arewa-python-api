from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route("/api/download", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"success": False, "message": "No URL provided."}), 400

    try:
        # Run yt-dlp with better options
        command = ["yt-dlp", "--no-playlist", "-j", url]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check if yt-dlp returned error
        if result.returncode != 0:
            return jsonify({
                "success": False,
                "message": "Error fetching video info.",
                "error": result.stderr.strip()
            }), 500

        # Parse JSON response from yt-dlp
        info = json.loads(result.stdout)
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

    except json.JSONDecodeError as e:
        return jsonify({
            "success": False,
            "message": "Failed to parse video info.",
            "error": str(e)
        }), 500
    except Exception as e:
        return jsonify({"success": False, "message": "Server error.", "error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "✅ Arewa Python API is live!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
