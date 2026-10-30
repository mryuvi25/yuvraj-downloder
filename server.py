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

        # Pehle standard options try karenge, agar fail hua toh fallback use hoga
        formats_to_try = ['bv*+ba/b', 'best', 'worst'] if download_type != 'audio' else ['bestaudio/best']
        
        success = False
        last_error = ""

        for fmt in formats_to_try:
            ydl_opts = {
                'outtmpl': output_base,
                'quiet': True,
                'no_warnings': True,
                'format': fmt,
                'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            }

            if download_type == 'audio':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            try:
                print(f"📥 Trying download with format {fmt} for URL: {clean_url}")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([clean_url])
                success = True
                break
            except Exception as sub_e:
                last_error = str(sub_e)
                print(f"⚠️ Format {fmt} failed: {last_error}")
                continue

        if not success:
            return jsonify({'error': f'Download fail ho gaya: {last_error}'}), 500
            
        target_ext = '.mp3' if download_type == 'audio' else '.mp4'
        filename = output_base + target_ext
        
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
        print(f"❌ Error Details: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
