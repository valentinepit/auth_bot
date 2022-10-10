This is the telegram bot for getting configuration for WireGuard peers.

Bot must be located on wguard server side. 

Bot can Add/Delete users from server configuration

And for new user bot preparing configuration template.

[Interface]
PrivateKey = <Your key>
ListenPort = 63665
Address = 10.1.19.14/32
DNS = 1.1.1.1
MTU = 1380

[Peer]
PublicKey = rSa5YSfFLNAjtts2XoDSWUhxQke14JEOFZPNe6qAxUc=
AllowedIPs = 0.0.0.0/0 # 10.30.0.0/20, 10.1.9.0/24, 10.10.128.3/32
Endpoint = 10.1.9.1:51194
PersistentKeepalive = 15