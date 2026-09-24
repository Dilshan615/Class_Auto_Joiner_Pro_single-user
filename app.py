import datetime
import os
import subprocess
import sys
import threading
import time
import webbrowser
import customtkinter as ctk
from tkinter import messagebox

# Import automation engine
from portal_automation import run_full_flow, run_login_only_flow

DATA_FILE = "user_data.txt"

DEFAULT_KEYS = [
    "USERNAME",
    "PASSWORD",
    "FIRST_NAME",
    "LAST_NAME",
    "EMAIL",
    "NATIONAL_ID",
    "PHONE_NUMBER",
    "SCHEDULED_TIME"
]


def load_user_data():
    """Reads user profile and credentials exclusively from user_data.txt."""
    data = {k: "" for k in DEFAULT_KEYS}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip().upper()
                    if key in data:
                        data[key] = val.strip()
        except Exception:
            pass
    return data


def save_user_data(data):
    """Writes updated user profile and credentials to user_data.txt."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write("# =========================================================\n")
            f.write("# JAVA INSTITUTE CLASS AUTO-JOINER - USER CONFIGURATION\n")
            f.write("# You can view and edit your credentials and profile here.\n")
            f.write("# =========================================================\n\n")
            for k in DEFAULT_KEYS:
                f.write(f"{k}={data.get(k, '')}\n")
    except Exception:
        pass


class ModernAutoJoinerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance & Modern Theme Configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Java Institute | Class Auto-Joiner Pro")
        self.geometry("1020x870")
        self.minsize(920, 740)
        self.configure(fg_color="#090D16")

        # Scheduler state
        self.scheduler_running = False
        self.scheduler_target = None
        self.sched_thread = None

        # Load profile exclusively from user_data.txt
        self.user_data = load_user_data()

        # Build Modern UI Layout
        self._build_header()
        self._build_body()
        self._build_footer()

        # Start live digital clock thread
        self._start_live_clock()

    def _start_live_clock(self):
        def _clock_tick():
            while True:
                now = datetime.datetime.now()
                time_str = now.strftime("%I:%M:%S %p")
                date_str = now.strftime("%a, %b %d, %Y")
                try:
                    self.after(0, lambda: self.clock_lbl.configure(text=f"🕒 {time_str}  •  📅 {date_str}"))
                except Exception:
                    break
                time.sleep(1)

        threading.Thread(target=_clock_tick, daemon=True).start()

    def _build_header(self):
        header = ctk.CTkFrame(self, height=88, corner_radius=0, fg_color="#0F172A", border_width=1, border_color="#1E293B")
        header.pack(fill="x", padx=0, pady=0)

        # Brand / Logo Box
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=25, pady=12)

        logo_title_row = ctk.CTkFrame(title_box, fg_color="transparent")
        logo_title_row.pack(anchor="w")

        # Glowing Badge Icon
        icon_badge = ctk.CTkLabel(
            logo_title_row,
            text="⚡",
            font=ctk.CTkFont(size=20),
            text_color="#38BDF8",
            fg_color="#1E293B",
            corner_radius=8,
            width=36,
            height=36
        )
        icon_badge.pack(side="left", padx=(0, 12))

        title = ctk.CTkLabel(
            logo_title_row,
            text="CLASS AUTO-JOINER PRO",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#F8FAFC"
        )
        title.pack(side="left")

        pro_badge = ctk.CTkLabel(
            logo_title_row,
            text="v2.5 PRO",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#38BDF8",
            fg_color="#0C4A6E",
            corner_radius=6,
            padx=8,
            pady=2
        )
        pro_badge.pack(side="left", padx=(10, 0))

        subtitle = ctk.CTkLabel(
            title_box,
            text="Java Institute Student Portal Login  •  Timetable Scanner  •  Zoom Auto-Registrar",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8"
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Right Controls: Status Pill & Real-time Clock
        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right", padx=25, pady=10)

        self.status_pill = ctk.CTkButton(
            right_box,
            text="● SYSTEM READY",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#064E3B",
            hover_color="#065F46",
            text_color="#34D399",
            corner_radius=20,
            width=160,
            height=34,
            border_width=1,
            border_color="#059669",
            state="disabled"
        )
        self.status_pill.pack(anchor="e", pady=(0, 4))

        self.clock_lbl = ctk.CTkLabel(
            right_box,
            text="🕒 --:--:--  •  📅 --",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B"
        )
        self.clock_lbl.pack(anchor="e")

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=15)

        body.columnconfigure(0, weight=4, minsize=400)
        body.columnconfigure(1, weight=6, minsize=480)
        body.rowconfigure(0, weight=1)

        # ----------------- LEFT PANEL: CREDENTIALS & ZOOM PROFILE -----------------
        left_panel = ctk.CTkScrollableFrame(
            body,
            fg_color="#111827",
            corner_radius=14,
            border_width=1,
            border_color="#1E293B"
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # Card 1: Portal Login Credentials
        cred_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        cred_header.pack(fill="x", padx=15, pady=(15, 10))

        cred_title = ctk.CTkLabel(
            cred_header,
            text="🔑  Portal Login Credentials",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#F8FAFC"
        )
        cred_title.pack(side="left")

        # Username / Student ID
        ctk.CTkLabel(left_panel, text="Student ID / Registration No", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(4, 3))
        self.user_entry = ctk.CTkEntry(
            left_panel,
            placeholder_text="e.g. 200516703056",
            height=40,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        self.user_entry.insert(0, self.user_data.get("USERNAME", ""))
        self.user_entry.pack(fill="x", padx=15, pady=(0, 10))

        # Password
        ctk.CTkLabel(left_panel, text="Portal Password", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(4, 3))
        
        pass_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        pass_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.pass_entry = ctk.CTkEntry(
            pass_frame,
            placeholder_text="Enter your portal password",
            show="•",
            height=40,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        self.pass_entry.insert(0, self.user_data.get("PASSWORD", ""))
        self.pass_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.show_pass_btn = ctk.CTkButton(
            pass_frame,
            text="👁",
            width=44,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#1E293B",
            hover_color="#334155",
            border_color="#334155",
            border_width=1,
            corner_radius=8,
            command=self._toggle_password_visibility
        )
        self.show_pass_btn.pack(side="right")

        # Divider
        ctk.CTkFrame(left_panel, height=1, fg_color="#1E293B").pack(fill="x", padx=15, pady=6)

        # Card 2: Zoom Registration Details
        zoom_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        zoom_header.pack(fill="x", padx=15, pady=(12, 10))

        zoom_title = ctk.CTkLabel(
            zoom_header,
            text="⚡  Zoom Auto-Registration Profile",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#38BDF8"
        )
        zoom_title.pack(side="left")

        # First & Last Name row
        name_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        name_row.pack(fill="x", padx=15, pady=(0, 8))
        name_row.columnconfigure(0, weight=1)
        name_row.columnconfigure(1, weight=1)

        ctk.CTkLabel(name_row, text="First Name", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(name_row, text="Last Name", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.fn_entry = ctk.CTkEntry(
            name_row,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        self.fn_entry.insert(0, self.user_data.get("FIRST_NAME", ""))
        self.fn_entry.grid(row=1, column=0, sticky="ew", pady=(3, 0))

        self.ln_entry = ctk.CTkEntry(
            name_row,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        self.ln_entry.insert(0, self.user_data.get("LAST_NAME", ""))
        self.ln_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(3, 0))

        # Email
        ctk.CTkLabel(left_panel, text="Email Address (for Zoom confirmation)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(6, 3))
        self.email_entry = ctk.CTkEntry(
            left_panel,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        self.email_entry.insert(0, self.user_data.get("EMAIL", ""))
        self.email_entry.pack(fill="x", padx=15, pady=(0, 8))

        # National ID Number
        ctk.CTkLabel(left_panel, text="National ID Number (NIC)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(6, 3))
        self.id_entry = ctk.CTkEntry(
            left_panel,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        self.id_entry.insert(0, self.user_data.get("NATIONAL_ID", ""))
        self.id_entry.pack(fill="x", padx=15, pady=(0, 8))

        # Mobile Phone
        ctk.CTkLabel(left_panel, text="Mobile Phone Number", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=15, pady=(6, 3))
        self.phone_entry = ctk.CTkEntry(
            left_panel,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#1E293B",
            border_color="#334155",
            border_width=1,
            corner_radius=8
        )
        self.phone_entry.insert(0, self.user_data.get("PHONE_NUMBER", ""))
        self.phone_entry.pack(fill="x", padx=15, pady=(0, 16))

        # Save and Reload Profile Action Buttons
        btn_grid = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_grid.pack(fill="x", padx=15, pady=(0, 20))
        btn_grid.columnconfigure(0, weight=3)
        btn_grid.columnconfigure(1, weight=1)

        save_btn = ctk.CTkButton(
            btn_grid,
            text="💾  Save Details",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#1E293B",
            hover_color="#2563EB",
            text_color="#F8FAFC",
            border_width=1,
            border_color="#3B82F6",
            height=38,
            corner_radius=8,
            command=self._save_profile_action
        )
        save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        reload_btn = ctk.CTkButton(
            btn_grid,
            text="🔄 Reload",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#94A3B8",
            border_width=1,
            border_color="#334155",
            height=38,
            corner_radius=8,
            command=self._reload_profile_action
        )
        reload_btn.grid(row=0, column=1, sticky="ew")

        # ----------------- RIGHT PANEL: ACTIONS & LIVE TERMINAL -----------------
        right_panel = ctk.CTkFrame(body, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        # Big Hero Action Card
        action_card = ctk.CTkFrame(
            right_panel,
            fg_color="#111827",
            corner_radius=14,
            border_width=1,
            border_color="#1E293B"
        )
        action_card.grid(row=0, column=0, sticky="ew", pady=(0, 15), ipady=8)

        hero_badge_row = ctk.CTkFrame(action_card, fg_color="transparent")
        hero_badge_row.pack(fill="x", padx=20, pady=(12, 10))

        hero_badge = ctk.CTkLabel(
            hero_badge_row,
            text="🎯 COMMAND CENTER",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#38BDF8",
            fg_color="#0C4A6E",
            corner_radius=6,
            padx=10,
            pady=4
        )
        hero_badge.pack(side="left")

        # Master Start Button (Rich Radiant Blue)
        self.start_btn = ctk.CTkButton(
            action_card,
            text="🚀  JOIN TODAY'S LECTURE NOW",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            height=50,
            corner_radius=10,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            cursor="hand2",
            border_width=1,
            border_color="#3B82F6",
            command=self.start_joining_process
        )
        self.start_btn.pack(fill="x", padx=20, pady=(4, 8))

        # Login Only Button (Modern Emerald / Teal)
        self.login_btn = ctk.CTkButton(
            action_card,
            text="🔑  LOGIN TO STUDENT PORTAL ONLY",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=40,
            corner_radius=10,
            fg_color="#0D9488",
            hover_color="#0F766E",
            cursor="hand2",
            border_width=1,
            border_color="#14B8A6",
            command=self.start_login_only_process
        )
        self.login_btn.pack(fill="x", padx=20, pady=(0, 10))

        # Media Controls Row (Mute Mic & Turn Off Camera)
        media_row = ctk.CTkFrame(action_card, fg_color="#0B0F19", corner_radius=10, border_width=1, border_color="#1E293B")
        media_row.pack(fill="x", padx=20, pady=(0, 10))
        media_row.columnconfigure(0, weight=1)
        media_row.columnconfigure(1, weight=1)

        self.mic_switch = ctk.CTkSwitch(
            media_row,
            text="🎤  Mute Mic on Join",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            progress_color="#EF4444",
            text_color="#F8FAFC"
        )
        self.mic_switch.select() # Default ON (Muted)
        self.mic_switch.grid(row=0, column=0, padx=16, pady=10, sticky="w")

        self.cam_switch = ctk.CTkSwitch(
            media_row,
            text="📷  Turn Off Camera",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            progress_color="#EF4444",
            text_color="#F8FAFC"
        )
        self.cam_switch.select() # Default ON (Camera Off)
        self.cam_switch.grid(row=0, column=1, padx=16, pady=10, sticky="w")




        # ----------------- SCHEDULE AUTO-JOINER CARD -----------------
        schedule_frame = ctk.CTkFrame(action_card, fg_color="#0B0F19", corner_radius=10, border_width=1, border_color="#1E293B")
        schedule_frame.pack(fill="x", padx=20, pady=(0, 8))

        sched_header = ctk.CTkFrame(schedule_frame, fg_color="transparent")
        sched_header.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            sched_header,
            text="⏰  Scheduled Auto-Join Timer",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#38BDF8"
        ).pack(side="left")

        self.sched_countdown_lbl = ctk.CTkLabel(
            sched_header,
            text="● Timer Inactive",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#94A3B8"
        )
        self.sched_countdown_lbl.pack(side="right")

        # Time Pickers Row
        # Mode & Time Pickers Row
        time_pick_row = ctk.CTkFrame(schedule_frame, fg_color="transparent")
        time_pick_row.pack(fill="x", padx=14, pady=(0, 12))

        # Action mode selector (Join vs Login only)
        self.sched_mode_menu = ctk.CTkOptionMenu(
            time_pick_row,
            values=["🚀 Auto Join Lecture", "🔑 Portal Login Only"],
            width=145,
            height=34,
            fg_color="#1E293B",
            button_color="#334155",
            corner_radius=8
        )
        self.sched_mode_menu.pack(side="left", padx=(0, 8))

        # Parse stored scheduled time if available (Default 11:40 PM)
        sched_str = self.user_data.get("SCHEDULED_TIME", "11:40 PM")
        default_h, default_m, default_ampm = "11", "40", "PM"
        if sched_str:
            try:
                parts = sched_str.strip().split()
                if len(parts) >= 2:
                    t_part, ampm_part = parts[0], parts[1].upper()
                    if ":" in t_part:
                        hm = t_part.split(":")
                        if len(hm) >= 2:
                            default_h = f"{int(hm[0]):02d}"
                            default_m = f"{int(hm[1]):02d}"
                    if ampm_part in ["AM", "PM"]:
                        default_ampm = ampm_part
            except Exception:
                pass

        # Hours dropdown
        hours = [f"{i:02d}" for i in range(1, 13)]
        self.hour_menu = ctk.CTkOptionMenu(
            time_pick_row,
            values=hours,
            width=60,
            height=34,
            fg_color="#1E293B",
            button_color="#334155",
            corner_radius=8
        )
        self.hour_menu.set(default_h)
        self.hour_menu.pack(side="left", padx=(0, 2))

        ctk.CTkLabel(time_pick_row, text=":", font=ctk.CTkFont(size=14, weight="bold"), text_color="#F8FAFC").pack(side="left", padx=1)

        # Minutes dropdown
        mins = [f"{i:02d}" for i in range(0, 60)]
        self.min_menu = ctk.CTkOptionMenu(
            time_pick_row,
            values=mins,
            width=60,
            height=34,
            fg_color="#1E293B",
            button_color="#334155",
            corner_radius=8
        )
        self.min_menu.set(default_m)
        self.min_menu.pack(side="left", padx=(2, 4))

        # AM / PM dropdown
        self.ampm_menu = ctk.CTkOptionMenu(
            time_pick_row,
            values=["AM", "PM"],
            width=68,
            height=34,
            fg_color="#1E293B",
            button_color="#334155",
            corner_radius=8
        )
        self.ampm_menu.set(default_ampm)
        self.ampm_menu.pack(side="left", padx=(0, 8))

        # Start / Cancel Schedule Button
        self.schedule_btn = ctk.CTkButton(
            time_pick_row,
            text="⏱  Set Auto Timer",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=34,
            corner_radius=8,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            command=self._toggle_schedule
        )
        self.schedule_btn.pack(side="left", fill="x", expand=True)


        # Live Activity Console Card
        log_card = ctk.CTkFrame(
            right_panel,
            fg_color="#111827",
            corner_radius=14,
            border_width=1,
            border_color="#1E293B"
        )
        log_card.grid(row=1, column=0, sticky="nsew")
        log_card.rowconfigure(1, weight=1)
        log_card.columnconfigure(0, weight=1)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))

        log_title_box = ctk.CTkFrame(log_header, fg_color="transparent")
        log_title_box.pack(side="left")

        ctk.CTkLabel(
            log_title_box,
            text="💻  Live Activity Console",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#F8FAFC"
        ).pack(side="left")

        # Console controls: Copy & Clear
        log_ctrls = ctk.CTkFrame(log_header, fg_color="transparent")
        log_ctrls.pack(side="right")

        copy_btn = ctk.CTkButton(
            log_ctrls,
            text="📋 Copy",
            width=65,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#1E293B",
            hover_color="#334155",
            border_width=1,
            border_color="#334155",
            corner_radius=6,
            command=self._copy_log
        )
        copy_btn.pack(side="left", padx=(0, 6))

        clear_btn = ctk.CTkButton(
            log_ctrls,
            text="🧹 Clear",
            width=65,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#1E293B",
            hover_color="#334155",
            border_width=1,
            border_color="#334155",
            corner_radius=6,
            command=self._clear_log
        )
        clear_btn.pack(side="left")

        # Color-Styled CTkTextbox Console
        self.log_box = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#050811",
            text_color="#CBD5E1",
            corner_radius=10,
            border_width=1,
            border_color="#1E293B",
            wrap="word"
        )
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        # Configure Color Tags for Cyber Console
        self.log_box.tag_config("timestamp", foreground="#64748B")
        self.log_box.tag_config("info", foreground="#38BDF8")
        self.log_box.tag_config("success", foreground="#34D399")
        self.log_box.tag_config("warning", foreground="#FBBF24")
        self.log_box.tag_config("error", foreground="#F87171")
        self.log_box.tag_config("highlight", foreground="#A78BFA")
        self.log_box.tag_config("divider", foreground="#334155")

        self.append_log("System initialized. Configuration loaded from user_data.txt.", "highlight")
        self.append_log("Ready! Click 'JOIN TODAY\'S LECTURE NOW' to begin automation.", "info")

    def _build_footer(self):
        footer = ctk.CTkFrame(self, height=42, corner_radius=0, fg_color="#0F172A", border_width=1, border_color="#1E293B")
        footer.pack(fill="x", side="bottom")

        dev_lbl = ctk.CTkLabel(
            footer,
            text="⚡ Developed by Manja  •  Java Institute Automation Suite v2.5 Pro",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#38BDF8"
        )
        dev_lbl.pack(side="left", padx=20, pady=8)

        # Quick Links on Footer
        web_btn = ctk.CTkButton(
            footer,
            text="🌐 Open Portal",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color="#1E293B",
            text_color="#94A3B8",
            width=90,
            height=26,
            command=lambda: webbrowser.open("https://web.javainstitute.org/web-portal/login/student.jsp")
        )
        web_btn.pack(side="right", padx=(0, 15), pady=6)

        open_txt_btn = ctk.CTkButton(
            footer,
            text="📄 user_data.txt",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color="#1E293B",
            text_color="#94A3B8",
            width=100,
            height=26,
            command=self._open_user_data_file
        )
        open_txt_btn.pack(side="right", padx=(0, 5), pady=6)

        open_folder_btn = ctk.CTkButton(
            footer,
            text="📂 Folder",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color="#1E293B",
            text_color="#94A3B8",
            width=70,
            height=26,
            command=self._open_project_folder
        )
        open_folder_btn.pack(side="right", padx=(0, 5), pady=6)

    def _toggle_password_visibility(self):
        if self.pass_entry.cget("show") == "•":
            self.pass_entry.configure(show="")
            self.show_pass_btn.configure(text="🔒")
        else:
            self.pass_entry.configure(show="•")
            self.show_pass_btn.configure(text="👁")

    def _clear_log(self):
        self.log_box.delete("1.0", "end")
        self.append_log("Console cleared.", "info")

    def _copy_log(self):
        content = self.log_box.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.append_log("Console logs copied to clipboard!", "success")

    def _open_project_folder(self):
        try:
            os.startfile(os.path.dirname(os.path.abspath(__file__)))
        except Exception:
            pass

    def _open_user_data_file(self):
        try:
            if os.path.exists(DATA_FILE):
                os.startfile(os.path.abspath(DATA_FILE))
        except Exception:
            pass

    def _save_profile_action(self):
        data = self._gather_user_data()
        save_user_data(data)
        self.append_log("User profile & credentials saved to user_data.txt successfully!", "success")

    def _reload_profile_action(self):
        self.user_data = load_user_data()
        self.user_entry.delete(0, "end")
        self.user_entry.insert(0, self.user_data.get("USERNAME", ""))
        self.pass_entry.delete(0, "end")
        self.pass_entry.insert(0, self.user_data.get("PASSWORD", ""))
        self.fn_entry.delete(0, "end")
        self.fn_entry.insert(0, self.user_data.get("FIRST_NAME", ""))
        self.ln_entry.delete(0, "end")
        self.ln_entry.insert(0, self.user_data.get("LAST_NAME", ""))
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, self.user_data.get("EMAIL", ""))
        self.id_entry.delete(0, "end")
        self.id_entry.insert(0, self.user_data.get("NATIONAL_ID", ""))
        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, self.user_data.get("PHONE_NUMBER", ""))
        self.append_log("Profile fields refreshed from user_data.txt.", "info")

    def _gather_user_data(self):
        h = self.hour_menu.get() if hasattr(self, "hour_menu") else "08"
        m = self.min_menu.get() if hasattr(self, "min_menu") else "30"
        ampm = self.ampm_menu.get() if hasattr(self, "ampm_menu") else "AM"
        return {
            "USERNAME": self.user_entry.get().strip(),
            "PASSWORD": self.pass_entry.get().strip(),
            "FIRST_NAME": self.fn_entry.get().strip(),
            "LAST_NAME": self.ln_entry.get().strip(),
            "EMAIL": self.email_entry.get().strip(),
            "NATIONAL_ID": self.id_entry.get().strip(),
            "PHONE_NUMBER": self.phone_entry.get().strip(),
            "SCHEDULED_TIME": f"{h}:{m} {ampm}"
        }

    def _toggle_schedule(self):
        if self.scheduler_running:
            self._cancel_schedule()
        else:
            self._start_schedule()

    def _start_schedule(self):
        data = self._gather_user_data()
        if not data["USERNAME"] or not data["PASSWORD"]:
            messagebox.showwarning("Missing Credentials", "Please enter your username and password before setting a schedule.")
            return

        save_user_data(data)

        h_str = self.hour_menu.get()
        m_str = self.min_menu.get()
        ampm_str = self.ampm_menu.get()

        try:
            hour = int(h_str)
            minute = int(m_str)
            if ampm_str == "PM" and hour != 12:
                hour += 12
            elif ampm_str == "AM" and hour == 12:
                hour = 0
        except Exception:
            messagebox.showerror("Invalid Time", "Invalid time selected.")
            return

        now = datetime.datetime.now()
        target_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if target_dt <= now:
            target_dt += datetime.timedelta(days=1)
            sched_day_text = "Tomorrow"
        else:
            sched_day_text = "Today"

        self.scheduler_target = target_dt
        self.scheduler_running = True

        mode_text = self.sched_mode_menu.get()
        time_display = f"{h_str}:{m_str} {ampm_str}"
        self.schedule_btn.configure(
            text="❌ Cancel Timer",
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )
        self.sched_mode_menu.configure(state="disabled")
        self.hour_menu.configure(state="disabled")
        self.min_menu.configure(state="disabled")
        self.ampm_menu.configure(state="disabled")

        self.update_status(f"● TIMER: {time_display}", color="#FBBF24", bg="#78350F", border="#D97706")
        self.append_log("--------------------------------------------------", "divider")
        self.append_log(f"⏰ Auto Timer set for {sched_day_text} at {time_display} ({mode_text})!", "highlight")
        self.append_log(f"The system will automatically wake up and run {mode_text} when {time_display} arrives.", "info")

        self.sched_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.sched_thread.start()

    def _cancel_schedule(self):
        self.scheduler_running = False
        self.schedule_btn.configure(
            text="⏱  Set Auto Timer",
            fg_color="#4F46E5",
            hover_color="#4338CA"
        )
        self.sched_mode_menu.configure(state="normal")
        self.hour_menu.configure(state="normal")
        self.min_menu.configure(state="normal")
        self.ampm_menu.configure(state="normal")
        self.sched_countdown_lbl.configure(text="● Timer Inactive", text_color="#94A3B8")
        self.update_status("● SYSTEM READY", color="#34D399", bg="#064E3B", border="#059669")
        self.append_log("⏰ Auto timer cancelled by user.", "warning")

    def _scheduler_worker(self):
        while self.scheduler_running:
            now = datetime.datetime.now()
            diff = self.scheduler_target - now
            seconds_left = int(diff.total_seconds())

            if seconds_left <= 0:
                self.scheduler_running = False
                mode = self.sched_mode_menu.get()
                def _trigger():
                    self.schedule_btn.configure(
                        text="⏱  Set Auto Timer",
                        fg_color="#4F46E5",
                        hover_color="#4338CA"
                    )
                    self.sched_mode_menu.configure(state="normal")
                    self.hour_menu.configure(state="normal")
                    self.min_menu.configure(state="normal")
                    self.ampm_menu.configure(state="normal")
                    self.sched_countdown_lbl.configure(text="🚀 Launching now!", text_color="#34D399")
                    
                    if "Login Only" in mode:
                        self.append_log("⏰ Scheduled time reached (11:40 PM)! Starting automated portal login...", "success")
                        self.start_login_only_process()
                    else:
                        self.append_log("⏰ Scheduled time reached (11:40 PM)! Starting automated lecture join...", "success")
                        self.start_joining_process()

                self.after(0, _trigger)
                break

            hrs, rem = divmod(seconds_left, 3600)
            mins, secs = divmod(rem, 60)
            countdown_str = f"⏳ In {hrs:02d}h {mins:02d}m {secs:02d}s"

            def _update_ui(c_str=countdown_str):
                if self.scheduler_running:
                    self.sched_countdown_lbl.configure(text=c_str, text_color="#FBBF24")

            self.after(0, _update_ui)
            time.sleep(1)


    def append_log(self, text, level="info"):
        def _update():
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            prefix = ""
            if level == "success":
                prefix = "✔ "
            elif level == "error":
                prefix = "✖ "
            elif level == "warning":
                prefix = "▲ "
            elif level == "highlight":
                prefix = "● "

            self.log_box.insert("end", f"[{ts}] ", "timestamp")
            self.log_box.insert("end", f"{prefix}{text}\n", level)
            self.log_box.see("end")

        self.after(0, _update)

    def update_status(self, text, color="#34D399", bg="#064E3B", border="#059669"):
        def _set():
            self.status_pill.configure(text=text, text_color=color, fg_color=bg, border_color=border)
        self.after(0, _set)

    def start_joining_process(self):
        data = self._gather_user_data()
        if not data["USERNAME"] or not data["PASSWORD"]:
            messagebox.showwarning("Missing Credentials", "Please enter your username and password.")
            return

        save_user_data(data)

        student_info = {
            "username": data["USERNAME"],
            "password": data["PASSWORD"],
            "first_name": data["FIRST_NAME"],
            "last_name": data["LAST_NAME"],
            "email": data["EMAIL"],
            "id_number": data["NATIONAL_ID"],
            "phone": data["PHONE_NUMBER"]
        }

        mute_mic = self.mic_switch.get() == 1
        turn_off_cam = self.cam_switch.get() == 1

        self.start_btn.configure(state="disabled", text="⏳  AUTOMATING IN PROGRESS...", fg_color="#334155")
        self.login_btn.configure(state="disabled")
        self.update_status("● AUTOMATING...", color="#FBBF24", bg="#78350F", border="#D97706")

        self.append_log("--------------------------------------------------", "divider")
        self.append_log("Starting auto-login, lecture detection & Zoom registration...", "highlight")
        self.append_log(f"Preferences: Mic Muted = {mute_mic} | Camera Off = {turn_off_cam}", "info")

        thread = threading.Thread(
            target=self._run_automation_thread,
            args=(student_info["username"], student_info["password"], student_info, mute_mic, turn_off_cam),
            daemon=True
        )
        thread.start()

    def _run_automation_thread(self, username, password, student_info, mute_mic, turn_off_cam):
        try:
            success = run_full_flow(
                username=username,
                password=password,
                student_info=student_info,
                mute_mic=mute_mic,
                turn_off_cam=turn_off_cam,
                log_callback=self.append_log
            )
            if success:
                self.append_log("Process completed successfully! Chrome and Zoom will stay open.", "success")
                self.update_status("● JOINED SUCCESSFULLY", color="#34D399", bg="#064E3B", border="#059669")
            else:
                self.append_log("Flow completed. Chrome is open on your screen.", "highlight")
                self.update_status("● SESSION ACTIVE", color="#38BDF8", bg="#0C4A6E", border="#0284C7")
        except Exception as e:
            self.append_log(f"Execution Error: {str(e)}", "error")
            self.update_status("● ERROR", color="#F87171", bg="#7F1D1D", border="#DC2626")
        finally:
            def _reset():
                self.start_btn.configure(
                    state="normal",
                    text="🚀  JOIN TODAY'S LECTURE NOW",
                    fg_color="#2563EB"
                )
                self.login_btn.configure(
                    state="normal",
                    text="🔑  LOGIN TO STUDENT PORTAL ONLY",
                    fg_color="#0D9488"
                )
            self.after(0, _reset)

    def start_login_only_process(self):
        data = self._gather_user_data()
        if not data["USERNAME"] or not data["PASSWORD"]:
            messagebox.showwarning("Missing Credentials", "Please enter your username and password.")
            return

        save_user_data(data)

        self.start_btn.configure(state="disabled")
        self.login_btn.configure(state="disabled", text="⏳  LOGGING IN...", fg_color="#334155")
        self.update_status("● LOGGING IN...", color="#FBBF24", bg="#78350F", border="#D97706")

        self.append_log("--------------------------------------------------", "divider")
        self.append_log("Starting portal login only (Student Dashboard)...", "highlight")

        thread = threading.Thread(
            target=self._run_login_only_thread,
            args=(data["USERNAME"], data["PASSWORD"]),
            daemon=True
        )
        thread.start()

    def _run_login_only_thread(self, username, password):
        try:
            success = run_login_only_flow(
                username=username,
                password=password,
                log_callback=self.append_log
            )
            if success:
                self.append_log("Successfully logged into student portal! Chrome will stay open.", "success")
                self.update_status("● PORTAL ACTIVE", color="#34D399", bg="#064E3B", border="#059669")
            else:
                self.append_log("Portal login encountered an issue. Please check the browser window.", "warning")
                self.update_status("● CHECK BROWSER", color="#FBBF24", bg="#78350F", border="#D97706")
        except Exception as e:
            self.append_log(f"Login Error: {str(e)}", "error")
            self.update_status("● ERROR", color="#F87171", bg="#7F1D1D", border="#DC2626")
        finally:
            def _reset():
                self.start_btn.configure(
                    state="normal",
                    text="🚀  JOIN TODAY'S LECTURE NOW",
                    fg_color="#2563EB"
                )
                self.login_btn.configure(
                    state="normal",
                    text="🔑  LOGIN TO STUDENT PORTAL ONLY",
                    fg_color="#0D9488"
                )
            self.after(0, _reset)




def main():
    app = ModernAutoJoinerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
