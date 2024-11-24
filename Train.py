import tkinter as tk
from tkinter.messagebox import showinfo
from random import choice

from scipy.stats import betabinom

import chess

class Mixin:
    def train(self):
        if self.fen_reglages is None:
            self.fen_reglages = tk.Toplevel(master=self,bg="white")
            self.fen_reglages.transient(self)
            self.fen_reglages.resizable(width=tk.FALSE,height=tk.FALSE)
            self.fen_reglages.title("Settings")
            self.fen_reglages.protocol('WM_DELETE_WINDOW',lambda :None)

            lbl_coul=tk.Label(self.fen_reglages,text="Train as:",bg="white")
            self.val_coul=tk.StringVar(self.fen_reglages)
            self.val_coul.set("white")
            lstbox_coul=tk.OptionMenu(
                self.fen_reglages,self.val_coul,
                "white","black")

            lbl_ecart=tk.Label(self.fen_reglages,
                               text="Allowed gap from main move:",bg="white")
            self.val_ecart=tk.IntVar(self.fen_reglages)
            self.val_ecart.set(0)
            lstbox_ecart=tk.OptionMenu(
                self.fen_reglages,self.val_ecart,
                0,1,2,3)

            lbl_choix_partie=tk.Label(self.fen_reglages,
                                      text="Position:",bg="white")
            self.val_choix=tk.StringVar(self.fen_reglages)
            self.val_choix.set("current")
            lstbox_choix_partie=tk.OptionMenu(
                self.fen_reglages,self.val_choix,
                "current","game start","random game start")

            lbl_choix_coup=tk.Label(
                self.fen_reglages,text="Move choice:",bg="white")
            self.val_coup=tk.StringVar(self.fen_reglages)
            self.val_coup.set("order dependant")
            lstbox_choix_coup=tk.OptionMenu(
                self.fen_reglages,self.val_coup,
                "order dependant","uniform")

            lbl_ligne_vide=tk.Label(self.fen_reglages,text="",bg="white")

            frame_action = tk.Frame(self.fen_reglages)

            button_go=tk.Button(frame_action,text="Let's go!",
                                command=self.train_go)
            button_go.pack(side=tk.RIGHT)
            button_cancel=tk.Button(frame_action,text="Cancel",
                                    command=self.fen_reglages.withdraw)
            button_cancel.pack(side=tk.RIGHT)

            lbl_coul.pack()
            lstbox_coul.pack()
            lbl_ecart.pack()
            lstbox_ecart.pack()
            lbl_choix_partie.pack()
            lstbox_choix_partie.pack()
            lbl_choix_coup.pack()
            lstbox_choix_coup.pack()
            lbl_ligne_vide.pack()
            frame_action.pack()
        else:
            self.fen_reglages.deiconify()

    def train_go(self):
        self.fen_reglages.withdraw()
        self.player_color = chess.WHITE if self.val_coul.get() == "white"\
                                        else chess.BLACK
        self.flipped = not self.player_color
        if self.val_choix.get() == "random game start":
            self.pgn = choice(self.pgn_games)
            self.pgn_index = self.pgn_games.index(self.pgn)
        elif self.val_choix.get() == "game start":
            self.pgn = self.pgn.game()
        self.editbar.pack_forget()
        self.navbar.pack_forget()
        self.vert_sep.remove(self.frame_infos)
        self.minsize(480,608)
        self.trainbar.pack(fill=tk.X)
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>",self.click_train)
        self.training=True
        if self.pgn.turn() != self.player_color:
            self.choose_move()
        else:
            self.chessboard = self.pgn.board()
            self.maybe_endtraining()
            
    def maybe_endtraining(self):
        self.set_pgn()
        if not self.pgn.variations:
            showinfo("The end","Back to navigation")
            self.stop_training()

    def choose_move(self):
        self.maybe_endtraining()
        if self.pgn.variations:
            if self.val_coup.get() == "uniform":
                self.pgn = choice(self.pgn.variations)
            elif self.val_coup.get() == "order dependant":
                self.pgn = self.pgn.variations[
                    betabinom.rvs(len(self.pgn.variations)-1,0.6,1.2)]
            else:
                assert False
            self.maybe_endtraining()
            if self.analyzing:
                self.change_analyze()

    def clue(self):
        self.selected_square = self.pgn.variations[0].move.from_square
        self.hilight(self.selected_square)
        self.refresh()

    def stop_training(self):
        self.trainbar.pack_forget()
        self.training=False
        self.set_pgn()
        if self.editing:
            self.edit()
        else:
            self.edit()
            self.read()

    def click_train(self, event):
        current_column = event.x // self.square_size
        current_row = 7 - (event.y // self.square_size)
        if self.flipped:
            current_row = 7-current_row
            current_column = 7-current_column

        square = chess.square(current_column,current_row)

        if self.selected_square is not None:
            move=chess.Move(from_square=self.selected_square,
                            to_square=square)
            self.selected_square = None
            self.hilighted = []
            if self.pgn.has_variation(move):
                child = self.pgn.variation(move)
                i = self.pgn.variations.index(child)
                if i<=self.val_ecart.get():
                    self.pgn = child
                    self.choose_move()
        else:
            self.hilight(square)
        self.refresh()
