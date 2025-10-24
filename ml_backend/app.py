from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import pandas as pd
import os 

app = Flask(__name__)
# Allow access from the frontend development server
CORS(app, resources={r"/predict": {"origins": "*"}}) 

# Define model paths (assuming they are in the same ml_backend directory)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_urgency_model.joblib")
COLUMNS_PATH = os.path.join(os.path.dirname(__file__), "model_feature_columns.joblib")

# Initialize model and feature columns list
model = None
feature_columns = None # This will hold the saved list of all OHE column names

# Define feature order (must match training data order)
# NOTE: These are the names of the INPUT columns before OHE.
feature_cols = ["State", "PeopleAffected", "Domain", "ResourcesRequired", "UrgencyReason", "Timeline"]
cat_cols = ["State", "Domain", "ResourcesRequired", "UrgencyReason", "Timeline"]
urgency_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"} # For final output

# Load model and encoder (columns list) during application startup
try:
    if os.path.exists(MODEL_PATH) and os.path.exists(COLUMNS_PATH):
        model = joblib.load(MODEL_PATH)
        # Load the list of 30+ feature column names (the encoder artifact)
        feature_columns = joblib.load(COLUMNS_PATH)
        print("✅ Model and feature columns loaded successfully")
    else:
        print(f"❌ Model files not found in {os.path.dirname(__file__)}")
except Exception as e:
    print("❌ Model loading error:", e)
    model = None
    feature_columns = None


@app.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint to receive NGO request data, preprocess it, and return an urgency prediction.
    """
    if model is None or feature_columns is None:
        return jsonify({"error": "ML Model not available or failed to load. Check server console for details."}), 500

    data = request.get_json()

    try:
        # 1. Prepare input dictionary (Match frontend fields to model features)
        input_dict = {
            "State": data.get("state", ""),
            "PeopleAffected": int(data.get("peopleAffected", 0)), 
            "Domain": data.get("domain", ""),
            "ResourcesRequired": data.get("resourceType", ""), # Corrected mapping
            "UrgencyReason": data.get("urgencyReason", ""),
            "Timeline": data.get("timeline", "")
        }
        
        # 2. Create DataFrame and ENFORCE TYPES
        df = pd.DataFrame([input_dict]) # DataFrame automatically uses input_dict keys
        
        # Ensure numerical type (critical for consistency)
        df['PeopleAffected'] = pd.to_numeric(df['PeopleAffected'], errors='coerce').fillna(0).astype(float)
        
        # 3. Apply One-Hot Encoding (OHE) - MUST match training: drop_first=True
        df_encoded = pd.get_dummies(df, drop_first=True)
        
        # 4. Align columns using the saved feature_columns list (THIS IS THE FIX)
        # Adds missing OHE columns (value=0) and drops any extra/unknown ones.
        features_final = df_encoded.reindex(columns=feature_columns, fill_value=0)
        
        # 5. Predict urgency (model expects a NumPy array/DataFrame)
        urgency_pred_id = model.predict(features_final)[0]
        urgency_label = urgency_map.get(urgency_pred_id, "UNKNOWN")

        # 6. Predict confidence (optional but good practice)
        confidence = 0.8 # Default fallback
        if hasattr(model, "predict_proba"):
            confidence = float(np.max(model.predict_proba(features_final)))

        return jsonify({
            "status": "success",
            "urgency": urgency_label,
            "confidence": round(confidence, 4),
            "timestamp": pd.Timestamp.now().isoformat()
        }), 200

    except Exception as e:
        app.logger.error(f"Prediction processing error: {e}") 
        return jsonify({"error": f"Prediction processing failed: {str(e)}"}), 500

if __name__ == "__main__":
    # The server will run on port 5000 by default.
    app.run(debug=True, port=5000)