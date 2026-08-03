from datetime import datetime # Required for getting current time
from pathlib import Path # Required for directory work
from zoneinfo import ZoneInfo # Required for using timezones

import requests # Required for fetching HTTP response

# Setting timezone for logging purposes

snapshotDate = datetime.now(
    ZoneInfo("Europe/Bucharest")
).date().isoformat()

# Declare API URLs

urlNord = "https://api.nordvpn.com/v1/servers?limit=16384"
urlMullvad = "https://api.mullvad.net/www/relays/all"

# Fetch JSONs, check if fetch works, store for parsing.
# If the response type changes (e.g. list to dict), throw an error.

responseNord = requests.get(urlNord, timeout=20)
responseNord.raise_for_status()
serversNord = responseNord.json()

if not isinstance(serversNord, list):
    raise TypeError("NordVPN response is not a list")

responseMullvad = requests.get(urlMullvad, timeout=20)
responseMullvad.raise_for_status()
serversMullvad = responseMullvad.json()

if not isinstance(serversMullvad, list):
    raise TypeError("Mullvad response is not a list")

# Create output folders

rawDirNord = Path("data/raw/nordvpn")
rawDirMullvad = Path("data/raw/mullvad")
ipDirNord = Path("data/ips/nordvpn")
ipDirMullvad = Path("data/ips/mullvad")

for directory in (
    rawDirNord,
    rawDirMullvad,
    ipDirMullvad,
    ipDirNord
):
    directory.mkdir(parents=True, exist_ok=True)

# Save original responses for future parsing

rawFileNord = rawDirNord / f"{snapshotDate}.json"
rawFileNord.write_bytes(responseNord.content)
rawFileMullvad = rawDirMullvad / f"{snapshotDate}.json"
rawFileMullvad.write_bytes(responseMullvad.content)

# Extract addresses for current use. 
# Check returned JSON structure for key-value pairs, modify accordingly.
# Use sets instead of arrays to deduplicate.

ipsNord = set()
ipsMullvad = set()

for server in serversNord:
    ip = server["station"]

    if not isinstance(ip, str):
        raise TypeError("NordVPN IP address is not a string")

    ipsNord.add(ip)

for server in serversMullvad:
    ip = server["ipv4_addr_in"]

    if not isinstance(ip, str):
        raise TypeError("Mullvad IP is not a string")

    ipsMullvad.add(ip)

# Save obtained IPs for current reference. No structure required, .txt should be fine.

ipFileNord = ipDirNord / f"{snapshotDate}.txt"
ipFileMullvad = ipDirMullvad / f"{snapshotDate}.txt"

ipFileNord.write_text(
    "\n".join(sorted(ipsNord)) + "\n",
    encoding="utf-8"
)

ipFileMullvad.write_text(
    "\n".join(sorted(ipsMullvad)) + "\n",
    encoding="utf-8"
)

# Confirm run.

print(f"NordVPN: saved {len(ipsNord)} unique IP addresses")
print(f"Mullvad: saved {len(ipsMullvad)} unique IP addresses")
print(f"Snapshot date: {snapshotDate}")