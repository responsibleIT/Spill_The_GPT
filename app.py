import os
from flask import Flask, request, jsonify, render_template, send_file
import whisper
from openai import OpenAI
from el import text_to_speech_file


app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transcribe-audio', methods=['POST'])
def api_transcribe_audio():
    if 'audio_file' not in request.files:
        return jsonify({"error": "Missing audio_file"}), 400
    audio_file = request.files['audio_file']
    transcription = transcribe_audio(audio_file)
    return jsonify({"transcription": transcription})

def transcribe_audio(audio_file):
    model = whisper.load_model("tiny")
    # If audio_file is a file-like object, save it temporarily
    if hasattr(audio_file, "read"):
        temp_path = "temp_audio.wav"
        with open(temp_path, "wb") as f:
            f.write(audio_file.read())
        audio_path = temp_path
    else:
        audio_path = audio_file
    result = model.transcribe(audio_path)
    print(result)
    return result["text"]

@app.route('/api/clean-text', methods=['POST'])
def clean_text():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Use OpenAI to clean/anonymize the text
    prompt = f"Change the given text into an anonymized sentence of gossip:\n{text}"
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are changing gossip or stories that people give into an anonymized sentence in the form of gossip. The output should be the same language as the input."},
                {"role": "user", "content": prompt}
            ]
        )
        cleaned_text = response.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"cleaned_text": cleaned_text})

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    try:
        audio_path = text_to_speech_file(text)
        # Serve the audio file via a URL
        audio_url = f"/audio/{os.path.basename(audio_path)}"
        return jsonify({"audio_url": audio_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    audio_dir = os.path.join(os.path.abspath(os.getcwd()), "audio")
    file_path = os.path.join(audio_dir, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Audio file not found"}), 404
    return send_file(file_path, mimetype="audio/mpeg")

@app.route('/gossip-loop')
def gossip_loop():
    audio_dir = os.path.join(os.path.abspath(os.getcwd()), "audio")
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith(".mp3")]
    audio_urls = [f"/audio/{fname}" for fname in audio_files]
    return render_template("gossip_loop.html", audio_urls=audio_urls)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not set
    app.run(host="0.0.0.0", port=port)
