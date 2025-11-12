"""
Configuration file for Resume Matching System
Using Groq AI - Fast & Free! (FIXED RATE LIMITING)
"""

import os
import certifi
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

# ============== GROQ AI CONFIGURATION ==============
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')
GROQ_MODEL = "llama-3.3-70b-versatile"

# Rate Limiting (Groq Free Tier) - ADJUSTED FOR SAFETY
REQUESTS_PER_MINUTE = 30
DELAY_BETWEEN_REQUESTS = 4.0  # 3 seconds between calls (safer than 2.5)

# AI Reasoning Parameters
AI_REASONING_MAX_TOKENS = 4096
AI_REASONING_TEMPERATURE = 0.3

# Batch Processing Settings
BATCH_SIZE = 5  # Process 5 resumes at a time
BATCH_DELAY = 60  # Wait 60 seconds between batches if needed

# ============== MONGODB CONFIGURATION ==============

# Get credentials from environment (with fallback to hardcoded values)
MONGO_USERNAME = os.getenv('MONGO_USERNAME', 'rukeshsahayarajan_db_user')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'Rukesh1405')
MONGO_CLUSTER = os.getenv('MONGO_CLUSTER', 'test.slusmul.mongodb.net')
DATABASE_NAME = os.getenv('MONGO_DATABASE', 'resume_match_db_v2')

# URL-encode username and password to handle special characters
username_encoded = quote_plus(MONGO_USERNAME)
password_encoded = quote_plus(MONGO_PASSWORD)

# Construct MongoDB URI with proper SSL parameters for Python 3.11
MONGO_URI = (
    f"mongodb+srv://{username_encoded}:{password_encoded}@{MONGO_CLUSTER}/"
    f"?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
)

# Alternative: Use environment variable directly if provided
if os.getenv('MONGO_URI'):
    MONGO_URI = os.getenv('MONGO_URI')

# Collections
COLLECTION_JD = "job_descriptions"
COLLECTION_RESUMES = "resumes"
COLLECTION_RESULTS = "evaluation_results"
COLLECTION_RUBRICS = "rubrics_config"

# MongoDB Connection Parameters (for db_manager.py)
MONGO_CONNECTION_PARAMS = {
    'tls': True,
    'tlsCAFile': certifi.where(),
    'tlsAllowInvalidCertificates': True,  # Key fix for Python 3.11 SSL issues
    'serverSelectionTimeoutMS': 30000,
    'connectTimeoutMS': 30000,
    'socketTimeoutMS': 30000,
    'retryWrites': True,
    'w': 'majority'
}

# MongoDB SSL/TLS behavior flags
MONGO_TLS_ENABLED = True
MONGO_TLS_ALLOW_INVALID_CERTS = True
MONGO_TLS_ALLOW_INVALID_HOSTNAMES = True
MONGO_SERVER_SELECTION_TIMEOUT_MS = 30000

# ============== FILE PROCESSING ==============
SUPPORTED_EXTENSIONS = ['pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'bmp']

# ============== EVALUATION RUBRICS ==============
DEFAULT_RUBRICS_WEIGHTS = {
    "skills": 25,
    "tools": 25,
    "experience": 20,
    "education": 5,
    "projects": 15,
    "certifications": 5,
    "profile_quality": 5
}

# Candidate Tier Thresholds
TIER_THRESHOLDS = {
    "TOP": 80,         # Exceptional fit (80–100%)
    "BEST": 60,        # Strong fit (60–79%)
    "MODERATE": 40,    # Acceptable / average fit (40–59%)
    "LOW": 20,         # Weak fit (20–39%)
    "VERY_LOW": 0      # Poor fit (<20%)
}

# Scoring Parameters
MAX_SCORE = 100
MIN_SCORE = 0

# ============== DISPLAY SETTINGS ==============
MAX_RECENT_ITEMS = 5
MAX_TOP_CANDIDATES = 10

# ============== STARTUP INFO ==============
print("=" * 60)
print("🚀 AI RESUME MATCHER PRO - CONFIGURATION LOADED")
print("=" * 60)
print(f"✅ Groq AI Model: {GROQ_MODEL}")
print(f"⚡ Rate Limit: {REQUESTS_PER_MINUTE} requests/minute")
print(f"⏳ Delay Between Calls: {DELAY_BETWEEN_REQUESTS}s")
print(f"🗄️  Database: {DATABASE_NAME}")
print(f"📝 MongoDB User: {MONGO_USERNAME}")
print(f"🌐 MongoDB Cluster: {MONGO_CLUSTER}")
print(f"🔐 SSL/TLS: Enabled (Invalid certs allowed for Python 3.11)")
print("=" * 60)