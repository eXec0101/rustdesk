import os
import re

SERVER = "remote.hitech-computers.net"
PUB_KEY = "Y7JI9CuH17k2GZwEKBzNUAFLpJnqc5SVfn3weaWAp9Q="
SHORT_NAME = "YRD"
FULL_NAME = "YRD - Ylberi Remote Desktop"
COMPANY = "Ylberi Hitech-Computers"
BUNDLE_ID = "net.hitech-computers.yrd"

def patch_file(path, transform_fn):
    if not os.path.exists(path):
        print(f"[SKIP] Nuk u gjet: {path}")
        return
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    new_content = transform_fn(content)
    if new_content != content:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print(f"[OK] U përditësua: {path}")
    else:
        print(f"[INFO] Asnjë ndryshim i nevojshëm: {path}")

# 1. Identiteti i brendshëm (Shërbimi, folderi AppData) dhe serveri i ngulitur
def update_config_rs(c):
    c = re.sub(r'pub const APP_NAME:\s*&str\s*=\s*"[^"]+";', f'pub const APP_NAME: &str = "{SHORT_NAME}";', c)
    c = re.sub(r'pub const ORG:\s*&str\s*=\s*"[^"]+";', f'pub const ORG: &str = "{COMPANY}";', c)
    c = c.replace('option_env!("RENDEZVOUS_SERVER").unwrap_or("")', f'option_env!("RENDEZVOUS_SERVER").unwrap_or("{SERVER}")')
    c = c.replace('option_env!("RS_PUB_KEY").unwrap_or("")', f'option_env!("RS_PUB_KEY").unwrap_or("{PUB_KEY}")')
    return c

patch_file("libs/hbb_common/src/config.rs", update_config_rs)

# 2. Titulli i dritares dhe metadata e Windows (.exe / Task Manager / Properties)
patch_file("flutter/windows/runner/main.cpp", lambda c: c.replace('L"RustDesk"', f'L"{FULL_NAME}"'))

def update_runner_rc(c):
    c = re.sub(r'VALUE "CompanyName",\s*"[^"]*"', f'VALUE "CompanyName", "{COMPANY}"', c)
    c = re.sub(r'VALUE "FileDescription",\s*"[^"]*"', f'VALUE "FileDescription", "{FULL_NAME}"', c)
    c = re.sub(r'VALUE "ProductName",\s*"[^"]*"', f'VALUE "ProductName", "{FULL_NAME}"', c)
    c = re.sub(r'VALUE "LegalCopyright",\s*"[^"]*"', f'VALUE "LegalCopyright", "Copyright (C) 2026 {COMPANY}"', c)
    return c

patch_file("flutter/windows/runner/Runner.rc", update_runner_rc)

# 3. Identiteti i macOS (Emri i shfaqur YRD dhe Bundle ID i veçantë)
def update_macos_xcconfig(c):
    c = re.sub(r'PRODUCT_BUNDLE_IDENTIFIER\s*=.*', f'PRODUCT_BUNDLE_IDENTIFIER = {BUNDLE_ID}', c)
    c = re.sub(r'PRODUCT_COPYRIGHT\s*=.*', f'PRODUCT_COPYRIGHT = Copyright © 2026 {COMPANY}. All rights reserved.', c)
    return c

patch_file("flutter/macos/Runner/Configs/AppInfo.xcconfig", update_macos_xcconfig)

def update_macos_plist(c):
    c = re.sub(r'(<key>CFBundleName</key>\s*<string>)[^<]*(</string>)', rf'\g<1>{SHORT_NAME}\g<2>', c)
    if "<key>CFBundleDisplayName</key>" in c:
        c = re.sub(r'(<key>CFBundleDisplayName</key>\s*<string>)[^<]*(</string>)', rf'\g<1>{SHORT_NAME}\g<2>', c)
    else:
        c = c.replace("<dict>\n", f"<dict>\n\t<key>CFBundleDisplayName</key>\n\t<string>{SHORT_NAME}</string>\n", 1)
    return c

patch_file("flutter/macos/Runner/Info.plist", update_macos_plist)

# 4. Paleta e ngjyrave të Ylberi Hitech-Computers (Blu e errët #1E3A8A)
def update_colors(c):
    c = c.replace("0xFF0071FF", "0xFF1E3A8A").replace("0xff0071ff", "0xFF1E3A8A")
    return c

patch_file("flutter/lib/common.dart", update_colors)

# 5. Tekstet e ndërfaqes (i18n) nga RustDesk në YRD
def update_i18n(c):
    c = re.sub(r'(:\s*["\'][^"\']*?)RustDesk([^"\']*?["\'])', rf'\g<1>{SHORT_NAME}\g<2>', c)
    return c

for lang_file in ["flutter/lib/utils/i18n/en.dart", "flutter/lib/utils/i18n/sq.dart"]:
    patch_file(lang_file, update_i18n)

# 6. Emërtimi i skedarëve përfundimtarë (.exe, .msi, .dmg) në GitHub Actions
def update_workflow(c):
    c = c.replace("rustdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.exe", "YRD-${{ env.VERSION }}-windows-${{ matrix.job.arch }}.exe")
    c = c.replace("rustdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.msi", "YRD-${{ env.VERSION }}-windows-${{ matrix.job.arch }}.msi")
    c = c.replace("rustdesk-${{ env.VERSION }}-${{ matrix.job.arch }}.dmg", "YRD-${{ env.VERSION }}-macos-${{ matrix.job.arch }}.dmg")
    c = c.replace("rustdesk-${VERSION}-${ARCH}.dmg", "YRD-${VERSION}-macos-${ARCH}.dmg")
    c = c.replace("rustdesk*-${{ matrix.job.arch }}.dmg", "YRD*-macos-${{ matrix.job.arch }}.dmg")
    return c

patch_file(".github/workflows/flutter-build.yml", update_workflow)
print("\n[PËRFUNDOI] Brendimi për YRD (Ylberi Remote Desktop) u aplikua me sukses!")