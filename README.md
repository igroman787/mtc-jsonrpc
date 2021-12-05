# About mtc-jsonrpc

This module is designed to enable MyTonCtrl and TonAdmin to work together.
It's a JSONRPC api that connects to MyTonCtrl.
Before installation your must be sure that you have **[MyTonCtrl](https://github.com/igroman787/mytonctrl)**. JSONRPC api accepts commands from TonAdmin and executes them in MyTonCtrl. In this version only **readonly** interface is implemented for early testing of the admin panel.

# Installation
1. Install `mtc-jsonrpc` module:
`mytonctrl` -> `installer` -> `enable JR`

2. Set password:
`mytonctrl` -> `installer` -> `setwebpass`

# Another installation
Clone  repository:

` git clone --recursive https://github.com/igroman787/mtc-jsonrpc.git`

Be shure that you have python3. if you have MyTonCtrl - you have it.
Run the script:

` cd mtc-jsonrpc
 python3 mtc-jsonrpc.py`

The script will ask for a  **password** to access the api. This password you will use to access through TonAdmin. If in the future you want to change the password, run the script with the flag **-p**.
` python3 mtc-jsonrpc.py -p`

By default, the script runs on port **4000**. You can also change it to the desired one using the **-port** flag.

` python3 mtc-jsonrpc.py -port 3228`

If the module is started successfully, you will receive a similar message:
>Running on https://79.143.73.169:4000/ (Press CTRL+C to quit)

Copy path `https://79.143.73.169:4000/` and enter it into [TonAdmin](https://tonadmin.org) login page. Еnter your password and go jump with happiness, because this crutch magically started. 🥳
