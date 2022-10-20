const hre = require("hardhat");

// deploy the reduced FlatLaunchpeg contract
async function main() {

  const FlatLaunchpeg = await hre.ethers.getContractFactory("FlatLaunchpegMini");
  const flatLaunchpeg = await FlatLaunchpeg.deploy();
  await flatLaunchpeg.deployed();

  console.log(`Deployed FlatLaunchpeg at address: ${flatLaunchpeg.address}, on the network: ${hre.network.name}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
