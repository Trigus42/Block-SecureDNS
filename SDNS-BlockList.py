#Import
import sys
import os
from urllib.request import urlopen
from re import findall
from subprocess import check_call, CalledProcessError

#Install and import 'dnsstamps' module
try:
	from dnsstamps import parse
except ModuleNotFoundError:
	print("'dnsstamps' not found, installing 'dnsstamps'")
	install("dnsstamps")
	from dnsstamps import parse

#Functions
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
	
def enablePrint():
    sys.stdout = sys.__stdout__

def install(package):
	try:
		check_call([sys.executable, "-m", "pip", "install", "--user", package])
		input(f"\nInstalled '{package}'. Please restart the script")
		exit()
	except CalledProcessError:
		if(os.name == 'posix'):
			os.system("sudo apt install python3-pip -y")
			check_call([sys.executable, "-m", "pip", "install", package])
			input(f"\nInstalled '{package}'. Please restart the script")
			exit();
		else:
			print("""Error: 'pip' not installed.""")
			
def save_(type):
	open("SDNS-Hostnames.list", "w") if(type == "hostnames") else open("SDNS-IPs.list", "w") if(type == "ips") else None
	file = open("SDNS-Hostnames.list", "a") if(type == "hostnames") else open("SDNS-IPs.list", "a") if(type == "ips") else None
	if(type == "hostnames"):
		for hostname in hostnames:
			file.write(str(hostname)+"\n")
	elif(type == "ips"):
		for ip in ips:
			file.write(str(ip)+"\n")
	file.close()
	
def print_(type):
	if(type == "hostnames"):
		for hostname in hostnames:
			print(hostname)
	elif(type == "ips"):
		for ip in ips:
			print(ip)
	

#Process arguments	
if("-y" in sys.argv[1:]):
	overwrite = True
	only_result = False
	sys.argv.remove("-y")
elif("-o" in sys.argv[1:]):
	overwrite = False
	only_result = True
	sys.argv.remove("-o")
	blockPrint()
elif("-y" in sys.argv[1:] and "-o" in sys.argv[1:]):
	print("\nOptions '-y' and '-o' can not be used together")
	exit()
else:
	overwrite = False
	only_result = False

if("-f" in sys.argv[1:]):
	path = sys.argv[sys.argv[1:].index("-f")+2]
	try:
		resolvers_file_url_list = open(path, "r")
	except NameError:
		print("Option '-f' takes a list (file) of URLs")
		exit()
	
#Default
extract_IPs = False
extract_hostnames = True

if("-ip" in sys.argv[1:]):
	extract_IPs = True
	sys.argv.remove("-ip")
	extract_hostnames = False
	
if("-hn" in sys.argv[1:]):
	extract_hostnames = True
	sys.argv.remove("-hn")

try:
	sys.argv[1]
except IndexError:
	input("""\nSDNS-BlockList: Extract hostnames from SDNS stamp containing files
Tested with Python 3.8 and dnsstamps 1.3.0\n
Use: $python SDNS-BlockList.py <arguments> <Resolvers_List_URLs>

Arguments:  
'-y': Overwrite any existing lists
'-f': Use URLs from file
'-ip': Get IPs
'-hn': Get Hostnames (Default)
'-o': Only print results
 
Required Modules:
Preinstalled: 'urllib.request', 're', 'os', 'subprocess', 'sys'
Manual install: 'dnsstamps'\n""")
	exit()

#Intialize Lists
hostnames = []
ips = []

#Process URLs
for resolvers_file_url in (sys.argv[1:] if("-f" not in sys.argv[1:]) else resolvers_file_url_list):
	print(f"\nFile: {os.path.basename(resolvers_file_url)}")
	
	#Downloading and decoding
	try:
		resolvers_file = urlopen(resolvers_file_url)
	except ValueError:
		print("Invalid URL")
		continue
	data = resolvers_file.read()
	text = data.decode('utf-8')
	
	#Extract SDNS stamps
	lines_encoded = findall(r'sdns://\S*', text)
	print(f"Warning: No SDNS stamps found in {file_name}" if(lines_encoded == []) else f"Found {len(lines_encoded)} SDNS stamps (likely including dublicate hostnames)")
	
	#Decode SDNS Stamp && add hostname and/or IP to list
	for line_encoded in lines_encoded:
		parameters = parse(line_encoded.split()[0])
		if(extract_hostnames):
			hostname_port = parameters.hostname if(parameters.hostname != "") else parameters.path if(parameters.path != "") else ""
			hostname = hostname_port[:hostname_port.find(":")] if(hostname_port.find(":") != -1) else hostname_port
			hostnames.append(hostname) if(hostname not in hostnames and hostname != None and hostname != "") else None
		if(extract_IPs):
			ip_port = parameters.address
			#IPv6
			if("]" in ip_port):
				ip = ip_port[:ip_port.find("]:")+1] if("]:" in ip_port) else ip_port
			#IPv4
			elif(":" in ip_port):
				ip = ip_port[:ip_port.find(":")]
			else:
				ip = ip_port
			ips.append(ip) if(ip not in ips and ip != None and ip != "") else None
			
#Print amount of hostnames/IPs
print(f"Found {len(hostnames)} unique hostnames") if(extract_hostnames) else None
print(f"Found {len(ips)} unique ips") if(extract_IPs) else None
	
#Save results to file
if(not only_result):
	if(not overwrite):
		if(extract_hostnames):
			try:
				open("SDNS-Hostnames.list", "x")
				save_("hostnames")
			except FileExistsError:
				if(input("\nAre you sure, you want to overwrite SDNS-Hostnames.list? (y/n)").upper() == "Y"):
					save_("hostnames")
				else:
					if(input("Do you want to print the hostname list? (y/n)").upper() == "Y"):
						print("\nhostnames:")
						print_("hostnames")
		if(extract_IPs):
			try:
				open("SDNS-IPs.list", "x")
				save_("ips")
			except FileExistsError:
				if(input("\nAre you sure, you want to overwrite SDNS-IPs.list? (y/n)").upper() == "Y"):
					save_("ips")
				else:
					if(input("Do you want to print the IP list? (y/n)").upper() == "Y"):
						print("\nIPs:")
						print_("ips")
	else:
		save_("hostnames")
		save_("ips")
else:
	enablePrint()
	if(extract_hostnames):
		print_("hostnames")
	if(extract_IPs):
		print_("ips")