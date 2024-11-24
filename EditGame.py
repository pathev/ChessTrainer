from tkinter.messagebox import askokcancel

import chess

class Mixin:
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
        if askokcancel("Are you sure ?",
                       "Node and variations will be lost",
                       icon='warning',
                       default='cancel'):
            self.pgn.parent.remove_variation(self.pgn)
            self.pgn = self.pgn.parent
            self.set_pgn(unsaved=True)

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

    def click_edit(self, event):
        current_column = event.x // self.square_size
        current_row = 7 - (event.y // self.square_size)
        if self.flipped:
            current_row = 7-current_row
            current_column = 7-current_column

        square = chess.square(current_column, current_row)

        if self.selected_square is not None:
            if square in self.hilighted:
                move=chess.Move(
                    from_square=self.selected_square,
                    to_square=square)
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

    def click_read(self, event):

        if len(self.pgn.variations) == 1:
            # Une seule variation/flèche ; où que l’on clique, le coup est joué
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
                move=chess.Move(
                    from_square=self.selected_square,
                    to_square=square)
                self.selected_square = None
                self.hilighted = []
                self.refresh()
                if self.pgn.has_variation(move):
                    self.pgn = self.pgn.variation(move)
                    self.set_pgn()
            else:
                to_square_var_list = list(filter(
                    lambda n:n.move.to_square == square,
                    self.pgn.variations))
                if len(to_square_var_list) == 1:
                    self.pgn = to_square_var_list[0]
                    self.set_pgn()
                else:
                    from_square_var_list=list(filter(
                        lambda n:n.move.from_square == square,
                        self.pgn.variations))
                    if len(from_square_var_list) == 1:
                        self.pgn = from_square_var_list[0]
                        self.set_pgn()
                    elif len(from_square_var_list) >=1:
                        self.selected_square = square
                        self.hilighted = [n.move.to_square
                                          for n in from_square_var_list]
                        self.refresh()
