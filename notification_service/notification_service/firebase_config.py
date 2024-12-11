# firebase.py
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

# Инициализация Firebase
cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
firebase_admin.initialize_app(cred)
