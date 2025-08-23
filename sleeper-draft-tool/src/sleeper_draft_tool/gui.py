from tkinter import Tk, Frame, Label, Button, BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM
from tkinter import messagebox
from tkinter.ttk import Treeview, Scrollbar, Style, Notebook
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

        # Notebook for position tabs
        self.notebook = Notebook(table_frame)
        self.notebook.pack(fill=BOTH, expand=True)

        # style
        style = Style()
        style.configure("Treeview", rowheight=20)

        # column definitions (StdDevs, Raw Value, Teamshare, VORP, ...)
        self.columns = (
            "raw_value",
            "stddevs",
            "teamshare",
            "vorp",
            "projection",
            "name",
            "team",
            "position",
            "player_id",
        )
        self.column_headings = {
            "raw_value": "Raw Value",
            "stddevs": "StdDevs",
            "teamshare": "Teamshare",
            "vorp": "VORP",
            "projection": "Projection",
            "name": "Name",
            "team": "Team",
            "position": "Pos",
            "player_id": "Player ID",
        }

        # map position -> (frame, tree, vsb, hsb)
        self.trees = {}

        # create an "All" tab up front
        self._create_tab("All")

        # double click will be bound per-tree when created
        self.load_players_async()

    def _create_tab(self, tab_name: str):
        if tab_name in self.trees:
            return self.trees[tab_name]

        frame = Frame(self.notebook)
        # create treeview
        tree = Treeview(frame, columns=self.columns, show="headings", selectmode="browse")
        for col in self.columns:
            tree.heading(col, text=self.column_headings.get(col, col))
        tree.column("raw_value", width=90, anchor="e")
        tree.column("stddevs", width=80, anchor="e")
        tree.column("teamshare", width=90, anchor="e")
        tree.column("vorp", width=90, anchor="e")
        tree.column("projection", width=110, anchor="e")
        tree.column("name", width=220, anchor="w")
        tree.column("team", width=70, anchor="center")
        tree.column("position", width=50, anchor="center")
        tree.column("player_id", width=90, anchor="center")

        vsb = Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

        # bind double click
        tree.bind("<Double-1>", self.on_row_double_click)

        self.notebook.add(frame, text=tab_name)
        self.trees[tab_name] = (frame, tree, vsb, hsb)
        return self.trees[tab_name]

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
            all_players = fetchers.fetch_relevant_players_with_projections(
                self.configs.API_ENDPOINT,
                self.configs.STATS_ENDPOINT,
                self.configs.LEAGUE_ID,
                self.configs.SEASON,
                self.configs.SEASON_TYPE,
                self.configs.SPORT,
                getattr(self.configs, "DRAFT_AMOUNT", None),
            )
        except Exception as e:
            self.set_status("Error loading data")
            messagebox.showerror("Error", f"Failed to load players: {e}")
            self.refresh_btn.config(state="normal")
            return

        # Build rows and collect positions
        rows = []  # tuples: (stddevs, raw_value, teamshare, vorp, proj, name, team, pos, pid)
        positions = set()
        for pid, player in all_players.players.items():
            # raw_value from player attribute or raw
            raw_value = getattr(player, "raw_value", None)
            if raw_value is None:
                raw = getattr(player, "raw", {}) or {}
                raw_value = raw.get("raw_value") or raw.get("value") or raw.get("score")
            # keep raw_value as string/number; try float for display
            try:
                raw_value_num = float(raw_value) if raw_value is not None else None
                raw_value_display = raw_value_num if raw_value_num is not None else (str(raw_value) if raw_value is not None else "")
            except Exception:
                raw_value_display = str(raw_value) if raw_value is not None else ""

            # stddevs from player attribute or raw
            stddevs = getattr(player, "stddevs", None)
            if stddevs is None:
                raw = getattr(player, "raw", {}) or {}
                stddevs = raw.get("stddevs") or raw.get("std_dev") or raw.get("stddev")
            try:
                stddevs = float(stddevs) if stddevs is not None else 0.0
            except Exception:
                stddevs = 0.0

            # teamshare from player attribute or raw
            teamshare = getattr(player, "teamshare", None)
            if teamshare is None:
                raw = getattr(player, "raw", {}) or {}
                teamshare = raw.get("teamshare") or raw.get("team_share") or raw.get("share")
            try:
                teamshare = float(teamshare) if teamshare is not None else 0.0
            except Exception:
                teamshare = 0.0

            vorp = getattr(player, "vorp", None)
            if vorp is None:
                raw = getattr(player, "raw", {}) or {}
                vorp = raw.get("vorp") or raw.get("value") or raw.get("vorp_score")
            try:
                vorp = float(vorp) if vorp is not None else 0.0
            except Exception:
                vorp = 0.0

            proj = None
            for attr in ("projection", "proj", "projected", "pts_ppr"):
                proj = getattr(player, attr, None)
                if proj is not None:
                    break
            if proj is None:
                raw = getattr(player, "raw", {}) or {}
                if isinstance(raw, dict):
                    proj = raw.get("projection") or raw.get("proj") or raw.get("pts_ppr")
                    stats = raw.get("stats")
                    if proj is None and isinstance(stats, dict):
                        proj = stats.get("pts_ppr") or stats.get("pts_std") or stats.get("pts")
            try:
                proj = float(proj) if proj is not None else 0.0
            except Exception:
                proj = 0.0

            name = " ".join(filter(None, (getattr(player, "first_name", None), getattr(player, "last_name", None)))).strip() or getattr(player, "search_full_name", "") or pid
            team = getattr(player, "team", "") or (getattr(player, "raw", {}) or {}).get("team", "")
            # determine primary position
            pos = getattr(player, "position", "") or ",".join(getattr(player, "fantasy_positions", [])[:1] or [])
            pos = pos or "UNK"
            positions.add(pos)

            rows.append((raw_value_display, stddevs, teamshare, vorp, proj, name, team, pos, pid))

        # sort globally by VORP desc then projection
        rows.sort(key=lambda r: (r[3] is None, -r[3] if isinstance(r[3], (int, float)) else 0, -r[4] if isinstance(r[4], (int, float)) else 0))

        # ensure tabs exist for each position (plus "All")
        for pos in sorted(positions):
            self._create_tab(pos)

        # update UI on main thread
        def update_tree():
            # clear all trees
            for tab_name, (_frame, tree, _vsb, _hsb) in self.trees.items():
                tree.delete(*tree.get_children())

            # populate "All" tab and position tabs
            for raw_value_display, stddevs, teamshare, vorp, proj, name, team, pos, pid in rows:
                stddevs_display = f"{stddevs:.2f}" if isinstance(stddevs, (int, float)) else str(stddevs)
                teamshare_display = f"{teamshare:.3f}" if isinstance(teamshare, (int, float)) else str(teamshare)
                vorp_display = f"{vorp:+.2f}"
                proj_display = f"{proj:.2f}" if isinstance(proj, (int, float)) else str(proj)
                raw_value_display = f"${raw_value_display:.2f}" if isinstance(raw_value_display, (int, float)) else str(raw_value_display)
                # insert into All
                _, all_tree, _, _ = self.trees["All"]
                all_tree.insert("", "end", values=(raw_value_display, stddevs_display, teamshare_display, vorp_display, proj_display, name, team, pos, pid))
                # insert into position tab if exists
                tab_key = pos if pos in self.trees else None
                if tab_key:
                    _, pos_tree, _, _ = self.trees[tab_key]
                    pos_tree.insert("", "end", values=(raw_value_display, stddevs_display, teamshare_display, vorp_display, proj_display, name, team, pos, pid))

            self.set_status(f"Loaded {len(rows)} players")
            self.refresh_btn.config(state="normal")

        self.master.after(0, update_tree)

    def on_row_double_click(self, event):
        tree = event.widget
        item = tree.selection()
        if not item:
            return
        vals = tree.item(item, "values")
        # columns: stddevs, raw_value, teamshare, vorp, projection, name, team, position, player_id
        stddevs = vals[0]
        raw_value = vals[1]
        teamshare = vals[2]
        vorp = vals[3]
        proj = vals[4]
        name = vals[5]
        pid = vals[8]
        messagebox.showinfo(
            "Player Details",
            f"{name}\nPlayer ID: {pid}\nProjection: {proj}\nVORP: {vorp}\nTeamshare: {teamshare}\nStdDevs: {stddevs}\nRaw Value: {raw_value}",
        )


if __name__ == "__main__":
    root = Tk()
    gui = SleeperDraftToolGUI(root)
    root.geometry("900x600")
    root.mainloop()