from flask import Flask, render_template, request, jsonify, url_for
import pandas as pd
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')

def load_env():
    load_dotenv()
    source_dir = os.environ.get("SOURCE_DIR", "conf")
    prefix_col = os.environ.get("PREFIX", "PREFIX")
    suffix_col = os.environ.get("SUFFIX", "SUFFIX")
    
    # Ensure conf directory exists
    os.makedirs(source_dir, exist_ok=True)
    return prefix_col, suffix_col, source_dir

def generate_combinations(keywords, csv_data, prefix_col, suffix_col):
    combinations = []
    for keyword in keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
            
        for _, row in csv_data.iterrows():
            prefix_str = str(row[prefix_col])
            suffix_str = str(row[suffix_col])
            
            if prefix_str.lower() == "nan":
                prefix_str = ""
            if suffix_str.lower() == "nan":
                suffix_str = ""
                
            if len(prefix_str) > 0 or len(suffix_str) > 0:
                combinations.append(f"{prefix_str}{keyword}{suffix_str}")
    
    return combinations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        prefix_col, suffix_col, source_dir = load_env()
        
        # Get keywords from textarea
        keywords_text = request.form.get('keywords', '')
        keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
        
        # Read the default CSV file
        csv_path = os.path.join(source_dir, 'prefixes_suffixes.csv')
        if not os.path.exists(csv_path):
            return jsonify({
                'error': f'CSV file not found at {csv_path}. Please create it with PREFIX and SUFFIX columns.'
            }), 400
            
        data = pd.read_csv(csv_path)
        
        # Generate combinations
        combinations = generate_combinations(keywords, data, prefix_col, suffix_col)
        
        return jsonify({
            'combinations': combinations,
            'total': len(combinations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) 