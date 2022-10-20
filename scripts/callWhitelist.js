const hre = require("hardhat");
const abi = require("../artifacts/contracts/FlatLaunchpegMini.sol/FlatLaunchpegMini.json")['abi'];
const fujiContractAddress = "0xDa294c40c0c64d9d3b4937f9C3DdbAe0A7e7C0DF";
const avalancheContractAddress = "0x";

// set whitelist for NFT contract
async function main() {

  let flatLaunchpeg;
  let toWhitelist = ["0x8fBBEBA1A22fA1D176F9AaAC138DD200c0b4e71C"];
  let whitelistAmount = 10;
  // console.log((await hre.ethers.getSigners()).address) // deployer address

  if (hre.network.name == "fuji") { // testnet

    let flatLaunchpeg = await hre.ethers.getContractAt(abi,fujiContractAddress);
    await flatLaunchpeg.setAllowlist(toWhitelist,whitelistAmount);
    console.log(toWhitelist[0],";",await flatLaunchpeg.allowlist(toWhitelist[0]));

  } else { // mainnet

    let flatLaunchpeg = await hre.ethers.getContractAt(abi,avalancheContractAddress);
    await flatLaunchpeg.setAllowlist(toWhitelist,whitelistAmount);
    console.log(toWhitelist[0],";",await flatLaunchpeg.allowlist(toWhitelist[0]));
    
  }

}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
