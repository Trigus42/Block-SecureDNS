# Block-SecureDNS

## SDNS-BlockList.py:
SDNS-BlockList: Extract domains from SDNS stamp containing files
Tested with Python 3.8 and dnsstamps 1.3.0
Use: $python SDNS-BlockList.py <arguments> <Resolvers_List_URLs>

Arguments:  
'-y': Overwrite existing lists
'-f': Use URLs from file
'-d': File already contains domains
'-ip': Get IPs
'-dn': Get Domains (Default)
'-o': Only print results
'-r': Lookup IPs/Aliases for found Domains; Domains/Aliases for found IPs (takes a while)

Required Modules:
Preinstalled: 'urllib', 're', 'os', 'subprocess', 'sys'
Manual install: 'dnsstamps'

Default Lists:
SDNS Stamps: https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v2/public-resolvers.md
Domains: https://raw.githubusercontent.com/wiki/curl/curl/DNS-over-HTTPS.md

### Example use:
```
SDNS-BlockList.py -d -dn
SDNS-BlockList.py -ip -dn https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v2/public-resolvers.md
```

### SDNS-Hostnames.list:
A list of SecureDNS Server hostnames.
Generated using lists from SDNS-Resolvers-Lists.list

### SDNS-IPs.list:
A list of SecureDNS Server IPs.
Generated using lists from SDNS-Resolvers-Lists.list

## Example: Use script with Pi-Hole
### Create a cronjob:
*Upates every sunday at 00:00*
```
00 00 7 * *  /usr/local/bin/pihole -b $(/usr/bin/python3 /etc/pihole/scripts/SDNS-BlockList.py -f /etc/pihole/scripts/sdns_resolvers_lists.list -hn -o)
```
