from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import urllib.parse

app = Flask(__name__)
CORS(app)

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

    # Universal options jo har block ko bypass karegi
    ydl_opts = {
        'outtmpl': output_base,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
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

if __name__ == '__main__':
    print("🚀 Yuvraj Server Chalu Ho Gaya Hai! (http://127.0.0.1:5000)")
    app.run(port=5000, debug=True)