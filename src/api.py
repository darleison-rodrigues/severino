from flask import Flask, request, jsonify
from src.llm_inference.local_llm import LocalLLM  # Assuming this path
import os
from src.utils.text_processor import TextProcessor, ProcessingConfig
from src.utils.network_monitor import get_network_usage, ping_host

app = Flask(__name__)

# Initialize your local LLM model
# You might need to adjust how LocalLLM is initialized based on its constructor
llm = LocalLLM() 

# Initialize TextProcessor for performance metrics
text_processor = TextProcessorV2(config=ProcessingConfig(enable_caching=True, cache_size=100))

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('prompt')
    context = data.get('context', '') # Optional context
    multimodal_data = data.get('multimodal_data', None) # Optional multimodal data

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # Assuming your LocalLLM has a method like 'generate' or 'infer'
        # You might need to adapt this call based on your actual LocalLLM API
        response = llm.generate(prompt, context=context, multimodal_data=multimodal_data)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files')
def list_files():
    try:
        # For simplicity, list files in the current directory
        # In a real application, you'd want to restrict this to the project directory
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/read_file')
def read_file_content():
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'error': 'File path is required'}), 400

    try:
        # Basic security: ensure file is within the current directory
        # A more robust solution would use os.path.abspath and check against PROJECT_ROOT
        if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
            return jsonify({'error': 'Invalid file path'}), 400

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content})
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/text_processing_metrics')
def get_text_processing_metrics():
    return jsonify(text_processor.get_performance_report())

@app.route('/network_metrics')
def get_network_metrics():
    metrics = get_network_usage()
    host = request.args.get('host')
    if host:
        latency = ping_host(host)
        metrics['ping_latency_ms'] = latency
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(port=5000)

