import json
import os

FILE = "config/joy_center.json"


def save_center(center):
    os.makedirs("config", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(center, f)
    print("💾 Center kaydedildi:", center)


def load_center():
    if not os.path.exists(FILE):
        return None

    try:
        with open(FILE, "r") as f:
            center = json.load(f)

        if not isinstance(center, list) or len(center) < 4:
            raise ValueError("Center listesi bozuk")

        print("📁 Center yüklendi:", center)
        return center

    except Exception as e:
        print("⚠️ joy_center.json bozuk, siliyorum:", e)
        try:
            os.remove(FILE)
        except:
            pass
        return None


def reset_center():
    if os.path.exists(FILE):
        os.remove(FILE)
        print("🗑️ Center silindi")
