import urllib.request, json, tempfile, shutil, subprocess, requests, threading, winreg, feedparser, random, re, time, sys, os
from packaging import version
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from newspaper import Article
from bs4 import BeautifulSoup
from dateutil import parser
from dateutil.tz import gettz

DARK_BG = "#1e1e1e"
DARK_BG2 = "#444444"
DARK_FG = "#ffffff"
DARK_ACCENT = "#2e2e2e"

CURRENT_VERSION = "1.0.2"
VERSION_URL = "https://raw.githubusercontent.com/Logiztiic/OSINTTool/main/version.json"

APP_NAME = "OSINTTool"
APPDATA_DIR = os.path.join(os.getenv("APPDATA"), APP_NAME)
UPDATER_PATH = os.path.join(APPDATA_DIR, "OSINTUpdater.exe")

original_stdout = sys.__stdout__
original_stderr = sys.__stderr__


rgb_active_state = [False]
REG_PATH = r"Software\WarScraper\Settings"
RGB_COLORS = ["#ff0000", "#ff9900", "#ffff00", "#33cc33", "#00ccff", "#6600cc", "#ff00ff"]


TZ_LOOKUP = {
    "PST": gettz("America/Los_Angeles"),
    "PDT": gettz("America/Los_Angeles"),
    "MST": gettz("America/Denver"),
    "MDT": gettz("America/Denver"),
    "CST": gettz("America/Chicago"),
    "CDT": gettz("America/Chicago"),
    "EST": gettz("America/New_York"),
    "EDT": gettz("America/New_York"),
    "UTC": gettz("UTC"),
    "GMT": gettz("UTC")
}

def parse_datetime(dt_str):
    try:
        return parser.parse(dt_str, tzinfos=TZ_LOOKUP)
    except Exception as e:
        print(f"[ERROR] Failed to parse datetime: {e}")
        return None

dt = parse_datetime("Wed, 26 Jun 2024 14:30 PST")


SECTIONS = {
    "Al Jazeera English": "https://www.aljazeera.com/news/",
    "Deutsche Welle (DW)": "https://www.dw.com/en/top-stories/s-9097",
    "France 24": "https://www.france24.com/en/",
    "The Times of India": "https://timesofindia.indiatimes.com/world",
    "The Japan Times": "https://www.japantimes.co.jp/news/",
    "CBC News (Canada)": "https://www.cbc.ca/news/world",
    "RT News (Russia)": "https://www.rt.com/news/",
    "South China Morning Post": "https://www.scmp.com/news",
    "The Globe and Mail": "https://www.theglobeandmail.com/world/",
    "The Straits Times": "https://www.straitstimes.com/world",
    "Bellingcat (RSS)": "rss::https://www.bellingcat.com/feed/",
    "Curated Intelligence (RSS)": "rss::https://www.curatedintel.org/feeds/posts/default",
    "Cyber Intelligence Insights (RSS)": "rss::https://intelinsights.substack.com/feed",
    "Krebs on Security (RSS)": "rss::https://krebsonsecurity.com/feed/",
    "38 North (RSS)": "rss::https://www.38north.org/feed/",
    "Daily NK (RSS)": "rss::https://www.dailynk.com/english/feed/",
    "North Korea Leadership Watch (RSS)": "rss::http://www.nkleadershipwatch.org/feed/",    
    "Ukrinform": "https://www.ukrinform.net/",
    "Kyiv Post": "https://www.kyivpost.com/",
    "Africanews": "https://www.africanews.com/news/",
    "Mail & Guardian": "https://mg.co.za/section/news/",
    "Daily Nation": "https://nation.africa/kenya/news",
    "The New Times": "https://www.newtimes.co.rw/news",
    "AllAfrica": "https://allafrica.com/latest/",
    "Argentina Reports": "https://www.argentinareports.com/",
    "Brazil Reports": "https://www.brazilreports.com/",
    "Tico Times": "https://ticotimes.net/",
    "Jamaica Gleaner": "https://jamaica-gleaner.com/",
    "Nikkei Asia": "https://asia.nikkei.com/",
    "China Daily": "https://www.chinadaily.com.cn/world",
    "The Hindu": "https://www.thehindu.com/news/international/",
    "Korea Herald": "https://www.koreaherald.com/list.php?ct=02000000",
    "Bangkok Post": "https://www.bangkokpost.com/world",
    "Philippine Daily Inquirer": "https://globalnation.inquirer.net/",
    "Jerusalem Post": "https://www.jpost.com/",
    "Haaretz": "https://www.haaretz.com/middle-east-news",
    "Arab News": "https://www.arabnews.com/node/1378566/middle-east",
    "Gulf News": "https://gulfnews.com/world",
    "Tehran Times": "https://www.tehrantimes.com/",
    "Spiegel International": "https://www.spiegel.de/international/",
    "El País (EN)": "https://english.elpais.com/",
    "RTE News": "https://www.rte.ie/news/world/",
    "Aftenposten": "https://www.aftenposten.no/verden/i/",
    "BBC US/Canada (RSS)": "rss::https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
    "The Guardian US (RSS)": "rss::https://www.theguardian.com/us-news/rss",
    "NPR News (RSS)": "rss::https://feeds.npr.org/1001/rss.xml",
    "HuffPost US News (RSS)": "rss::https://www.huffpost.com/section/us-news/feed",
    "Mother Jones (RSS)": "rss::https://www.motherjones.com/feed/",
    "The Intercept (RSS)": "rss::https://theintercept.com/feed/",
    "The Daily Wire (RSS)": "rss::https://www.dailywire.com/feeds/rss.xml",
    "Newsmax (RSS)": "rss::https://www.newsmax.com/rss/Newsfront/16",
    "The Blaze (RSS)": "rss::https://follow.it/theblaze/rss",   
    "Bloomberg": "https://www.bloomberg.com/",
    "MSNBC": "https://www.msnbc.com",
    "The Guardian US": "https://www.theguardian.com/us",
    "Defense.gov – DoD News (RSS)": "rss::https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1",
    "Defense One (RSS)": "rss::https://www.defenseone.com/rss/all/",
    "19FortyFive (RSS)": "rss::https://www.19fortyfive.com/feed/",
    "Breaking Defense (RSS)": "rss::https://breakingdefense.com/feed/",
    "War on the Rocks (RSS)": "rss::https://warontherocks.com/feed/",
    "Washington Examiner": "https://www.washingtonexaminer.com/",
    "The Federalist": "https://thefederalist.com/",
    "Townhall": "https://townhall.com/",
    "The Blaze": "https://www.theblaze.com/",
    "Task & Purpose – ATW": "https://taskandpurpose.com/category/around-the-world/",
    "Task & Purpose - News": "https://taskandpurpose.com/category/news/",
    "Task & Purpose - Pentagon": "https://taskandpurpose.com/category/the-pentagon-rundown/",
}

KEYWORD_POOL = [
    "war", "coup", "sanctions", "diplomacy", "election",
    "invasion", "regime", "unrest", "nuclear", "ceasefire",
    "conflict", "rebellion", "terrorism", "military", "proxy war",
    "summit", "un", "peacekeeping", "insurgency", "hostilities"
]

KEYWORD_EXPANSIONS = {
    "war": ["warfare", "conflict", "battle", "fighting", "hostilities", "military action"],
    "coup": ["regime change", "military takeover", "uprising", "rebellion"],
    "diplomacy": ["negotiation", "talks", "summit", "peace effort", "mediation"],
    "nuclear": ["atomic", "radiological", "nuclear weapons", "warhead", "icbm", "irbm"],
    "ceasefire": ["truce", "armistice", "peace agreement", "peace negotiations"],
    "sanctions": ["embargo", "trade restrictions", "economic penalties", "blacklist"],
    "israel": ["gaza", "palestine", "israeli airstrikes", "israel humanitarian", "israel hezbollah", "israel hamas"],
    "hamas": ["gaza", "palestine", "oct 7th", "hamas tunnels", "hamas iran support", "israel hamas", "hamas support"],
    "regime": ["government", "authority", "administration", "leadership"],
    "airstrike": ["bombing", "strafe", "jdam", "missile strike", "ballistic missile"],
    "geopolitics": ["global affairs", "strategic rivalry", "international relations"],
    "space force": ["trump space force", "norad", "international space station", "space x"],
    "elon musk": ["doge", "tesla", "elon musk twitter", "us politics", "elon vs trump", "tesla stocks", "space x", "starlink"],
    "politics": ["us affairs", "us strategic partner", "state elections", "voter registration", "voter id"],
    "military": ["armed forces", "troops", "soldiers", "combat units"],
    "election": ["vote", "voting", "polls", "electoral process"],
    "us election": ["us vote", "us voting", "us polls", "us electoral process", "current us election polls", "us election results"],
    "un": ["united nations", "security council", "un peacekeeping"],
    "unrest": ["civil unrest", "riots", "riot", "protest", "civil war"],
    "invasion": ["incursion", "occupation", "offensive", "military entry", "special military operation"],
    "iran": ["tehran", "irgc", "revolutionary guard", "islamic republic", "ayatollah"],
    "us": ["us bombs", "us airstrike", "united states", "us military", "aegis", "thadd", "us hypersonic", "cia", "fbi"],
    "atf": ["nfa repeal", "nfa", "machine gun laws", "waco", "ruby ridge", "atf explosives", "atf marijuana", "atf gun charges"],
    "africa": ["south africa", "african christians", "african muslims", "al shabaab", "harakat al shabaab al mujahideen", "somalia", "al shabaab militant training camp", "african radicalization campaign"],
    "syria": ["aleppo", "hts", "al nusra front", "chemical weapons in syria", "russian bases in syria", "bashar al assad", "hezbollah fighters syria"],
    "north korea": ["dprk", "kim jong un", "nk", "pyongyang", "nuclear provocation"],
    "china": ["ccp", "bejing", "pla", "prc", "5th gen aircraft", "6th gen aircraft", "stealth", "xi jinping"],
    "ukraine": ["zelenskyy", "ukraine aid", "azov", "armed forces of ukraine", "f16", "himars", "kursk", "kyiv"],
    "kyiv": ["patriot air defense", "kinzhal", "russian strategic bombers", "afu", "ukrainian defense", "fpv drones", "isr", "starlink"],
    "events": ["current world events", "breaking news", "todays news", "world events", "military industrial complex"],
    "pla": ["china", "pla air defense", "taiwan invasion", "taiwan defense", "south china sea"],
    "india": ["narendra modi", "modi", "delhi", "pegasus spyware", "rupee", "digital india"],
    "us afghanistan": ["taliban", "isis", "kandahar", "kabul", "al qaeda", "counterinsurgency", "drone strike", "Operation Enduring Freedom"],
    "afghanistan": ["terrorist", "womens rights under taliban", "pakistan isi", "kabul", "loya jirga", "counterinsurgency", "drone strike", "Operation Enduring Freedom", "hamid karzai"],
    "iran proxies": ["hezbollah", "hamas", "palestinian islamic jihad", "houthis", "harakat hezbollah al nujaba", "zaynabiyoun brigade", "fatemiyoun division", "saraya al mukhtar", "asaib ahl al haq"],
    "taliban": ["isis", "al qaeda", "kandahar", "kabul", "democratic transition", "Haqqani network", "cross-border movement", "Abu Bakr al Baghdadi"],
    "russia": ["cccp", "kremlin", "putin", "gru", "russian federation", "su-57", "russia nuclear threats", "russian hackers", "apt"]
}

BLACKLISTED_KEYWORDS = ["privacy", "terms", "cookies", "about", "contact", "login"]

def extract_updater_if_needed():
    if not os.path.exists(APPDATA_DIR):
        os.makedirs(APPDATA_DIR)
    
    if not os.path.exists(UPDATER_PATH):
        try:
            embedded_updater = os.path.join(sys._MEIPASS, "updater.exe")
            shutil.copyfile(embedded_updater, UPDATER_PATH)
        except Exception as e:
            print(f"[Updater Extract Failed]: {e}")

extract_updater_if_needed()

def build_regex_patterns(keywords):
    return [re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in keywords]
    
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    return "#{:02x}{:02x}{:02x}".format(max(0, min(255, int(rgb_tuple[0]))), max(0, min(255, int(rgb_tuple[1]))), max(0, min(255, int(rgb_tuple[2]))))


def interpolate(c1, c2, factor):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * factor) for i in range(3))
    
def adjust_color_brightness(hex_color, factor):
    rgb = hex_to_rgb(hex_color)
    brightened = tuple(min(255, int(c * factor)) for c in rgb)
    return rgb_to_hex(brightened)
    
def toggle_debug_console():
    if show_debug_console.get():
        sys.stdout = ConsoleRedirect()
        sys.stderr = ConsoleRedirect()
        debug_console.configure(state="normal")
        debug_console.insert("end", "[STATS] Debug console enabled\n", "STATS")
        debug_console.configure(state="disabled")
        notebook.select(console_tab)
    else:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        debug_console.configure(state="normal")
        debug_console.delete("1.0", "end")
        debug_console.configure(state="disabled")

def update_viewer_brightness():
    factor = viewer_brightness.get()
    bg = adjust_color_brightness(DARK_BG, factor)
    fg = adjust_color_brightness(DARK_FG, factor)

    output_text.config(bg=bg, fg=fg, insertbackground=fg, selectbackground=DARK_ACCENT, selectforeground=fg)

def extract_article_links(homepage_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        res = requests.get(homepage_url, headers=headers, timeout=8)
        print(f"[DEBUG] GET {homepage_url} → {res.status_code}")

        soup = BeautifulSoup(res.text, "html.parser")
        links = [a['href'] for a in soup.find_all("a", href=True)]

        full_urls = []
        base = '/'.join(homepage_url.split('/')[:3])

        for link in links:
            lower_link = link.lower()
            if any(bad in lower_link for bad in BLACKLISTED_KEYWORDS):
                continue

            if link.startswith("http"):
                full_urls.append(link)
            elif link.startswith("/"):
                full_urls.append(base + link)

        clean_links = list(set(full_urls))
        print(f"[DEBUG] Extracted {len(clean_links)} links from {homepage_url}")
        return clean_links[:10]

    except Exception as e:
        print(f"[extract_article_links ERROR] {e}")
        return []
        
def update_viewer_highlight_colors():
    factor = viewer_tag_brightness.get()
    style = highlight_style.get()

    def apply(tag, base_color):
        bright = adjust_color_brightness(base_color, factor)
        output_text.tag_config(tag, foreground=bright)

    if style == "vibrant":
        apply("match-direct", "#ff00ff")
        apply("match-expanded", "#ff9900")
        apply("title", "#ff33cc")
        apply("url", "#00ccff")
    elif style == "contrast":
        apply("match-direct", "#00ffff")
        apply("match-expanded", "#ffff00")
        apply("title", "#cc00cc")
        apply("url", "#ffcc00")
    elif style == "pastel":
        apply("match-direct", "#c080c0")
        apply("match-expanded", "#f0c987")
        apply("title", "#aec6cf")
        apply("url", "#9fe2bf")
    elif style == "neon":
        apply("match-direct", "#00ff00")
        apply("match-expanded", "#ff0055")
        apply("title", "#33ffff")
        apply("url", "#ffff33")
    elif style == "solarized":
        apply("match-direct", "#268bd2")
        apply("match-expanded", "#b58900")
        apply("title", "#2aa198")  
        apply("url", "#859900")
    else:
        apply("match-direct", "#008000")
        apply("match-expanded", "#0000ff")
        apply("title", "#0000ff")
        apply("url", "#008080")

    apply("warn", "#ffa500")     
        
def extract_rss_links(rss_url, limit=10):
    try:
        feed = feedparser.parse(rss_url)
        links = [entry.link for entry in feed.entries]
        return links[:limit]
    except Exception:
        return []
        
def safe_insert(text_widget, *args, tag=None):
    def callback():
        if tag:
            text_widget.insert(tk.END, *args, tag)
        else:
            text_widget.insert(tk.END, *args)
    text_widget.after(0, callback)
    
def safe_delete(widget, start="1.0", end=tk.END):
    def callback():
        widget.delete(start, end)
    widget.after(0, callback)
    
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
    
def set_highlight_style(style):
    highlight_style.set(style)
    update_viewer_highlight_colors()
    
def fade_background(widget, color_index=0, step=0):
    if not rgb_enabled.get():
        if rgb_active_state[0]:
            widget.config(bg=DARK_BG2)
            rgb_active_state[0] = False
        widget.after(300, fade_background, widget, color_index, step)
        return

    rgb_active_state[0] = True

    steps = fade_steps.get()
    c1 = hex_to_rgb(RGB_COLORS[color_index % len(RGB_COLORS)])
    c2 = hex_to_rgb(RGB_COLORS[(color_index + 1) % len(RGB_COLORS)])
    factor = step / steps
    blended_rgb = interpolate(c1, c2, factor)

    b = rgb_brightness.get()
    brightened = tuple(min(255, int(c * b)) for c in blended_rgb)
    blended_hex = rgb_to_hex(brightened)

    widget.config(bg=blended_hex)

    delay = max(10, rgb_speed.get())
    if step < steps:
        widget.after(delay, fade_background, widget, color_index, step + 1)
    else:
        widget.after(delay, fade_background, widget, color_index + 1, 0)
        
def save_settings_to_registry():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, "rgb_speed", 0, winreg.REG_DWORD, rgb_speed.get())
        winreg.SetValueEx(key, "rgb_brightness", 0, winreg.REG_SZ, str(rgb_brightness.get()))
        winreg.SetValueEx(key, "fade_steps", 0, winreg.REG_DWORD, fade_steps.get())
        winreg.SetValueEx(key, "viewer_brightness", 0, winreg.REG_SZ, str(viewer_brightness.get()))
        winreg.SetValueEx(key, "viewer_tag_brightness", 0, winreg.REG_SZ, str(viewer_tag_brightness.get()))
        winreg.SetValueEx(key, "rgb_enabled", 0, winreg.REG_DWORD, int(rgb_enabled.get()))
        winreg.SetValueEx(key, "highlight_style", 0, winreg.REG_SZ, highlight_style.get())
        winreg.SetValueEx(key, "show_debug_console", 0, winreg.REG_DWORD, int(show_debug_console.get()))

        winreg.CloseKey(key)
    except Exception as e:
        print("Error saving settings:", e)
        
def load_settings_from_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)

        rgb_speed.set(winreg.QueryValueEx(key, "rgb_speed")[0])
        rgb_brightness.set(float(winreg.QueryValueEx(key, "rgb_brightness")[0]))
        fade_steps.set(winreg.QueryValueEx(key, "fade_steps")[0])
        viewer_brightness.set(float(winreg.QueryValueEx(key, "viewer_brightness")[0]))
        viewer_tag_brightness.set(float(winreg.QueryValueEx(key, "viewer_tag_brightness")[0]))
        rgb_enabled.set(bool(winreg.QueryValueEx(key, "rgb_enabled")[0]))
        highlight_style.set(winreg.QueryValueEx(key, "highlight_style")[0])
        show_debug_console.set(bool(winreg.QueryValueEx(key, "show_debug_console")[0]))
        toggle_debug_console()
        update_viewer_highlight_colors()
        notebook.select(settings_frame)

        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    except Exception as e:
        print("Error loading settings:", e)
        
def reset_settings():
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    except FileNotFoundError:
        pass

    rgb_speed.set(50)
    rgb_brightness.set(1.0)
    viewer_brightness.set(1.0)
    fade_steps.set(25)
    viewer_tag_brightness.set(1.0)
    rgb_enabled.set(False)
    highlight_style.set("default")
    show_debug_console.set(False)

    editor_bg.set(DARK_BG)
    editor_fg.set(DARK_FG)
    editor_cursor.set(DARK_FG)

    update_viewer_brightness()
    update_viewer_highlight_colors()
    rgb_active_state[0] = True
    fade_background(source_frame)
    toggle_debug_console()

    slider_rgb_speed.set(rgb_speed.get())
    slider_rgb_brightness.set(rgb_brightness.get())
    slider_viewer_brightness.set(viewer_brightness.get())
    slider_fade_steps.set(fade_steps.get())
    slider_viewer_tag_brightness.set(viewer_tag_brightness.get())
    checkbox_rgb_enabled.deselect() if not rgb_enabled.get() else checkbox_rgb_enabled.select()
    checkbox_debug_console.deselect() if not show_debug_console.get() else checkbox_debug_console.select()

    settings_tab.update_idletasks()

    messagebox.showinfo(title="Settings Reset", message="All settings have been reset to default.\n\nRegistry entries cleared.")
    
def run_updater(exe_name="OSINTTool.exe", update_file="OSINTTool_update.exe"):
    log_path = os.path.join(os.path.dirname(sys.executable), "update_log.txt")

    def log(msg):
        with open(log_path, "a") as f:
            f.write(f"{time.ctime()} | {msg}\n")

    reset_settings()

    if not os.path.exists(UPDATER_PATH):
        log(f"[ERROR] Updater not found at: {UPDATER_PATH}")
        return

    try:
        args = [UPDATER_PATH, exe_name, update_file]
        startupinfo = None

        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.Popen(args, startupinfo=startupinfo)
        log(f"[INFO] Updater launched with args: {args}")
    except Exception as e:
        log(f"[ERROR] Failed to launch updater: {e}")

    root.destroy()
    
def check_for_update():
    try:
        print("[DEBUG] Starting update check...")
        with urllib.request.urlopen(VERSION_URL) as res:
            print("[DEBUG] Fetched version.json")
            data = json.loads(res.read().decode())

        latest_version = data["version"]
        download_url = data["url"]
        print(f"[DEBUG] Current: {CURRENT_VERSION}, Latest: {latest_version}")

        if version.parse(latest_version) > version.parse(CURRENT_VERSION):
            print("[DEBUG] New version available")
            result = messagebox.askyesno("Update Available", f"A new version ({latest_version}) is available.\n\nDownload and install now?")
            if result:
                tmp_path = os.path.join(tempfile.gettempdir(), "OSINTTool_update.exe")
                print(f"[DEBUG] Downloading to: {tmp_path}")
                urllib.request.urlretrieve(download_url, tmp_path)
                print("[DEBUG] Download complete. Launching updater.")
                run_updater("OSINTTool.exe", tmp_path)
        else:
            print("[DEBUG] Already up to date.")
            messagebox.showinfo("No Update", "You're already using the latest version.")
    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{e}")

def run_scan():
    base_keywords = [k.strip().lower() for k in keyword_entry.get().split(",") if k.strip()]
    selected = [name for name, var in source_vars.items() if var.get()]
    safe_delete(output_text, "1.0", tk.END)

    if not base_keywords or not selected:
        messagebox.showwarning("Missing Info", "Please enter keywords and select at least one source.")
        return

    regex_patterns = []
    pattern_source = {}

    for kw in base_keywords:
        pat = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
        regex_patterns.append(pat)
        pattern_source[pat] = ("direct", kw)

    for kw in base_keywords:
        for synonym in KEYWORD_EXPANSIONS.get(kw, []):
            pat = re.compile(rf"\b{re.escape(synonym)}\b", re.IGNORECASE)
            regex_patterns.append(pat)
            pattern_source[pat] = ("expanded", synonym)

    total_sources = len(selected)
    source_failures = 0

    for name in selected:
        try:
            home_url = SECTIONS[name]
            display_url = home_url.replace("rss::", "")
            safe_insert(output_text, f"\n📡 {name} ({display_url})\n{'-'*80}\n", tag="header")

            if home_url.startswith("rss::"):
                article_links = extract_rss_links(home_url.replace("rss::", ""))
            else:
                article_links = extract_article_links(home_url)

            if not article_links:
                safe_insert(output_text, "  ⚠️ No links found on homepage.\n\n", "warn")
                print(f"[WARN] No links returned for {name}: {home_url}")
                continue

            found_any = False
            for link in article_links:
                try:
                    print(f"[DEBUG] Processing article: {link}")
                    a = Article(link)
                    a.download()
                    a.parse()
                    title = a.title.strip() or "(No title)"
                    text = a.text

                    if not text.strip():
                        print(f"[WARN] Empty article text: {link}")
                        continue

                    matched_terms = []
                    for pat in regex_patterns:
                        if pat.search(text):
                            match_type, term_str = pattern_source[pat]
                            matched_terms.append((term_str, match_type))

                    if matched_terms:
                        found_any = True
                        safe_insert(output_text, f"📰 {title}\n", "title")
                        safe_insert(output_text, f"🔗 {link}\n", "url")

                        direct_hits = [term for term, kind in matched_terms if kind == "direct"]
                        expanded_hits = [term for term, kind in matched_terms if kind == "expanded"]

                        if direct_hits:
                            safe_insert(output_text, f"✅ Direct: {', '.join(direct_hits)}\n", "match-direct")
                        if expanded_hits:
                            safe_insert(output_text, f"🔄 Synonyms: {', '.join(expanded_hits)}\n", "match-expanded")

                        for pat in regex_patterns:
                            match = pat.search(text)
                            if match:
                                loc = match.start()
                                snippet = text[max(0, loc - 60):loc + 160].replace("\n", " ").strip()
                                match_type, _ = pattern_source[pat]
                                tag = "match-direct" if match_type == "direct" else "match-expanded"
                                safe_insert(output_text, f"    → {snippet}...\n", tag)
                        safe_insert(output_text, "\n")
                except Exception as e:
                    print(f"[ERROR] Article parse failed: {link} → {e}")
                    continue

            if not found_any:
                safe_insert(output_text, "  🚫 No matching keywords found in articles.\n\n", "warn")
        except Exception as e:
            source_failures += 1
            safe_insert(output_text, f"  ❌ Error processing {name}: {e}\n\n", "warn")
            print(f"[ERROR] Source '{name}' failed: {e}")

    print(f"[STATS] Completed scan. Sources attempted: {total_sources}, Failures: {source_failures}")

root = tk.Tk()
icon_image = tk.PhotoImage(file=resource_path("7793227.png"))
root.iconphoto(False, icon_image)
rgb_speed = tk.IntVar(value=50)
rgb_brightness = tk.DoubleVar(value=1.0)
viewer_brightness = tk.DoubleVar(value=1.0)
fade_steps = tk.IntVar(value=25)
viewer_tag_brightness = tk.DoubleVar(value=1.0)
rgb_enabled = tk.BooleanVar(value=False)
highlight_style = tk.StringVar(value="default")
show_debug_console = tk.BooleanVar(value=False)
editor_bg = tk.StringVar(value=DARK_BG)
editor_fg = tk.StringVar(value=DARK_FG)
editor_cursor = tk.StringVar(value=DARK_FG)
root.configure(bg=DARK_BG)
style = ttk.Style()
style.theme_use("default")
style.configure("TFrame", background=DARK_BG)
style.configure("TLabel", background=DARK_BG, foreground=DARK_FG)
style.configure("TCheckbutton", background=DARK_BG, foreground=DARK_FG)
style.configure("TNotebook", background=DARK_BG)
style.configure("TNotebook.Tab", background=DARK_ACCENT, foreground=DARK_FG)
style.map("TNotebook.Tab", background=[("selected", DARK_FG)], foreground=[("selected", DARK_BG)])
root.title(f"📰 OSINT Scraper (GUI) v{CURRENT_VERSION} @Logiztiic")
root.geometry("980x690")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

settings_frame = ttk.Frame(notebook)
notebook.add(settings_frame, text="Source Selection")

tk.Label(settings_frame, text="Keywords (comma-separated):", bg=DARK_BG, fg=DARK_FG).pack(pady=(10, 0))
keyword_entry = tk.Entry(settings_frame, width=100)
random_keywords = random.sample(KEYWORD_POOL, 5)
keyword_entry.insert(0, ", ".join(random_keywords))
keyword_entry.pack(pady=5)

source_vars = {}
source_container = tk.Frame(settings_frame, bg=DARK_BG)
source_container.pack(padx=10, pady=10, fill="both")
tk.Label(source_container, text="News Sources", fg=DARK_FG, bg=DARK_BG, font=("Helvetica", 10, "bold")).pack(anchor="w", padx=5)
source_frame = tk.Frame(source_container, bg=DARK_BG2)
source_frame.pack(padx=5, pady=5, fill="both")

cols = 4
random_sources = random.sample(list(SECTIONS.keys()), 3)

def shuffle_sources():
    for var in source_vars.values():
        var.set(False)
    random_sources = random.sample(list(SECTIONS.keys()), 3)
    for name in random_sources:
        source_vars[name].set(True)

for i, name in enumerate(SECTIONS):
    var = tk.BooleanVar(value=(name in random_sources))
    source_vars[name] = var
    cb = tk.Checkbutton(source_frame, text=name, variable=var, bg=DARK_BG, fg=DARK_FG, activebackground=DARK_BG, activeforeground=DARK_FG, selectcolor=DARK_ACCENT)
    cb.grid(row=i//cols, column=i%cols, sticky="w", padx=10)

tk.Button(settings_frame, text="🔍 Start Scan", command=lambda: threading.Thread(target=run_scan).start(), bg=DARK_ACCENT, fg=DARK_FG, activebackground=DARK_FG, activeforeground=DARK_BG).pack(pady=10)
tk.Button(settings_frame, text="🎲 Shuffle Sources", command=shuffle_sources, bg=DARK_ACCENT, fg=DARK_FG, activebackground=DARK_FG, activeforeground=DARK_BG).pack(pady=2)


results_frame = ttk.Frame(notebook)
notebook.add(results_frame, text="Results Viewer")
notebook.enable_traversal()
notebook.pack(padx=0, pady=0)

output_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=120, height=36)
output_text.config(bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, selectbackground=DARK_ACCENT, selectforeground=DARK_FG)
output_text.tag_configure("header", font=("Helvetica", 10, "bold"))
output_text.tag_configure("title", foreground="#0000ff", font=("Helvetica", 10, "bold"))
output_text.tag_configure("url", foreground="#008080")
output_text.tag_configure("match-direct", foreground="#008000")
output_text.tag_configure("match-expanded", foreground="#0000ff")
output_text.tag_configure("warn", foreground="#ffa500")
output_text.pack(padx=10, pady=10, fill="both", expand=True)

settings_tab = ttk.Frame(notebook)
notebook.add(settings_tab, text="Settings")
settings_tab.pack_propagate(False)

console_tab = ttk.Frame(notebook)
notebook.add(console_tab, text="Debug Console")
debug_console = scrolledtext.ScrolledText(console_tab, height=8, bg=DARK_BG, fg=DARK_FG, insertbackground=DARK_FG, state="disabled")
debug_console.pack(fill="both", expand=True)

debug_console.tag_config("DEBUG", foreground="#cc00cc")
debug_console.tag_config("STATS", foreground="#008000")
debug_console.tag_config("WARN", foreground="#ffa500")
debug_console.tag_config("ERROR", foreground="#ff4c4c") 

class ConsoleRedirect:
    def write(self, text):
        debug_console.configure(state="normal")

        prefix = text.lstrip().upper()
        if prefix.startswith("[DEBUG]"):
            tag = "DEBUG"
        elif prefix.startswith("[STATS]"):
            tag = "STATS"
        elif prefix.startswith("[ERROR]"):
            tag = "ERROR"
        elif prefix.startswith("[WARN]"):
            tag = "WARN"
        else:
            tag = None

        if tag:
            debug_console.insert("end", text, tag)
        else:
            debug_console.insert("end", text)

        debug_console.see("end")
        debug_console.configure(state="disabled")

    def flush(self): pass

settings_inner = tk.Frame(settings_tab, bg=DARK_BG, bd=0, highlightthickness=0)
settings_inner.pack(fill="both", expand=True, pady=0)

theme_frame = tk.Frame(settings_inner, bg=DARK_BG)
theme_frame.grid(row=0, column=0, columnspan=1, sticky="nw", padx=10, pady=0)

checkers_frame = tk.Frame(settings_inner, bg=DARK_BG)
checkers_frame.grid(row=1, column=0, columnspan=1, sticky="nw", padx=10, pady=10)

tk.Label(theme_frame, text="Viewer Text Highlight Themes", bg=DARK_BG, fg=DARK_FG, font=("Helvetica", 9, "bold")).pack(anchor="w")
tk.Radiobutton(theme_frame, text="Default (Green/Blue)", variable=highlight_style, value="default", command=lambda: set_highlight_style("default"), bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w", pady=0)
tk.Radiobutton(theme_frame, text="Vibrant (Magenta/Orange)", variable=highlight_style, value="vibrant", command=lambda: set_highlight_style("vibrant"), bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w", pady=0)
tk.Radiobutton(theme_frame, text="Contrast (Cyan/Yellow)", variable=highlight_style, value="contrast", command=lambda: set_highlight_style("contrast"), bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w", pady=0)
tk.Radiobutton(theme_frame, text="Pastel (Lavender/Peach)", variable=highlight_style, value="pastel", command=lambda: set_highlight_style("pastel"), bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w", pady=0)
tk.Radiobutton(theme_frame, text="Neon (BrightGreen/BrightRed)", variable=highlight_style, value="neon", command=lambda: set_highlight_style("neon"), bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w", pady=0)
tk.Radiobutton(theme_frame, text="Solarized (Blue/Orange)", variable=highlight_style, value="solarized", command=lambda: set_highlight_style("solarized"), bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w", pady=0)

col = 1

slider_rgb_speed = tk.DoubleVar()
slider_rgb_brightness = tk.DoubleVar()
slider_viewer_brightness = tk.DoubleVar()
slider_fade_steps = tk.DoubleVar()
slider_viewer_tag_brightness = tk.DoubleVar()


frame_rgb_speed = tk.Frame(settings_inner, bg=DARK_BG)
frame_rgb_speed.grid(row=1, column=col, columnspan=2, pady=10)
settings_inner.grid_rowconfigure(1, minsize=0, pad=0, weight=0)
tk.Label(frame_rgb_speed, text="RGB Cycle Speed (ms):", bg=DARK_BG, fg=DARK_FG).pack(anchor="w", pady=0)
slider_rgb_speed_widget = tk.Scale(frame_rgb_speed, from_=10, to=300, variable=rgb_speed, orient="horizontal", length=300, bg=DARK_BG, fg=DARK_FG, troughcolor=DARK_ACCENT)
slider_rgb_speed_widget.pack(pady=0)

frame_rgb_brightness = tk.Frame(settings_inner, bg=DARK_BG)
frame_rgb_brightness.grid(row=2, column=col, columnspan=2, pady=0)
settings_inner.grid_rowconfigure(2, minsize=0, pad=0, weight=0)
tk.Label(frame_rgb_brightness, text="RGB Brightness:", bg=DARK_BG, fg=DARK_FG).pack(anchor="w", pady=0)
slider_rgb_brightness_widget = tk.Scale(frame_rgb_brightness, from_=0.1, to=1.0, resolution=0.05, variable=rgb_brightness, orient="horizontal", length=300, bg=DARK_BG, fg=DARK_FG, troughcolor=DARK_ACCENT)
slider_rgb_brightness_widget.pack(pady=0)

frame_viewer_brightness = tk.Frame(settings_inner, bg=DARK_BG)
frame_viewer_brightness.grid(row=3, column=col, columnspan=2, pady=5)
tk.Label(frame_viewer_brightness, text="Results Viewer Brightness:", bg=DARK_BG, fg=DARK_FG).pack(anchor="w", pady=0)
slider_viewer_brightness_widget = tk.Scale(frame_viewer_brightness, from_=0.5, to=1.5, resolution=0.05, variable=viewer_brightness, orient="horizontal", length=300, bg=DARK_BG, fg=DARK_FG, troughcolor=DARK_ACCENT, command=lambda _: update_viewer_brightness())
slider_viewer_brightness_widget.pack(pady=0)

frame_fade_steps = tk.Frame(settings_inner, bg=DARK_BG)
frame_fade_steps.grid(row=4, column=col, columnspan=2, pady=5)
tk.Label(frame_fade_steps, text="Fade Smoothness (Steps):", bg=DARK_BG, fg=DARK_FG).pack(anchor="w", pady=0)
slider_fade_steps_widget = tk.Scale(frame_fade_steps, from_=5, to=100, variable=fade_steps, orient="horizontal", length=300, bg=DARK_BG, fg=DARK_FG, troughcolor=DARK_ACCENT)
slider_fade_steps_widget.pack(pady=0)

frame_viewer_tag_brightness = tk.Frame(settings_inner, bg=DARK_BG)
frame_viewer_tag_brightness.grid(row=5, column=col, columnspan=2, pady=5)
tk.Label(frame_viewer_tag_brightness, text="Text Highlight Brightness:", bg=DARK_BG, fg=DARK_FG).pack(anchor="w", pady=0)
slider_viewer_tag_brightness_widget = tk.Scale(frame_viewer_tag_brightness, from_=0.5, to=1.5, resolution=0.05, variable=viewer_tag_brightness, orient="horizontal", length=300, bg=DARK_BG, fg=DARK_FG, troughcolor=DARK_ACCENT, command=lambda _: update_viewer_highlight_colors())
slider_viewer_tag_brightness_widget.pack(pady=0)

label_interface_options = tk.Label(checkers_frame, text="RGB & Debug Settings", font=("Helvetica", 9, "bold"), bg=DARK_BG, fg=DARK_FG)
label_interface_options.grid(row=0, column=0, sticky="w", pady=(0, 5))

checkbox_rgb_enabled = tk.Checkbutton(checkers_frame, text="Enable RGB Animation", variable=rgb_enabled, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG)
checkbox_rgb_enabled.grid(row=1, column=0, sticky="w", pady=(0, 2), padx=10)

checkbox_debug_console = tk.Checkbutton(checkers_frame, text="Enable Debug Console", variable=show_debug_console, command=toggle_debug_console, bg=DARK_BG, fg=DARK_FG, selectcolor=DARK_ACCENT, activebackground=DARK_BG, activeforeground=DARK_FG)
checkbox_debug_console.grid(row=2, column=0, sticky="w", pady=(0, 10), padx=10)

update_button = tk.Button(checkers_frame, text="Check for Updates", command=check_for_update, bg=DARK_ACCENT, fg=DARK_FG, activebackground=DARK_FG, activeforeground=DARK_BG)
update_button.grid(row=4, column=0, columnspan=1, pady=(0, 2))

reset_button = tk.Button(settings_inner, text="🔄 Reset All Settings", command=reset_settings, bg=DARK_ACCENT, fg=DARK_FG, activebackground=DARK_FG, activeforeground=DARK_BG)
reset_button.grid(row=6, column=col, columnspan=2, pady=10)

settings_inner.grid_rowconfigure(2, weight=0)
settings_inner.grid_rowconfigure(1, weight=0, minsize=0, pad=0)
settings_inner.grid_columnconfigure(0, weight=1)
settings_inner.grid_columnconfigure(1, weight=1)
settings_inner.grid_columnconfigure(2, weight=1)
settings_inner.grid_propagate(False)

root.after(0, load_settings_from_registry)

fade_background(source_frame) 

root.protocol("WM_DELETE_WINDOW", lambda: (save_settings_to_registry(), root.destroy())) 
root.mainloop()

