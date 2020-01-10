# Block-SecureDNS

## SDNS-BlockList.py:
Extract hostnames from SDNS stamp containing files.
Tested with Python 3.8 and dnsstamps 1.3.0

Use: $python SDNS-BlockList.py <arguments> <Resolvers_List_URLs>

Arguments:
'-y': Overwrite existing lists
'-f': Use URLs from file
'-ip': Get IPs
'-hn': Get Hostnames (Default)
'-o': Only print results

Required Modules: 'dnsstamps'

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
