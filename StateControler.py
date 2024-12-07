import tkinter as tk
from idlelib.tooltip import Hovertip

from PIL import Image, ImageTk

import chess

import Transposition

class Mixin:
    
    icons = {}

    def unsaved_state(self):
        if not self.unsaved:
            self.unsaved = True
            self.file_menu.entryconfig("Save", state='normal')
        
    def navbar_states(self):
        if self.pgn.parent is None:
            self.button_back.configure(state=tk.DISABLED)
            self.button_fullback.configure(state=tk.DISABLED)
            if self.pgn.variations:
                self.button_train.configure(state=tk.NORMAL)
            else:
                self.button_train.configure(state=tk.DISABLED)
        else:
            self.button_train.configure(state=tk.NORMAL)
            self.button_back.configure(state=tk.NORMAL)
            self.button_fullback.configure(state=tk.NORMAL)
        
        if self.unsaved:
            self.file_menu.entryconfig("Save", state='normal')
        else:
            self.file_menu.entryconfig("Save", state='disabled')

        if Transposition.check_transposition(self.pgn):
            self.button_loop_transposition.configure(state=tk.NORMAL,
                                                     bg='green')
            if Transposition.check_secondary(self.pgn):
                self.button_to_primary_transposition.configure(state=tk.NORMAL)
            else:
                self.button_to_primary_transposition.configure(state=tk.DISABLED)
        else:
            self.button_loop_transposition.configure(state=tk.DISABLED,
                                                     bg=tk.Button().cget('bg'))
            self.button_to_primary_transposition.configure(state=tk.DISABLED)

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
        
        if not Transposition.check_transposition(self.pgn):
            self.button_primary_transposition.configure(
                text='⚓',
                activebackground=tk.Button().cget('activebackground'),
                command=self.make_primary_transposition)
            Hovertip(self.button_primary_transposition,
                     'Make this position a primary transposition',
                     hover_delay=1000)
            if Transposition.noeud_transposition != {}:
                self.button_link_transposition.configure(state=tk.NORMAL)
            else:
                self.button_link_transposition.configure(state=tk.DISABLED)
        else:
            if Transposition.check_primary(self.pgn):
                self.button_primary_transposition.configure(
                    text='⛏',
                    activebackground='red',
                    command=self.remove_primary_transposition)
                Hovertip(
                    self.button_primary_transposition,
                    'Remove this primary transposition and its secondary ones',
                    hover_delay=1000)
            else:
                self.button_primary_transposition.configure(
                    text='⇄',
                    activebackground='yellow',
                    command=self.exchange_primary_transposition)
                Hovertip(
                    self.button_primary_transposition,
                    'Exchange this secondary transposition with its primary one',
                    hover_delay=1000)
            self.button_link_transposition.configure(state=tk.DISABLED)

    def set_pgn(self,unsaved=None):
        self.chessboard = self.pgn.board()
        if unsaved:
            self.unsaved = True
        elif not unsaved is None:
            self.unsaved = False
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
        if self.editing and not self.training:
            if Transposition.check_secondary(self.pgn):
                self.canvas.unbind("<Button-1>")
                self.canvas_unbind_arrow_create()
                self.text_comment.unbind("<Button-1>")
            else:
                self.canvas.bind("<Button-1>", self.click_edit)
                self.canvas_bind_arrow_create()
                self.text_comment.bind("<Button-1>", self.edit_comment)

    def read(self):
        self.editing = False
        self.editbar.pack_forget()
        self.button_edit.configure(command=self.edit,text="Edit")
        self.canvas_unbind_arrow_create()
        self.canvas.bind("<Button-1>", self.click_read)
        self.text_comment.unbind("<Button-1>")
        self.text_headers.unbind("<Button-1>")

    def edit(self):
        self.navbar.pack(fill=tk.X)
        self.editbar.pack(fill=tk.X)
        self.vert_sep.add(self.frame_infos,minsize=300)
        self.minsize(800,608)
        self.editing = True
        self.button_edit.configure(command=self.read,text="Read only")
        self.editbar.pack(fill=tk.X)
        self.editbar_states()
        self.canvas.bind("<Button-1>", self.click_edit)
        self.canvas_bind_arrow_create()
        self.text_headers.bind("<Button-1>", self.edit_headers)
        self.text_comment.bind("<Button-1>", self.edit_comment)

    def flip(self):
        self.flipped = not self.flipped
        self.refresh()

    def hilight(self, square):
        piece = self.chessboard.piece_at(square)
        if piece is not None and (piece.color == self.chessboard.turn):
            self.selected_square = square
            self.hilighted = list(map(lambda m:m.to_square,
                                      filter(lambda m:m.from_square == square,
                                             self.chessboard.legal_moves)))

    def redraw_pieces(self):
        self.icons={}
        self.canvas.delete("piece")
        self.canvas.delete("bg")
        for square,piece in self.chessboard.piece_map().items():
            x,y = chess.square_rank(square), chess.square_file(square)
            if self.flipped:
                x,y=7-x,7-y
            filename = "img/%s%s.png" % (chess.COLOR_NAMES[piece.color],
                                         piece.symbol().lower())

            if filename not in self.icons:
                self.icons[filename] = ImageTk.PhotoImage(
                    Image.open(filename).resize(
                        (self.square_size,self.square_size)))

            x0 = (2*y+1) * self.square_size // 2
            y0 = (2*(7-x)+1) * self.square_size // 2
            self.canvas.create_image(x0,y0,
                                     image=self.icons[filename],
                                     tags="piece", anchor="c")
        bgfile="img/black_bg.png" if self.flipped else "img/white_bg.png"
        self.icons["bg"]=ImageTk.PhotoImage(
            Image.open(bgfile).resize(
                (self.square_size*8,self.square_size*8)))
        self.canvas.create_image(4*self.square_size,4*self.square_size,
                                 image=self.icons["bg"],
                                 tags="bg",anchor="c")

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

        self.canvas.delete("analyze_arrow")
        self.canvas.delete("square")
        self.canvas.delete("arrow")
        color = chess.WHITE
        for row in range(8):
            color = not color
            for col in range(8):
                cur_square = chess.square(col, row)
                if self.flipped:
                    x1= (7-col) * self.square_size
                    y1 = row * self.square_size
                else:
                    x1 = col * self.square_size
                    y1 = (7-row) * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                if (self.selected_square is not None)\
                   and cur_square == self.selected_square:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="black",
                        fill="#D6CEFF" if color else "#B5A5FF", tags="square")
                elif(self.hilighted !=[] and cur_square in self.hilighted):
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="black",
                        fill="#FFFCA2" if color else "#CBCA82", tags="square")
                else:
                    if cur_move is not None\
                       and (cur_square in {from_square,to_square}):
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2,
                            outline="black",
                            fill="#C8FFCE" if color else "#A0CBA5",
                            tags="square")
                    else:
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2,
                            outline="black",
                            fill="white" if color else "grey", tags="square")
                color = not color
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
