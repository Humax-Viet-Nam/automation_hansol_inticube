goserver guide:
1. chmod 777 goserver
2. ./goserver 10 

- 10: number of ports (from 9000 to 9000 + number of port -1) 

---------------------
http client guide:

1. chmod 777 httppostclient
2. chmod 777 logservice
3. ./httppostclient --host ./hostdb.txt --input ./msg.txt --request 10000