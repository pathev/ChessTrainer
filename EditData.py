import tkinter as tk
import re

class Mixin:
    
    fen_reglages=None
    fen_change_comment=None

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
            t = tk.Entry(f,width=60)
            text_dict[key]=t
            t.insert("end",value)
            t.pack(side=tk.LEFT)
            f.pack()
        frame_action = tk.Frame(fen_change_headers)

        button_go=tk.Button(frame_action,text="Change",
                            command=lambda :self.accept_headers(fen_change_headers,text_dict))
        button_go.pack(side=tk.RIGHT)
        button_cancel=tk.Button(frame_action,text="Cancel",
                                command=lambda :self.destroy_change_headers(fen_change_headers))
        button_cancel.pack(side=tk.RIGHT)

        frame_action.pack()

    def destroy_change_headers(self,fen):
        fen.destroy()
        self.text_headers.bind("<Button-1>", self.edit_headers)

    def accept_headers(self,fen,text_dict):
        for key in text_dict:
            text=text_dict[key].get()
            if text !="":
                self.pgn.game().headers[key] = text
            else:
                self.pgn.game().headers.pop(key)
        self.change_headers()
        self.destroy_change_headers(fen)
        self.unsaved_state()
        self.change_game_list()

    def edit_comment(self,event):
        if self.fen_change_comment is None:
            self.fen_change_comment = tk.Toplevel(master=self,bg="white")
            self.fen_change_comment.transient(self)
            self.fen_change_comment.resizable(width=tk.FALSE,height=tk.FALSE)
            self.fen_change_comment.title("Comment")
            self.fen_change_comment.protocol('WM_DELETE_WINDOW',lambda :None)
            self.text_newcomment = tk.Text(self.fen_change_comment, wrap="word",
                                           height=10)
            self.text_newcomment.pack()
            frame_action = tk.Frame(self.fen_change_comment)

            button_go=tk.Button(frame_action,text="Change",
                                command=self.accept_comment)
            button_go.pack(side=tk.RIGHT)
            button_cancel=tk.Button(frame_action,text="Cancel",
                                    command=self.fen_change_comment.withdraw)
            button_cancel.pack(side=tk.RIGHT)

            frame_action.pack()
        else:
            self.fen_change_comment.deiconify()
        self.text_newcomment.delete(1.0,"end")
        self.text_newcomment.insert("end",''.join(re.split(r'\[%[^\]]*\]', self.pgn.comment)))
        self.text_newcomment.wait_visibility()
        self.text_newcomment.mark_set(tk.INSERT,self.text_newcomment.index("end"))
        self.text_newcomment.focus_set()

    def accept_comment(self):
        self.fen_change_comment.withdraw()
        self.pgn.comment = self.text_newcomment.get(1.0,"end")[:-1]+\
                           ''.join(re.findall(r'\[%[^\]]*\]',self.pgn.comment))
        self.change_comment()
        self.unsaved_state()
    
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
        self.text_comment.insert("end",''.join(re.split(r'\[%[^\]]*\]', self.pgn.comment)))
        self.text_comment.configure(state=tk.DISABLED)