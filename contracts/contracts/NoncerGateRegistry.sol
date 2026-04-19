// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title NoncerGateRegistry
 * @notice Holds RUNNER_ROLE for addresses allowed to trigger the Noncer gate.
 *         DEFAULT_ADMIN_ROLE (typically a multisig) grants/revokes runners — revoke is the killswitch.
 */
contract NoncerGateRegistry is AccessControl {
    bytes32 public constant RUNNER_ROLE = keccak256("RUNNER");

    constructor(address admin) {
        if (admin == address(0)) revert();
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    /// @notice Grant runner eligibility to `account`.
    function grantRunner(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(RUNNER_ROLE, account);
    }

    /// @notice Revoke gate eligibility immediately (killswitch for `account`).
    function revokeRunner(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _revokeRole(RUNNER_ROLE, account);
    }
}
