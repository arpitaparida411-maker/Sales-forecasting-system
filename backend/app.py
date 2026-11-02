from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"


def read_csv(name):
    return pd.read_csv(OUTPUTS / name)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/history")
def history():
    data = read_csv("weekly_history.csv")
    return jsonify(data.to_dict(orient="records"))


@app.route("/forecast")
def forecast():
    weeks = request.args.get("weeks", default=26, type=int)
    weeks = max(1, min(weeks, 26))
    data = read_csv("future_forecast.csv").head(weeks)
    return jsonify(data.to_dict(orient="records"))


@app.route("/models")
def models():
    data = read_csv("model_comparison.csv")
    return jsonify(data.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)