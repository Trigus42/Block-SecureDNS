# Block-SecureDNS

## SDNS-BlockList.py:
SDNS-BlockList: Extract domains from SDNS stamp containing files  
Tested with Python 3.9.1 and dnsstamps 1.3.0  
Use: $python SDNS-BlockList.py <arguments> <Resolvers_List_URLs>  

Arguments:  
'-y': Overwrite existing lists  
'-f': Use URLs from file  
'-s': Extract domains from SDNS stamps (Default)  
'-d': Extract domains directly  
'-dn': Return domains (Default)  
'-ip': Resolve domains to return IPs  
'-o': Only print results  
'-r': Lookup IPs/aliases for found domains; domains/aliases for found IPs (takes a while)  
'-e': Exclude following domains  

Required Modules: 'dnsstamps'  

Default Lists:  
SDNS stamps: https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v3/public-resolvers.md  
Domains: https://raw.githubusercontent.com/wiki/curl/curl/DNS-over-HTTPS.md

### Example use:
```
# Extract domains from DNS-over-HTTPS.md and public-resolvers.md and all their aliases
SDNS-BlockList.py -d -s -r
# Extract domains from DNS-over-HTTPS.md and resolve them to return IPs
SDNS-BlockList.py -ip -dn https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v3/public-resolvers.md
# Extract domains from DNS-over-HTTPS.md but exclude "dns.google" and "dns.adguard.com"
SDNS-BlockList.py -d -e dns.google,dns.adguard.com -r
```

### SDNS-Domains.list:
A list of SecureDNS server hostnames.
Generated using lists from SDNS-Resolvers-Lists.list

### SDNS-IPs.list:
A list of SecureDNS server IPs.
Generated using lists from SDNS-Resolvers-Lists.list

## Example: Use script with Pi-Hole
### Create a cronjob:
*Upates every sunday at 00:00*
```
00 00 7 * * /usr/local/bin/pihole -b $(/usr/bin/python3 /root/SDNS-BlockList.py -s -d -o)
```
