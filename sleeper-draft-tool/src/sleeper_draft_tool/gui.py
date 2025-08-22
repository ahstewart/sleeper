from tkinter import Tk, Listbox, Label, Button, Frame, Scrollbar, StringVar, Entry

class SleeperDraftToolGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sleeper Draft Tool")

        self.frame = Frame(master)
        self.frame.pack()

        self.label = Label(self.frame, text="Available Players")
        self.label.pack()

        self.player_listbox = Listbox(self.frame)
        self.player_listbox.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")

        self.player_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.player_listbox.yview)

        self.selected_player_label = Label(master, text="Selected Player:")
        self.selected_player_label.pack()

        self.selected_player_var = StringVar()
        self.selected_player_entry = Entry(master, textvariable=self.selected_player_var)
        self.selected_player_entry.pack()

        self.select_button = Button(master, text="Select Player", command=self.select_player)
        self.select_button.pack()

    def select_player(self):
        selected_player = self.player_listbox.get(self.player_listbox.curselection())
        self.selected_player_var.set(selected_player)

    def update_player_list(self, players):
        self.player_listbox.delete(0, 'end')
        for player in players:
            self.player_listbox.insert('end', player)

if __name__ == "__main__":
    root = Tk()
    gui = SleeperDraftToolGUI(root)
    root.mainloop()