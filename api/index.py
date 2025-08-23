# api/index.py
from Furlink_Backend.wsgi import application

# Vercel expects "app"
app = application
