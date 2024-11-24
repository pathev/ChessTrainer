import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askokcancel, showerror
from chess import pgn

import Transposition

class Mixin:
    def before_new_file(self):
        if (self.unsaved and askokcancel("Are you sure ?",
                                         "Unsaved pgn will be lost",
                                         icon='warning',
                                         default='cancel')) or not self.unsaved:
            self.ask_new_fen(self.new_file)

    def close_and_action(self,w,fun,fen):
        w.destroy()
        fun(fen=fen)

    def ask_new_fen(self,fun):
        w = tk.Toplevel(master=self,bg="white")
        w.transient(self)
        w.resizable(width=tk.FALSE,height=tk.FALSE)
        w.title("New PGN")
        w.protocol('WM_DELETE_WINDOW',lambda :None)

        l = tk.Label(w,text="Give the FEN (empty for default one)",
                     bg="white",width=30)
        l.pack()
        text_fen = tk.Text(w,width=32,height=3)
        text_fen.pack()

        button_OK=tk.Button(w,text="OK",
                            command=lambda :\
                                self.close_and_action(
                                    w,
                                    fun,
                                    text_fen.get(1.0,"end")[:-1]))
        button_OK.pack()

    def new_file(self,fen=""):
        self.pgn=pgn.Game()
        if fen:
            try:
                self.pgn.setup(fen)
                self.unsaved = True
            except:
                showerror("Error","invalid FEN")
        else:
            self.unsaved = False
        self.pgn_games=[self.pgn.game()]
        self.pgn_index=0
        self.change_game_list()
        self.canvas.delete("arrow")
        self.chessboard = self.pgn.board()
        self.label_filename.configure(text="")
        self.edit()
        self.set_pgn()

    def load(self):
        if (self.unsaved and askokcancel("Are you sure ?",
                                         "Unsaved pgn will be lost",
                                         icon='warning',
                                         default='cancel')) or not self.unsaved:
            filename = askopenfilename(filetypes = [("PGN files","*.pgn")])
            if filename:
                self.do_load(filename)

    def do_load(self,filename):
        filebasename=filename.split('/')[-1].split('.')[0]
        self.label_filename.configure(text=filebasename)
        self.pgn_games=[]
        with open(filename) as file:
            game = pgn.read_game(file)
            while game is not None:
                self.pgn_games.append(game)
                game = pgn.read_game(file)
        self.pgn_index=0
        self.change_game_list()
        self.read()
        self.pgn = self.pgn_games[self.pgn_index]
        self.set_pgn(unsaved=False)
        Transposition.init(self.pgn)

    def change_game_list(self):
        self.game_menu.delete(0,tk.END)
        for i,game in enumerate(self.pgn_games,start=1):
            v=f"{i}. {game.headers['Event']}"
            self.game_menu.add_command(label=v,
                                       command=lambda i=i:self.change_game(i))
        self.game_menu.add_separator()
        self.game_menu.add_command(label="New one",command=lambda :self.ask_new_fen(self.new_game))
        if len(self.pgn_games) > 1:
            self.game_menu.add_separator()
            self.game_menu.add_command(label="Delete",
                                       command=self.del_game,
                                       activebackground='red')
        self.game_menu.entryconfigure(self.pgn_index,state='disabled')

    def save(self):
        pgn_filename = asksaveasfilename(filetypes = [("PGN files","*.pgn")],
                                         defaultextension = ".pgn")
        if pgn_filename not in ['',()]:
            with open(pgn_filename, 'w') as pgn_file:
                for game in self.pgn_games:
                    print(game, file=pgn_file, end="\n\n")
        self.unsaved = False
        self.file_menu.entryconfig("Save", state='disabled')

    def change_game(self,n):
        self.game_menu.entryconfigure(self.pgn_index, state='normal')
        i = self.pgn_index = n-1
        self.pgn = self.pgn_games[i]
        self.change_headers()
        self.game_menu.entryconfigure(i, state='disabled')
        self.set_pgn()
    
    def new_game(self,fen=""):
        self.pgn = pgn.Game()
        if fen:
            try:
                self.pgn.setup(fen)
            except:
                showerror("Error","invalid FEN")
        self.pgn_games.append(self.pgn)
        self.change_game_list()
        self.change_game(len(self.pgn_games))
        self.unsaved_state()
 
    def del_game(self):
        if self.unsaved:
            if askokcancel("Are you sure ?",
                           "This game line will be lost\n"
                           "(and the file has not been saved)",
                           icon='warning',
                           default='cancel'):
                self.do_del_game()
        else:
            if askokcancel("Are you sure ?",
                           "This game line will be lost",
                           icon='warning',
                           default='cancel'):
                self.do_del_game()
        
    def do_del_game(self):
        del self.pgn_games[self.pgn_index]
        self.pgn_index = 0
        self.change_game_list()
        self.change_game(1)
        self.unsaved_state()
