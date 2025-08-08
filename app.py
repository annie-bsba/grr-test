from flask import Flask
app = Flask(__name__)

@app.get("/")
def home():
    return "BigBucks Secret App: OK"
