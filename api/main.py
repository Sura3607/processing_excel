from flask import Flask, request, send_file, jsonify
from api.file_processing import process_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/uploaded_files"
PROCESSED_FOLDER = "/tmp/processed_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("No selected file in the request")
        return jsonify({"error": "No selected file"}), 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(input_path)
        app.logger.info(f"File saved to {input_path}")

        output_path = os.path.join(PROCESSED_FOLDER, f"processed_{file.filename}")
        process_file(input_path, output_path)
        app.logger.info(f"Processed file saved to {output_path}")

        return send_file(output_path, as_attachment=True)
    except Exception as e:
        app.logger.exception("Error occurred while processing file")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
            app.logger.info(f"Removed temporary file {input_path}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
