/** 
 * @type import('hardhat/config').HardhatUserConfig 
 */

const dotenv = require("dotenv");
dotenv.config({path:'.env'}); // load env vars from .env
require("@nomicfoundation/hardhat-toolbox");

const MAINNET_RPC_URL = process.env.MAINNET_RPC_URL;
const TESTNET_RPC_URL = process.env.TESTNET_RPC_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY;

module.exports = {
    defaultNetwork: "hardhat",
    networks: {
        hardhat: {
            forking: {
               url: MAINNET_RPC_URL,
               blockNumber: 21246389
            }
        },
        avalanche: {
            url: MAINNET_RPC_URL,
            chainId: 43114,
            accounts: [`0x${PRIVATE_KEY}`],
            saveDeployments: true,
        },
        fuji: {
            url: TESTNET_RPC_URL,
            chainId: 43113,
            accounts: [`0x${PRIVATE_KEY}`],
            saveDeployments: true,
        },
    },
    solidity: {
        compilers: [
            {
                version: "0.8.6"
            },
        ]
    },
    mocha: {
        timeout: 300000
    }
}