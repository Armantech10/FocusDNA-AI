import sys
import os

# Ensure apps/api and ml are in Python path for Vercel Serverless Function imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

api_dir = os.path.join(root_dir, "apps", "api")
ml_dir = os.path.join(root_dir, "ml")

if api_dir not in sys.path:
    sys.path.insert(0, api_dir)
if ml_dir not in sys.path:
    sys.path.insert(0, ml_dir)

from main import app
