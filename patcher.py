#!/usr/bin/env python3
"""
Universal Unity Korean Font Patcher
A standalone tool to automatically patch, manage, and uninstall Korean custom fonts
in Unity (Mono x64) games using BepInEx runtime fallback injection.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR / "template"
FONTS_DIR = SCRIPT_DIR / "fonts"

def analyze_game_directory(game_path):
    """
    Analyzes whether the target path is a valid Unity 64-bit Mono game compatible with
    universal TextMeshPro fallback injection.
    Returns (status: bool, info: dict, message: str)
    """
    p = Path(game_path)
    if not p.exists() or not p.is_dir():
        return False, {}, f"경로가 존재하지 않거나 디렉터리가 아닙니다: {game_path}"

    # Search for *_Data directory
    data_dirs = [d for d in p.iterdir() if d.is_dir() and d.name.endswith("_Data")]
    if not data_dirs:
        return False, {}, "유니티 게임 데이터 폴더(*_Data)를 찾을 수 없습니다."

    data_dir = data_dirs[0]
    managed_dir = data_dir / "Managed"

    has_mono = (p / "MonoBleedingEdge").exists() or (data_dir / "Mono").exists()
    has_il2cpp = (data_dir / "il2cpp_data").exists() or (p / "GameAssembly.dll").exists()

    tmp_dll = managed_dir / "Unity.TextMeshPro.dll"
    has_tmp = tmp_dll.exists()

    # Check current patch state
    is_patched = (p / "winhttp.dll").exists() and (p / "BepInEx").exists()

    info = {
        "game_root": str(p),
        "data_dir": str(data_dir),
        "managed_dir": str(managed_dir),
        "is_mono": has_mono,
        "is_il2cpp": has_il2cpp,
        "has_tmp": has_tmp,
        "is_patched": is_patched,
        "game_name": p.name
    }

    if has_il2cpp and not has_mono:
        return False, info, "IL2CPP 게임 (미지원, Mono 64-bit 전용)"

    if not has_tmp:
        return False, info, "TextMeshPro 미사용 게임 (미지원)"

    # Detect known proprietary bitmap/sprite font engines or custom modloader conflicts
    has_pug_font = (managed_dir / "Pug.Other.dll").exists() or (managed_dir / "PugMod.dll").exists()
    if has_pug_font:
        return False, info, "자체 비트맵 폰트 게임 (미지원)"

    # Deep verification: verify if primary game assemblies actually reference TextMeshPro
    # In some games (like Valheim), game code is split into assembly_valheim.dll, assembly_guiutils.dll, etc.
    # In others, it is Assembly-CSharp.dll.
    game_assemblies = [
        f for f in managed_dir.glob("*.dll")
        if (
            f.name.lower().startswith("assembly")
            or f.name.lower().startswith("gui_")
            or f.name.lower() in ("game.dll", "client.dll", "main.dll")
        )
        and f.name != "Unity.TextMeshPro.dll"
    ]

    has_tmpro_ref = False
    for gasm in game_assemblies:
        try:
            content = gasm.read_bytes()
            if (b"TMP_FontAsset" in content) or (b"TMPro" in content) or (b"TextMeshPro" in content):
                has_tmpro_ref = True
                break
        except Exception:
            pass

    if game_assemblies and not has_tmpro_ref:
        return False, info, "TextMeshPro 미사용 게임 (미지원)"

    return True, info, "패치 호환 가능 (TextMeshPro x64)"




def install_patch(game_path, font_preset="maple", custom_font_files=None, log_fn=print):
    """
    Installs the universal font patch to the target game directory.
    """
    valid, info, msg = analyze_game_directory(game_path)
    if not valid:
        log_fn(f"[-] 설치 실패: {msg}")
        return False

    target_root = Path(game_path)
    log_fn(f"[*] 대상 게임: {info['game_name']} ({target_root})")

    # 1. Copy winhttp.dll and doorstop_config.ini
    log_fn("[*] Doorstop 로더 복사 중...")
    shutil.copy2(TEMPLATE_DIR / "winhttp.dll", target_root / "winhttp.dll")
    shutil.copy2(TEMPLATE_DIR / "doorstop_config.ini", target_root / "doorstop_config.ini")

    # 2. Copy BepInEx Core
    core_tgt = target_root / "BepInEx" / "core"
    core_tgt.mkdir(parents=True, exist_ok=True)
    log_fn("[*] BepInEx 코어 런타임 복사 중...")
    for item in (TEMPLATE_DIR / "BepInEx" / "core").glob("*.dll"):
        shutil.copy2(item, core_tgt / item.name)

    # 2.5. Copy Preconfigured BepInEx Config
    cfg_src = TEMPLATE_DIR / "BepInEx" / "config"
    if cfg_src.exists():
        cfg_tgt = target_root / "BepInEx" / "config"
        cfg_tgt.mkdir(parents=True, exist_ok=True)
        for cfg_file in cfg_src.glob("*.*"):
            shutil.copy2(cfg_file, cfg_tgt / cfg_file.name)

    # 3. Copy UniversalFontPlugin.dll
    plugin_tgt = target_root / "BepInEx" / "plugins"
    plugin_tgt.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_DIR / "BepInEx" / "plugins" / "UniversalFontPlugin.dll", plugin_tgt / "UniversalFontPlugin.dll")

    # 4. Copy Fonts
    fonts_tgt = plugin_tgt / "Fonts"
    fonts_tgt.mkdir(parents=True, exist_ok=True)

    # Clean existing fonts in fonts_tgt
    for old_f in fonts_tgt.glob("*.*"):
        try:
            old_f.unlink()
        except:
            pass

    log_fn(f"[*] 폰트 프리셋 적용 중: {font_preset}...")
    if custom_font_files:
        for cf in custom_font_files:
            cf_path = Path(cf)
            if cf_path.exists():
                shutil.copy2(cf_path, fonts_tgt / cf_path.name)
                log_fn(f"  + 커스텀 폰트 복사: {cf_path.name}")
    elif font_preset in ("nanum_barun", "maple"):
        # NanumBarunGothic Bold + Regular
        for nf in FONTS_DIR.glob("NanumBarunGothic*.ttf"):
            shutil.copy2(nf, fonts_tgt / nf.name)
            log_fn(f"  + 폰트 복사: {nf.name}")
    elif font_preset in ("nanum_gothic", "nanum"):
        # NanumGothic Bold + Regular
        for nf in FONTS_DIR.glob("NanumGothic*.ttf"):
            shutil.copy2(nf, fonts_tgt / nf.name)
            log_fn(f"  + 폰트 복사: {nf.name}")

    log_fn("[+] 패치가 성공적으로 설치되었습니다!")
    log_fn("[+] 게임을 실행하면 폰트가 자동 적용됩니다. (게임 중 F10 키로 폰트 핫리로드 가능)")
    return True


def uninstall_patch(game_path, log_fn=print):
    """
    Removes the universal font patch completely from the target game directory.
    """
    target_root = Path(game_path)
    if not target_root.exists():
        log_fn(f"[-] 경로가 존재하지 않습니다: {game_path}")
        return False

    removed_items = []
    winhttp = target_root / "winhttp.dll"
    if winhttp.exists():
        winhttp.unlink()
        removed_items.append("winhttp.dll")

    doorstop = target_root / "doorstop_config.ini"
    if doorstop.exists():
        doorstop.unlink()
        removed_items.append("doorstop_config.ini")

    bepinex = target_root / "BepInEx"
    if bepinex.exists() and bepinex.is_dir():
        shutil.rmtree(bepinex)
        removed_items.append("BepInEx 폴더")

    if removed_items:
        log_fn(f"[+] 패치 제거 완료: {', '.join(removed_items)} 삭제됨")
        log_fn("[+] 게임이 100% 바닐라 순정 상태로 복원되었습니다.")
        return True
    else:
        log_fn("[-] 설치된 패치 파일이 없습니다.")
        return False

# ==========================================================
# Tkinter GUI Implementation
# ==========================================================
def launch_gui():
    # Enable Windows High DPI scaling if available
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk()
    root.title("Universal Unity Korean Font Patcher")
    root.geometry("660x650")
    root.minsize(600, 580)
    root.resizable(True, True)

    # Styles
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Big.TButton", font=("Malgun Gothic", 10, "bold"), padding=8)

    main_frame = ttk.Frame(root, padding=16)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Header
    header_lbl = ttk.Label(main_frame, text="Universal Unity Korean Font Patcher", font=("Malgun Gothic", 14, "bold"))
    header_lbl.pack(anchor="w", pady=(0, 4))
    sub_lbl = ttk.Label(main_frame, text="유니티 TextMeshPro 게임 범용 한글 폰트 패처 (BepInEx Fallback Hook)", font=("Malgun Gothic", 9))
    sub_lbl.pack(anchor="w", pady=(0, 10))

    # Bottom Actions Bar (Pack at BOTTOM first so it is never clipped or pushed out)
    btn_box = ttk.Frame(main_frame)
    btn_box.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    # Game Selection
    game_box = ttk.LabelFrame(main_frame, text=" 1. 게임 폴더 선택 ", padding=10)
    game_box.pack(fill=tk.X, pady=(0, 8))

    path_var = tk.StringVar(value=r"E:\SteamLibrary\steamapps\common\House Flipper")

    def browse_folder():
        folder = filedialog.askdirectory(title="게임 설치 폴더 선택 (*_Data 폴더가 있는 루트)")
        if folder:
            path_var.set(folder)
            check_game()

    browse_btn = ttk.Button(game_box, text="찾아보기...", width=12, command=browse_folder)
    browse_btn.pack(side=tk.RIGHT, padx=(8, 0))

    path_entry = ttk.Entry(game_box, textvariable=path_var)
    path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Status Label
    status_lbl = ttk.Label(main_frame, text="상태: 게임 폴더를 확인해 주세요.", font=("Malgun Gothic", 9))
    status_lbl.pack(anchor="w", pady=(0, 8))

    def check_game(*args):
        p_val = path_var.get().strip().strip('"').strip("'")
        valid, info, msg = analyze_game_directory(p_val)
        if valid:
            state_text = f"상태: [호환] {info['game_name']}"
            if info["is_patched"]:
                state_text += " (패치 설치됨)"
            status_lbl.config(text=state_text, foreground="green")
            if 'install_btn' in globals() or 'install_btn' in locals():
                try:
                    install_btn.config(state=tk.NORMAL)
                except:
                    pass
        else:
            status_lbl.config(text=f"상태: [비호환] {msg}", foreground="red")
            if 'install_btn' in globals() or 'install_btn' in locals():
                try:
                    install_btn.config(state=tk.DISABLED)
                except:
                    pass


    path_var.trace_add("write", check_game)

    # Font Preset Selection
    font_box = ttk.LabelFrame(main_frame, text=" 2. 적용할 폰트 선택 (100% 무료/오픈소스 SIL OFL) ", padding=10)
    font_box.pack(fill=tk.X, pady=(0, 8))

    font_choice = tk.StringVar(value="nanum_barun")
    r1 = ttk.Radiobutton(font_box, text="나눔바른고딕 (NanumBarunGothic - 볼드/레귤러 자동 매핑)", variable=font_choice, value="nanum_barun")
    r1.pack(anchor="w", pady=2)
    r2 = ttk.Radiobutton(font_box, text="나눔고딕 (NanumGothic - 볼드/레귤러 자동 매핑)", variable=font_choice, value="nanum_gothic")
    r2.pack(anchor="w", pady=2)
    r3 = ttk.Radiobutton(font_box, text="사용자 정의 폰트 파일 직접 지정 (.ttf/.otf, 메이플/프리텐다드 등)", variable=font_choice, value="custom")
    r3.pack(anchor="w", pady=2)


    custom_files = []
    def browse_custom_font():
        files = filedialog.askopenfilenames(title="폰트 파일 선택", filetypes=[("Font Files", "*.ttf *.otf")])
        if files:
            nonlocal custom_files
            custom_files = list(files)
            font_choice.set("custom")
            log_print(f"[*] 선택된 커스텀 폰트: {', '.join(Path(f).name for f in custom_files)}")

    custom_btn = ttk.Button(font_box, text="폰트 파일 선택...", width=16, command=browse_custom_font)
    custom_btn.pack(anchor="w", padx=20, pady=(2, 0))

    # Log Area (Takes remaining vertical space in middle)
    log_box = ttk.LabelFrame(main_frame, text=" 실행 로그 ", padding=6)
    log_box.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

    log_text = tk.Text(log_box, height=6, font=("Consolas", 8), state=tk.DISABLED)
    log_scroll = ttk.Scrollbar(log_box, orient=tk.VERTICAL, command=log_text.yview)
    log_text.configure(yscrollcommand=log_scroll.set)
    log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def log_print(msg):
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)

    # Actions Handlers
    def on_install():
        game = path_var.get().strip()
        log_print("========================================")
        log_print(f"[*] 패치 설치 시작: {game}")
        preset = font_choice.get()
        c_files = custom_files if preset == "custom" else None
        success = install_patch(game, font_preset=preset, custom_font_files=c_files, log_fn=log_print)
        check_game()
        if success:
            messagebox.showinfo("완료", "폰트 패치가 성공적으로 설치되었습니다!\n스팀에서 게임을 실행하세요.")
        else:
            messagebox.showerror("오류", "패치 설치에 실패했습니다. 로그를 확인하세요.")

    def on_uninstall():
        game = path_var.get().strip()
        if messagebox.askyesno("패치 제거", "게임에서 폰트 패치를 제거하고 순정 상태로 복원하시겠습니까?"):
            log_print("========================================")
            log_print(f"[*] 패치 제거 시작: {game}")
            success = uninstall_patch(game, log_fn=log_print)
            check_game()
            if success:
                messagebox.showinfo("완료", "패치가 성공적으로 제거되었습니다.\n순정 상태로 복원되었습니다.")
            else:
                messagebox.showwarning("안내", "제거할 패치 파일이 없습니다.")

    install_btn = ttk.Button(btn_box, text="🚀 패치 설치", style="Big.TButton", command=on_install)
    install_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

    uninstall_btn = ttk.Button(btn_box, text="🗑️ 패치 제거 (순정 복원)", style="Big.TButton", command=on_uninstall)
    uninstall_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

    check_game()
    root.mainloop()

# ==========================================================
# CLI Entrypoint
# ==========================================================
def main():
    parser = argparse.ArgumentParser(description="Universal Unity Korean Font Patcher")
    subparsers = parser.add_subparsers(dest="command")

    # install command
    p_inst = subparsers.add_parser("install", help="Install font patch to target game")
    p_inst.add_argument("path", help="Game root directory path")
    p_inst.add_argument("--font", default="nanum_barun", choices=["nanum_barun", "nanum_gothic", "nanum", "maple"], help="Font preset (nanum_barun, nanum_gothic)")
    p_inst.add_argument("--custom", nargs="*", help="Paths to custom .ttf/.otf files")


    # uninstall command
    p_uninst = subparsers.add_parser("uninstall", help="Uninstall font patch from target game")
    p_uninst.add_argument("path", help="Game root directory path")

    # analyze command
    p_chk = subparsers.add_parser("analyze", help="Analyze target game directory compatibility")
    p_chk.add_argument("path", help="Game root directory path")

    # gui command
    subparsers.add_parser("gui", help="Launch interactive Tkinter GUI")

    args = parser.parse_args()

    if args.command == "install":
        install_patch(args.path, font_preset=args.font, custom_font_files=args.custom)
    elif args.command == "uninstall":
        uninstall_patch(args.path)
    elif args.command == "analyze":
        valid, info, msg = analyze_game_directory(args.path)
        print("호환 가능 여부:", "성공" if valid else "실패")
        print("메시지:", msg)
        for k, v in info.items():
            print(f"  {k}: {v}")
    elif args.command == "gui" or len(sys.argv) == 1:
        launch_gui()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
