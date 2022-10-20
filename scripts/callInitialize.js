const hre = require("hardhat");
const abi = require("../artifacts/contracts/FlatLaunchpegMini.sol/FlatLaunchpegMini.json")['abi'];
const fujiContractAddress = "0xDa294c40c0c64d9d3b4937f9C3DdbAe0A7e7C0DF";
const avalancheContractAddress = "0x";

// set whitelist for NFT contract
async function main() {

  let flatLaunchpeg;

  let currentUnixTime = Math.floor(Date.now()/1000);

  let _allowlistStartTime = currentUnixTime+20;
  let _publicSaleStartTime = currentUnixTime+30*60;
  let _allowlistPrice = 0;
  let _salePrice = 1e9;
  
  // console.log((await hre.ethers.getSigners()).address) // deployer address

  if (hre.network.name == "fuji") { // testnet

    let flatLaunchpeg = await hre.ethers.getContractAt(abi,fujiContractAddress);
    await flatLaunchpeg.initializePhases(_allowlistStartTime,_publicSaleStartTime,_allowlistPrice,_salePrice);
    console.log(fujiContractAddress,";","initialized",_allowlistStartTime);

  } else { // mainnet

    let flatLaunchpeg = await hre.ethers.getContractAt(abi,avalancheContractAddress);
    await flatLaunchpeg.initializePhases(_allowlistStartTime,_publicSaleStartTime,_allowlistPrice,_salePrice);
    console.log(avalancheContractAddress,";","initialized",_allowlistStartTime);
    
  }

}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
