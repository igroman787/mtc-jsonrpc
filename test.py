import requests
import json


url = "http://localhost:4000/jsonrpc"

def Get(method, params=None):
	payload = {"method": method, "params": params, "jsonrpc": "2.0", "id": 0}
	response = requests.post(url, json=payload)
	data = response.json()
	result = data.get("result")
	error = data.get("error")
	if error:
		text = error.get("data").get("message")
		raise Exception(text)
	return result
#end define

data = Get("status")
print(json.dumps(data, indent=4))

data = Get("seqno", ["validator_wallet_001"])
print("seqno", json.dumps(data, indent=4))

# data = Get("nw", ["wallet_001"])
# print("nw", json.dumps(data, indent=4))

# data = Get("mg", ["validator_wallet_001", data.get("addr_init"), 1])
# print("mg", json.dumps(data, indent=4))

# data = Get("aw", ["wallet_001"])
# print("aw", json.dumps(data, indent=4))

data = Get("wl")
print("wl", json.dumps(data, indent=4))

# data = Get("dw", ["wallet_001"])
# print(json.dumps(data, indent=4))

data = Get("vas", ["kf_COrB2c9Sm41aVhq54CotaTZJ55_3iDApuMkrBmGRiJ8_P"])
print("vas", json.dumps(data, indent=4))

data = Get("vah", ["kf_COrB2c9Sm41aVhq54CotaTZJ55_3iDApuMkrBmGRiJ8_P", 10])
print("vah", json.dumps(data, indent=4))

data = Get("ol")
print("ol", json.dumps(data, indent=4))

# data = Get("vo", [1165461231687465153745135435438151384354343])
# print("vo", json.dumps(data, indent=4))

data = Get("el")
print("el", json.dumps(data, indent=4))

data = Get("ve")
print("ve", json.dumps(data, indent=4))

data = Get("vl")
print("vl", json.dumps(data, indent=4))

data = Get("cl")
print("cl", json.dumps(data, indent=4))

# data = Get("vc", [12345678, 1321346545498416587651687435438748645348])
# print("vc", json.dumps(data, indent=4))













