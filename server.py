from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    return "❌ Error: index.html file nahi mili!", 404

@app.route('/download', methods=['POST'])
def download_media():
    try:
        data = request.get_json()
        raw_url = data.get('url')
        download_type = data.get('type', 'video')  # 'video' ya 'audio'
        
        if not raw_url:
            return jsonify({'error': 'URL missing hai'}), 400

        # Story aur Post/Reel ke liye exact URL pass karna taaki ID misplace na ho
        clean_url = raw_url.strip()

        output_base = 'downloaded_media'
        
        # Purane files saaf karna
        for ext in ['.mp4', '.mp3', '.m4a', '.webm', '.opus', '.mkv', '.jpg', '.png', '.webp']:
            if os.path.exists(output_base + ext):
                try:
                    os.remove(output_base + ext)
                except:
                    pass

        # Advanced options for Instagram Media, Posts & Stories
        ydl_opts = {
            'outtmpl': output_base,
            'quiet': True,
            'no_warnings': True,
            'geo_bypass': True,
            'extractor_args': {
                'instagram': {
                    'max_comments': 0
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
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

        print(f"📥 Downloading Instagram URL: {clean_url} | Type: {download_type}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([clean_url])
            
            # Check karne ke liye kaunsi file bani hai (mp4, mp3, ya image formats)
            target_ext = '.mp3' if download_type == 'audio' else '.mp4'
            filename = output_base + target_ext
            
            if not os.path.exists(filename):
                for file in os.listdir('.'):
                    if file.startswith('downloaded_media'):
                        filename = file
                        break

            if os.path.exists(filename):
                file_ext = os.path.splitext(filename)[1]
                download_name = "yuvraj_audio.mp3" if download_type == 'audio' else f"yuvraj_media{file_ext}"
                return send_file(filename, as_attachment=True, download_name=download_name)
            else:
                return jsonify({'error': 'File generate nahi ho payi! Post public honi chahiye.'}), 500
                
    except Exception as e:
        print(f"❌ Error Details: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Yuvraj Server Chalu Ho Gaya Hai on port {port}!")
    app.run(host='0.0.0.0', port=port)
