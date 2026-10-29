from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import urllib.parse

app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return send_file('index.html')
@app.route('/download', methods=['POST'])
def download_media():
    data = request.get_json()
    raw_url = data.get('url')
    download_type = data.get('type', 'video')  # 'video' ya 'audio'
    
    if not raw_url:
        return jsonify({'error': 'URL missing hai'}), 400

    # URL clean karna
    parsed_url = urllib.parse.urlparse(raw_url)
    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    output_base = 'downloaded_media'
    
    # Purane files saaf karna
    for ext in ['.mp4', '.mp3', '.m4a', '.webm', '.opus', '.mkv']:
        if os.path.exists(output_base + ext):
            try:
                os.remove(output_base + ext)
            except:
                pass

    ydl_opts = {
        'outtmpl': output_base,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    }

    if download_type == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'best/bestvideo+bestaudio'
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([clean_url])
            
            target_ext = '.mp3' if download_type == 'audio' else '.mp4'
            filename = output_base + target_ext
            
            # Agar direct extension nahi mila toh folder me file dhoondna
            if not os.path.exists(filename):
                for file in os.listdir('.'):
                    if file.startswith('downloaded_media'):
                        filename = file
                        break

            if os.path.exists(filename):
                download_name = "yuvraj_audio.mp3" if download_type == 'audio' else "yuvraj_video.mp4"
                return send_file(filename, as_attachment=True, download_name=download_name)
            else:
                return jsonify({'error': 'File generate nahi ho payi!'}), 500
            
    except Exception as e:
        print(f"Error Details: {str(e)}")
        return jsonify({'error': str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Yuvraj Server Chalu Ho Gaya Hai on port {port}!")
    app.run(host='0.0.0.0', port=port)
