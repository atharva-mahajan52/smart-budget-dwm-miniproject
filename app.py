from flask import Flask, request, jsonify, render_template_string
import sqlite3
import math

app = Flask(__name__)

# ==========================================
# CUSTOM MATHEMATICAL FORMULAE (FROM SCRATCH)
# ==========================================

def calculate_mean(values):
    """Formula: Mean (μ) = Σ x_i / N"""
    return sum(values) / len(values) if values else 0.0

def euclidean_distance(point1, point2):
    """Formula: d(p, q) = sqrt( Σ (p_i - q_i)^2 )"""
    return math.sqrt(sum((p - q) ** 2 for p, q in zip(point1, point2)))

# ==========================================
# CUSTOM DATA MINING ALGORITHMS (FROM SCRATCH)
# ==========================================

class CustomNaiveBayes:
    """
    Supervised Risk Classifier:
    P(Risk_Class | Features) ∝ P(Risk_Class) * Π P(Feature_i | Risk_Class)
    """
    def __init__(self):
        self.class_priors = {}
        self.likelihoods = {}

    def fit(self, training_data):
        total_samples = len(training_data)
        classes = set(row['risk'] for row in training_data)
        
        for c in classes:
            class_samples = [r for r in training_data if r['risk'] == c]
            self.class_priors[c] = len(class_samples) / total_samples
            
            # Feature conditional probabilities with Laplace smoothing
            amounts = [r['amount'] for r in class_samples]
            avg_amt = calculate_mean(amounts)
            weekend_ratio = calculate_mean([r['is_weekend'] for r in class_samples])
            
            self.likelihoods[c] = {
                'avg_amount': avg_amt,
                'weekend_ratio': weekend_ratio
            }

    def predict(self, amount, is_weekend):
        posteriors = {}
        for c, prior in self.class_priors.items():
            avg_amt = self.likelihoods[c]['avg_amount']
            # Gaussian-inspired distance kernel for continuous amount likelihood
            amount_likelihood = math.exp(-((amount - avg_amt) ** 2) / (2 * (1000 ** 2)))
            weekend_prob = self.likelihoods[c]['weekend_ratio'] if is_weekend == 1 else (1.0 - self.likelihoods[c]['weekend_ratio'])
            posteriors[c] = prior * (amount_likelihood + 1e-4) * (weekend_prob + 1e-2)
            
        return max(posteriors, key=posteriors.get)

def custom_kmeans_clustering(data, k=3, max_iters=25):
    """
    Unsupervised Spender Segmenter using custom Euclidean distance & mean centroids
    """
    if len(data) < k:
        return {"centroids": data, "assignments": [0] * len(data)}
    
    # Initialize centroids evenly across min and max
    sorted_vals = sorted(data)
    step = len(sorted_vals) // k
    centroids = [[sorted_vals[min(i * step, len(sorted_vals) - 1)]] for i in range(k)]

    assignments = [0] * len(data)
    for _ in range(max_iters):
        # Cluster Assignment Step via Euclidean Distance
        clusters = {i: [] for i in range(k)}
        for idx, val in enumerate(data):
            distances = [euclidean_distance([val], c) for c in centroids]
            cluster_idx = distances.index(min(distances))
            assignments[idx] = cluster_idx
            clusters[cluster_idx].append(val)
        
        # Centroid Update Step via Arithmetic Mean
        new_centroids = []
        for i in range(k):
            if clusters[i]:
                new_centroids.append([calculate_mean(clusters[i])])
            else:
                new_centroids.append(centroids[i])
                
        if new_centroids == centroids:
            break
        centroids = new_centroids

    return {
        "centroids": [round(c[0], 2) for c in centroids],
        "clusters": {f"Cluster_{i} (Mean: ₹{round(centroids[i][0], 1)})": clusters[i] for i in range(k)}
    }

# ==========================================
# REST API ROUTES
# ==========================================

def get_db():
    conn = sqlite3.connect('budget_dwm.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/transactions', methods=['GET', 'POST'])
def handle_transactions():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        category = data['category']
        amount = float(data['amount'])
        is_weekend = int(data.get('is_weekend', 0))

        # Train model dynamically from historical transactions
        cursor.execute("SELECT amount, is_weekend, risk_label FROM transactions")
        rows = cursor.fetchall()
        train_data = [{'amount': r['amount'], 'is_weekend': r['is_weekend'], 'risk': r['risk_label']} for r in rows]
        
        nb = CustomNaiveBayes()
        nb.fit(train_data)
        predicted_risk = nb.predict(amount, is_weekend)

        # Insert new transaction
        cursor.execute(
            "INSERT INTO transactions (user_id, category, amount, is_weekend, risk_label) VALUES (1, ?, ?, ?, ?)",
            (category, amount, is_weekend, predicted_risk)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "predicted_risk": predicted_risk})

    cursor.execute("SELECT * FROM transactions ORDER BY tx_id DESC")
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(transactions)

@app.route('/api/mining/clusters', methods=['GET'])
def get_spend_clusters():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM transactions")
    amounts = [row['amount'] for row in cursor.fetchall()]
    conn.close()

    clustering_result = custom_kmeans_clustering(amounts, k=3)
    return jsonify(clustering_result)

@app.route('/')
def home():
    # Returns frontend single-page interface
    with open('index.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    from database import init_db
    init_db()
    app.run(port=5000, debug=True)
