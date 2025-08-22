from tkinter import Tk, Frame, Label, Button, BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM
from tkinter import messagebox
from tkinter.ttk import Treeview, Scrollbar, Style
import threading

import config
import fetchers


class SleeperDraftToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sleeper Draft Tool - Players by Projection")

        self.configs = config.Config()

        # Top frame for controls
        ctrl_frame = Frame(master)
        ctrl_frame.pack(fill=X, padx=8, pady=6)

        self.refresh_btn = Button(ctrl_frame, text="Load / Refresh", command=self.load_players_async)
        self.refresh_btn.pack(side=LEFT)

        self.status_label = Label(ctrl_frame, text="Ready")
        self.status_label.pack(side=LEFT, padx=8)

        # Table frame
        table_frame = Frame(master)
        table_frame.pack(fill=BOTH, expand=True, padx=8, pady=(0,8))

        # Treeview setup
        style = Style()
        style.configure("Treeview", rowheight=20)

        cols = ("projection", "name", "team", "position", "player_id")
        self.tree = Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("projection", text="Projection")
        self.tree.heading("name", text="Name")
        self.tree.heading("team", text="Team")
        self.tree.heading("position", text="Pos")
        self.tree.heading("player_id", text="Player ID")

        self.tree.column("projection", width=110, anchor="e")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("team", width=70, anchor="center")
        self.tree.column("position", width=50, anchor="center")
        self.tree.column("player_id", width=90, anchor="center")

        vsb = Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

        # double click -> show details
        self.tree.bind("<Double-1>", self.on_row_double_click)

        # load initially
        self.load_players_async()

    def set_status(self, text):
        self.status_label.config(text=text)
        self.master.update_idletasks()

    def load_players_async(self):
        t = threading.Thread(target=self.load_players, daemon=True)
        t.start()

    def load_players(self):
        self.set_status("Loading players and projections...")
        self.refresh_btn.config(state="disabled")
        try:
            all_players = fetchers.fetch_all_players_with_projections(
                self.configs.API_ENDPOINT,
                self.configs.STATS_ENDPOINT,
                self.configs.LEAGUE_ID,
                self.configs.SEASON,
                self.configs.SEASON_TYPE,
                self.configs.SPORT,
            )
        except Exception as e:
            self.set_status("Error loading data")
            messagebox.showerror("Error", f"Failed to load players: {e}")
            self.refresh_btn.config(state="normal")
            return

        # Build list of (projection, player) and sort descending
        rows = []
        for pid, player in all_players.players.items():
            # try common projection attributes first
            proj = None
            for attr in ("projection", "proj", "projected", "pts_ppr"):
                proj = getattr(player, attr, None)
                if proj is not None:
                    break
            # check raw/stat fallback
            if proj is None:
                raw = getattr(player, "raw", {}) or {}
                # projections sometimes stored under raw.get("projection") or raw.get("stats")
                if isinstance(raw, dict):
                    proj = raw.get("projection") or raw.get("proj") or raw.get("pts_ppr")
                    # if stats object present inside raw, try to extract standard pts_ppr
                    stats = raw.get("stats")
                    if proj is None and isinstance(stats, dict):
                        proj = stats.get("pts_ppr") or stats.get("pts_std") or stats.get("pts")
            # final fallback
            try:
                proj = float(proj) if proj is not None else 0.0
            except Exception:
                proj = 0.0

            name = " ".join(filter(None, (getattr(player, "first_name", None), getattr(player, "last_name", None)))).strip() or getattr(player, "search_full_name", "") or pid
            team = getattr(player, "team", "") or (player.raw.get("team") if getattr(player, "raw", None) else "")
            pos = getattr(player, "position", "") or ",".join(getattr(player, "fantasy_positions", [])[:1] or [])

            rows.append((proj, name, team, pos, pid))

        # sort by projection desc
        rows.sort(key=lambda r: (r[0] is None, -r[0] if isinstance(r[0], (int, float)) else 0))

        # update UI on main thread
        def update_tree():
            self.tree.delete(*self.tree.get_children())
            for proj, name, team, pos, pid in rows:
                proj_display = f"{proj:.2f}" if isinstance(proj, (int, float)) else str(proj)
                self.tree.insert("", "end", values=(proj_display, name, team, pos, pid))
            self.set_status(f"Loaded {len(rows)} players")
            self.refresh_btn.config(state="normal")

        self.master.after(0, update_tree)

    def on_row_double_click(self, _event):
        item = self.tree.selection()
        if not item:
            return
        vals = self.tree.item(item, "values")
        pid = vals[4]
        name = vals[1]
        proj = vals[0]
        messagebox.showinfo("Player Details", f"{name}\nPlayer ID: {pid}\nProjection: {proj}")


if __name__ == "__main__":
    root = Tk()
    gui = SleeperDraftToolGUI(root)
    root.mainloop()