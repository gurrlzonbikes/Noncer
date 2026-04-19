# Noncer

Control what agents can do, when they can do it, and how many times.

---

## Why this exists

CI pipelines and autonomous agents are increasingly powerful—and increasingly unsafe.

They:

* hold long-lived secrets
* execute high-impact actions
* are hard to stop once triggered

Today’s model is:

```text
if you have the key → you can do everything
```

That doesn’t scale to autonomous systems.

---

## What Noncer does

Noncer replaces static permissions with **deterministic execution control**.

Every action must:

```text
1. come from a valid identity
2. be allowed right now
3. be the next expected action
```

---

## Core model

```text
Auth = identity + eligibility + nonce
```

* **Identity** → who is acting (agent key)
* **Eligibility** → are they allowed right now (server-controlled)
* **Nonce** → is this the correct next action (no replay, no skipping)

---

## Architecture

```text
Agent (CLI)
   ↓
Noncer Server (control layer)
   ↓
Protected command / system
```

* Server owns **nonce state**
* Server enforces **eligibility**
* CLI acts as a **thin execution wrapper**

---

## Features

* 🔐 No API keys or shared secrets
* 🔁 Replay protection via nonce
* ⚡ Instant revocation (real-time eligibility)
* 🎯 Deterministic execution order

---

## Installation

```bash
git clone https://github.com/<your-username>/noncer.git
cd noncer

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

---

## Running the server

```bash
python server/app.py
```

Server runs on:

```text
http://localhost:3000
```

---

## Usage

### Allow your agent

```bash
noncer allow
```

---

### Execute a command

```bash
noncer exec -- echo hello
```

---

### Revoke access

```bash
noncer revoke
```

---

## Example

```bash
noncer allow
noncer exec -- echo "step 1"
noncer exec -- echo "step 2"
noncer revoke
noncer exec -- echo "step 3"
```

Expected:

```text
✅ Authorized → step 1
✅ Authorized → step 2
❌ Blocked: revoked
```

---

## What this demonstrates

* commands cannot be replayed
* commands cannot be executed out of order
* access can be revoked instantly
* no secrets are required
