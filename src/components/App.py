import json, struct
from web3 import Web3
from web3 import exceptions
from eth_account import account
from flask import Flask, render_template, request, redirect

# Load Blockchain Data
def loadBlockchain():  
  ganache_url = 'http://127.0.0.1:8545'
  global web3
  web3 = Web3(Web3.HTTPProvider(ganache_url))
  # print("Web3 Connection: ", web3.isConnected())
  netId = web3.eth.chain_id
  # print(netId)
  global account
  web3.eth.defaultAccount = web3.eth.accounts[0]
  account = web3.eth.defaultAccount
  # print(web3.eth.defaultAccount)
  balance = web3.eth.get_balance(web3.eth.defaultAccount)
  # print(balance)

# Load Token Contract Data
def loadTokenContract():
  # Opening Token JSON file and returns JSON object as a dictionary
  with open('../abis/Token.json') as tokenFile:  
    info_json = json.load(tokenFile)
  # get contract ABI
  ABI = info_json["abi"]
  # get bytecode
  BYTECODE = info_json["bytecode"]
  CONTRACT_ADDRESS = info_json["networks"]["4447"]["address"]  
  # Initialize Token contract
  global tokenContract
  tokenContract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI, bytecode=BYTECODE)
  
# Load dBank Contract Data
def loadDbankContract():
  # Opening dBank JSON file and returns JSON object as a dictionary
  with open('../abis/dBank.json') as dbankFile:  
    info_json = json.load(dbankFile)
  # get contract ABI
  ABI = info_json["abi"]
  # get bytecode
  BYTECODE = info_json["bytecode"]
  CONTRACT_ADDRESS = info_json["networks"]["4447"]["address"]  
  # Initialize dBank contract
  global dbankContract  
  dbankContract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI, bytecode=BYTECODE)

# Function to convert a float into hex
def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

# Function to convert-to-ether
def toEther(balance):    
    return web3.fromWei(balance, 'ether')

# Function to convert-to-wei
def toWei(balance):    
    return web3.toWei(balance, 'ether')

# Set a new deposit funds
def deposit(amount):   
  print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)')  
  print(f'Deposit amount: {amount}(ETH)')      
  if(amount <= 0.01):     
    print('Deposit amount must be more than 0.01(ETH)\n')      
  else:        
    # Convert-to-wei    
    amount_in_wei = toWei(amount)     
    try:
      # In try block call dBank deposit();            
      deposit_txHash = dbankContract.functions.deposit().transact({'from': web3.toChecksumAddress(account), 'value': amount_in_wei}) 
      # Wait for transaction to be mined
      deposit_txReceipt = web3.eth.waitForTransactionReceipt(deposit_txHash)        
      print(f"From: {deposit_txReceipt['from']} To: {deposit_txReceipt['to']}")
      print(f"Deposit Amount on Wei: {web3.eth.getTransaction(deposit_txHash)['value']} & Ether: {toEther(web3.eth.getTransaction(deposit_txHash)['value'])}")          
      print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)\n')  
    except exceptions.SolidityError as error:
      print(error)    
      
# Call a new withdrawAll funds
def withdrawAll():     
  print(f'Withdraw all deposit amount.')      
  try:
    # In try block call dBank withdraw(); 
    withdraw_txHash = dbankContract.functions.withdraw().transact({'from': web3.toChecksumAddress(account)})      
    # Wait for transaction to be mined
    withdraw_txReceipt = web3.eth.waitForTransactionReceipt(withdraw_txHash)
    print(f'Withdrawal completed to account): {web3.toChecksumAddress(account)}')    
    print(f"From: {withdraw_txReceipt['from']}, To: {withdraw_txReceipt['to']}")
    print(withdraw_txReceipt)
    print(f"TransactionHash--> {web3.eth.getTransaction(withdraw_txHash)}\n")          
  except exceptions.SolidityError as error:
      print(error)    

# Call a new withdraw funds
def withdraw(amount):     
  print(f'Withdraw amount: {amount}(ETH)')  
  if(amount <= 0.01):     
    print('Deposit amount must be more than 0.01(ETH)')      
  else:
    # Convert-to-wei    
    amount_in_wei = toWei(amount)   
    try:
      # In try block call dBank withdraw(); 
      withdraw_txHash = dbankContract.functions.withdraw().transact({'from': web3.toChecksumAddress(account)})      
      # Wait for transaction to be mined
      withdraw_txReceipt = web3.eth.waitForTransactionReceipt(withdraw_txHash)
      print(f'Withdrawal completed to account): {web3.toChecksumAddress(account)}')    
      print(f"From: {withdraw_txReceipt['from']}, To: {withdraw_txReceipt['to']}")
      print(withdraw_txReceipt)
      print(f"TransactionHash--> {web3.eth.getTransaction(withdraw_txHash)}\n")      
      # print(f"Withdrawal Amount on Wei: {web3.eth.getTransaction(withdraw_txHash)['value']} on Ether: {toEther(web3.eth.getTransaction(withdraw_txHash)['value'])} \n")          
    except exceptions.SolidityError as error:
        print(error)

# Set a new borrow funds
def borrow(amount):
  print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)')  
  print(f'Borrow amount: {amount}(ETH)')      
  if(amount <= 0.01):    
    print('Borrow amount must be more than 0.01(ETH)\n')  
  else:  
    # Convert-to-wei    
    amount_in_wei = toWei(amount)   
    try:
      # In try block call dBank borrow();      
      borrow_txHash = dbankContract.functions.borrow().transact({'from': web3.toChecksumAddress(account), 'value': amount_in_wei})  
      # Wait for transaction to be mined
      borrow_txReceipt = web3.eth.waitForTransactionReceipt(borrow_txHash)
      print(borrow_txReceipt)
      print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)\n')  
    except exceptions.SolidityError as error:
      print(error)    

# Call a new payOff funds
def payOff():  
  collateralEther = dbankContract.functions.collateralEther(web3.toChecksumAddress(account)).call({'from': web3.toChecksumAddress(account)})    
  tokenBorrowed = collateralEther/2    
  # Convert-to-wei    
  amount_in_wei = toWei(tokenBorrowed)
  # {IERC20-allowance} : allowance(address owner, address spender)
  tokenContract.functions.allowance(web3.toChecksumAddress(dbankContract.address), web3.toChecksumAddress(account)).call({'from': web3.toChecksumAddress(account)})
  try:
    # In try block call dBank approve(); address owner, address spender, uint256 amount
    # {IERC20-approve} : approve(address spender, uint256 amount)      
    approve_txHash = tokenContract.functions.approve(web3.toChecksumAddress(dbankContract.address), amount_in_wei).transact({'from': web3.toChecksumAddress(account)}) 
    # Wait for transaction to be mined  
    web3.eth.waitForTransactionReceipt(approve_txHash)  
    # In try block call dBank payOff();
    payOff_txHash = dbankContract.functions.payOff().transact({'from': web3.toChecksumAddress(account)})  
    # Wait for transaction to be mined    
    payOff_txReceipt = web3.eth.waitForTransactionReceipt(payOff_txHash)  
    print(payOff_txReceipt)    
    print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)\n')  
  except exceptions.SolidityError as error:
      print(error)    
               
# Flask http web display
app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'
# app.config['SECRET_KEY'] = '12345'

@app.route('/')
def index():
    # initial_result = getGreetingFromBlockchain()
    return render_template('index.html')

@app.route('/Deposit', methods=['POST'])
def Deposit():
    # global _global_principal_address    
    # _global_principal_address = request.form['principle']    
    # accountImageCreation(_global_principal_address)    
    # start_block = int(request.form['fromBlk'])
    # end_block = int(request.form['toBlk']) + 1
    # listLength, From, To, EthValue, USDValue, Nonce, BlockNumber, Hash, BlockHash = txResultHistoryData(_global_principal_address, start_block, end_block, _global_principal_address)           
    # return render_template('query_display.html', value0=_global_principal_address, value1=start_block, value2=end_block, value3=listLength, value4=From, value5=To, value6=EthValue, value7=USDValue, value8=Nonce, value9=BlockNumber, value10=Hash, value11=BlockHash)
    # return redirect(url_for('AccountDashBoard'))
    depositValue = request.form['depositAmount']     
    print(depositValue)
    return render_template('deposit_process.html')

@app.route('/Withdraw', methods=['GET', 'POST'])
def Withdraw():    
    return render_template('withdraw_process.html')

@app.route('/Borrow', methods=['GET', 'POST'])
def Borrow():    
    return render_template('borrow_process.html')

@app.route('/Payoff', methods=['GET', 'POST'])
def Payoff():    
    return render_template('payoff_process.html')

# Development Debug Environment
if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)

# # Main Functions
# if __name__ == "__main__":  
#   loadBlockchain()
#   loadTokenContract()
#   loadDbankContract()  
#   deposit(10.52)       
#   withdrawAll()
#   # withdraw(10.52)
#   borrow(8.85)
#   payOff()

# https://web3py.readthedocs.io/en/stable/contracts.html#contract-deployment-example
