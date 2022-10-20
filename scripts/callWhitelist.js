const hre = require("hardhat");
const abi = require("../artifacts/contracts/FlatLaunchpegMini.sol/FlatLaunchpegMini.json")['abi'];
const fujiContractAddress = "0xDa294c40c0c64d9d3b4937f9C3DdbAe0A7e7C0DF";
const avalancheContractAddress = "0xBb8B9bDf061F43894E491aa579d6Fcdeaa735D0A";

// set whitelist for NFT contract
async function main() {

  let flatLaunchpeg;
  let toWhitelist = ["0x8fBBEBA1A22fA1D176F9AaAC138DD200c0b4e71C","0xBaE02a23abFA62D5EA59c6c72a3F91888f850267","0xb00012F2785E50A4135B1450E2D6C32F3053efF7"];
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
