# Noncer

**Noncer** is a small **gate** in front of a real process on a machine you run. A high-stakes action only runs if a **Ledger**-backed key has signed a structured **intent** (EIP-712), a **public chain** still says the sender is **allowed** via an **AccessControl** registry (`hasRole`), the **next** application **nonce** matches what the gate expects, and the signed `action` is only a **key** into a local **allow-list** of fixed `argv` (no shell). That stack is a way to think about **governed automation** without making that one path depend on a long-lived **bearer API key** for authorization.

It is **opinionated and heavy** on purpose: keys, chain, and a second device flow. That is a bad trade for “run tests on every push” and a reasonable trade for “this run can do real damage or touch real data if it is the wrong person or the wrong order.”

---

## Problem / non-goals

**What it is trying to address**

- Pipelines and agents often get **broad secrets**; anyone with the token can do a lot.
- **Revocation** and “who was allowed when” are easy to lose in a pile of internal configs.
- You may want a **dumb executor** (the gate) that does not implement your org’s full policy in custom code—only checks you can state **from the outside** (signer, on-chain flag, sequence, then a **fixed** local command table).

**What it is *not* (use something else)**

- **Not** a drop-in for **OIDC / workload identity** for normal CI or SaaS login at scale.
- **Not** a **privacy** system: relevant txs and addresses are **public** on the chain you use.
- **Not** optimized for **latency** or **volume** (Ledger + RPC + confirmation).

**When to bother**

If the worst case is “the pipeline turns red,” you probably do not need this shape. If the worst case is “wrong human or wrong order runs **this** binary against **that** environment,” the split above is what this repo is experimenting with.

---

## Mechanism (bullet map)

- **Identity:** EIP-712 `Intent(nonce, action, policyCommitment)` + broadcast tx → both signed on Ledger (`action` = allow-list **key**, not argv).
- **Live allow:** OpenZeppelin-style `hasRole(RUNNER_ROLE, sender)` on **`NoncerGateRegistry`** (**killswitch:** admin calls `revokeRunner(sender)` — see `contracts/`).
- **Ordering:** Gate stores next **application nonce** per address; bumps only after successful argv run.
- **Execution:** `allowlist.json` maps keys → argv; `subprocess` **without** shell.

**Calldata v1:** `0x01 || abi.encode(nonce, action, policyCommitment, v, r, s)` — gate recovers EIP-712 signer, requires `recover == tx.from`, then eligibility + nonce + argv.

**Flow:** `noncer emit` → Ledger ×2 → Base Sepolia · `noncer-watch` → decode → verify → allow-list argv · HTTP `GET /nonce` for expected nonce.

---

## Allow-list (required)

Default: `~/.noncer/allowlist.json` · override: `--allowlist` / `NONCER_ALLOWLIST`

```json
{"commands": {"echo-demo": ["/bin/echo", "hello"], "true-cmd": ["/bin/true"]}}
```

Optional: `--strict-executable` / `NONCER_STRICT_EXECUTABLE=1` (require `argv[0]` exists + executable).

---

## Prerequisites

- Python ≥3.10, `npm install` at repo root (Ledger signer), Ledger (Ethereum app, typed data).
- Base Sepolia **gas**; deploy **`NoncerGateRegistry`** and **`grantRunner`** your emitter address.
- Default RPC `https://sepolia.base.org`, chain `84532`.

### Registry deploy

See **`contracts/README.md`**: Hardhat + OpenZeppelin `AccessControl`; constructor sets **admin** (use a multisig). Admin grants **`grantRunner(0xEmitter)`**; emergency **`revokeRunner(0xEmitter)`** removes eligibility without touching the gate host.

---

## Install

```bash
git clone https://github.com/<your-org>/noncer.git && cd noncer
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
npm install
```

---

## Env (common)

| Var / flag | Role |
|------------|------|
| `NONCER_STATE_DIR` | State + default allow-list dir (`~/.noncer`) |
| `NONCER_ALLOWLIST` | Allow-list path |
| `NONCER_RPC_URL` / `NONCER_CHAIN_ID` | RPC / chain (default Sepolia Base) |
| `NONCER_GATE_URL` | Nonce HTTP for CLI (default `http://127.0.0.1:3090`) |
| `NONCER_EIP712_*`, `NONCER_VERIFYING_CONTRACT` | Must match between **emit** and **watch** |
| `NONCER_POLICY_*`, `NONCER_EXPECTED_POLICY_COMMITMENT` | Optional policy bytes32 binding |
| `NONCER_REGISTRY_CONTRACT` | Registry address (`--registry-contract`) |
| `NONCER_RUNNER_ROLE` | Optional bytes32 hex for `hasRole` (default `keccak256("RUNNER")`) |

---

## Run

**Gate**

```bash
noncer-watch --registry-contract 0xYourDeployedRegistry
```

**Emit** (`--action` = allow-list key)

```bash
noncer emit --address 0x… --derivation-path "44'/60'/0'/0/0" \
  --action echo-demo \
  --policy-commitment 0x0000000000000000000000000000000000000000000000000000000000000000
```

Watcher up for `/nonce`, or pass `--nonce N`.

---

## Status

Experimental—harden RPC trust, `/nonce` exposure, and policy for non-lab use.
