from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Iterable, Iterator

@dataclass
class Player:
    player_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    search_first_name: Optional[str] = None
    search_last_name: Optional[str] = None
    search_full_name: Optional[str] = None
    hashtag: Optional[str] = None
    number: Optional[int] = None
    position: Optional[str] = None
    fantasy_positions: List[str] = field(default_factory=list)
    depth_chart_position: Optional[int] = None
    depth_chart_order: Optional[int] = None
    status: Optional[str] = None
    injury_status: Optional[str] = None
    injury_start_date: Optional[str] = None
    practice_participation: Optional[str] = None
    sport: Optional[str] = None
    team: Optional[str] = None
    college: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    age: Optional[int] = None
    years_exp: Optional[int] = None
    fantasy_data_id: Optional[int] = None
    rotoworld_id: Optional[int] = None
    rotowire_id: Optional[str] = None
    espn_id: Optional[str] = None
    yahoo_id: Optional[str] = None
    sportradar_id: Optional[str] = None
    stats_id: Optional[str] = None
    birth_country: Optional[str] = None
    search_rank: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)  # keep original JSON for reference

    @classmethod
    def from_sleeper_json(cls, player_id: str, data: Dict[str, Any]) -> "Player":
        return cls(
            player_id=str(player_id),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            search_first_name=data.get("search_first_name"),
            search_last_name=data.get("search_last_name"),
            search_full_name=data.get("search_full_name"),
            hashtag=data.get("hashtag"),
            number=data.get("number"),
            position=data.get("position"),
            fantasy_positions=list(data.get("fantasy_positions") or []),
            depth_chart_position=data.get("depth_chart_position"),
            depth_chart_order=data.get("depth_chart_order"),
            status=data.get("status"),
            injury_status=data.get("injury_status"),
            injury_start_date=data.get("injury_start_date"),
            practice_participation=data.get("practice_participation"),
            sport=data.get("sport"),
            team=data.get("team"),
            college=data.get("college"),
            height=data.get("height"),
            weight=data.get("weight"),
            age=data.get("age"),
            years_exp=data.get("years_exp"),
            fantasy_data_id=data.get("fantasy_data_id"),
            rotoworld_id=data.get("rotoworld_id"),
            rotowire_id=data.get("rotowire_id"),
            espn_id=data.get("espn_id"),
            yahoo_id=data.get("yahoo_id"),
            sportradar_id=data.get("sportradar_id"),
            stats_id=data.get("stats_id"),
            birth_country=data.get("birth_country"),
            search_rank=data.get("search_rank"),
            raw=dict(data),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AllPlayers:
    """
    Container for all Player objects returned by the /players endpoint.
    - players: mapping player_id -> Player
    - raw: original JSON dict as returned by the API
    """
    players: Dict[str, "Player"] = field(default_factory=dict)
    raw: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Dict[str, Any]]) -> "AllPlayers":
        """
        Build AllPlayers from the top-level /players JSON where each key is a player_id.
        """
        players: Dict[str, "Player"] = {}
        for pid, pdata in (data or {}).items():
            # Player.from_sleeper_json expects player_id and the data dict
            try:
                player_obj = Player.from_sleeper_json(pid, pdata)
            except Exception:
                # fallback: construct with minimal fields if parsing fails
                player_obj = Player(player_id=str(pid), raw=dict(pdata))
            players[str(pid)] = player_obj
        return cls(players=players, raw={str(k): dict(v) for k, v in (data or {}).items()})

    def get(self, player_id: str) -> Optional["Player"]:
        return self.players.get(str(player_id))

    def all(self) -> List["Player"]:
        return list(self.players.values())

    def by_position(self, position: str) -> List["Player"]:
        pos = (position or "").upper()
        return [p for p in self.players.values() if (p.position or "").upper() == pos or pos in [fp.upper() for fp in p.fantasy_positions]]

    def by_team(self, team: str) -> List["Player"]:
        t = (team or "").upper()
        return [p for p in self.players.values() if (p.team or "").upper() == t]

    def search_name(self, query: str) -> List["Player"]:
        q = (query or "").lower()
        results: List["Player"] = []
        for p in self.players.values():
            if p.search_full_name and q in p.search_full_name:
                results.append(p)
                continue
            if p.first_name and p.last_name and q in f"{p.first_name.lower()} {p.last_name.lower()}":
                results.append(p)
                continue
            if p.search_first_name and q in p.search_first_name:
                results.append(p)
                continue
            if p.search_last_name and q in p.search_last_name:
                results.append(p)
                continue
        return results

    def __len__(self) -> int:
        return len(self.players)

    def __iter__(self) -> Iterator["Player"]:
        return iter(self.players.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "players": {pid: p.to_dict() for pid, p in self.players.items()},
            "raw": dict(self.raw),
        }


@dataclass
class User:
    user_id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Any]) -> "User":
        """
        Create a User instance from a Sleeper user JSON object.
        """
        return cls(
            user_id=str(data.get("user_id") or data.get("user_id")),
            username=data.get("username"),
            display_name=data.get("display_name"),
            avatar=data.get("avatar"),
            raw=dict(data),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AllUsers:
    """
    Container for User objects returned by the users endpoint.
    - users: mapping user_id -> User
    - raw: original JSON as returned by the API (dict or list normalized)
    """
    users: Dict[str, User] = field(default_factory=dict)
    raw: Any = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Dict[str, Any]] | Iterable[Dict[str, Any]]) -> "AllUsers":
        """
        Accept either:
        - mapping-like response (dict) where each key is a user_id and each value is the user JSON,
        - or an iterable/list of user dicts.
        """
        users: Dict[str, User] = {}

        if not data:
            return cls(users={}, raw={})

        # If data is a list/iterable (no .items), normalize
        if isinstance(data, list) or not hasattr(data, "items"):
            raw_list = []
            for i, u in enumerate(data):
                raw_list.append(dict(u) if isinstance(u, dict) else u)
                try:
                    user_obj = User.from_sleeper_json(u)
                except Exception:
                    # fallback minimal
                    uid = str(u.get("user_id") or u.get("userId") or i)
                    user_obj = User(user_id=uid, raw=dict(u) if isinstance(u, dict) else {"raw": u})
                users[str(user_obj.user_id)] = user_obj
            return cls(users=users, raw={"list": raw_list})

        # data is a mapping user_id -> user dict
        for uid, udata in (data or {}).items():
            try:
                user_obj = User.from_sleeper_json(udata)
            except Exception:
                user_obj = User(user_id=str(uid), raw=dict(udata))
            users[str(user_obj.user_id or uid)] = user_obj

        return cls(users=users, raw={str(k): dict(v) for k, v in (data or {}).items()})

    def get(self, user_id: str) -> Optional[User]:
        return self.users.get(str(user_id))

    def all(self) -> List[User]:
        return list(self.users.values())

    def by_username(self, username: str) -> List[User]:
        uname = (username or "").lower()
        return [u for u in self.users.values() if (u.username or "").lower() == uname or (u.display_name or "").lower() == uname]

    def __len__(self) -> int:
        return len(self.users)

    def __iter__(self) -> Iterator[User]:
        return iter(self.users.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "users": {uid: u.to_dict() for uid, u in self.users.items()},
            "raw": dict(self.raw) if isinstance(self.raw, dict) else self.raw,
        }


@dataclass
class Team:
    roster_id: Optional[int] = None
    owner_id: Optional[str] = None
    league_id: Optional[str] = None
    players: List[str] = field(default_factory=list)
    starters: List[str] = field(default_factory=list)
    reserve: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Any]) -> "Team":
        """
        Create a Team instance from a Sleeper team JSON object.
        Ensures player IDs are strings and provides the original raw JSON.
        """
        return cls(
            roster_id=data.get("roster_id"),
            owner_id=data.get("owner_id"),
            league_id=data.get("league_id"),
            players=[str(p) for p in (data.get("players") or [])],
            starters=[str(s) for s in (data.get("starters") or [])],
            reserve=[str(r) for r in (data.get("reserve") or [])],
            settings=dict(data.get("settings") or {}),
            raw=dict(data),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



@dataclass
class AllTeams:
    """
    Container for Team objects returned by the teams/league endpoint.
    - teams: mapping roster_id (as str) -> Team
    - raw: original JSON dict as returned by the API
    """
    teams: Dict[str, "Team"] = field(default_factory=dict)
    raw: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Dict[str, Any]] | Iterable[Dict[str, Any]]) -> "AllTeams":
        """
        Accept either:
        - mapping-like response (dict) where each value is a Team JSON object, or
        - a list/iterable of team dicts (common when API returns an array).
        Returns an AllTeams instance keyed by roster_id (or index if roster_id missing).
        """
        teams: Dict[str, "Team"] = {}

        if not data:
            return cls(teams={}, raw={})

        # If caller passed a list/iterable, normalize to mapping by roster_id or index
        if isinstance(data, list) or not hasattr(data, "items"):
            # data is a sequence of team dicts
            raw_list = []
            for i, tdata in enumerate(data):
                raw_list.append(dict(tdata) if isinstance(tdata, dict) else tdata)
                try:
                    team_obj = Team.from_sleeper_json(tdata)
                except Exception:
                    team_obj = Team(raw=dict(tdata) if isinstance(tdata, dict) else {"raw": tdata})
                roster_key = str(team_obj.roster_id) if team_obj.roster_id is not None else str(i)
                teams[roster_key] = team_obj
            # keep original list under a simple key so raw stays serializable
            return cls(teams=teams, raw={"list": raw_list})

        # Otherwise assume mapping/dict
        for key, tdata in (data or {}).items():
            try:
                team_obj = Team.from_sleeper_json(tdata)
            except Exception:
                team_obj = Team(raw=dict(tdata))
            roster_key = str(team_obj.roster_id) if team_obj.roster_id is not None else str(key)
            teams[roster_key] = team_obj

        return cls(teams=teams, raw={str(k): dict(v) for k, v in (data or {}).items()})

    def get(self, roster_id: str) -> Optional["Team"]:
        return self.teams.get(str(roster_id))

    def all(self) -> List["Team"]:
        return list(self.teams.values())

    def by_owner(self, owner_id: str) -> List["Team"]:
        return [t for t in self.teams.values() if t.owner_id == str(owner_id)]

    def by_league(self, league_id: str) -> List["Team"]:
        return [t for t in self.teams.values() if t.league_id == str(league_id)]

    def by_player(self, player_id: str) -> List["Team"]:
        pid = str(player_id)
        return [t for t in self.teams.values() if pid in t.players or pid in t.starters or pid in t.reserve]

    def __len__(self) -> int:
        return len(self.teams)

    def __iter__(self) -> Iterator["Team"]:
        return iter(self.teams.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "teams": {rid: t.to_dict() for rid, t in self.teams.items()},
            "raw": dict(self.raw),
        }


@dataclass
class Draft:
    draft_id: Optional[str] = None
    league_id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[int] = None
    sport: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    season_type: Optional[str] = None
    season: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_picked: Optional[int] = None
    last_message_time: Optional[int] = None
    last_message_id: Optional[str] = None
    draft_order: Dict[str, int] = field(default_factory=dict)        # user_id -> pick slot
    slot_to_roster_id: Dict[int, int] = field(default_factory=dict)  # slot -> roster_id
    creators: Optional[Any] = None
    created: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Any]) -> "Draft":
        """
        Construct a Draft object from Sleeper draft JSON.
        - draft_order: keep user_id (str) -> slot (int)
        - slot_to_roster_id: convert slot keys to int
        """
        draft_order = {str(k): int(v) for k, v in (data.get("draft_order") or {}).items()}
        # slot_to_roster_id JSON keys are strings like "1": 10 -> convert keys to int
        slot_to_roster_id = {int(k): int(v) for k, v in (data.get("slot_to_roster_id") or {}).items()}

        return cls(
            draft_id=data.get("draft_id"),
            league_id=data.get("league_id"),
            type=data.get("type"),
            status=data.get("status"),
            start_time=data.get("start_time"),
            sport=data.get("sport"),
            settings=dict(data.get("settings") or {}),
            season_type=data.get("season_type"),
            season=str(data.get("season")) if data.get("season") is not None else None,
            metadata=dict(data.get("metadata") or {}),
            last_picked=data.get("last_picked"),
            last_message_time=data.get("last_message_time"),
            last_message_id=data.get("last_message_id"),
            draft_order=draft_order,
            slot_to_roster_id=slot_to_roster_id,
            creators=data.get("creators"),
            created=data.get("created"),
            raw=dict(data),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AllDrafts:
    """
    Container for Draft objects returned by the drafts endpoint.
    - drafts: mapping draft_id -> Draft
    - raw: original JSON as returned by the API (dict or list normalized)
    """
    drafts: Dict[str, "Draft"] = field(default_factory=dict)
    raw: Any = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Dict[str, Any]] | Iterable[Dict[str, Any]]) -> "AllDrafts":
        drafts: Dict[str, "Draft"] = {}

        if not data:
            return cls(drafts={}, raw={})

        # Accept list/iterable or mapping
        if isinstance(data, list) or not hasattr(data, "items"):
            raw_list = []
            for i, d in enumerate(data):
                raw_list.append(dict(d) if isinstance(d, dict) else d)
                try:
                    draft_obj = Draft.from_sleeper_json(d)
                except Exception:
                    # fallback minimal Draft with draft_id if present
                    did = str(d.get("draft_id") or i) if isinstance(d, dict) else str(i)
                    draft_obj = Draft(draft_id=did, raw=dict(d) if isinstance(d, dict) else {"raw": d})
                drafts[str(draft_obj.draft_id)] = draft_obj
            return cls(drafts=drafts, raw={"list": raw_list})

        # mapping-like input
        for key, ddata in (data or {}).items():
            try:
                draft_obj = Draft.from_sleeper_json(ddata)
            except Exception:
                draft_obj = Draft(draft_id=str(key), raw=dict(ddata))
            drafts[str(draft_obj.draft_id or key)] = draft_obj

        return cls(drafts=drafts, raw={str(k): dict(v) for k, v in (data or {}).items()})

    def get(self, draft_id: str) -> Optional["Draft"]:
        return self.drafts.get(str(draft_id))

    def all(self) -> List["Draft"]:
        return list(self.drafts.values())

    def by_league(self, league_id: str) -> List["Draft"]:
        return [d for d in self.drafts.values() if getattr(d, "league_id", None) == str(league_id)]

    def __len__(self) -> int:
        return len(self.drafts)

    def __iter__(self) -> Iterator["Draft"]:
        return iter(self.drafts.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "drafts": {did: (d.to_dict() if hasattr(d, "to_dict") else asdict(d)) for did, d in self.drafts.items()},
            "raw": dict(self.raw) if isinstance(self.raw, dict) else self.raw,
        }


@dataclass
class DraftPick:
    player_id: str
    picked_by: Optional[str] = None  # user_id (may be "")
    roster_id: Optional[str] = None
    round: Optional[int] = None
    draft_slot: Optional[int] = None
    pick_no: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_keeper: Optional[bool] = None
    draft_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Any]) -> "DraftPick":
        """
        Build a DraftPick from a single Sleeper pick JSON object.
        Accepts both string and numeric values for ids/slots.
        """
        return cls(
            player_id=str(data.get("player_id")) if data.get("player_id") is not None else None,
            picked_by=str(data.get("picked_by")) if data.get("picked_by") not in (None, "") else (data.get("picked_by") or ""),
            roster_id=str(data.get("roster_id")) if data.get("roster_id") is not None else None,
            round=int(data.get("round")) if data.get("round") is not None else None,
            draft_slot=int(data.get("draft_slot")) if data.get("draft_slot") is not None else None,
            pick_no=int(data.get("pick_no")) if data.get("pick_no") is not None else None,
            metadata=dict(data.get("metadata") or {}),
            is_keeper=(data.get("is_keeper") if data.get("is_keeper") is not None else None),
            draft_id=data.get("draft_id"),
            raw=dict(data),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AllDraftPicks:
    picks: List[DraftPick] = field(default_factory=list)
    draft_id: Optional[str] = None
    raw: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_sleeper_list(cls, picks_list: Iterable[Dict[str, Any]]) -> "AllDraftPicks":
        """
        Build AllDraftPicks from an iterable/list of pick JSON objects returned by Sleeper.
        Preserves original raw list and sets draft_id if available from first pick.
        """
        picks = [DraftPick.from_sleeper_json(p) for p in picks_list]
        draft_id = picks[0].draft_id if picks else None
        raw = [dict(p) for p in picks_list]
        return cls(picks=picks, draft_id=draft_id, raw=raw)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "draft_id": self.draft_id,
            "picks": [p.to_dict() for p in self.picks],
            "raw": list(self.raw),
        }

    def by_round(self, rnd: int) -> List[DraftPick]:
        return [p for p in self.picks if p.round == rnd]

    def by_roster(self, roster_id: str) -> List[DraftPick]:
        return [p for p in self.picks if p.roster_id == str(roster_id)]

    def by_player(self, player_id: str) -> List[DraftPick]:
        return [p for p in self.picks if p.player_id == str(player_id)]


@dataclass
class StatValue:
    """
    Normalized wrapper for a stat value which can be:
    - a plain number (int/float)
    - an object like {"source": "23.0", "parsedValue": 23}
    - a string that can be parsed to a number
    """
    raw: Any = None
    parsed: Optional[float] = None
    source: Optional[str] = None

    @classmethod
    def from_raw(cls, v: Any) -> "StatValue":
        if v is None:
            return cls(raw=None, parsed=None, source=None)
        if isinstance(v, (int, float)):
            return cls(raw=v, parsed=float(v), source=None)
        if isinstance(v, dict):
            parsed = v.get("parsedValue")
            source = v.get("source")
            # try to coerce parsed or source to number if possible
            if parsed is None and source is not None:
                try:
                    parsed = float(source)
                except Exception:
                    parsed = None
            try:
                parsed_f = float(parsed) if parsed is not None else None
            except Exception:
                parsed_f = None
            return cls(raw=dict(v), parsed=parsed_f, source=source)
        # fallback: try to parse string
        try:
            parsed_f = float(v)
            return cls(raw=v, parsed=parsed_f, source=str(v))
        except Exception:
            return cls(raw=v, parsed=None, source=str(v))

    def value(self) -> Optional[float]:
        return self.parsed

    def to_primitive(self) -> Any:
        # returns a serializable representation
        if self.raw is None:
            return None
        if self.source is None and isinstance(self.raw, (int, float)):
            return self.parsed
        return {"raw": self.raw, "parsed": self.parsed, "source": self.source}


@dataclass
class StatPlayerInfo:
    player_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: Optional[str] = None
    team: Optional[str] = None
    fantasy_positions: List[str] = field(default_factory=list)
    injury_status: Optional[str] = None
    years_exp: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Any]) -> "StatPlayerInfo":
        if not data:
            return cls()
        return cls(
            player_id=data.get("player_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            position=data.get("position"),
            team=data.get("team"),
            fantasy_positions=list(data.get("fantasy_positions") or []),
            injury_status=data.get("injury_status"),
            years_exp=data.get("years_exp"),
            metadata=dict(data.get("metadata") or {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    

@dataclass
class StatsProfileEntry:
    """
    One entry in a stats profile (the inner object like the "0" entry).
    Converts stats values into StatValue wrappers.
    """
    index_key: Optional[str] = None  # the "0", "1", etc key from the profile map
    player_id: Optional[str] = None
    season: Optional[str] = None
    season_type: Optional[str] = None
    category: Optional[str] = None
    team: Optional[str] = None
    company: Optional[str] = None
    week: Optional[int] = None
    last_modified: Optional[int] = None
    updated_at: Optional[int] = None
    game_id: Optional[str] = None
    stats: Dict[str, StatValue] = field(default_factory=dict)
    player: StatPlayerInfo = field(default_factory=StatPlayerInfo)
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, index_key: str, data: Dict[str, Any]) -> "StatsProfileEntry":
        stats_raw = dict(data.get("stats") or {})
        stats_conv: Dict[str, StatValue] = {k: StatValue.from_raw(v) for k, v in stats_raw.items()}
        week_val = data.get("week")
        try:
            week_val = int(week_val) if week_val is not None else None
        except Exception:
            week_val = None

        return cls(
            index_key=str(index_key),
            player_id=data.get("player_id"),
            season=str(data.get("season")) if data.get("season") is not None else None,
            season_type=data.get("season_type"),
            category=data.get("category"),
            team=data.get("team"),
            company=data.get("company"),
            week=week_val,
            last_modified=data.get("last_modified"),
            updated_at=data.get("updated_at"),
            game_id=data.get("game_id"),
            stats=stats_conv,
            player=StatPlayerInfo.from_sleeper_json(data.get("player") or {}),
            raw=dict(data),
        )

    def stat_value(self, key: str) -> Optional[StatValue]:
        return self.stats.get(key)

    def stat_float(self, key: str) -> Optional[float]:
        sv = self.stat_value(key)
        return sv.value() if sv else None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["player"] = self.player.to_dict()
        d["stats"] = {k: v.to_primitive() for k, v in self.stats.items()}
        return d


@dataclass
class StatsProfile:
    """
    Container for a player's stats profile returned as a map (keys like "0","1"...).
    - entries: mapping index_key -> StatsProfileEntry
    - player_id: filled if available from entries
    - raw: original profile JSON
    """
    entries: Dict[str, StatsProfileEntry] = field(default_factory=dict)
    player_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_sleeper_profile(cls, data: Dict[str, Any]) -> "StatsProfile":
        entries: Dict[str, StatsProfileEntry] = {}
        pid: Optional[str] = None
        for k, v in (data or {}).items():
            entry = StatsProfileEntry.from_sleeper_json(k, v)
            entries[str(k)] = entry
            if not pid and entry.player_id:
                pid = entry.player_id
        return cls(entries=entries, player_id=pid, raw={str(k): dict(v) for k, v in (data or {}).items()})

    def latest_entry(self) -> Optional[StatsProfileEntry]:
        # choose latest by updated_at then last_modified then index order
        if not self.entries:
            return None
        def keyfn(e: StatsProfileEntry):
            return (e.updated_at or e.last_modified or 0, int(e.index_key) if e.index_key.isdigit() else 0)
        return max(self.entries.values(), key=keyfn)

    def season_entry(self, season: str, season_type: Optional[str] = None) -> List[StatsProfileEntry]:
        return [e for e in self.entries.values() if e.season == season and (season_type is None or e.season_type == season_type)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
            "raw": dict(self.raw),
        }


# ...existing code...

@dataclass
class AllStats:
    """
    Container for StatsProfile objects for many players.
    - profiles: mapping player_id -> StatsProfile
    - raw: original JSON as returned by the API (dict or list normalized)
    """
    profiles: Dict[str, StatsProfile] = field(default_factory=dict)
    raw: Any = field(default_factory=dict)

    @classmethod
    def from_sleeper_json(cls, data: Dict[str, Any] | Iterable[Dict[str, Any]]) -> "AllStats":
        """
        Accept either:
        - mapping player_id -> profile-mapping (typical response)
        - or an iterable/list of profile objects (various shapes)
        Tries to be tolerant and extract player_id when possible.
        """
        profiles: Dict[str, StatsProfile] = {}

        if not data:
            return cls(profiles={}, raw={})

        # helper to try to extract player_id and profile mapping from an item
        def _extract(item: Any) -> (Optional[str], Dict[str, Any]):
            if not isinstance(item, dict):
                return None, item
            # case: single-key mapping like { "4881": { "0": { ... } } }
            if len(item) == 1:
                k, v = next(iter(item.items()))
                if isinstance(v, dict) and not k.isdigit() and ("0" in v or "1" in v or "entries" in v):
                    return str(k), v
            # case: profile mapping keyed by numeric indices: { "0": {...}, "1": {...} }
            if any(str(k).isdigit() for k in item.keys()):
                # try to find player_id from first entry
                first = next(iter(item.values()))
                if isinstance(first, dict) and "player_id" in first:
                    return str(first.get("player_id")), item
                return None, item
            # case: profile object with player_id at top-level
            if "player_id" in item:
                return str(item.get("player_id")), item
            # fallback: not recognized
            return None, item

        # If data is a mapping of player_id -> profile mapping
        if isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
            raw = {str(k): dict(v) for k, v in (data or {}).items()}
            for pid, pdata in (data or {}).items():
                try:
                    profile = StatsProfile.from_sleeper_profile(pdata)
                except Exception:
                    profile = StatsProfile(entries={}, player_id=str(pid), raw=dict(pdata))
                profiles[str(profile.player_id or pid)] = profile
            return cls(profiles=profiles, raw=raw)

        # otherwise treat as iterable/list of items
        raw_list = []
        for item in data:
            raw_list.append(dict(item) if isinstance(item, dict) else item)
            pid, pdata = _extract(item)
            try:
                if isinstance(pdata, dict) and any(str(k).isdigit() for k in pdata.keys()):
                    profile = StatsProfile.from_sleeper_profile(pdata)
                else:
                    # if item is {player_id: profile} handle that case
                    if isinstance(item, dict) and len(item) == 1:
                        k, v = next(iter(item.items()))
                        if isinstance(v, dict):
                            profile = StatsProfile.from_sleeper_profile(v)
                            pid = pid or k
                        else:
                            profile = StatsProfile(entries={}, player_id=pid, raw=dict(item))
                    else:
                        profile = StatsProfile.from_sleeper_profile(pdata) if isinstance(pdata, dict) else StatsProfile(entries=[], player_id=pid, raw=dict(item))
                profiles[str(profile.player_id or pid or len(profiles))] = profile
            except Exception:
                key = str(pid) if pid else str(len(profiles))
                profiles[key] = StatsProfile(entries={}, player_id=pid, raw=dict(item) if isinstance(item, dict) else {"raw": item})

        return cls(profiles=profiles, raw={"list": raw_list})

    def get(self, player_id: str) -> Optional[StatsProfile]:
        return self.profiles.get(str(player_id))

    def all(self) -> List[StatsProfile]:
        return list(self.profiles.values())

    def by_season(self, season: str, season_type: Optional[str] = None) -> List[StatsProfile]:
        season = str(season)
        results: List[StatsProfile] = []
        for p in self.profiles.values():
            if any(e.season == season and (season_type is None or e.season_type == season_type) for e in p.entries.values()):
                results.append(p)
        return results

    def __len__(self) -> int:
        return len(self.profiles)

    def __iter__(self) -> Iterator[StatsProfile]:
        return iter(self.profiles.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profiles": {pid: p.to_dict() for pid, p in self.profiles.items()},
            "raw": dict(self.raw) if isinstance(self.raw, dict) else self.raw,
        }
