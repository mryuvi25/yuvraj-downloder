from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import urllib.parse
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/download', methods=['POST'])
def download_media():
    try:
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
            'format': 'best',
        }

        if download_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        print(f"📥 Downloading Instagram URL: {clean_url} | Type: {download_type}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([clean_url])
            
            target_ext = '.mp3' if download_type == 'audio' else '.mp4'
            filename = output_base + target_ext
            
            if not os.path.exists(filename):
                for file in os.listdir('.'):
                    if file.startswith('downloaded_media'):
                        filename = file
                        break

            if os.path.exists(filename):
                download_name = "yuvraj_instagram.mp3" if download_type == 'audio' else "yuvraj_instagram.mp4"
                return send_file(filename, as_attachment=True, download_name=download_name)
            else:
                return jsonify({'error': 'File generate nahi ho payi!'}), 500
                
    except Exception as e:
        print(f"❌ Error Details: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Yuvraj Server Chalu Ho Gaya Hai on port {port}!")
    app.run(host='0.0.0.0', port=port)
