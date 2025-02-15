from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load model
model_path = "fatigue_model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file {model_path} not found.")
model = joblib.load(model_path)

def get_fatigue_category(prediction):
    if prediction <= 3.0: return "Better"
    elif prediction <= 5.0: return "Good"
    elif prediction <= 7.0: return "Average"
    elif prediction <= 9.0: return "High"
    else: return "Critical"

def generate_recommendations(data, category):
    recommendations = []
    
    # Screen time recommendations
    if data['ScreenTime'] > 6:
        recommendations.append("🖥️ Reduce screen time by 1-2 hours daily")
    
    # Social media usage
    if data['SocialMediaTime'] > 4:
        recommendations.append("📱 Schedule social media breaks every 45 minutes")
    
    # Platform specific advice
    platform = data['PrimaryPlatform'].lower()
    platform_tips = {
        'instagram': "Use grayscale mode to reduce engagement",
        'youtube': "Enable 'Take a Break' reminders",
        'tiktok': "Set daily time limit in digital wellbeing settings"
    }
    recommendations.append(platform_tips.get(platform, "Take 5-minute breaks every hour"))
    
    # Fatigue level based advice
    if category in ["High", "Critical"]:
        recommendations.append("💤 Improve sleep quality with pre-bed digital detox")
    
    return recommendations[:3]  # Return top 3 recommendations

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json() or {}
        
        # Default values with type validation
        defaults = {
            "Age": 25, "SocialMediaTime": 2.5, "ScreenTime": 5.0,
            "PrimaryPlatform": "Other", "EntertainmentSpending": 50,
            "SocialIsolation": 3, "MessagingTime": 1.5, "VideoTime": 2.0,
            "ScreenTimePerNotification": 0.5, "MusicTime": 1.0,
            "TechSavviness": 7, "GamingTime": 1.0, "EntertainmentPlatform": "Web",
            "PreferredDevice": "Mobile", "SleepQuality": 6,
            "TotalEntertainmentTime": 4.0, "SocialMediaGoal": "Connection"
        }
        
        # Merge input with defaults
        input_data = {**defaults, **data}
        
        # Convert to DataFrame
        input_df = pd.DataFrame([input_data])
        
        # Generate prediction
        prediction = model.predict(input_df)[0]
        category = get_fatigue_category(prediction)
        
        # Create response
        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "predicted_fatigue_level": round(float(prediction), 2),
            "fatigue_category": category,
            "recommendations": generate_recommendations(input_data, category),
            "input_parameters": input_data
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
