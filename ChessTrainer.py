#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# Version : 1.5 (November 2024)
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
##################################
#                                #
#        Patrick Thévenon        #
#                                #
#      Oct 2021 -> Nov 2024      #
#                                #
##################################

import asyncio

import tkinter as tk
import tkinter.font
from tkinter.messagebox import askokcancel
from idlelib.tooltip import Hovertip

import EngineSettings

import Arrows, Analyze
import StateControler, FileControler
import EditGame, EditData
import Train
import TranspositionControler

FONT = 'Liberation'

class GUI(tk.Tk,
          Arrows.Mixin,
          Analyze.Mixin,
          StateControler.Mixin,
          FileControler.Mixin,
          EditGame.Mixin,
          EditData.Mixin,
          Train.Mixin,
          TranspositionControler.Mixin,
          ):
    square_size=64
    selected_square = None
    selected_from_square = None
    hilighted = []
    flipped=False

    editing=True
    training=False
    unsaved = False
    pgn_index = 0

    def __init__(self):

        tk.Tk.__init__(self)

        self.title("ChessTrainer : a chess opening trainer")
        self.minsize(800,608)
        self.protocol('WM_DELETE_WINDOW',self.quit_prog)

        tk.font.nametofont("TkDefaultFont").config(family=f'{FONT} Sans',
                                                   size=11)
        tk.font.nametofont("TkFixedFont").config(family=f'{FONT} Mono',
                                                 size=11)
        self.option_add("*Menu.Font", (f'{FONT} Sans', 11))
        
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="New",command=self.before_new_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open",command=self.load)
        self.file_menu.add_command(label="Save",command=self.save)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Quit",
                                   command=self.quit_prog,
                                   activebackground='red')

        self.game_menu = tk.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label= "Game", menu=self.game_menu)

        self.game_menu.add_command(label="1.",
                                   command=lambda :self.change_game(1))
        self.game_menu.entryconfig("1.", state='disabled')
        self.game_menu.add_command(
            label="New one",
            command=lambda :self.ask_new_fen(self.new_game))

        self.vert_sep = tk.PanedWindow(self, orient="horizontal")
        self.vert_sep.pack(fill="both", expand=True)

        self.MainFrame = tk.Frame(self.vert_sep,bg="white",width=470)
        self.frame_infos = tk.Frame(self.vert_sep,bg="white")

        self.buttons_frame = tk.Frame(self.MainFrame)
        self.buttons_frame.pack(side=tk.BOTTOM,fill=tk.X)

        self.canvas = tk.Canvas(self.MainFrame,
                                height=8*self.square_size,
                                width=8*self.square_size,
                                background="grey")

        self.canvas.bind("<Configure>", self.refresh)

        self.canvas.pack(side=tk.BOTTOM,expand=True,fill=tk.BOTH)

        self.mainbar = tk.Frame(self.buttons_frame)

        self.button_analyze = tk.Button(
            self.mainbar, text="Analyze",width=6,
            command=lambda : asyncio.run(self.start_analyze()))
        self.button_analyze.pack(side=tk.LEFT)
        self.label_score = tk.Label(self.mainbar, text="")
        self.label_score.pack(side=tk.LEFT)

        self.button_flip = tk.Button(self.mainbar, text="Flip",
                                     command=self.flip)
        self.button_flip.pack(side=tk.RIGHT)


        self.mainbar.pack(fill=tk.X)

        self.navbar = tk.Frame(self.buttons_frame)

        buttons = 6*[None]
        for i,(sym,comm,tiptext) in enumerate(
                zip(["⏮","⏴","⏵","⏭","🔁","⤞"],
                    [self.fullback,
                     self.back,
                     self.forward,
                     self.fullforward,
                     self.loop_transposition,
                     self.to_primary_transposition],
                    ['Move to first position (fullback)',
                     'Move back',
                     'Move forward (main variation)',
                     'Move to end of main variation (fullforward)',
                     'Loop through transpositions',
                     'Go to primary transposition'])):
            buttons[i] = tk.Button(self.navbar,
                                   text = sym,
                                   font = (f'{FONT} Serif', 17),
                                   pady=0,state=tk.DISABLED,
                                   command = comm)
            buttons[i].pack(side=tk.LEFT)
            Hovertip(buttons[i],tiptext, hover_delay=1000)

        self.button_fullback,\
        self.button_back,\
        self.button_forward,\
        self.button_fullforward,\
        self.button_loop_transposition,\
        self.button_to_primary_transposition\
        = buttons

        self.button_train = tk.Button(self.navbar, text="Train",
                                      command=self.train)
        self.button_train.pack(side=tk.RIGHT)
        self.button_edit = tk.Button(self.navbar, text="Edit",
                                     command=self.edit)
        self.button_edit.pack(side=tk.RIGHT)

        self.navbar.pack(fill=tk.X)

        self.editbar = tk.Frame(self.buttons_frame)

        self.promotebar = tk.Frame(self.editbar)
        self.button_promote_to_main = tk.Button(
            self.promotebar, text="Promote to main",
            command=self.promote_to_main,state=tk.DISABLED)
        self.button_promote_to_main.pack(side=tk.LEFT)
        self.button_promote = tk.Button(self.promotebar, text="Promote",
                                        command=self.promote,state=tk.DISABLED)
        self.button_promote.pack(side=tk.LEFT)
        self.button_demote = tk.Button(self.promotebar, text="Demote",
                                       command=self.demote,state=tk.DISABLED)
        self.button_demote.pack(side=tk.LEFT)
        self.button_remove = tk.Button(self.promotebar, text="Remove",
                                       command=self.remove,state=tk.DISABLED)
        self.button_remove.pack(side=tk.LEFT)
        self.promotebar.pack(side=tk.LEFT,fill=tk.X)

        self.transpositionbar = tk.Frame(self.editbar)
        buttons = 2*[None]

        for i,(sym,comm,tiptext) in enumerate(
                zip(["⚓","🔗"], # '⛏'
                    [self.make_primary_transposition,
                     self.link_transposition],
                    ['Make this position a primary transposition',
                     'Try to link this position to a primary transposition'])):
            buttons[i] = tk.Button(
                self.transpositionbar,
                text = sym,
                font = (f'{FONT} Serif', 17),
                pady=0,state=tk.DISABLED,
                command = comm)
            buttons[i].pack(side=tk.LEFT)
            Hovertip(buttons[i],tiptext, hover_delay=1000)
        self.button_primary_transposition,\
        self.button_link_transposition\
        = buttons
        self.button_primary_transposition.configure(state=tk.NORMAL)
        self.transpositionbar.pack(side=tk.RIGHT,fill=tk.X)

        self.trainbar = tk.Frame(self.buttons_frame)

        self.button_clue = tk.Button(self.trainbar, text="Clue",
                                     command=self.clue)
        self.button_clue.pack(side=tk.LEFT)
        self.button_stop = tk.Button(self.trainbar, text="Stop",
                                     command=self.stop_training)
        self.button_stop.pack(side=tk.RIGHT)

        self.label_filename = tk.Label(self.frame_infos, text="", bg="white")
        self.label_filename.pack(fill="both")
        self.text_headers = tk.Text(self.frame_infos,width=50,
                                    state=tk.DISABLED, wrap="word",height=7)
        self.text_headers.pack(fill="both")
        self.text_fen_line = tk.Text(self.frame_infos,width=50,
                                     state=tk.DISABLED,height=2)
        self.text_fen_line.pack(fill="both")
        print(self.text_fen_line.cget("font"))

        self.hor_sep = tk.PanedWindow(self.frame_infos,orient="vertical")
        self.hor_sep.pack(fill="both",expand=True)

        self.text_san_line = tk.Text(self.hor_sep,
                                     height=8,width=50,
                                     state=tk.DISABLED, wrap="word")
        self.text_comment = tk.Text(self.hor_sep,
                                    heigh=20,width=50,
                                    state=tk.DISABLED, wrap="word")

        self.hor_sep.add(self.text_san_line,minsize=50)
        self.hor_sep.add(self.text_comment,minsize=50)

        self.vert_sep.add(self.MainFrame,minsize=470)
        self.vert_sep.add(self.frame_infos,minsize=300)

    def wait_before_quit(self):
        if self.analysis is not None:
            self.after(20,self.wait_before_quit)
        else:
            self.destroy()

    def quit_prog(self):
        if (self.unsaved\
         and askokcancel("Are you sure ?",
                         "Unsaved pgn will be lost",
                         icon='warning',
                         default='cancel')) or not self.unsaved:
            if self.analyzing:
                self.analyzing = False
            self.after(10,self.wait_before_quit)

def init():
    EngineSettings.parse_cmd_arguments()
    window = GUI()
    window.new_file()
    window.mainloop()

if __name__ == '__main__':
    init()
