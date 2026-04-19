from flask import Flask, request, jsonify

app = Flask(__name__)

# --- authoritative state
nonces = {}
allowed = set()

# --- demo: allow one address
# you can replace later
# allowed.add("0x...")

@app.route("/auth", methods=["POST"])
def auth():
    address = request.json["address"]

    if address not in allowed:
        return "not eligible", 403

    nonces.setdefault(address, 0)
    return jsonify({"ok": True})


@app.route("/nonce", methods=["GET"])
def get_nonce():
    address = request.args.get("address")
    return jsonify({"nonce": nonces.get(address, 0)})


@app.route("/execute", methods=["POST"])
def execute():
    data = request.json
    address = data["address"]
    nonce = data["nonce"]
    action = data["action"]

    # 1. eligibility
    if address not in allowed:
        return "revoked", 403

    # 2. nonce
    expected = nonces.get(address, 0)
    if nonce != expected:
        return f"bad nonce (expected {expected})", 400

    # 3. (signature check later)
    print(f"EXECUTING: {action}")

    # 4. increment
    nonces[address] = expected + 1

    return jsonify({"ok": True})


@app.route("/allow", methods=["POST"])
def allow_addr():
    address = request.json["address"]
    allowed.add(address)
    return {"allowed": True}


@app.route("/revoke", methods=["POST"])
def revoke_addr():
    address = request.json["address"]
    allowed.discard(address)
    return {"revoked": True}


if __name__ == "__main__":
    app.run(port=3000)