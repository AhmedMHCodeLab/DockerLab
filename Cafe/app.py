import os
from flask import Flask, render_template, url_for, request, redirect, session
import redis

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")  # sessions

# ---------- Redis ----------
def get_redis_client():
    url = os.getenv("REDIS_URL")
    if url:
        return redis.Redis.from_url(url, decode_responses=True)
    host = os.getenv("REDIS_HOST", "127.0.0.1")
    port = int(os.getenv("REDIS_PORT", "6379"))
    db = int(os.getenv("REDIS_DB", "0"))
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)

r = get_redis_client()

def redis_incr(key):
    try:
        return r.incr(key)
    except redis.exceptions.RedisError:
        return None

def redis_get_int(key):
    try:
        val = r.get(key)
        return int(val) if val is not None else 0
    except redis.exceptions.RedisError:
        return 0

# Count each unique visitor once per session
@app.before_request
def count_unique_session():
    if not session.get("counted"):
        redis_incr("visits")
        session["counted"] = True

# ---------- Stickers ----------
def get_sticker_urls():
    folder = os.path.join(app.static_folder, "img", "stickers")
    if not os.path.isdir(folder):
        return []
    exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in exts]
    files.sort()
    return [url_for("static", filename=f"img/stickers/{name}") for name in files]

# Globals for all templates
@app.context_processor
def inject_globals():
    return {
        "sticker_urls": get_sticker_urls(),
        "MEET_LINK": os.getenv("MEET_LINK", "#"),
        "visit_count": redis_get_int("visits"),
    }

# ---------- Menus (NEW: Specialty + expanded sets) ----------
COFFEE_CLASSICS = [
    {"name": "Espresso",         "desc": "30ml, bold, no nonsense.",         "price": 2.50},
    {"name": "Americano",        "desc": "Espresso + hot water.",            "price": 3.00},
    {"name": "Latte",            "desc": "Espresso + steamed milk.",         "price": 3.50},
    {"name": "Cappuccino",       "desc": "Balanced foam & milk.",            "price": 3.50},
    {"name": "Flat White",       "desc": "Silky microfoam finish.",          "price": 3.80},
]
COFFEE_SPECIALTY = [
    {"name": "Arabic Coffee",    "desc": "Light roast, cardamom aroma.",     "price": 3.80},
    {"name": "French Press",     "desc": "Full-bodied immersion brew.",      "price": 4.00},
    {"name": "Turkish Coffee",   "desc": "Finely ground, strong & sweet.",   "price": 3.50},
    {"name": "Strawberry Matcha","desc": "Ceremonial matcha + strawberry.",  "price": 4.80},
]

PASTRY_CAKES = [
    {"name": "Lemon Cheesecake",     "desc": "Bright citrus, creamy finish.",        "price": 3.90},
    {"name": "Blueberry Cheesecake", "desc": "Bursting berries, buttery base.",      "price": 3.90},
    {"name": "Tiramisu",             "desc": "Mascarpone, espresso-soaked ladyfingers.","price": 4.20},
    {"name": "Orange Cake",          "desc": "Zesty glaze, tender crumb.",           "price": 3.20},
    {"name": "Banana Cupcake",       "desc": "Moist banana, light frosting.",        "price": 1.80},
]
PASTRY_TARTS_ICE = [
    {"name": "Fruit Tart",           "desc": "Seasonal fruit, vanilla cream.",       "price": 3.50},
    {"name": "Dark Chocolate Tart",  "desc": "70% cocoa ganache.",                   "price": 3.80},
    {"name": "Ice Cream Scoop",      "desc": "Vanilla / chocolate / strawberry.",    "price": 1.80},
]
PASTRY_CLASSICS = [
    {"name": "Croissant",            "desc": "Buttery layers, daily bake.",          "price": 2.00},
    {"name": "Pain au Chocolat",     "desc": "Classic bar of dark chocolate.",       "price": 2.20},
    {"name": "Cinnamon Roll",        "desc": "Warm glaze & spice.",                  "price": 2.40},
    {"name": "Cookies",              "desc": "Daily flavors; crisp edges, soft center.","price": 1.50},
]
PASTRY_PINOY = [
    {"name": "Puto",                 "desc": "Steamed rice cake.",                   "price": 1.20},
    {"name": "Kuchinta",             "desc": "Brown sugar rice cake.",               "price": 1.20},
    {"name": "Biko",                 "desc": "Sticky rice + coconut.",               "price": 1.50},
    {"name": "Leche Flan",           "desc": "Silky caramel custard.",               "price": 2.50},
    {"name": "Maja Blanca",          "desc": "Coconut milk pudding.",                "price": 1.80},
    {"name": "Ginataang",            "desc": "Coconut milk sweet porridge.",         "price": 2.50},
    {"name": "Champorado",           "desc": "Chocolate rice porridge.",             "price": 2.50},
    {"name": "Suman",                "desc": "Sticky rice in banana leaf.",          "price": 1.50},
]

# ---------- Tab helpers ----------
def get_tab(): return session.setdefault("tab", [])
def save_tab(tab): session["tab"] = tab
def add_to_tab(name, price):
    tab = get_tab()
    for item in tab:
        if item["name"] == name:
            item["qty"] += 1
            save_tab(tab)
            return
    tab.append({"name": name, "price": float(price), "qty": 1})
    save_tab(tab)
def clear_tab(): session["tab"] = []

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html", theme="landing")

@app.route("/coffee")
def coffee():
    groups = [
        {"title": "Specialty Coffee", "items": COFFEE_SPECIALTY},
        {"title": "Classics",         "items": COFFEE_CLASSICS},
    ]
    # background filename handled in template via `theme`
    return render_template("menu.html",
                           title="Coffee Menu", icon="☕",
                           groups=groups, theme="coffee")

@app.route("/pastries")
def pastries():
    groups = [
        {"title": "Cakes & Cheesecakes", "items": PASTRY_CAKES},
        {"title": "Tarts & Ice Cream",   "items": PASTRY_TARTS_ICE},
        {"title": "Pastry Classics",     "items": PASTRY_CLASSICS},
        {"title": "Pinoy Favorites",     "items": PASTRY_PINOY},
    ]
    return render_template("menu.html",
                           title="Pastries Menu", icon="🥐",
                           groups=groups, theme="pastries")

@app.route("/add", methods=["POST"])
def add_item():
    name = request.form.get("name")
    price = request.form.get("price")
    ref = request.form.get("ref") or url_for("index")
    if name and price:
        add_to_tab(name, price)
    return redirect(ref)

@app.route("/tab")
def tab_view():
    tab = get_tab()
    total = sum(i["price"] * i["qty"] for i in tab)
    return render_template("tab.html", tab=tab, total=total, theme="landing")

@app.route("/pay")
def pay():
    tab = get_tab()
    total = sum(i["price"] * i["qty"] for i in tab)
    clear_tab()
    return render_template("paid.html", total=total, theme="landing")

# Spec test endpoint — increments and shows value
@app.route("/count")
def count():
    val = redis_incr("visits")
    return f"visits: {val if val is not None else redis_get_int('visits')}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
