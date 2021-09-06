import json, struct, requests
from web3 import Web3
from web3 import exceptions
from eth_account import account
from flask import Flask, render_template, request, redirect, url_for, flash, Markup

# Global variables
_tokenContract = ''
_dbankContract = ''

# Load Blockchain Data
def loadBlockchain():  
  global web3, account
  ganache_url = 'http://127.0.0.1:8545'  
  web3 = Web3(Web3.HTTPProvider(ganache_url))
  # print("Web3 Connection: ", web3.isConnected())
  netId = web3.eth.chain_id
  # print(netId)        
  web3.eth.defaultAccount = web3.eth.accounts[0]
  account = web3.eth.defaultAccount
  # print(web3.eth.defaultAccount)  
  _global_principal_address = account
  _global_principal_ether_balance = toEther(web3.eth.get_balance(web3.eth.defaultAccount))
  _global_principal_usd_balance = toUSD(web3.eth.get_balance(web3.eth.defaultAccount))
  # print(_global_principal_ether_balance)
  return _global_principal_address, _global_principal_ether_balance, _global_principal_usd_balance

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
  global _tokenContract
  _tokenContract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI, bytecode=BYTECODE)
  
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
  global _dbankContract  
  _dbankContract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI, bytecode=BYTECODE)

# Function to convert a float into hex
def float_to_hex(f):
    return hex(struct.unpack('<I', struct.pack('<f', f))[0])

# Function to convert-to-ether
def toEther(balance):    
    return web3.fromWei(balance, 'ether')

# Function to convert-to-wei
def toWei(balance):    
    return web3.toWei(balance, 'ether')

# Get the current USD price of cryptocurrency conversion from API URL
API_URL = 'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=ETH,USD'
apiReq = requests.get(API_URL)
USD_CURRENT_PRICE=json.loads(apiReq.content)["USD"] 

# Function to return USD conversion values
def toUSD(balance):
    usd_sum = round(USD_CURRENT_PRICE * float(toEther(balance)), 2)    
    return usd_sum

# Set a new deposit funds
def deposit(amount):  
  # Local variables
  _deposit_txReceipt = ''
  _deposit_ether_amount = 0
  _deposit_usd_amount = 0
  _deposit_Transaction = ''
  _deposit_BlockNum = 0
  # print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)')  
  # print(f'Deposit amount: {amount}(ETH)')      
  if(amount < 0.01):     
    print('Deposit amount must be more than 0.01(ETH)\n')      
  else:        
    # Convert-to-wei    
    amount_in_wei = toWei(amount)     
    try:
      # In try block call dBank deposit();            
      deposit_txHash = _dbankContract.functions.deposit().transact({'from': web3.toChecksumAddress(account), 'value': amount_in_wei}) 
      # Wait for transaction to be mined
      _deposit_txReceipt = web3.eth.waitForTransactionReceipt(deposit_txHash)        
      _deposit_ether_amount = toEther(web3.eth.getTransaction(deposit_txHash)['value'])
      _deposit_usd_amount = toUSD(web3.eth.getTransaction(deposit_txHash)['value'])      
      _deposit_Transaction = web3.toHex(_deposit_txReceipt['transactionHash'])
      _deposit_BlockNum = _deposit_txReceipt['blockNumber']
      # print(f"From: {_deposit_txReceipt['from']} To: {_deposit_txReceipt['to']}")
      # print(f"Deposit Amount on Wei: {web3.eth.getTransaction(deposit_txHash)['value']} & Ether: {toEther(web3.eth.getTransaction(deposit_txHash)['value'])}") 
      # print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)\n')  
      # print(f"Transaction: {web3.toHex(_deposit_txReceipt['transactionHash'])} Block Number: {_deposit_txReceipt['blockNumber']}\n")       
    except exceptions.SolidityError as error:
      # print(error)       
      message = Markup(f'Error - Deposit has already taken previously.<br> {error}<br>') 
      flash(message, 'exceptErrorMsg')   
  return _deposit_txReceipt, _deposit_ether_amount, _deposit_usd_amount, _deposit_Transaction, _deposit_BlockNum

# Call a new withdrawAll funds
def withdrawAll(): 
  # Local variables
  _withdraw_txReceipt = ''
  _withdraw_BlockNum = ''
  _withdraw_Status = 0  
  # print(f'Withdraw all deposit amount.')      
  try:
    # In try block call dBank withdraw(); 
    withdraw_txHash = _dbankContract.functions.withdraw().transact({'from': web3.toChecksumAddress(account)})      
    # Wait for transaction to be mined
    _withdraw_txReceipt = web3.eth.waitForTransactionReceipt(withdraw_txHash)
    # print(f'Withdrawal completed to account: {web3.toChecksumAddress(account)}')    
    # print(f"From: {_withdraw_txReceipt['from']}, To: {_withdraw_txReceipt['to']}")    
    # print(f"TransactionHash--> {web3.eth.getTransaction(withdraw_txHash)}\n")    
    _withdraw_Transaction = web3.toHex(_withdraw_txReceipt['transactionHash'])
    _withdraw_BlockNum = _withdraw_txReceipt['blockNumber']    
    _withdraw_Status = _withdraw_txReceipt['status']  
  except exceptions.SolidityError as error:
      # print(error)
      message = Markup(f'Error - WithdrawAll has already taken previously.<br> {error}<br>') 
      flash(message, 'exceptErrorMsg')
  return _withdraw_txReceipt, _withdraw_BlockNum, _withdraw_Status

# Call a new withdraw funds
def withdraw(amount):     
  print(f'Withdraw amount: {amount}(ETH)')  
  if(amount < 0.01):     
    print('Deposit amount must be more than 0.01(ETH)')      
  else:
    # Convert-to-wei    
    amount_in_wei = toWei(amount)   
    try:
      # In try block call dBank withdraw(); 
      withdraw_txHash = _dbankContract.functions.withdraw().transact({'from': web3.toChecksumAddress(account)})      
      # Wait for transaction to be mined
      withdraw_txReceipt = web3.eth.waitForTransactionReceipt(withdraw_txHash)
      print(f'Withdrawal completed to account): {web3.toChecksumAddress(account)}')    
      print(f"From: {withdraw_txReceipt['from']}, To: {withdraw_txReceipt['to']}")
      print(withdraw_txReceipt)
      print(f"TransactionHash--> {web3.eth.getTransaction(withdraw_txHash)}\n")      
      # print(f"Withdrawal Amount on Wei: {web3.eth.getTransaction(withdraw_txHash)['value']} on Ether: {toEther(web3.eth.getTransaction(withdraw_txHash)['value'])} \n")          
    except exceptions.SolidityError as error:
        print(error)
        message = Markup(f'Error - There has no deposit previously.<br> {error}<br>') 
        flash(message, 'exceptErrorMsg')

# Set a new borrow funds
def borrow(amount):
  print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)')  
  print(f'Borrow amount: {amount}(ETH)')      
  if(amount < 0.01):    
    print('Borrow amount must be more than 0.01(ETH)\n')  
  else:  
    # Convert-to-wei    
    amount_in_wei = toWei(amount)   
    try:
      # In try block call dBank borrow();      
      borrow_txHash = _dbankContract.functions.borrow().transact({'from': web3.toChecksumAddress(account), 'value': amount_in_wei})  
      # Wait for transaction to be mined
      borrow_txReceipt = web3.eth.waitForTransactionReceipt(borrow_txHash)
      print(borrow_txReceipt)
      print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)\n')  
    except exceptions.SolidityError as error:
      print(error) 
      message = Markup(f'Error - Borrow has already taken previously.<br> {error}<br>')
      flash(message, 'exceptErrorMsg')

# Call a new payOff funds
def payOffAll():  
  collateralEther = _dbankContract.functions.collateralEther(web3.toChecksumAddress(account)).call({'from': web3.toChecksumAddress(account)})    
  tokenBorrowed = collateralEther/2    
  # Convert-to-wei    
  amount_in_wei = toWei(tokenBorrowed)
  # {IERC20-allowance} : allowance(address owner, address spender)
  _tokenContract.functions.allowance(web3.toChecksumAddress(_dbankContract.address), web3.toChecksumAddress(account)).call({'from': web3.toChecksumAddress(account)})
  try:
    # In try block call dBank approve(); address owner, address spender, uint256 amount
    # {IERC20-approve} : approve(address spender, uint256 amount)      
    approve_txHash = _tokenContract.functions.approve(web3.toChecksumAddress(_dbankContract.address), amount_in_wei).transact({'from': web3.toChecksumAddress(account)}) 
    # Wait for transaction to be mined  
    web3.eth.waitForTransactionReceipt(approve_txHash)  
    # In try block call dBank payOff();
    payOff_txHash = _dbankContract.functions.payOff().transact({'from': web3.toChecksumAddress(account)})  
    # Wait for transaction to be mined    
    payOff_txReceipt = web3.eth.waitForTransactionReceipt(payOff_txHash)  
    print(payOff_txReceipt)    
    print(f'Balance amount: {toEther(web3.eth.getBalance(account))}(ETH)\n')  
  except exceptions.SolidityError as error:
      print(error)    
      message = Markup(f'Error - There has no loans previously.<br> {error}<br>') 
      flash(message, 'exceptErrorMsg')

# Init function to load blockchains
def __init__():
  account_details = loadBlockchain()  
  loadTokenContract()
  loadDbankContract()
  return account_details
               
# Flask http web display
app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = '12345$'

@app.route('/', methods=['GET', 'POST'])
def index():  
  account_details = __init__()
  return render_template('index.html', value0=account_details[0], value1=account_details[1], value2=account_details[2]) 

@app.route('/Deposit', methods=['GET'])
def Deposit():        
    return render_template('deposit_process.html')

@app.route('/depositProcess', methods=['POST'])
def depositProcess():    
    __init__()
    depositValue = float(request.form['depositAmount'])
    depositReceipt = deposit(depositValue)    
    if depositReceipt[0] is None or depositReceipt[0] == '':
        return redirect(url_for('Deposit'))
    depositReceiptMsg = Markup(f'Deposit to Ethereum dBank: {depositReceipt[0]["to"]}<br>Ethereum Amount: {depositReceipt[1]} = USD Amount: {depositReceipt[2]}<br>Transaction: {depositReceipt[3]} , Block Number: {depositReceipt[4]}')
    return render_template('deposit_process.html', value0=depositReceiptMsg)
   
@app.route('/Withdraw', methods=['GET'])
def Withdraw():        
    return render_template('withdraw_process.html')

@app.route('/withdrawProcess', methods=['POST'])
def withdrawProcess(): 
    __init__()
    withdrawReceipt = withdrawAll()
    if withdrawReceipt is None or withdrawReceipt == '':
        return redirect(url_for('Withdraw'))
    # withdrawReceiptMsg = Markup(f'WithdrawAll to {withdrawReceipt[0]["to"]}<br>Ether: {withdrawReceipt[1]} = USD: {withdrawReceipt[2]} <br>')
    withdrawReceiptMsg = Markup(f'{withdrawReceipt}<br>')
    return render_template('withdraw_process.html', value0=withdrawReceiptMsg)         

@app.route('/Borrow', methods=['GET'])
def Borrow():        
    return render_template('borrow_process.html')

@app.route('/borrowProcess', methods=['POST'])
def borrowProcess():    
    __init__()
    # borrowValue = float(request.form['borrowAmount'])
    # borrowReceipt = borrow(borrowValue)        
    return redirect(url_for('Borrow'))    

@app.route('/Payoff', methods=['GET'])
def Payoff():        
    return render_template('payoff_process.html')

@app.route('/payOffProcess', methods=['POST'])
def payOffProcess():    
    __init__()
    payOffAll()
    return redirect(url_for('Payoff'))    

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
#   payOffAll()

