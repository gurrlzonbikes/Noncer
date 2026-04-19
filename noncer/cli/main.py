import sys
import os
import json
import requests
import subprocess
import secrets

SERVER = "http://localhost:3000"

# ----------------------
# Identity management
# ----------------------

BASE = os.path.expanduser("~/.noncer")
IDENTITY_FILE = os.path.join(BASE, "identity.json")

os.makedirs(BASE, exist_ok=True)


def load_identity():
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE) as f:
            return json.load(f)

    identity = {"address": secrets.token_hex(20)}

    with open(IDENTITY_FILE, "w") as f:
        json.dump(identity, f)

    return identity


# ----------------------
# Server helpers
# ----------------------

def bootstrap(address):
    requests.post(f"{SERVER}/auth", json={"address": address})


def get_nonce(address):
    r = requests.get(f"{SERVER}/nonce", params={"address": address})
    return r.json().get("nonce", 0)


def execute_request(address, nonce, action, signature):
    return requests.post(
        f"{SERVER}/execute",
        json={
            "address": address,
            "nonce": nonce,
            "action": action,
            "sig": signature,
        },
    )


def allow(address):
    requests.post(f"{SERVER}/allow", json={"address": address})


def revoke(address):
    requests.post(f"{SERVER}/revoke", json={"address": address})


# ----------------------
# Commands
# ----------------------

def cmd_allow(address):
    allow(address)
    print("✅ Allowed:", address)


def cmd_revoke(address):
    revoke(address)
    print("🚫 Revoked:", address)


def cmd_status(address):
    nonce = get_nonce(address)
    print("🔍 Status")
    print("Address :", address)
    print("Nonce   :", nonce)


def cmd_exec(address, args):
    if "--" not in args:
        print("Usage: noncer exec -- <command>")
        sys.exit(1)

    sep = args.index("--")
    command = args[sep + 1:]
    action = " ".join(command)

    # 1. bootstrap
    bootstrap(address)

    # 2. nonce
    nonce = get_nonce(address)

    # 3. sign (mock for now)
    signature = f"signed({address}:{nonce}:{action})"

    # 4. execute request
    r = execute_request(address, nonce, action, signature)

    if r.status_code != 200:
        print("❌ Blocked:", r.text)
        sys.exit(1)

    print(f"✅ Authorized (nonce={nonce}) → {action}")

    # 5. run command
    subprocess.run(command)


# ----------------------
# Main entrypoint
# ----------------------

def main():
    identity = load_identity()
    address = identity["address"]

    if len(sys.argv) < 2:
        print("Usage: noncer [allow|revoke|exec|status]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "allow":
        cmd_allow(address)

    elif cmd == "revoke":
        cmd_revoke(address)

    elif cmd == "status":
        cmd_status(address)

    elif cmd == "exec":
        cmd_exec(address, sys.argv[1:])

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()