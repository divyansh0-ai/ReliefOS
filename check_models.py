import google.generativeai as genai
import sys

try:
    genai.configure(api_key="AIzaSyCcFDI4rBV1yiqJyNhZ41PJv_XB5X7edsc")
    models = genai.list_models()
    for m in models:
        print(m.name)
except Exception as e:
    print("Error:", e)
