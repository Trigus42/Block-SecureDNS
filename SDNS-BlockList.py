# Import
import sys
import os
import socket
import concurrent.futures
from urllib.request import urlopen
from re import findall, compile, match
from subprocess import check_call, CalledProcessError

# Functions
def get_domains(url, type="Domains", reverse=False, exclude=[]):
    count_domains = 0
    domains = []
    ips = []
    
    #Not SDNS domains to exclude by default
    exclude.extend(["github.com", "imaal.byu.edu", "commons.host", "my.nextdns.io", "blog.cloudflare.com"])

    https_url_re = compile(r"https*:\/\/[a-zA-Z0-9+&@#\/%=~_|$?!:,.-]+")

    # Download
    try:
        lines = get_from_url(url, True)
    except:
        print("Invalid URL")
        return [[], []]

    if url == "https://raw.githubusercontent.com/wiki/curl/curl/DNS-over-HTTPS.md":
        for line in lines:
            if line.startswith("|"):
                url_col = line.split("|")[2]
                for match in https_url_re.findall(url_col):
                    domain = domain_from_string(match)
                    for x in domain:
                        domains.append(x.lower()) if (
                            x
                            and x.lower() not in domains
                            and x.lower() not in exclude
                        ) else None
    else:
        for line in lines:
            domain = domain_from_string(line)
            for x in domain:
                domains.append(x.lower()) if (
                    x and x.lower() not in domains and x not in exclude
                ) else None

    if reverse or "IPs" in type:
        rev = do_reverse(type, domains, ips, exclude)
        domains.extend(rev[0])
        ips.extend(rev[1])

    print(
        f"Found {len(domains)} unique Domains\n" if ("Domains" in type) else "",
        f"Found {len(ips)} unique IPs\n" if ("IPs" in type) else "",
    )

    return [domains, ips]


# def get_from_ip(url, type, reverse, verbose):
# Return IPs and domains


def get_from_stamp(url, type="Domains", reverse=False, exclude=[]):
    count_stamps = 0
    domains = []
    ips = []

    # Download
    try:
        lines = get_from_url(url)
    except:
        print("Invalid URL")
        return [[], []]

    # Decode SDNS Stamp && add domain and/or IP to list
    for parameters in get_stamp_parameters(lines):
        count_stamps += 1
        if "Domains" in type:
            domain = rm_port(
                parameters.hostname if (parameters.hostname) else parameters.path
            )
            domains.append(domain) if (
                domain and domain not in domains and domain not in exclude
            ) else None
        if "IPs" in type:
            ip = rm_port(parameters.address)
            ips.append(ip) if (ip and ip not in ips) else None

    if reverse:
        rev = do_reverse(type, domains, ips, exclude)
        domains.extend(rev[0])
        ips.extend(rev[1])

    print(
        f"Found {count_stamps} SDNS stamps (likely including dublicate domains)\n",
        f"Found {len(domains)} unique Domains\n" if ("Domains" in type) else "",
        f"Found {len(ips)} unique IPs\n" if ("IPs" in type) else "",
    )

    return [domains, ips]


def domain_from_string(string, min_sub="1", max_sub=""):
    domain_re = compile(
        r"(?=.{2,255}$)(?=[a-zA-Z])(?!\-)(?:(?!\.)[A-Za-z0-9-]{1,63}\.){"
        + str(min_sub)
        + ","
        + str(max_sub)
        + r"}[A-Za-z0-9-]{1,24}(?<!\-)"
    )
    return domain_re.findall(string)


def do_reverse(type, domains=[], ips=[], exclude=[]):
    domains_ex = []
    ips_ex = []
    domain_info = None

    with concurrent.futures.ThreadPoolExecutor(max_workers=(len(ips)+len(domains))) as executor:
        threads_domains = []
        threads_ips = []

        for domain in domains:
            thread = executor.submit(socket.gethostbyname_ex, domain)
            threads_domains.append(thread)

        for thread in concurrent.futures.as_completed(threads_domains):
            try:
                domain_info = thread.result()
            except:
                pass

            if domain_info:
                # IP (list)
                if "IPs" in type:
                    for x in domain_info[2]:
                        ips_ex.append(x) if (x and x not in ips_ex) else None
                # Alias (list)
                for x in domain_info[1]:
                    domains_ex.append(x) if (x and x not in domains_ex) else None

        for ip in ips:
            thread = executor.submit(socket.gethostbyaddr, ip)
            threads_ips.append(thread)
            
        for thread in concurrent.futures.as_completed(threads_ips):
            try:
                ip_info = thread.result()
            except:
                pass

            if "Domains" in type:
                # Domain
                domains_ex.append(ip_info[0]) if (
                    ip_info[0] and ip_info[0] not in domains_ex and ip_info[0]
                ) else None
                # Alias (list)
                for x in ip_info[1]:
                    domains_ex.append(x) if (x and x not in domains_ex) else None

    for x in domains_ex:
        domains.append(x) if (x and x not in domains and x not in exclude) else None
    for x in ips_ex:
        ips.append(x) if (x and x not in ips) else None

    return [domains, ips]


def get_from_url(url, return_lines=False):
    print(f"\nFile: {os.path.basename(url)}")
    lines = []
    with urlopen(url) as file:
        if return_lines:
            for line in file:
                lines.append(line.decode())
            return lines
        else:
            return file.read().decode()


def get_stamp_parameters(file):
    lines = findall(r"sdns://\S*", file)
    print("Warning: No SDNS stamps found") if (lines == []) else None
    for line in lines:
        yield parse(line.split()[0])


def rm_port(address):
    # IPv6
    if "]" in address:
        return (
            address[: address.find("]:") + 1] if ("]:" in address) else address
        ).translate({ord(i): None for i in "[]"})
    # IPv4/Domain
    elif ":" in address:
        return address[: address.find(":")]
    else:
        return address


def blockPrint():
    sys.stdout = open(os.devnull, "w")


def enablePrint():
    sys.stdout = sys.__stdout__


def install(package):
    try:
        check_call([sys.executable, "-m", "pip", "install", "--user", package])
        input(f"\nInstalled '{package}'. Please restart the script")
        exit()
    except CalledProcessError:
        if os.name == "posix":
            os.system("sudo apt install python3-pip -y")
            check_call([sys.executable, "-m", "pip", "install", package])
            input(f"\nInstalled '{package}'. Please restart the script")
            exit()
        else:
            print("""Error: 'pip' not installed.""")


def save_(type):
    global domains, ips
    if "Domains" in type:
        open("SDNS-Domains.list", "w")
        domains_file = open("SDNS-Domains.list", "a")
        for domain in domains:
            domains_file.write(str(domain) + "\n")
        domains_file.close()
    if "IPs" in type:
        open("SDNS-IPs.list", "w")
        ips_file = open("SDNS-IPs.list", "a")
        for ip in ips:
            ips_file.write(str(ip) + "\n")
        ips_file.close()


def print_(type):
    global domains, ips
    if "Domains" in type:
        for domain in domains:
            print(domain)
    if "IPs" in type:
        for ip in ips:
            print(ip)


if __name__ == "__main__":
    # Check for arguments, print help
    try:
        sys.argv[1]
    except IndexError:
        input(
            """\nSDNS-BlockList: Extract domains from SDNS stamp containing files
Tested with Python 3.8 and dnsstamps 1.3.0
Use: $python SDNS-BlockList.py <Resolvers_List_URLs>

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
Domains: https://raw.githubusercontent.com/wiki/curl/curl/DNS-over-HTTPS.md"""
        )
        exit()

    # Process arguments
    arguments = sys.argv[1:]

    if "-s" in arguments and "-d" in arguments:
        print("\nOptions '-s' and '-d' can not be used together")
        exit()
    elif "-d" in arguments:
        format = "direct"
        arguments.remove("-d")
    else:
        arguments.remove("-s") if ("-s" in arguments) else None
        format = "stamp"
        # Import or install 'dnsstamps' module
        try:
            from dnsstamps import parse
        except ModuleNotFoundError:
            print("'dnsstamps' not found, installing 'dnsstamps'")
            install("dnsstamps")
            from dnsstamps import parse

    if "-ip" in arguments and "-dn" not in arguments:
        arguments.remove("-ip")
        extract = "IPs"
    elif "-ip" in arguments and "-dn" in arguments:
        arguments.remove("-dn")
        arguments.remove("-ip")
        extract = "Domains/IPs"
    else:
        arguments.remove("-dn") if ("-dn" in arguments) else None
        extract = "Domains"

    if "-f" in arguments:
        input_type = "file"
    else:
        input_type = "url"

    if "-r" in arguments:
        arguments.remove("-r")
        reverse = True
    else:
        reverse = False

    if "-y" in arguments and "-o" in arguments:
        print("\nOptions '-y' and '-o' can not be used together")
        exit()
    elif "-y" in arguments:
        arguments.remove("-y")
        overwrite = True
        only_result = False
    elif "-o" in arguments:
        arguments.remove("-o")
        overwrite = False
        only_result = True
        blockPrint()
    else:
        overwrite = False
        only_result = False
        enablePrint()

    if "-e" in arguments:
        exclude = arguments[arguments.index("-e") + 1].split(",")
        arguments.remove(arguments[arguments.index("-e") + 1])
        arguments.remove("-e")
    else:
        exclude = []

    option = compile(r"-.*")
    for x in arguments:
        invalid = match(option, x)
        if invalid:
            print(f"Invalid arguments!")
            exit()

    # Get URLs
    if input_type == "file":
        path = arguments[arguments.index("-f") + 1]
        try:
            with open(path, "r") as f:
                urls = f.readlines()
        except NameError:
            print("Option '-f' takes a list (file) of URLs")
            exit()
    else:
        if arguments:
            urls = arguments
        else:
            # Default URL
            urls = (
                ["https://raw.githubusercontent.com/wiki/curl/curl/DNS-over-HTTPS.md"]
                if (format == "direct")
                else [
                    "https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v3/public-resolvers.md"
                ]
            )

    # Call functions
    domains = []
    ips = []
    if format == "stamp":
        for url in urls:
            lists = get_from_stamp(url, extract, reverse, exclude)
            domains.extend(lists[0])
            ips.extend(lists[1])

    elif format == "direct":
        for url in urls:
            lists = get_domains(url, extract, reverse, exclude)
            domains.extend(lists[0])
            ips.extend(lists[1])

    ips.sort()
    domains.sort()

    # Save results to file
    if not only_result:
        if not overwrite:
            if "Domains" in extract:
                try:
                    open("SDNS-Domains.list", "x")
                    save_("Domains")
                except FileExistsError:
                    if (
                        input(
                            "\nAre you sure, you want to overwrite SDNS-Domains.list? (y/n)"
                        ).upper()
                        == "Y"
                    ):
                        save_("Domains")
                    else:
                        if (
                            input("Do you want to print the domain list? (y/n)").upper()
                            == "Y"
                        ):
                            print("\nDomains:")
                            print_("Domains")
            if "IPs" in extract:
                try:
                    open("SDNS-IPs.list", "x")
                    save_("IPs")
                except FileExistsError:
                    if (
                        input(
                            "\nAre you sure, you want to overwrite SDNS-IPs.list? (y/n)"
                        ).upper()
                        == "Y"
                    ):
                        save_("IPs")
                    else:
                        if (
                            input("Do you want to print the IP list? (y/n)").upper()
                            == "Y"
                        ):
                            print("\nIPs:")
                            print_("IPs")
        else:
            save_("domains")
            save_("ips")
    else:
        enablePrint()
        if "Domains" in extract:
            print_("Domains")
        if "IPs" in extract:
            print("\n") if ("Domains" in extract) else None
            print_("IPs")
