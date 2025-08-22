class DraftState:
    def __init__(self):
        self.available_players = []
        self.drafted_players = []
        self.team_budgets = {}
    
    def add_available_player(self, player):
        self.available_players.append(player)
    
    def draft_player(self, player, team):
        if player in self.available_players:
            self.available_players.remove(player)
            self.drafted_players.append(player)
            self.team_budgets[team] -= player.cost  # Assuming player has a cost attribute
    
    def get_available_players(self):
        return self.available_players
    
    def get_drafted_players(self):
        return self.drafted_players
    
    def set_team_budget(self, team, budget):
        self.team_budgets[team] = budget
    
    def get_team_budget(self, team):
        return self.team_budgets.get(team, 0)