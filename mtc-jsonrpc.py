#!/usr/bin/env python3
# -*- coding: utf_8 -*-l

# pip3 install Werkzeug json-rpc
import secrets
from sys import path
from werkzeug.wrappers import Request, Response
from werkzeug.datastructures import Headers
from werkzeug.serving import run_simple, make_ssl_devcert
from werkzeug.security import check_password_hash, generate_password_hash
from jsonrpc import JSONRPCResponseManager, dispatcher

path.append("/usr/src/mytonctrl/")
from mytoncore import *

local = MyPyClass(__file__)
ton = MyTonCore()


class IP:
	def __init__(self, addr):
		self.addr = addr
		self.wrongNumber = 0
		self.isBlock = False
		self.token = None
		self.inputToken = None
		self.timestamp = None
		self.lifetime = 2629743 # 1 month
	#end define

	def WrongAccess(self):
		if self.wrongNumber > 5:
			self.isBlock = True
		else:
			self.wrongNumber += 1
		raise Exception(403, "Forbidden")
	#end define

	def GenerateToken(self):
		self.wrongNumber = 0
		self.token = secrets.token_urlsafe(32)
		self.timestamp = self.TS()
	#end define

	def DestroyToken(self):
		self.wrongNumber = 0
		self.token = None
		self.timestamp = None
	#end define

	def CheckAccess(self):
		if self.isBlock or self.token is None or self.timestamp is None:
			self.WrongAccess()
		timestamp = self.TS()
		isAlive = self.timestamp + self.lifetime > timestamp
		isCorrectToken = self.token == self.inputToken

		if isAlive and isCorrectToken:
			pass
		else:
			self.WrongAccess()
	#end define

	def CheckPassword(self, passwd):
	#	if self.isBlock:
		#	self.WrongAccess()
		passwdHash = ton.GetSettings("passwdHash")

		if passwdHash and check_password_hash(passwdHash, passwd):
			self.GenerateToken()
		else:
			self.WrongAccess()
	#end define

	def TS(self):
		timestamp = int(time.time())
		return timestamp
	#end define
#end class


@Request.application
def application(request):
	global ip
	token = GetUserToken(request)

	ip = GetIp(request.remote_addr, token)
	rpc = JSONRPCResponseManager.handle(request.data, dispatcher)
	headers = Headers()
	headers.add("Access-Control-Allow-Origin", '*')
	headers.add("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
	headers.add("Access-Control-Allow-Headers", "Content-Length,Content-Type,x-compress,Cache-Control,Authorization")
	response = Response(rpc.json, mimetype="application/json", headers=headers)
	return response
#end define

def GetUserToken(request):
	token = None
	buffer = request.headers.get("Authorization")
	if buffer is not None and "token " in buffer:
		buffer = buffer.split(' ')
		token = buffer[1]
	return token
#end define

@dispatcher.add_method
def login(api, passwd):
	global ip
	ip.CheckPassword(passwd)
	return {"api": api, "token": ip.token}
#end define

@dispatcher.add_method
def logout():
	global ip
	ip.DestroyToken()
	return 1;
#end define


def GetIp(addr, token):
	ipList = GetIpList()
	ip = ipList.get(addr)
	if ip is None:
		ip = IP(addr)
		ipList[addr] = ip
	ip.inputToken = token
	return ip
#end define

def GetIpList():
	ipList = local.buffer.get("ipList")
	if ipList is None:
		ipList = dict()
		local.buffer["ipList"] = ipList
	return ipList
#end define

@dispatcher.add_method
def status():
	global ip
	ip.CheckAccess()
	config15 = ton.GetConfig15()
	config17 = ton.GetConfig17()
	config34 = ton.GetConfig34()
	config36 = ton.GetConfig36()
	tpsAvg = ton.GetTpsAvg()
	loadavg = GetLoadAvg()
	netLoadAvg = ton.GetNetLoadAvg()
	adnlAddr = ton.adnlAddr
	mytoncoreStatus = GetServiceStatus("mytoncore")
	rootWorkchainEnabledTime_int = ton.GetRootWorkchainEnabledTime()
	validatorsElectedFor = config15["validatorsElectedFor"]
	electionsStartBefore = config15["electionsStartBefore"]
	electionsEndBefore = config15["electionsEndBefore"]
	stakeHeldFor = config15["stakeHeldFor"]
	minStake = config17["minStake"]
	maxStake = config17["maxStake"]
	totalValidators = config34["totalValidators"]
	onlineValidators = ton.GetOnlineValidators()
	if onlineValidators:
		onlineValidators = len(onlineValidators)
	oldStartWorkTime = config36.get("startWorkTime")
	if oldStartWorkTime is None:
		oldStartWorkTime = config34.get("startWorkTime")
	shardsNumber = ton.GetShardsNumber()
	validatorStatus = ton.GetValidatorStatus()
	fullConfigAddr = ton.GetFullConfigAddr()
	fullElectorAddr = ton.GetFullElectorAddr()
	startWorkTime = ton.GetActiveElectionId(fullElectorAddr)
	validatorIndex = ton.GetValidatorIndex()
	validatorEfficiency = ton.GetValidatorEfficiency()
	validatorWallet = ton.GetLocalWallet(ton.validatorWalletName)
	dbSize = ton.GetDbSize()
	offersNumber = ton.GetOffersNumber()
	complaintsNumber = ton.GetComplaintsNumber()
	if validatorWallet is not None:
		validatorAccount = ton.GetAccount(validatorWallet.addr)
	else:
		validatorAccount = None
	#end if

	if startWorkTime == 0:
		startWorkTime = oldStartWorkTime
	#end if

	# Calculate time
	startValidation = startWorkTime
	endValidation = startWorkTime + validatorsElectedFor
	startElection = startWorkTime - electionsStartBefore
	endElection = startWorkTime - electionsEndBefore
	startNextElection = startElection + validatorsElectedFor

	# bla bla bla
	data = dict()
	data["electionId"] = startWorkTime
	data["tpsAvg"] = tpsAvg
	data["totalValidators"] = totalValidators
	data["onlineValidators"] = onlineValidators
	data["shardsNumber"] = shardsNumber
	data["validatorStatus"] = validatorStatus
	data["complaintsNumber"] = complaintsNumber

	data["validatorIndex"] = validatorIndex
	data["validatorEfficiency"] = validatorEfficiency
	data["adnlAddr"] = adnlAddr
	if validatorWallet is not None:
		data["validatorWalletAddr"] = validatorWallet.addr
		data["validatorWalletBalance"] = validatorAccount.balance
	data["loadavg"] = loadavg
	data["netLoadAvg"] = netLoadAvg
	data["mytoncoreStatus"] = mytoncoreStatus
	data["dbSize"] = dbSize

	data["fullConfigAddr"] = fullConfigAddr
	data["fullElectorAddr"] = fullElectorAddr
	data["validatorsElectedFor"] = validatorsElectedFor
	data["electionsStartBefore"] = electionsStartBefore
	data["electionsEndBefore"] = electionsEndBefore
	data["stakeHeldFor"] = stakeHeldFor
	data["minStake"] = minStake
	data["maxStake"] = maxStake

	data["startValidation"] = startValidation
	data["endValidation"] = endValidation
	data["startElection"] = startElection
	data["endElection"] = endElection
	data["startNextElection"] = startNextElection
	return data
#end define

@dispatcher.add_method
def seqno(walletName):
	global ip
	ip.CheckAccess()
	wallet = ton.GetLocalWallet(walletName)
	seqno = ton.GetSeqno(wallet)
	return seqno
#end define

@dispatcher.add_method
def getconfig(configId):
	global ip
	ip.CheckAccess()
	data = ton.GetConfig(configId)
	return data
#end define

@dispatcher.add_method
def nw(walletName, workchain=0):
	global ip
	ip.CheckAccess()
	wallet = ton.CreateWallet(walletName, workchain)
	return wallet.__dict__
#end define

@dispatcher.add_method
def aw(walletName):
	global ip
	ip.CheckAccess()
	wallet = ton.GetLocalWallet(walletName)
	ton.ActivateWallet(wallet)
	return True
#end define

@dispatcher.add_method
def wl():
	global ip
	ip.CheckAccess()
	data = dict()
	wallets = ton.GetWallets()
	for wallet in wallets:
		account = ton.GetAccount(wallet.addr)
		buff = dict()
		buff["name"] = wallet.name
		buff["addr"] = wallet.addr
		buff["workchain"] = wallet.workchain
		buff["status"] = account.status
		buff["balance"] = account.balance
		data[wallet.name] = buff
	return data
#end define

@dispatcher.add_method
def vas(addr):
	global ip
	ip.CheckAccess()
	account = ton.GetAccount(addr)
	return account.__dict__
#end define

@dispatcher.add_method
def vah(addr, limit):
	global ip
	ip.CheckAccess()
	account = ton.GetAccount(addr)
	history = ton.GetAccountHistory(account, limit)
	return history
#end define

@dispatcher.add_method
def ol():
	global ip
	ip.CheckAccess()
	offers = ton.GetOffers()
	return offers
#end define

@dispatcher.add_method
def el():
	global ip
	ip.CheckAccess()
	entries = ton.GetElectionEntries()
	return entries
#end define

@dispatcher.add_method
def ve():
	global ip
	ip.CheckAccess()
	ton.ReturnStake()
	ton.ElectionEntry()
	return True
#end define

@dispatcher.add_method
def vl():
	global ip
	ip.CheckAccess()
	validators = ton.GetValidatorsList()
	return validators
#end define

@dispatcher.add_method
def cl():
	global ip
	ip.CheckAccess()
	complaints = ton.GetComplaints()
	return complaints
#end define

@dispatcher.add_method
def get(name):
	global ip
	ip.CheckAccess()
	result = ton.GetSettings(name)
	return result
#end define

def SetWebPassword():
	local.AddLog("start SetWebPassword function", "debug")
	passwd = input("Set a new password for the web admin panel: ")
	passwdHash = generate_password_hash(passwd)
	ton.SetSettings("passwdHash", passwdHash)
	print("New password:", passwd)
#end define

def Init():
	# Event reaction
	if ("-p" in sys.argv):
		SetWebPassword()
		return
	#end if
	if not ton.GetSettings("passwdHash"):
		SetWebPassword()
		return

	port = 4000
	# Event reaction
	if ("-port" in sys.argv):
		port = int(sys.argv[2])
	#end if

	ip = requests.get("https://ifconfig.me").text

	sslKeyPath = local.buffer["myWorkDir"] + "ssl"
	crtPath = sslKeyPath + ".crt"
	keyPath = sslKeyPath + ".key"
	if os.path.isfile(keyPath) == False:
		make_ssl_devcert(sslKeyPath, host=ip)
	#end if

	run_simple(ip, port, application, ssl_context=(crtPath, keyPath))
#end define


###
### Старт программы
###

if __name__ == "__main__":
	Init()
#end if
