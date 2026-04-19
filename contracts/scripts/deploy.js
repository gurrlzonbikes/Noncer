const hre = require("hardhat");

async function main() {
  const admin = process.env.ADMIN_ADDRESS;
  if (!admin) {
    throw new Error("Set ADMIN_ADDRESS (multisig or deployer wallet) before deploy.");
  }

  const Factory = await hre.ethers.getContractFactory("NoncerGateRegistry");
  const registry = await Factory.deploy(admin);
  await registry.waitForDeployment();

  console.log("NoncerGateRegistry:", await registry.getAddress());
  console.log("RUNNER_ROLE:", await registry.RUNNER_ROLE());
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
