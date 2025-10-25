from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import joblib
import pandas as pd
import os
import secrets
from datetime import datetime, timedelta 

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ml_dashboard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'ngo', 'donor', 'admin'
    cis = db.Column(db.String(50), nullable=True)
    current_badge = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with badges
    badges = db.relationship('UserBadge', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'cis': self.cis,
            'current_badge': self.current_badge,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_name': self.badge_name,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }

# Database setup functions
def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
            return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_sample_users():
    """Create sample users for testing"""
    try:
        with app.app_context():
            # Check if users already exist
            user_count = User.query.count()
            
            if user_count == 0:
                # Create sample users
                sample_users = [
                    {
                        'name': 'Admin User',
                        'email': 'admin@example.com',
                        'password': 'admin123',
                        'role': 'admin',
                        'cis': 'ADM001',
                        'current_badge': 'Admin',
                        'bio': 'System Administrator'
                    },
                    {
                        'name': 'NGO User',
                        'email': 'ngo@example.com',
                        'password': 'password123',
                        'role': 'ngo',
                        'cis': 'NGO001',
                        'current_badge': 'NGO Leader',
                        'bio': 'Non-profit organization leader'
                    },
                    {
                        'name': 'Donor User',
                        'email': 'donor@example.com',
                        'password': 'password123',
                        'role': 'donor',
                        'cis': 'DON001',
                        'current_badge': 'Generous Donor',
                        'bio': 'Regular donor and supporter'
                    }
                ]
                
                for user_data in sample_users:
                    user = User(
                        name=user_data['name'],
                        email=user_data['email'],
                        password=generate_password_hash(user_data['password']),
                        role=user_data['role'],
                        cis=user_data['cis'],
                        current_badge=user_data['current_badge'],
                        bio=user_data['bio']
                    )
                    db.session.add(user)
                
                db.session.commit()
                print("✅ Sample users created successfully!")
            else:
                print(f"✅ Users already exist ({user_count} users found)")
            
            return True
    except Exception as e:
        print(f"❌ Error creating sample users: {e}")
        return False

def setup_database():
    """Complete database setup"""
    print("🔄 Setting up database...")
    
    # Create tables
    if not create_tables():
        return False
    
    # Create sample users if none exist
    create_sample_users()
    
    print("✅ Database setup completed successfully!")
    return True

# Allow access from the frontend development server
CORS(app, resources={r"/*": {"origins": "*"}}) 

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

# Authentication helper functions
def create_user(name, email, password, role, cis=None, bio=None):
    """Create a new user in the database"""
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "User with this email already exists"
        
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            cis=cis,
            bio=bio
        )
        
        db.session.add(user)
        db.session.commit()
        return user, "User created successfully"
    except Exception as e:
        print(f"Error creating user: {e}")
        return None, f"Error creating user: {str(e)}"

def authenticate_user(email, password):
    """Authenticate user login"""
    try:
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            return user
        return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

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

# Authentication endpoints
@app.route("/api/auth/register", methods=["POST"])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'ngo')  # Default to 'ngo'
        cis = data.get('cis')
        bio = data.get('bio')
        
        # Validate required fields
        if not all([name, email, password]):
            return jsonify({"error": "Name, email, and password are required"}), 400
        
        # Validate role
        if role not in ['admin', 'ngo', 'donor']:
            return jsonify({"error": "Invalid role. Must be 'admin', 'ngo', or 'donor'"}), 400
        
        # Create user
        user, message = create_user(name, email, password, role, cis, bio)
        if user:
            return jsonify({
                "status": "success",
                "message": message,
                "user": user.to_dict()
            }), 201
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({"error": "Email and password are required"}), 400
        
        user = authenticate_user(email, password)
        if user:
            # Create session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = user.role
            
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user": user.to_dict()
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
            
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """User logout endpoint"""
    try:
        session.clear()
        return jsonify({"status": "success", "message": "Logged out successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500

@app.route("/api/auth/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user profile by ID"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            "status": "success",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get user: {str(e)}"}), 500

@app.route("/api/auth/init-db", methods=["POST"])
def init_database():
    """Initialize database tables and sample data"""
    try:
        if setup_database():
            return jsonify({
                "status": "success",
                "message": "Database initialized successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Database initialization failed"
            }), 500
    except Exception as e:
        return jsonify({"error": f"Database initialization failed: {str(e)}"}), 500

@app.route("/test-db", methods=["GET"])
def test_database():
    """Test database connection"""
    try:
        with app.app_context():
            # Test database connection
            user_count = User.query.count()
            
            return jsonify({
                "status": "success",
                "message": "Database connection successful",
                "user_count": user_count
            }), 200
        
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

@app.route("/db-status", methods=["GET"])
def database_status():
    """Check database and tables status"""
    try:
        with app.app_context():
            # Get user count
            user_count = User.query.count()
            
            # Get all users
            users = User.query.all()
            users_data = [user.to_dict() for user in users]
            
            return jsonify({
                "status": "success",
                "database": "ml_dashboard",
                "user_count": user_count,
                "users": users_data,
                "tables": ["users", "user_badges"]
            }), 200
        
    except Exception as e:
        return jsonify({"error": f"Database status check failed: {str(e)}"}), 500

@app.route("/users", methods=["GET"])
def get_all_users():
    """Get all users (for testing purposes)"""
    try:
        with app.app_context():
            users = User.query.all()
            users_data = [user.to_dict() for user in users]
            
            return jsonify({
                "status": "success",
                "users": users_data,
                "count": len(users_data)
            }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch users: {str(e)}"}), 500

if __name__ == "__main__":
    # Setup database automatically on startup
    with app.app_context():
        if setup_database():
            print("🚀 Starting Flask application...")
            app.run(debug=True, port=5000)
        else:
            print("❌ Failed to setup database. Please check XAMPP MySQL is running.")
            print("💡 Make sure:")
            print("   1. XAMPP is running")
            print("   2. MySQL service is started in XAMPP")
            print("   3. MySQL is accessible on localhost:3306")