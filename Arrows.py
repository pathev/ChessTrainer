import chess
import tkinter as tk

arrow_color = ["#FF3333","#FF9933","#EEEE33","#33FF33","#9933FF","#0099FF","#DDDDDD"]
comment_arrow_color = {"red": "#AA1111", "yellow": "#AAAA11", "blue": "#1111AA", "green": "#11AA11"}
analyze_arrow_color = ["#6666FF","#9999FF","#DDDDFF"]

class Mixin:
    def canvas_bind_arrow_create(self):
        self.canvas.bind("<Button-3>",
                         lambda e:self.click_arrow_create(e,"green"))
        self.canvas.bind("<Alt-Button-3>",
                         lambda e:self.click_arrow_create(e,"blue"))
        self.canvas.bind("<Control-Button-3>",
                         lambda e:self.click_arrow_create(e,"red"))
        self.canvas.bind("<Control-Alt-Button-3>",
                         lambda e:self.click_arrow_create(e,"yellow"))
    
    def canvas_unbind_arrow_create(self):
        self.canvas.unbind("<Button-3>")
        self.canvas.unbind("<Alt-Button-3>")
        self.canvas.unbind("<Control-Button-3>")
        self.canvas.unbind("<Control-Alt-Button-3>")

    def click_arrow_create(self, event,color):
        self.canvas.unbind("<Button-1>")
        self.canvas_unbind_arrow_create()
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
            self.draw_arrow(self.selected_from_square,square,
                            comment_arrow_color.get(color))
        else:
            self.draw_arrow_square(self.selected_from_square,
                                   comment_arrow_color.get(color))


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
                    arrows.append(chess.svg.Arrow(tail=self.selected_from_square,
                                                  head=square,color=color))
                break
        if not found:
            arrows.append(chess.svg.Arrow(tail=self.selected_from_square,
                                          head=square,color=color))
        self.pgn.set_arrows(arrows)
        self.unsaved_state()

        self.refresh()

        self.selected_from_square = None

        self.canvas.bind("<Button-1>", self.click_edit)
        self.canvas_bind_arrow_create()

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
            x1 = (7-col1) * self.square_size
            y1 = row1 * self.square_size
        else:
            x1 = col1 * self.square_size
            y1 = (7-row1) * self.square_size
        l=int(self.square_size*0.075)
        e=1+l//2
        self.canvas.create_rectangle(x1+e,y1+e,
                                     x1+self.square_size-e,y1+self.square_size-e,
                                     width=l,outline=color,tags="arrow")

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
        self.canvas.create_line(x1,y1,x2,y2,
                                arrow=tk.LAST,
                                width=self.square_size//5,
                                arrowshape=(15,12,5),fill=color,tags=tags)
