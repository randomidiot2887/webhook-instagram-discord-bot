from flask import Flask, request, jsonify
import threading

from instabot import init_driver, load_cookies_and_login, set_instagram_note
from discordbot import set_discord_status

app = Flask(__name__)
WEBHOOK_SECRET = "change-this-to-a-random-string"  # simple shared-secret auth


def run_instagram_update(phrase):
    driver = init_driver()
    try:
        load_cookies_and_login(driver)
        set_instagram_note(driver, phrase)
    finally:
        driver.quit()


def run_discord_update(phrase, emoji=None):
    set_discord_status(phrase, emoji)


def check_auth(data):
    return data.get("secret") == WEBHOOK_SECRET


@app.route("/update-note", methods=["POST"])
def update_note():
    data = request.get_json(silent=True) or {}

    if not check_auth(data):
        return jsonify({"error": "unauthorized"}), 401

    phrase = data.get("phrase")
    if not phrase:
        return jsonify({"error": "missing 'phrase' field"}), 400

    threading.Thread(target=run_instagram_update, args=(phrase,)).start()
    return jsonify({"status": "started"}), 202


@app.route("/update-discord-status", methods=["POST"])
def update_discord_status():
    data = request.get_json(silent=True) or {}

    if not check_auth(data):
        return jsonify({"error": "unauthorized"}), 401

    phrase = data.get("phrase")
    if not phrase:
        return jsonify({"error": "missing 'phrase' field"}), 400

    emoji = data.get("emoji")  # optional

    threading.Thread(target=run_discord_update, args=(phrase, emoji)).start()
    return jsonify({"status": "started"}), 202


@app.route("/update-both", methods=["POST"])
def update_both():
    data = request.get_json(silent=True) or {}

    if not check_auth(data):
        return jsonify({"error": "unauthorized"}), 401

    phrase = data.get("phrase")
    if not phrase:
        return jsonify({"error": "missing 'phrase' field"}), 400

    emoji = data.get("emoji")  # optional, Discord only

    threading.Thread(target=run_instagram_update, args=(phrase,)).start()
    threading.Thread(target=run_discord_update, args=(phrase, emoji)).start()
    return jsonify({"status": "started", "platforms": ["instagram", "discord"]}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)