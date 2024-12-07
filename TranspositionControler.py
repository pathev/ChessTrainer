from tkinter.messagebox import askokcancel

import Transposition

class Mixin:
    def make_primary_transposition(self):
        Transposition.make_primary(self.pgn)
        self.set_pgn()
    
    def remove_primary_transposition(self):
        if Transposition.isolate_primary(self.pgn)\
           or askokcancel("Are you sure ?",
                          "All linked transpositions will be removed too",
                          icon='warning',
                          default='cancel'):
            Transposition.remove_primary(self.pgn)
            self.set_pgn()

    def exchange_primary_transposition(self):
        Transposition.exchange_with_primary(self.pgn)
        self.set_pgn()

    def link_transposition(self):
        Transposition.link(self.pgn)
        self.set_pgn()
    
    def loop_transposition(self):
        pgn = Transposition.after(self.pgn)
        if not pgn is None:
            self.pgn = pgn
            self.set_pgn()
    
    def to_primary_transposition(self):
        pgn = Transposition.get_primary_from_secondary_node(self.pgn)
        if not pgn is None:
            self.pgn = pgn
        self.set_pgn()

