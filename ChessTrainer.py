#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# Version : 1.21 (October 2023)
#
# ChessTrainer (c) by Patrick Thévenon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#####################################
#                                   #
#         Patrick Thévenon          #
#                                   #
#       de Octobre 2021             #
#             à Decembre 2021       #
#                                   #
#####################################

import argparse
import chess
import chess.pgn as pgn
import asyncio
import chess.engine
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askokcancel, showinfo, showerror
from PIL import Image, ImageTk
from random import choice
from scipy.stats import betabinom
import argparse

arrow_color = ["#FF3333","#FF9933","#EEEE33","#33FF33","#9933FF","#0099FF","#DDDDDD"]
comment_arrow_color = {"red": "#AA1111", "yellow": "#AAAA11", "blue": "#1111AA", "green": "#11AA11"}
analyze_arrow_color = ["#6666FF","#9999FF","#DDDDFF"]
engine_path = "/usr/games/stockfish"
engine_max_threads = 16
maxCTdiff = 40

asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())

class GUI(tk.Tk):
    square_size=64
    selected_square = None
    selected_from_square = None
    hilighted = []
    icons = {}
    flipped=False

    editing=True
    fen_reglages=None
    fen_change_comment=None
    training=False
    analyzing=False
    analysis=None
    analyze_task = None
    unsaved = False

    def __init__(self):

        tk.Tk.__init__(self)

        self.title("Opening trainer")
        self.minsize(470,250)
        self.protocol('WM_DELETE_WINDOW',self.quit_prog)

        self.MainFrame = tk.Frame(self)

        self.MainFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.buttons_frame = tk.Frame(self.MainFrame)
        self.buttons_frame.pack(side=tk.BOTTOM,fill=tk.X)

        self.canvas = tk.Canvas(self.MainFrame, height=8*self.square_size, width=8*self.square_size,background="grey")

        self.canvas.bind("<Configure>", self.refresh)

        self.canvas.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)

        self.mainbar = tk.Frame(self.buttons_frame)

        self.button_quit = tk.Button(self.mainbar, text="New", command=self.before_new)
        self.button_quit.pack(side=tk.LEFT)
        self.button_flip = tk.Button(self.mainbar, text="Flip", command=self.flip)
        self.button_flip.pack(side=tk.LEFT)
        self.button_load = tk.Button(self.mainbar, text="Load pgn",  command=self.load)
        self.button_load.pack(side=tk.LEFT)
        self.button_save = tk.Button(self.mainbar, text="Save pgn",  command=self.save)
        self.button_save.pack(side=tk.LEFT)
        self.button_analyze = tk.Button(self.mainbar, text="Analyze", command=lambda : asyncio.run(self.start_analyze()))
        self.button_analyze.pack(side=tk.LEFT)
        self.label_score = tk.Label(self.mainbar, text="")
        self.label_score.pack(side=tk.LEFT)
        self.button_quit = tk.Button(self.mainbar, text="Quit", command=self.quit_prog)
        self.button_quit.pack(side=tk.RIGHT)

        self.mainbar.pack(fill=tk.X)

        self.navbar = tk.Frame(self.buttons_frame)

        self.sel_game_var=tk.StringVar(self.fen_reglages)
        self.sel_game_var.set("Select game")
        self.sel_game_menu = tk.OptionMenu(self.navbar,self.sel_game_var,"Select game")
        self.sel_game_var.trace("w",lambda *args:self.change_game(self.sel_game_var.get()))
        self.sel_game_menu.pack(side=tk.LEFT)

        self.button_fullback = tk.Button(self.navbar, text="|<", command=self.fullback,state=tk.DISABLED)
        self.button_fullback.pack(side=tk.LEFT)
        self.button_back = tk.Button(self.navbar, text="<", command=self.back,state=tk.DISABLED)
        self.button_back.pack(side=tk.LEFT)
        self.button_forward = tk.Button(self.navbar, text=">", command=self.forward,state=tk.DISABLED)
        self.button_forward.pack(side=tk.LEFT)
        self.button_fullforward = tk.Button(self.navbar, text=">|", command=self.fullforward,state=tk.DISABLED)
        self.button_fullforward.pack(side=tk.LEFT)
        self.button_train = tk.Button(self.navbar, text="Train", command=self.train)
        self.button_train.pack(side=tk.RIGHT)
        self.button_edit = tk.Button(self.navbar, text="Edit", command=self.edit,state=tk.DISABLED)
        self.button_edit.pack(side=tk.RIGHT)

        self.navbar.pack(fill=tk.X)

        self.editbar = tk.Frame(self.buttons_frame)

        self.button_promote_to_main = tk.Button(self.editbar, text="Promote to main", command=self.promote_to_main,state=tk.DISABLED)
        self.button_promote_to_main.pack(side=tk.LEFT)
        self.button_promote = tk.Button(self.editbar, text="Promote", command=self.promote,state=tk.DISABLED)
        self.button_promote.pack(side=tk.LEFT)
        self.button_demote = tk.Button(self.editbar, text="Demote", command=self.demote,state=tk.DISABLED)
        self.button_demote.pack(side=tk.LEFT)
        self.button_remove = tk.Button(self.editbar, text="Remove", command=self.remove,state=tk.DISABLED)
        self.button_remove.pack(side=tk.LEFT)
        self.button_read = tk.Button(self.editbar, text="Read only", command=self.read)
        self.button_read.pack(side=tk.RIGHT)

        self.trainbar = tk.Frame(self.buttons_frame)

        self.button_clue = tk.Button(self.trainbar, text="Clue", command=self.clue)
        self.button_clue.pack(side=tk.LEFT)
        self.button_stop = tk.Button(self.trainbar, text="Stop", command=self.stop)
        self.button_stop.pack(side=tk.RIGHT)

        self.frame_infos = tk.Frame(master=self,bg="white")

        self.label_filename = tk.Label(self.frame_infos, text="", bg="white")
        self.label_filename.pack()
        self.text_headers = tk.Text(self.frame_infos, state=tk.DISABLED, wrap="word", width=60,height=8)
        self.text_headers.pack()
        self.text_fen_line = tk.Text(self.frame_infos, state=tk.DISABLED, width=60,height=2)
        self.text_fen_line.pack()
        self.text_san_line = tk.Text(self.frame_infos, state=tk.DISABLED, wrap="word", width=60,height=14)
        self.text_san_line.pack()
        self.text_comment = tk.Text(self.frame_infos, state=tk.DISABLED, wrap="word", width=60,height=10)
        self.text_comment.pack()

    def navbar_states(self):
        if self.pgn.parent is None:
            self.button_back.configure(state=tk.DISABLED)
            self.button_fullback.configure(state=tk.DISABLED)
            if self.pgn.variations:
                self.button_save.configure(state=tk.NORMAL)
                self.button_train.configure(state=tk.NORMAL)
            else:
                self.button_save.configure(state=tk.DISABLED)
                self.button_train.configure(state=tk.DISABLED)
        else:
            self.button_save.configure(state=tk.NORMAL)
            self.button_train.configure(state=tk.NORMAL)
            self.button_back.configure(state=tk.NORMAL)
            self.button_fullback.configure(state=tk.NORMAL)

        self.text_headers.configure(state=tk.NORMAL)
        self.text_headers.delete(1.0,"end")
        for key,value in self.pgn.game().headers.items():
            self.text_headers.insert("end",key+": "+value+"\n")
        self.text_headers.configure(state=tk.DISABLED)

        if self.pgn.variations:
            self.button_forward.configure(state=tk.NORMAL)
            self.button_fullforward.configure(state=tk.NORMAL)
        else:
            self.button_forward.configure(state=tk.DISABLED)
            self.button_fullforward.configure(state=tk.DISABLED)

    def editbar_states(self):
        if self.pgn.parent is not None:
            if self.pgn.is_main_variation():
                self.button_promote_to_main.configure(state=tk.DISABLED)
                self.button_promote.configure(state=tk.DISABLED)
            else:
                self.button_promote_to_main.configure(state=tk.NORMAL)
                self.button_promote.configure(state=tk.NORMAL)
            self.button_demote.configure(state=tk.NORMAL)
            self.button_remove.configure(state=tk.NORMAL)
        else:
            self.button_promote_to_main.configure(state=tk.DISABLED)
            self.button_promote.configure(state=tk.DISABLED)
            self.button_demote.configure(state=tk.DISABLED)
            self.button_remove.configure(state=tk.DISABLED)

    def set_pgn(self,unsaved=None):
        self.chessboard = self.pgn.board()
        if self.analyzing:
            self.change_analyze()
        if self.editing:
            self.editbar_states()
        if not self.training:
            self.change_fen_line()
            self.change_san_line()
            self.change_comment()
            self.navbar_states()
        self.refresh()
        if unsaved:
            self.unsaved = True
        elif not unsaved is None:
            self.unsaved = False

    def before_new(self):
        if (self.unsaved and askokcancel("Are you sure ?","Unsaved pgn will be lost",icon='warning',default='cancel')) or not self.unsaved:
            self.ask_new()

    def set_new_fen(self,f,text):
        f.destroy()
        if text == "":
            self.new()
        else:
            self.new(fen=text)

    def ask_new(self):
        f = tk.Toplevel(master=self,bg="white")
        f.transient(self)
        f.resizable(width=tk.FALSE,height=tk.FALSE)
        f.title("New PGN")
        f.protocol('WM_DELETE_WINDOW',lambda :None)

        l = tk.Label(f,text="Give the FEN (empty for default one)",bg="white",width=30)
        l.pack()
        text_fen = tk.Text(f,width=32,height=3)
        text_fen.pack()

        button_OK=tk.Button(f,text="OK",command=lambda :self.set_new_fen(f,text_fen.get(1.0,"end")[:-1]))
        button_OK.pack()

    def new(self,fen=None):
        self.pgn=pgn.Game()
        if fen is not None:
            try:
                self.pgn.setup(fen)
            except:
                showerror("Error","invalid FEN")
        self.pgn_games=[self.pgn.game()]
        self.pgn_index=0
        self.change_game_list()
        self.canvas.delete("arrow")
        self.chessboard = self.pgn.board()
        self.label_filename.configure(text="")
        self.edit()
        self.set_pgn(unsaved=False)

    def flip(self):
        self.flipped=not(self.flipped)
        self.refresh()

    def load(self):
        if (self.unsaved and askokcancel("Are you sure ?","Unsaved pgn will be lost",icon='warning',default='cancel')) or not self.unsaved:
            filename = askopenfilename(filetypes = [("PGN files","*.pgn")])
            if filename:
                self.do_load(filename)

    def do_load(self,filename):
        file = open(filename)
        filebasename=filename.split('/')[-1].split('.')[0]
        self.label_filename.configure(text=filebasename)
        self.pgn_games=[]
        game = pgn.read_game(file)
        while game is not None:
            self.pgn_games.append(game)
            game = pgn.read_game(file)
        self.pgn_index=0
        self.change_game_list()
        self.read()
        self.pgn = self.pgn_games[self.pgn_index]
        self.set_pgn(unsaved=False)

    def change_game_list(self):
        self.sel_game_menu['menu'].delete(0,"end")
        for i,game in enumerate(self.pgn_games):
            v=str(i+1)+". "+game.headers["Event"]
            self.sel_game_menu['menu'].add_command(label=v, command = lambda v=v : self.sel_game_var.set(v))

    def save(self):
        pgn_filename = asksaveasfilename(filetypes = [("PGN files","*.pgn")], defaultextension = ".pgn")
        if pgn_filename not in ['',()]:
            with open(pgn_filename, 'w') as pgn_file:
                print(self.pgn.game(), file=pgn_file, end="\n\n")
            self.do_load(pgn_filename)

    async def start_analyze(self):
        self.analyzing = True
        self.button_analyze.configure(text="Stop",command=self.stop_analyze)
        self.transport, self.engine = await chess.engine.popen_uci(engine_path)
        await self.engine.configure({"Threads":engine_max_threads})
        while self.analyzing:
            self.changing = False
            self.analysis = await self.engine.analysis(self.chessboard,multipv=3)
            self.analyze_task = asyncio.create_task(self.analyze())
            await asyncio.gather(self.updater(),self.analyze_task)
        await self.engine.quit()
        self.analyze_task = None
        self.canvas.delete("analyze_arrow")
        self.button_analyze.configure(text="Analyze",command=lambda : asyncio.run(self.start_analyze()))
        self.label_score.configure(text="")

    async def analyze(self):
        if self.chessboard.is_checkmate():
            self.label_score.configure(text="Mate")
        else:
            while not self.changing and self.analyzing:
                try :
                    info = await self.analysis.get()
                    score = info.get("score")
                    if score is not None and info.get("multipv") == 1:
                        label=self.readable(score.white(),info.get("depth"))
                        self.label_score.configure(text=label)
                        if score.is_mate():
                            await asyncio.sleep(0.5)
                        if not self.training:
                            moves_scores_list = [(info.get("pv")[0],info.get("score").white().score()) for info in self.analysis.multipv]
                            bs=moves_scores_list[0][1]
                            self.draw_analyze_arrows([m for m,s in moves_scores_list if abs(s-bs) < engine_max_ct_diff])
                except chess.engine.AnalysisComplete:
                    break
                except asyncio.CancelledError:
                    break
        self.analysis.stop()
        self.analysis = None

    def readable(self,score,depth):
        val = score.score()
        if val is not None:
            if val >0:
                text="+"
            else:
                text=""
            text += str(val/100)
            depth = str(depth)
            return text+" (dep "+depth+")"
        else:
            mat = str(score.mate())
            return "Mate in "+mat

    def stop_analyze(self):
        self.analyze_task.cancel()
        self.analyzing = False

    def change_analyze(self):
        self.analyze_task.cancel()
        self.changing = True

    async def updater(self):
        while (self.analysis is not None) or (self.analyzing and (not self.changing)):
            self.update()
            await asyncio.sleep(1/120)

    def quit_prog(self):
        if (self.unsaved and askokcancel("Are you sure ?","Unsaved pgn will be lost",icon='warning',default='cancel')) or not self.unsaved:
            if self.analyzing:
                self.analyzing = False
            self.wait_before_quit()

    def wait_before_quit(self):
        if self.analysis is not None:
            self.after(20,self.wait_before_quit)
        else:
            self.destroy()

    def promote_to_main(self):
        self.pgn.parent.promote_to_main(self.pgn)
        self.set_pgn(unsaved=True)

    def promote(self):
        self.pgn.parent.promote(self.pgn)
        self.set_pgn(unsaved=True)

    def demote(self):
        self.pgn.parent.demote(self.pgn)
        self.set_pgn(unsaved=True)

    def remove(self):
        if askokcancel("Are you sure ?","Node and variations will be lost",icon='warning',default='cancel'):
            self.pgn.parent.remove_variation(self.pgn)
            self.pgn = self.pgn.parent
            self.set_pgn(unsaved=True)

    def clue(self):
        self.selected_square = self.pgn.variations[0].move.from_square
        self.hilight(self.selected_square)
        self.refresh()

    def stop(self):
        self.trainbar.pack_forget()
        self.training=False
        self.set_pgn()
        if self.editing:
            self.edit()
        else:
            self.edit()
            self.read()

    def read(self):
        self.editing = False
        self.editbar.pack_forget()
        self.button_edit.configure(state=tk.NORMAL)
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")
        self.canvas.unbind("<Alt-Button-3>")
        self.canvas.unbind("<Control-Button-3>")
        self.canvas.unbind("<Control-Alt-Button-3>")
        self.canvas.bind("<Button-1>", self.click_read)
        self.text_comment.unbind("<Button-1>")
        self.text_headers.unbind("<Button-1>")

    def edit(self):
        self.navbar.pack(fill=tk.X)
        self.editbar.pack(fill=tk.X)
        self.frame_infos.pack(side=tk.LEFT,fill=tk.Y)
        self.editing = True
        self.button_edit.configure(state=tk.DISABLED)
        self.editbar.pack(fill=tk.X)
        self.editbar_states()
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self.click_edit)
        self.canvas_bind_arrow_create()
        self.text_headers.unbind("<Button-1>")
        self.text_headers.bind("<Button-1>", self.edit_headers)
        self.text_comment.unbind("<Button-1>")
        self.text_comment.bind("<Button-1>", self.edit_comment)

    def canvas_bind_arrow_create(self):
        self.canvas.bind("<Button-3>", lambda e:self.click_arrow_create(e,"green"))
        self.canvas.bind("<Alt-Button-3>", lambda e:self.click_arrow_create(e,"blue"))
        self.canvas.bind("<Control-Button-3>", lambda e:self.click_arrow_create(e,"red"))
        self.canvas.bind("<Control-Alt-Button-3>", lambda e:self.click_arrow_create(e,"yellow"))

    def edit_headers(self,event):
        self.text_headers.unbind("<Button-1>")

        fen_change_headers = tk.Toplevel(master=self,bg="white")
        fen_change_headers.transient(self)
        fen_change_headers.resizable(width=tk.FALSE,height=tk.FALSE)
        fen_change_headers.title("Headers")
        fen_change_headers.protocol('WM_DELETE_WINDOW',lambda :None)

        text_dict={}
        for (key,value) in self.pgn.game().headers.items():
            f = tk.Frame(fen_change_headers)
            l = tk.Label(f,text=key,bg="white",width=10)
            l.pack(side=tk.LEFT)
            t = tk.Text(f,height=1,width=60)
            text_dict[key]=t
            t.insert("end",value)
            t.pack(side=tk.LEFT)
            f.pack()
        frame_action = tk.Frame(fen_change_headers)

        button_go=tk.Button(frame_action,text="Change",command=lambda :self.accept_headers(fen_change_headers,text_dict))
        button_go.pack(side=tk.RIGHT)
        button_cancel=tk.Button(frame_action,text="Cancel",command=lambda :self.destroy_change_headers(fen_change_headers))
        button_cancel.pack(side=tk.RIGHT)

        frame_action.pack()

    def destroy_change_headers(self,fen):
        fen.destroy()
        self.text_headers.bind("<Button-1>", self.edit_headers)

    def accept_headers(self,fen,text_dict):
        for key in text_dict:
            text=text_dict[key].get(1.0,"end")[:-1]
            if text !="":
                self.pgn.game().headers[key] = text
            else:
                self.pgn.game().headers.pop(key)
        self.change_headers()
        self.destroy_change_headers(fen)
        self.unsaved = True

    def edit_comment(self,event):
        if self.fen_change_comment is None:
            self.fen_change_comment = tk.Toplevel(master=self,bg="white")
            self.fen_change_comment.transient(self)
            self.fen_change_comment.resizable(width=tk.FALSE,height=tk.FALSE)
            self.fen_change_comment.title("Comment")
            self.fen_change_comment.protocol('WM_DELETE_WINDOW',lambda :None)
            self.text_newcomment = tk.Text(self.fen_change_comment, wrap="word", width=60,height=10)
            self.text_newcomment.pack()
            frame_action = tk.Frame(self.fen_change_comment)

            button_go=tk.Button(frame_action,text="Change",command=self.accept_comment)
            button_go.pack(side=tk.RIGHT)
            button_cancel=tk.Button(frame_action,text="Cancel",command=lambda :self.fen_change_comment.withdraw())
            button_cancel.pack(side=tk.RIGHT)

            frame_action.pack()
        else:
            self.fen_change_comment.deiconify()
        self.text_newcomment.delete(1.0,"end")
        self.text_newcomment.insert("end",self.pgn.comment.split("[%")[0])
        self.text_newcomment.wait_visibility()
        self.text_newcomment.mark_set(tk.INSERT,self.text_newcomment.index("end"))
        self.text_newcomment.focus_set()

    def accept_comment(self):
        self.fen_change_comment.withdraw()
        self.pgn.comment = self.text_newcomment.get(1.0,"end")[:-1]+"".join(self.pgn.comment.split("[%")[1:])
        self.change_comment()
        self.unsaved = True

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
            lstbox_coul=tk.OptionMenu(self.fen_reglages,self.val_coul,"white","black")

            lbl_ecart=tk.Label(self.fen_reglages,text="Allowed gap from main move:",bg="white")
            self.val_ecart=tk.IntVar(self.fen_reglages)
            self.val_ecart.set(0)
            lstbox_ecart=tk.OptionMenu(self.fen_reglages,self.val_ecart,0,1,2,3)

            lbl_choix_partie=tk.Label(self.fen_reglages,text="Position:",bg="white")
            self.val_choix=tk.StringVar(self.fen_reglages)
            self.val_choix.set("current")
            lstbox_choix_partie=tk.OptionMenu(self.fen_reglages,self.val_choix,"current","game start","random game start")

            lbl_choix_coup=tk.Label(self.fen_reglages,text="Move choice:",bg="white")
            self.val_coup=tk.StringVar(self.fen_reglages)
            self.val_coup.set("order dependant")
            lstbox_choix_coup=tk.OptionMenu(self.fen_reglages,self.val_coup,"order dependant","uniform")

            lbl_ligne_vide=tk.Label(self.fen_reglages,text="",bg="white")

            frame_action = tk.Frame(self.fen_reglages)

            button_go=tk.Button(frame_action,text="Let's go!",command=self.train_go)
            button_go.pack(side=tk.RIGHT)
            button_cancel=tk.Button(frame_action,text="Cancel",command=lambda :self.fen_reglages.withdraw())
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
        self.player_color = chess.WHITE if self.val_coul.get() == "white" else chess.BLACK
        self.flipped = not self.player_color
        if self.val_choix.get() == "random game start":
            self.pgn = choice(self.pgn_games)
            self.pgn_index = self.pgn_games.index(self.pgn)
        elif self.val_choix.get() == "game start":
            self.pgn = self.pgn.game()
        self.editbar.pack_forget()
        self.navbar.pack_forget()
        self.frame_infos.pack_forget()
        self.trainbar.pack(fill=tk.X)
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>",self.click_train)
        self.training=True
        if self.pgn.turn() != self.player_color:
            self.choose_move()
        else:
            self.chessboard = self.pgn.board()
            self.refresh()

    def choose_move(self):
        if self.pgn.variations:
            if self.val_coup.get() == "uniform":
                self.pgn = choice(self.pgn.variations)
            elif self.val_coup.get() == "order dependant":
                self.pgn = self.pgn.variations[betabinom.rvs(len(self.pgn.variations)-1,0.6,1.2)]
            else:
                assert False
            self.set_pgn()
            if not self.pgn.variations:
                showinfo("The end","Back to navigation")
                self.stop()
            elif self.analyzing:
                self.change_analyze()
        else:
            self.set_pgn()
            showinfo("The end","Back to navigation")
            self.stop()

    def change_game(self,Event):
        if Event != "Select game":
            self.pgn_index=int(self.sel_game_var.get().split(".")[0])-1
            self.pgn = self.pgn_games[self.pgn_index]
            self.change_headers()
            self.set_pgn()
            self.sel_game_var.set("Select game")
            self.sel_game_menu.event_generate("<Enter>") #
            self.sel_game_menu.event_generate("<Leave>") # Pas trouvé comment faire mieux

    def fullback(self):
        self.pgn = self.pgn.game()
        self.set_pgn()

    def back(self):
        self.pgn = self.pgn.parent
        self.set_pgn()

    def forward(self):
        self.pgn = self.pgn.variations[0]
        self.set_pgn()

    def fullforward(self):
        self.pgn = self.pgn.end()
        self.set_pgn()

    def change_headers(self):
        self.text_headers.configure(state=tk.NORMAL)
        self.text_headers.delete(1.0,"end")
        for key,value in self.pgn.game().headers.items():
            self.text_headers.insert("end",key+": "+value+"\n")
        self.text_headers.configure(state=tk.DISABLED)

    def change_fen_line(self):
        self.text_fen_line.configure(state=tk.NORMAL)
        self.text_fen_line.delete(1.0,"end")
        self.text_fen_line.insert("end",self.pgn.board().fen())
        self.text_fen_line.configure(state=tk.DISABLED)

    def change_san_line(self):
        self.text_san_line.configure(state=tk.NORMAL)
        self.text_san_line.delete(1.0,"end")
        if self.chessboard.move_stack != []:
            self.text_san_line.insert("end",self.pgn_games[self.pgn_index].board().variation_san(self.chessboard.move_stack))
        self.text_san_line.configure(state=tk.DISABLED)

    def change_comment(self):
        self.text_comment.configure(state=tk.NORMAL)
        self.text_comment.delete(1.0,"end")
        self.text_comment.insert("end",self.pgn.comment.split("[%")[0])
        self.text_comment.configure(state=tk.DISABLED)

    def click_edit(self, event):
        current_column = event.x // self.square_size
        current_row = 7 - (event.y // self.square_size)
        if self.flipped:
            current_row = 7-current_row
            current_column = 7-current_column

        square = chess.square(current_column, current_row)

        if self.selected_square is not None:
            if square in self.hilighted:
                move=chess.Move(from_square=self.selected_square,to_square=square)
                if self.pgn.has_variation(move):
                    self.pgn = self.pgn.variation(move)
                    self.set_pgn()
                else:
                    self.pgn.add_variation(move)
                    self.pgn = self.pgn.variations[-1]
                    self.set_pgn(unsaved=True)
                if self.analyzing:
                    self.change_analyze()
            self.selected_square = None
            self.hilighted = []
        else:
            self.hilight(square)
        self.refresh()

    def click_arrow_create(self, event,color):
        self.canvas.unbind("<Button-3>")
        self.canvas.unbind("<Alt-Button-3>")
        self.canvas.unbind("<Control-Button-3>")
        self.canvas.unbind("<Control-Alt-Button-3>")
        self.canvas.unbind("<Button-1>")
        current_column = event.x // self.square_size
        current_row = 7 - (event.y // self.square_size)
        if self.flipped:
            current_row = 7-current_row
            current_column = 7-current_column

        self.selected_from_square = chess.square(current_column, current_row)
        self.canvas.bind("<Motion>",lambda e:self.arrow_creating(e,color))
        self.canvas.bind("<ButtonRelease>",lambda e:self.arrow_end(e,color))
        self.arrow_creating(event,color)

    def arrow_creating(self, event,color):

        self.refresh()

        current_column = event.x // self.square_size
        current_row = 7 - (event.y // self.square_size)
        if self.flipped:
            current_row = 7-current_row
            current_column = 7-current_column

        square = chess.square(current_column, current_row)

        if self.selected_from_square != square:
            self.draw_arrow(self.selected_from_square,square,comment_arrow_color.get(color))
        else:
            self.draw_arrow_square(self.selected_from_square,comment_arrow_color.get(color))


    def arrow_end(self, event,color):
        self.canvas.unbind("<Motion>")
        self.canvas.unbind("<ButtonRelease>")

        current_column = event.x // self.square_size
        current_row = 7 - (event.y // self.square_size)
        if self.flipped:
            current_row = 7-current_row
            current_column = 7-current_column

        square = chess.square(current_column, current_row)

        arrows = self.pgn.arrows()
        found = False
        for arrow in arrows:
            from_square = arrow.tail
            to_square = arrow.head
            if (from_square,to_square) == (self.selected_from_square,square):
                found = True
                arrows.remove(arrow)
                if arrow.color != color:
                    arrows.append(chess.svg.Arrow(tail=self.selected_from_square,head=square,color=color))
                break
        if not found:
            arrows.append(chess.svg.Arrow(tail=self.selected_from_square,head=square,color=color))
        self.pgn.set_arrows(arrows)
        self.unsaved = True

        self.refresh()

        self.selected_from_square = None

        self.canvas.bind("<Button-1>", self.click_edit)
        self.canvas_bind_arrow_create()

    def click_read(self, event):

        if len(self.pgn.variations) == 1: # Une seule variation/flèche ; où que l’on clique, le coup est joué
            self.pgn = self.pgn.variations[0]
            self.set_pgn()
        else:
            current_column = event.x // self.square_size
            current_row = 7 - (event.y // self.square_size)
            if self.flipped:
                current_row = 7-current_row
                current_column = 7-current_column
            square = chess.square(current_column, current_row)

            if self.selected_square is not None:
                move=chess.Move(from_square=self.selected_square,to_square=square)
                self.selected_square = None
                self.hilighted = []
                self.refresh()
                if self.pgn.has_variation(move):
                    self.pgn = self.pgn.variation(move)
                    self.set_pgn()
            else:
                to_square_var_list = list(filter(lambda n:n.move.to_square == square,self.pgn.variations))
                if len(to_square_var_list) == 1:
                    self.pgn = to_square_var_list[0]
                    self.set_pgn()
                else:
                    from_square_var_list=list(filter(lambda n:n.move.from_square == square,self.pgn.variations))
                    if len(from_square_var_list) == 1:
                        self.pgn = from_square_var_list[0]
                        self.set_pgn()
                    elif len(from_square_var_list) >=1:
                        self.selected_square = square
                        self.hilighted = [n.move.to_square for n in from_square_var_list]
                        self.refresh()

    def click_train(self, event):
        current_column = event.x // self.square_size
        current_row = 7 - (event.y // self.square_size)
        if self.flipped:
            current_row = 7-current_row
            current_column = 7-current_column

        square = chess.square(current_column,current_row)

        if self.selected_square is not None:
            move=chess.Move(from_square=self.selected_square,to_square=square)
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

    def hilight(self, square):
        piece = self.chessboard.piece_at(square)
        if piece is not None and (piece.color == self.chessboard.turn):
            self.selected_square = square
            self.hilighted = list(map(lambda m:m.to_square, filter(lambda m:m.from_square == square,self.chessboard.legal_moves)))

    def draw_analyze_arrows(self,moves):
        self.canvas.delete("analyze_arrow")
        moves.reverse() # Parcours des flèches à l’envers pour que la meilleure/première soit au-dessus
        i=len(moves)-1
        for move in moves:
            from_square = move.from_square
            to_square = move.to_square
            self.draw_arrow(from_square,to_square,analyze_arrow_color[i],analyze=True)
            i-=1

    def draw_comment_arrows(self):
        arrows = self.pgn.arrows()
        for arrow in arrows:
            from_square = arrow.tail
            to_square = arrow.head
            color = arrow.color
            if from_square == to_square:
                self.draw_arrow_square(from_square,comment_arrow_color.get(color))
            else:
                self.draw_arrow(from_square,to_square,comment_arrow_color.get(color))

    def draw_variations_arrows(self):
        for i,node in enumerate(self.pgn.variations):
            m = node.move
            from_square = m.from_square
            to_square = m.to_square
            self.draw_arrow(from_square,to_square,arrow_color[i%len(arrow_color)])

    def draw_arrow_square(self,square,color):
        row1,col1=chess.square_rank(square),chess.square_file(square)
        if self.flipped:
            x1 = ((7-col1) * self.square_size)
            y1 = ((row1) * self.square_size)
        else:
            x1 = ((col1) * self.square_size)
            y1 = ((7-row1) * self.square_size)
        l=int(self.square_size*0.075)
        e=1+l//2
        self.canvas.create_rectangle(x1+e,y1+e,x1+self.square_size-e,y1+self.square_size-e,width=l,outline=color,tags="arrow")

    def draw_arrow(self,from_square,to_square,color,analyze=False):
        row1,col1=chess.square_rank(from_square),chess.square_file(from_square)
        row2,col2=chess.square_rank(to_square),chess.square_file(to_square)
        if self.flipped:
            x1 = ((7-col1) * self.square_size)+self.square_size//2
            y1 = ((row1) * self.square_size)+self.square_size//2
            x2 = ((7-col2) * self.square_size)+self.square_size//2
            y2 = ((row2) * self.square_size)+self.square_size//2
        else:
            x1 = ((col1) * self.square_size)+self.square_size//2
            y1 = ((7-row1) * self.square_size)+self.square_size//2
            x2 = ((col2) * self.square_size)+self.square_size//2
            y2 = ((7-row2) * self.square_size)+self.square_size//2
        if x2>x1: # Ajustements pour arriver avant le centre
            x2-=self.square_size//8
        elif x2<x1:
            x2+=self.square_size//8
        if y2>y1:
            y2-=self.square_size//8
        elif y2<y1:
            y2+=self.square_size//8
        tags = "analyze_arrow" if analyze else "arrow"
        self.canvas.create_line(x1,y1,x2,y2,arrow=tk.LAST,width=self.square_size//5,arrowshape=(15,12,5),fill=color,tags=tags)

    def redraw_pieces(self):
        self.icons={}
        self.canvas.delete("piece")
        self.canvas.delete("bg")
        for square,piece in self.chessboard.piece_map().items():
            x,y = chess.square_rank(square), chess.square_file(square)
            if self.flipped:
                x,y=7-x,7-y
            filename = "img/%s%s.png" % (chess.COLOR_NAMES[piece.color], piece.symbol().lower())

            if (filename not in self.icons):
                self.icons[filename] = ImageTk.PhotoImage(Image.open(filename).resize((self.square_size,self.square_size)))

            x0 = (2*y+1) * self.square_size // 2
            y0 = (2*(7-x)+1) * self.square_size // 2
            self.canvas.create_image(x0,y0, image=self.icons[filename], tags="piece", anchor="c")
        bgfile="img/black_bg.png" if self.flipped else "img/white_bg.png"
        self.icons["bg"]=ImageTk.PhotoImage(Image.open(bgfile).resize((self.square_size*8,self.square_size*8)))
        self.canvas.create_image(4*self.square_size,4*self.square_size,image=self.icons["bg"],tags="bg",anchor="c")

    def refresh(self, event={}):
        if event:
            xsize = (event.width-1) // 8
            ysize = (event.height-1) // 8
            self.square_size = min(xsize, ysize)
        try:
            cur_move=self.chessboard.peek()
            from_square=cur_move.from_square
            to_square=cur_move.to_square
        except IndexError:
            cur_move=None

        self.canvas.delete("square")
        self.canvas.delete("arrow")
        color = chess.WHITE
        for row in range(8):
            color = not color
            for col in range(8):
                cur_square = chess.square(col, row)
                if self.flipped:
                    x1=((7-col) * self.square_size)
                    y1 = (row * self.square_size)
                else:
                    x1 = (col * self.square_size)
                    y1 = ((7-row) * self.square_size)
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                if (self.selected_square is not None) and cur_square == self.selected_square:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="#D6CEFF" if color else "#B5A5FF", tags="square")
                elif(self.hilighted !=[] and cur_square in self.hilighted):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="#FFFCA2" if color else "#CBCA82", tags="square")
                else:
                    if cur_move is not None and (cur_square == from_square or cur_square == to_square):
                        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="#C8FFCE" if color else "#A0CBA5", tags="square")
                    else:
                        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white" if color else "grey", tags="square")
                color = not(color)
        self.redraw_pieces()
        if not self.training:
            self.draw_comment_arrows()
            self.draw_variations_arrows()
            if self.analyzing:
                try:
                    self.canvas.tag_raise("analyze_arrow","square")
                    self.canvas.tag_raise("analyze_arrow","piece")
                    self.canvas.tag_raise("analyze_arrow","arrow")
                except:
                    pass

def parse_cmd_arguments():
    global engine_path, engine_max_threads, maxCTdiff

    parser = argparse.ArgumentParser(prog='ChessTrainer',
                                     description='Learn and train your chess openings')
    parser.add_argument('--engine-path', help='Path to your engine', default=engine_path)
    parser.add_argument('--engine-max-threads', help='Maximum number of threads used by the engine',
                        type=int, default=engine_max_threads)
    parser.add_argument('--max-ct-diff', help='Maximum CT (CentiPoints) diff allowed',
                        type=int, default=maxCTdiff)

    config = parser.parse_args()
    engine_path = config.engine_path
    engine_max_threads = config.engine_max_threads
    maxCTdiff = config.max_ct_diff

def init():
    parse_cmd_arguments()
    window = GUI()
    window.new()
    window.mainloop()


if __name__ == '__main__':
    init()
