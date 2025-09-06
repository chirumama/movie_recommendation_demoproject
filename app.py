import os
import sys
import pandas as pd
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import random

app = Flask(__name__)
CORS(app)

# --- Resolve project paths in a portable way ---
base_app_dir = Path(__file__).resolve().parent        # .../Flask/app
project_root = base_app_dir.parent                     # .../Flask

# Look for CSV in order: env var, app folder, project root
env_path = os.environ.get('NETFLIX_CSV')
candidate_paths = []
if env_path:
    candidate_paths.append(Path(env_path))
candidate_paths.extend([
    base_app_dir / 'netflix_titles.csv',
    project_root / 'netflix_titles.csv'
])

data_path = None
for p in candidate_paths:
    if p and p.exists():
        data_path = p
        break

if data_path is None:
    app.logger.error(
        "Could not find 'netflix_titles.csv'. Place the file in 'app/' or project root "
        "or set the NETFLIX_CSV environment variable to its path."
    )
    sys.exit(1)

# --- Load and Process Data ---
# Load the dataset from the CSV file. This is done once when the app starts.
try:
    df = pd.read_csv(str(data_path))
    # Use the 'listed_in' column (genres) for our recommendation logic
    df['combined_features'] = df['listed_in'].fillna('')
    
    # Use TF-IDF Vectorizer to convert the text data into a matrix of token counts.
    # This helps in calculating the similarity between titles.
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['combined_features'])
except Exception as e:
    app.logger.exception("Unexpected error while loading data:")
    sys.exit(1)

# --- Recommendation Logic Function ---
def get_recommendations(titles):
    """
    Generates movie/series recommendations based on a list of user-provided titles.
    
    Args:
        titles (list): A list of movie or series titles.
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a recommended title.
    """
    recommended_indices = set()
    
    for title in titles:
        # Find the index of the chosen title in the DataFrame
        # Case-insensitive search
        idx = df[df['title'].str.lower() == title.lower()].index
        
        if len(idx) > 0:
            idx = idx[0]
            
            # Calculate the cosine similarity between the chosen item and all others
            # This measures the similarity based on their shared genres/features
            cosine_sim = linear_kernel(tfidf_matrix[idx:idx+1], tfidf_matrix).flatten()
            
            # Get the top 30 most similar items (excluding the item itself)
            sim_scores = list(enumerate(cosine_sim))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            # Randomly select 10 from top 30
            selected_scores = random.sample(sim_scores, min(10, len(sim_scores)))
            # Store the indices of the recommended items
            recommended_indices.update([i[0] for i in selected_scores])
            
    # Remove any of the original chosen titles from the recommendations
    chosen_indices = df[df['title'].str.lower().isin([t.lower() for t in titles])].index
    for idx in chosen_indices:
        if idx in recommended_indices:
            recommended_indices.remove(idx)
            
    # Get the recommended titles and format the output
    recommendations = []
    for i in list(recommended_indices):
        # Safely extract values and replace NaN with JSON-safe values
        title_val = df.iloc[i]['title']
        director_val = df.iloc[i]['director']
        genres_val = df.iloc[i]['listed_in']

        # Convert pandas NA/NaN to Python None or empty string for genres
        if pd.isna(title_val):
            title_val = ''
        if pd.isna(director_val):
            director_val = None
        if pd.isna(genres_val):
            genres_val = ''

        recommendations.append({
            'title': title_val,
            'director': director_val,
            'genres': genres_val
        })

    return recommendations

# --- Flask Routes ---
@app.route('/recommend', methods=['POST'])
def recommend():
    """
    API endpoint to get recommendations.
    Accepts a JSON payload with a 'titles' key containing a list of strings.
    """
    try:
        data = request.json
        titles = data.get('titles', [])
        
        if not titles:
            return jsonify({'error': 'No titles provided'}), 400
        
        recommendations = get_recommendations(titles)
        
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def home():
    return "Netflix Recommendation Backend is running. If you see this, the server is up!"

@app.route('/index.html')
def serve_index():
    # Serve index.html from the project root (portable)
    return send_from_directory(str(project_root), 'index.html')

if __name__ == '__main__':
    app.logger.info("Starting Flask app on 0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
