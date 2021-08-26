https://www.youtube.com/watch?v=xWFba_9QYmc&list=WL&index=12
1:53

$ truffle version
Truffle v5.1.64 (core: 5.1.64)
Solidity v0.5.16 (solc-js)
Node v12.21.0
Web3.js v1.2.9

https://github.com/dappuniversity/dbank/tree/starter_kit
https://github.com/dappuniversity/dbank/tree/borrow_lend

$ npm install
$ truffle compile
$ truffle migrate
$ truffle migrate --reset
$ truffle console
truffle(development)> const token = await Token.deployed()
truffle(development)> token 
truffle(development)> token.address
truffle(development)> token.name()
truffle(development)> token.symbol()
truffle(development)> token.totalSupply()
truffle(development)> web3.eth.getAccounts()
truffle(development)> const accts = web3.eth.getAccounts()
truffle(development)> accts 
truffle(development)> account = accts[0]
truffle(development)> account 
truffle(development)> web3.eth.getBalance(account)
truffle(development)> bal = web3.eth.getBalance(account)
truffle(development)> bal
truffle(development)> token.decimals()
truffle(development)> dec = await token.decimals()
truffle(development)> dec.toString()
truffle(development)> bal = await token.balanceOf(account)
truffle(development)> etherBalance = await web3.eth.getBalance(account)
truffle(development)> etherBalance.toString()
truffle(development)> web3.utils.fromWei(etherBalance)
truffle(development)> web3.utils.toWei(web3.utils.fromWei(etherBalance))
truffle(development)> token.mint(account, web3.utils.toWei(web3.utils.fromWei(etherBalance)))
truffle(development)> tokenBalance = await token.balanceOf(account)
truffle(development)> tokenBalance 
truffle(development)> tokenBalance.toString()
truffle(development)> web3.utils.fromWei(tokenBalance)
truffle(development)> totalSupply = await token.totalSupply()
truffle(development)> web3.utils.fromWei(totalSupply)


$ cat test/test.js
$ truffle test

$ sudo npm install -g npm@latest
$ sudo npm install -g react-scripts
$ npm run start
http://localhost:3000/