from tkinter import Tk, Frame, Label, Entry, Button, BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM
from tkinter import messagebox
from tkinter.ttk import Treeview, Scrollbar, Style, Notebook
import threading

import config
import fetchers
import utils

# plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class SleeperDraftToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sleeper Draft Tool - Players by Projection")

        self.configs = config.Config()
        self.rows = []          # full set of rows (tuples)
        self.positions = set()  # discovered positions

        # keep last highlighted lines per position so we can remove them
        self._selected_lines = {}         # pos -> {"line": Line2D, "marker": [Line2D,...]}
        self._position_stats = {}         # populated by load_players

        # Top frame for controls + search
        ctrl_frame = Frame(master)
        ctrl_frame.pack(fill=X, padx=8, pady=6)

        self.refresh_btn = Button(ctrl_frame, text="Load / Refresh", command=self.load_players_async)
        self.refresh_btn.pack(side=LEFT)

        Label(ctrl_frame, text="Search:").pack(side=LEFT, padx=(8, 4))
        self.search_entry = Entry(ctrl_frame)
        self.search_entry.pack(side=LEFT, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        clear_btn = Button(ctrl_frame, text="Clear", command=self.clear_search)
        clear_btn.pack(side=LEFT)

        self.status_label = Label(ctrl_frame, text="Ready")
        self.status_label.pack(side=LEFT, padx=8)

        # Graphs frame (above table)
        self.graphs_frame = Frame(master)
        self.graphs_frame.pack(fill=X, padx=8, pady=(0, 6))

        # Prepare placeholders for four position plots: WR, RB, TE, DEF
        self.plot_positions = ["WR", "RB", "TE", "DEF"]
        self._plot_frames = {}
        self._plot_canvases = {}
        for pos in self.plot_positions:
            pf = Frame(self.graphs_frame, width=200, height=150, relief="groove", bd=1)
            pf.pack(side=LEFT, fill=X, expand=True, padx=4)
            lbl = Label(pf, text=pos)
            lbl.pack(anchor="n")
            # placeholder canvas reference stored; actual canvas created when drawing
            self._plot_frames[pos] = pf
            self._plot_canvases[pos] = None

        # Table frame
        table_frame = Frame(master)
        table_frame.pack(fill=BOTH, expand=True, padx=8, pady=(0,8))

        # Notebook for position tabs
        self.notebook = Notebook(table_frame)
        self.notebook.pack(fill=BOTH, expand=True)

        # style
        style = Style()
        style.configure("Treeview", rowheight=20)

        # column definitions (Raw Value, StdDevs, Teamshare, VORP, ...)
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

        # bind double click and single selection
        tree.bind("<Double-1>", self.on_row_double_click)
        tree.bind("<<TreeviewSelect>>", self.on_row_select)

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
            # fetch league to compute position stats used for plots
            league = fetchers.fetch_league(self.configs.API_ENDPOINT, self.configs.LEAGUE_ID)
        except Exception as e:
            self.set_status("Error loading data")
            messagebox.showerror("Error", f"Failed to load players: {e}")
            self.refresh_btn.config(state="normal")
            return

        # Build rows and collect positions
        rows = []  # tuples: (raw_value_display, stddevs, teamshare, vorp, proj, name, team, pos, pid)
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

        # store for filtering and tab generation
        self.rows = rows
        self.positions = positions

        # ensure tabs exist for each position (plus "All")
        for pos in sorted(positions):
            self._create_tab(pos)

        # compute position stats required for graphs using utils helper
        try:
            position_stats = utils.calculate_position_stats(all_players, league)
        except Exception:
            position_stats = {}

        # store position stats for later (used when highlighting selected player)
        self._position_stats = position_stats

        # update UI on main thread: populate trees and update graphs
        self.master.after(0, lambda: self._populate_trees(self.rows))
        self.master.after(0, lambda: self._update_graphs(position_stats))
        self.refresh_btn.config(state="normal")

    def _populate_trees(self, rows):
        # clear all trees
        for tab_name, (_frame, tree, _vsb, _hsb) in self.trees.items():
            tree.delete(*tree.get_children())

        # populate "All" tab and position tabs
        for raw_value_display, stddevs, teamshare, vorp, proj, name, team, pos, pid in rows:
            stddevs_display = f"{stddevs:.2f}" if isinstance(stddevs, (int, float)) else str(stddevs)
            teamshare_display = f"{teamshare:.3f}" if isinstance(teamshare, (int, float)) else str(teamshare)
            vorp_display = f"{vorp:+.2f}"
            proj_display = f"{proj:.2f}" if isinstance(proj, (int, float)) else str(proj)
            raw_value_display_formatted = f"${raw_value_display:.2f}" if isinstance(raw_value_display, (int, float)) else str(raw_value_display)
            # insert into All
            _, all_tree, _, _ = self.trees["All"]
            all_tree.insert("", "end", values=(raw_value_display_formatted, stddevs_display, teamshare_display, vorp_display, proj_display, name, team, pos, pid))
            # insert into position tab if exists
            tab_key = pos if pos in self.trees else None
            if tab_key:
                _, pos_tree, _, _ = self.trees[tab_key]
                pos_tree.insert("", "end", values=(raw_value_display_formatted, stddevs_display, teamshare_display, vorp_display, proj_display, name, team, pos, pid))

        self.set_status(f"Loaded {len(rows)} players")

    def _update_graphs(self, position_stats: dict):
        """
        Draw normal curve plots for WR, RB, TE, DEF using mean/std from position_stats.
        position_stats expected format:
            { "WR": {"mean": .., "median": .., "std_dev": ..}, ... }

        Use default matplotlib axis scaling (do not force a fixed x range).
        Also update the position title label to include mean/median/stddev.
        """
        # clear any previous selection markers because canvases are recreated
        self._selected_lines = {}

        for pos in self.plot_positions:
            pf = self._plot_frames[pos]
            # capture the existing title label if present (it's the Label packed at init)
            title_label = None
            for child in pf.winfo_children():
                if isinstance(child, Label):
                    title_label = child
                    break

            # clear previous canvas/frame contents (keep title label)
            for child in pf.winfo_children():
                if child is title_label:
                    continue
                child.destroy()
            # remove old canvas if present
            old_canvas = self._plot_canvases.get(pos)
            if old_canvas:
                try:
                    old_canvas.get_tk_widget().destroy()
                except Exception:
                    pass
                self._plot_canvases[pos] = None

            stats = position_stats.get(pos)
            if not stats or stats.get("std_dev") is None or stats.get("mean") is None:
                # update title label if present
                if title_label:
                    title_label.config(text=pos + "\nN/A")
                na_label = Label(pf, text="N/A", fg="gray")
                na_label.pack(expand=True)
                continue

            mean = float(stats["mean"])
            std = float(stats["std_dev"]) if float(stats["std_dev"]) > 0 else 1.0
            median = stats.get("median", stats.get("med", None))
            try:
                median = float(median) if median is not None else None
            except Exception:
                median = None

            # update title label with stats
            if title_label:
                med_text = f" median: {median:.1f}" if median is not None else ""
                title_label.config(text=f"{pos}\nmean: {mean:.1f}{med_text}  std: {std:.2f}")

            # choose an x-range centered on the mean using std (default matplotlib autoscale will be used)
            span = max(4.0 * std, max(1.0, abs(mean) * 0.5))
            x = np.linspace(mean - span, mean + span, 300)
            # normal pdf
            y = (1.0 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)

            fig = Figure(figsize=(3, 1.8), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(x, y, color="tab:blue")
            ax.fill_between(x, y, color="tab:blue", alpha=0.2)
            ax.axvline(mean, color="tab:red", linestyle="--", linewidth=1)
            ax.set_title("")  # title moved to label
            ax.set_yticks([])
            ax.set_xlabel("Projection")
            # do NOT call ax.set_xlim(...) so matplotlib will use default/autoscale
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=pf)
            widget = canvas.get_tk_widget()
            widget.pack(fill=BOTH, expand=True)
            canvas.draw()
            self._plot_canvases[pos] = canvas

    def on_search_change(self, _event):
        q = (self.search_entry.get() or "").strip().lower()
        if not q:
            self._populate_trees(self.rows)
            return
        filtered = []
        for raw_value_display, stddevs, teamshare, vorp, proj, name, team, pos, pid in self.rows:
            if q in name.lower() or q in str(pid).lower():
                filtered.append((raw_value_display, stddevs, teamshare, vorp, proj, name, team, pos, pid))
        self._populate_trees(filtered)

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self._populate_trees(self.rows)

    def on_row_double_click(self, event):
        tree = event.widget
        item = tree.selection()
        if not item:
            return
        vals = tree.item(item, "values")
        # columns: raw_value, stddevs, teamshare, vorp, projection, name, team, position, player_id
        raw_value = vals[0]
        stddevs = vals[1]
        teamshare = vals[2]
        vorp = vals[3]
        proj = vals[4]
        name = vals[5]
        team = vals[6]
        pos = vals[7]
        pid = vals[8]
        messagebox.showinfo(
            "Player Details",
            f"{name}\nPlayer ID: {pid}\nProjection: {proj}\nVORP: {vorp}\nTeamshare: {teamshare}\nStdDevs: {stddevs}\nRaw Value: {raw_value}",
        )

        # try to highlight the selected player's projection on the appropriate position plot
        try:
            proj_val = float(str(proj).replace("+", "").strip())
        except Exception:
            # cannot parse projection, nothing to highlight
            return

        # use the first position token if multiple (e.g. "WR,RB")
        pos_key = (pos or "UNK").split(",")[0].strip().upper()
        if pos_key in self.plot_positions:
            self._highlight_on_graph(pos_key, proj_val)

    def on_row_select(self, event):
        """
        When a row is selected (single click), highlight that player's projection on the appropriate plot.
        """
        tree = event.widget
        item = tree.selection()
        if not item:
            return
        vals = tree.item(item, "values")
        # columns: raw_value, stddevs, teamshare, vorp, projection, name, team, position, player_id
        proj = vals[4]
        pos = vals[7] if len(vals) > 7 else None

        try:
            proj_val = float(str(proj).replace("+", "").strip())
        except Exception:
            return

        pos_key = (pos or "UNK").split(",")[0].strip().upper()
        if pos_key in self.plot_positions:
            self._highlight_on_graph(pos_key, proj_val)

    def _highlight_on_graph(self, pos: str, proj_value: float):
        """
        Add a vertical line and marker to the position plot for proj_value.
        Clears previous highlight for that position.
        """
        canvas = self._plot_canvases.get(pos)
        if not canvas:
            return
        fig = getattr(canvas, "figure", None)
        if not fig or not fig.axes:
            return
        ax = fig.axes[0]

        # remove existing highlight for this pos
        prev = self._selected_lines.get(pos)
        if prev:
            try:
                if prev.get("line") is not None:
                    prev["line"].remove()
                markers = prev.get("marker")
                if markers:
                    for m in markers:
                        try:
                            m.remove()
                        except Exception:
                            pass
            except Exception:
                pass
            self._selected_lines.pop(pos, None)

        # compute y coordinate for marker if mean/std known, else place at top of axis
        stats = self._position_stats.get(pos, {})
        y_val = None
        try:
            mean = float(stats.get("mean"))
            std = float(stats.get("std_dev")) if float(stats.get("std_dev")) > 0 else 1.0
            y_val = (1.0 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((proj_value - mean) / std) ** 2)
        except Exception:
            # fallback: place marker at 90% of current y-axis limit
            ylim = ax.get_ylim()
            y_val = ylim[1] * 0.9 if ylim[1] > 0 else None

        # add vertical line and marker
        try:
            line = ax.axvline(proj_value, color="green", linestyle="--", linewidth=1.5, zorder=5)
            marker_lines = []
            if y_val is not None:
                mk, = ax.plot([proj_value], [y_val], marker="o", color="green", markersize=6, zorder=6)
                marker_lines.append(mk)
            # redraw canvas
            canvas.draw()
            self._selected_lines[pos] = {"line": line, "marker": marker_lines}
        except Exception:
            # ignore plotting errors
            return


if __name__ == "__main__":
    root = Tk()
    gui = SleeperDraftToolGUI(root)
    root.geometry("1200x700")
    root.mainloop()