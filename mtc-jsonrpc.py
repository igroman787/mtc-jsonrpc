#!/usr/bin/env python3
# -*- coding: utf_8 -*-l

# pip3 install Werkzeug json-rpc
from sys import path
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher

path.append("/usr/src/mytonctrl/")
from mytoncore import *

ton = MyTonCore()


@Request.application
def application(request):
	response = JSONRPCResponseManager.handle(
		request.data, dispatcher)
	return Response(response.json, mimetype="application/json")
#end define

@dispatcher.add_method
def status():
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
	wallet = ton.GetLocalWallet(walletName)
	seqno = ton.GetSeqno(wallet)
	return seqno
#end define

@dispatcher.add_method
def getconfig(configId):
	data = ton.GetConfig(configId)
	return data
#end define

@dispatcher.add_method
def nw(walletName, workchain=0):
	wallet = ton.CreateWallet(walletName, workchain)
	return wallet.__dict__
#end define

@dispatcher.add_method
def aw(walletName):
	wallet = ton.GetLocalWallet(walletName)
	ton.ActivateWallet(wallet)
	return True
#end define

@dispatcher.add_method
def wl():
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
def dw(walletName):
	wallet = ton.GetLocalWallet(walletName)
	wallet.Delete()
	return True
#end define

@dispatcher.add_method
def vas(addr):
	account = ton.GetAccount(addr)
	return account.__dict__
#end define

@dispatcher.add_method
def vah(addr, limit):
	account = ton.GetAccount(addr)
	history = ton.GetAccountHistory(account, limit)
	return history
#end define

@dispatcher.add_method
def mg(walletName, destination, amount):
	wallet = ton.GetLocalWallet(walletName)
	ton.MoveCoins(wallet, destination, amount)
	return True
#end define

@dispatcher.add_method
def ol():
	offers = ton.GetOffers()
	return offers
#end define

@dispatcher.add_method
def vo(offerHash):
	ton.VoteOffer(offerHash)
	return True
#end define

@dispatcher.add_method
def el():
	entries = ton.GetElectionEntries()
	return entries
#end define

@dispatcher.add_method
def ve():
	ton.ReturnStake()
	ton.ElectionEntry()
	return True
#end define

@dispatcher.add_method
def vl():
	validators = ton.GetValidatorsList()
	return validators
#end define

@dispatcher.add_method
def cl():
	complaints = ton.GetComplaints()
	return complaints
#end define

@dispatcher.add_method
def vc(electionId, complaintHash):
	ton.VoteComplaint(electionId, complaintHash)
	return True
#end define


###
### Старт программы
###

if __name__ == "__main__":
	run_simple('localhost', 4000, application)
#end if


