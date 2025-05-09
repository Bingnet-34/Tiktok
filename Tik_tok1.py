from flask import Flask, render_template_string, request, jsonify, Response
import requests
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['TEMPLATES_AUTO_RELOAD'] = True

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="نزّل فيديوهات تيك توك بجودة HD بدون علامة مائية وبضغطة زر واحدة! أسرع طريقة لتحميل مقاطع التيك توك مباشرة من أي حساب.">
    <title>🎬 تيك توك ميديا | تنزيل الفيديوهات المجانية</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Cairo', sans-serif; }
        .loader {
            border-top-color: #3B82F6;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error-alert {
            animation: slideIn 0.3s ease-out;
        }
        .description.collapsed {
            height: 4.5em;
            overflow: hidden;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-900 to-blue-900 min-h-screen">
  
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-2xl">
            <h1 class="text-4xl font-bold text-center mb-8 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                🚀 تيك توك ميديا
                <p class="text-lg mt-2 text-gray-300">✶نزل أي فيديو تيك توك بجودة عالية✶</p>
            </h1>

            <div class="flex flex-col space-y-4">
                <input 
                    type="url" 
                    id="urlInput"
                    placeholder="👆 قم بلصق رابط الفيديو هنا..."
                    class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                <button 
                    onclick="processVideo()"
                    class="bg-gradient-to-r from-blue-500 to-purple-600 hover:opacity-90 text-white px-6 py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2"
                    id="processBtn"
                >
                    <i class="fas fa-rocket"></i> بدء التنزيل
                </button>
            </div>

            <div id="previewSection" class="mt-8 hidden animate-pop">
                <div class="bg-black/30 rounded-xl overflow-hidden p-4">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="col-span-1">
                            <img src="" id="videoThumbnail" class="w-full h-48 object-cover rounded-lg shadow-lg">
                        </div>
                        <div class="col-span-2 text-white">
                            <h2 id="videoTitle" class="text-2xl font-bold mb-2"></h2>
                            <div id="videoDescription" class="description mb-4"></div>
                            <button id="toggleDescBtn" onclick="toggleDescription()" class="text-blue-400 mb-4 hidden">عرض المزيد</button>
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                                <div class="bg-white/5 p-3 rounded-lg">
                                    <div class="text-blue-400 font-bold"><i class="fas fa-heart mr-1"></i>الإعجابات</div>
                                    <div id="likeCount" class="text-xl">0</div>
                                </div>
                                <div class="bg-white/5 p-3 rounded-lg">
                                    <div class="text-pink-400 font-bold"><i class="fas fa-comment mr-1"></i>التعليقات</div>
                                    <div id="commentCount" class="text-xl">0</div>
                                </div>
                                <div class="bg-white/5 p-3 rounded-lg">
                                    <div class="text-green-400 font-bold"><i class="fas fa-share mr-1"></i>المشاركات</div>
                                    <div id="shareCount" class="text-xl">0</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="mt-6 flex flex-wrap gap-4 justify-center">
                    <button 
                        onclick="downloadVideo()"
                        class="bg-gradient-to-r from-green-500 to-blue-500 hover:opacity-90 px-6 py-3 rounded-lg flex items-center gap-2"
                        id="downloadBtn"
                    >
                        <i class="fas fa-file-download"></i> حفظ الفيديو
                    </button>
                    <button 
                        onclick="downloadAudio()"
                        class="bg-gradient-to-r from-purple-500 to-pink-500 hover:opacity-90 px-6 py-3 rounded-lg flex items-center gap-2"
                        id="downloadAudioBtn"
                    >
                        <i class="fas fa-music"></i> حفظ الصوت
                    </button>
                </div>
            </div>

            <div id="errorMessage" class="mt-4 hidden"></div>
        </div>
    </div>

    <footer class="text-center text-gray-400 mt-8">
        &copy; {{ year }} جميع الحقوق محفوظة © Khalil
    </footer>

<script>
let videoData = null;

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.innerHTML = `
        <div class="error-alert bg-red-500/90 text-white px-4 py-3 rounded-lg flex items-center">
            <i class="fas fa-exclamation-triangle mr-2"></i>
            ${message}
        </div>
    `;
    errorDiv.classList.remove('hidden');
    setTimeout(() => errorDiv.classList.add('hidden'), 5000);
}

async function processVideo() {
    const url = document.getElementById('urlInput').value.trim();
    const btn = document.getElementById('processBtn');
    if (!url) return showError('الرجاء إدخال رابط الفيديو أولاً');
    
    btn.innerHTML = `<div class="loader h-6 w-6 border-4 rounded-full"></div>`;
    btn.disabled = true;
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'حدث خطأ غير متوقع');

        videoData = data;
        updateUI(data);
        document.getElementById('previewSection').style.display = 'block';
    } catch (err) {
        showError(err.message || 'فشل في معالجة الفيديو، يرجى المحاولة لاحقًا');
    } finally {
        btn.innerHTML = `<i class="fas fa-rocket"></i> بدء التنزيل`;
        btn.disabled = false;
    }
}

function toggleDescription() {
    const desc = document.getElementById('videoDescription');
    const btn = document.getElementById('toggleDescBtn');
    desc.classList.toggle('collapsed');
    btn.textContent = desc.classList.contains('collapsed') ? 'عرض المزيد' : 'عرض أقل';
}

async function downloadFile(url, type = 'video') {
    try {
        const endpoint = type === 'video' ? '/download' : '/download_audio';
        const btnId = type === 'video' ? 'downloadBtn' : 'downloadAudioBtn';
        const btn = document.getElementById(btnId);
        
        btn.innerHTML = `<div class="loader h-5 w-5 border-2 rounded-full"></div>`;
        btn.disabled = true;

        const response = await fetch(`${endpoint}?url=${encodeURIComponent(url)}`);
        if (!response.ok) throw new Error('فشل في التنزيل');
        
        const blob = await response.blob();
        const ext = type === 'video' ? 'mp4' : 'mp3';
        const filename = `tiktok_${Date.now()}.${ext}`;
        
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        a.click();
        URL.revokeObjectURL(a.href);
    } catch (err) {
        showError('تعذر اكتمال التنزيل، يرجى المحاولة مرة أخرى');
    } finally {
        const btn = document.getElementById(type === 'video' ? 'downloadBtn' : 'downloadAudioBtn');
        btn.innerHTML = type === 'video' 
            ? `<i class="fas fa-file-download"></i> حفظ الفيديو`
            : `<i class="fas fa-music"></i> حفظ الصوت`;
        btn.disabled = false;
    }
}

function downloadVideo() {
    if (!videoData?.video_url) return showError('رابط التنزيل غير متوفر');
    downloadFile(videoData.video_url, 'video');
}

function downloadAudio() {
    if (!videoData?.audio_url) return showError('رابط الصوت غير متوفر');
    downloadFile(videoData.audio_url, 'audio');
}

function updateUI(data) {
    document.getElementById('videoThumbnail').src = data.thumbnail || '';
    document.getElementById('videoTitle').textContent = data.title || 'بدون عنوان';
    
    const descDiv = document.getElementById('videoDescription');
    descDiv.textContent = data.description || '';
    if (data.description && data.description.length > 150) {
        descDiv.classList.add('collapsed');
        document.getElementById('toggleDescBtn').classList.remove('hidden');
    }
    
    document.getElementById('likeCount').textContent = data.likes || '0';
    document.getElementById('commentCount').textContent = data.comments || '0';
    document.getElementById('shareCount').textContent = data.shares || '0';
}
</script>
</body>
</html>
'''

def get_video_info(url):
    
    api_url = "https://www.tikwm.com/api"
    try:
        response = requests.get(api_url, params={"url": url}, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 0:
            return {'error': 'فشل في استخراج معلومات الفيديو'}
            
        info = data.get("data", {})
        return {
            'title': info.get("title", "فيديو تيك توك"),
            'thumbnail': info.get("cover", ""),
            'likes': info.get("digg_count", 0),
            'comments': info.get("comment_count", 0),
            'shares': info.get("share_count", 0),
            'video_url': info.get("play", ""),
            'audio_url': info.get("music", ""),
            'description': info.get("text", "")
        }
    except Exception as e:
        return {'error': 'تعذر الاتصال بالخادم، يرجى التحقق من الرابط والمحاولة مرة أخرى'}

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, year=datetime.now().year)

@app.route('/process', methods=['POST'])
def process():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'رابط الفيديو مطلوب'}), 400
            
        video_info = get_video_info(url)
        if video_info.get('error'):
            return jsonify({'error': video_info['error']}), 400
            
        return jsonify(video_info)
    except Exception as e:
        return jsonify({'error': 'حدث خطأ غير متوقع'}), 500

@app.route('/download')
def download_video():
  
    try:
        video_url = request.args.get('url')
        if not video_url:
            return jsonify({'error': 'رابط الفيديو مطلوب'}), 400
            
        resp = requests.get(video_url, stream=True, timeout=20)
        resp.raise_for_status()
        
        return Response(
            resp.iter_content(chunk_size=8192),
            headers={
                'Content-Type': 'video/mp4',
                'Content-Disposition': f'attachment; filename="tiktok_{uuid.uuid4().hex[:8]}.mp4"'
            }
        )
    except Exception as e:
        return jsonify({'error': 'تعذر تنزيل الفيديو'}), 500

@app.route('/download_audio')
def download_audio():
    
    try:
        audio_url = request.args.get('url')
        if not audio_url:
            return jsonify({'error': 'رابط الصوت مطلوب'}), 400
            
        resp = requests.get(audio_url, stream=True, timeout=20)
        resp.raise_for_status()
        
        return Response(
            resp.iter_content(chunk_size=8192),
            headers={
                'Content-Type': 'audio/mpeg',
                'Content-Disposition': f'attachment; filename="tiktok_audio_{uuid.uuid4().hex[:8]}.mp3"'
            }
        )
    except Exception as e:
        return jsonify({'error': 'تعذر تنزيل الصوت'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)