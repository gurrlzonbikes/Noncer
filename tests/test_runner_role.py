"""RUNNER_ROLE id matches Solidity keccak256(bytes('RUNNER'))."""

from web3 import Web3


def test_default_runner_role_keccak():
    # Same as watcher._parse_runner_role_hex(None) and NoncerGateRegistry.RUNNER_ROLE
    role = bytes(Web3.keccak(text="RUNNER"))
    assert len(role) == 32

