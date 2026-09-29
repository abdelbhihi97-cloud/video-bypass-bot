from flask import Flask, render_template, request, send_file
import ffmpeg
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def bypass_copyright(input_path, output_path):
    try:
        video_stream = (
            ffmpeg.input(input_path)
            .hflip()
            .filter('eq', brightness=0.02, contrast=1.03, saturation=1.05)
            .filter('noise', alls=1, allf='t')
        )
        audio_stream = (
            ffmpeg.input(input_path).audio
            .filter('atempo', 1.03)
            .filter('asetrate', 44100 * 1.02)
        )
        ffmpeg.output(
            video_stream, audio_stream, output_path,
            vcodec='libx264', acodec='aac', map_metadata=-1
        ).overwrite_output().run(quiet=True)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video_file' not in request.files:
        return "لم يتم رفع أي ملف", 400
    
    file = request.files['video_file']
    if file.filename == '':
        return "اسم الملف غير صحيح", 400

    if file:
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(OUTPUT_FOLDER, "clean_" + file.filename)
        
        file.save(input_path)
        success = bypass_copyright(input_path, output_path)
        
        if success:
            return send_file(output_path, as_attachment=True)
        else:
            return "فشلت المعالجة، تأكد من تثبيت FFmpeg", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)