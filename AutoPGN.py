#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# Version : 1.0
#
# Copyright (C) 2021 Patrick Thévenon
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
#             à Novembre 2021       #
#                                   #
#####################################

import sys
import chess
import chess.pgn as pgn
import asyncio
import chess.engine
import time, datetime

stockfish_path="/usr/games/stockfish"
maxthreads = 8

maxCTdiff = 80 # Différence de centipions maximale acceptée dans les scores des coups

asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())

# semaphore = asyncio.Semaphore(6)

count = None
approx_totalcount = None

def getpgn(fen=pgn.Game().board().fen(),tree_depth=10,engine_depth=20,ompv=3,player=chess.WHITE,pmpv=1):
    global count,approx_totalcount,t0
    pgn_tree = pgn.Game()
    pgn_tree.setup(fen)
    count = 0
    approx_totalcount = total_nodes(pmpv,ompv,tree_depth) if player == pgn_tree.turn() else total_nodes(ompv,pmpv,tree_depth)
    print()
    print("Approx. total nodes :",approx_totalcount)
    t0=datetime.datetime.now()
    print("Starting on",t0.strftime("%x at %X"))
    asyncio.run(get_node_from(0,pgn_tree,tree_depth,engine_depth,ompv,player,pmpv))
    t1=datetime.datetime.now()
    print("Ending on",t1.strftime("%x at %X"),"after",datetime.timedelta(seconds=(t1-t0).total_seconds()))
    print(pgn_tree)
    return pgn_tree

def total_nodes(pmpv,ompv,depth):
    S=1
    end_nodes=1
    for i in range(depth):
        mpv = pmpv if i%2==0 else ompv
        S+= end_nodes*mpv
        end_nodes*= mpv
    return S

async def get_node_from(from_depth,pgn_node,tree_depth,engine_depth,ompv,player,pmpv):
    global count
    count+=1
    if count >= 10:
        percent = round(count/approx_totalcount*100,2)
        time_left = (100-percent)*(datetime.datetime.now()-t0).total_seconds()/percent
        print("Approx.", percent, "% done. Time left estimated :", datetime.timedelta(seconds = time_left),end="\r")
    if from_depth == tree_depth:
        return pgn_node
    transport, engine = await chess.engine.popen_uci(stockfish_path)
    await engine.configure({"Threads":maxthreads})
    if pgn_node.turn() == player:
        mpv=pmpv
        analysis = await engine.analysis(pgn_node.board(),multipv=mpv,limit=chess.engine.Limit(depth=engine_depth))
    else:
        mpv=ompv
        analysis = await engine.analysis(pgn_node.board(),multipv=mpv,limit=chess.engine.Limit(depth=20))
    await analysis.wait()
    move_list = [(info.get("pv")[0],info.get("score").white().score()) for info in analysis.multipv]
    analysis.stop()
    await engine.quit()
    score0 = move_list[0][1]
    if score0 is not None:
        for move,score in move_list:
            if score is not None and abs(score-score0)<maxCTdiff:
                    pgn_node.add_variation(move)
            else:
                count+=total_nodes(ompv,pmpv,tree_depth-from_depth-1) if player == pgn_node.turn() else total_nodes(pmpv,ompv,tree_depth-from_depth-1)
    else:
        pgn_node.add_variation(move_list[0][0])
        tn = total_nodes(ompv,pmpv,tree_depth-from_depth-1) if player == pgn_node.turn() else total_nodes(pmpv,ompv,tree_depth-from_depth-1)
        count+=(mpv-1)*tn
#    async with semaphore: # Tentative d’éviter de lancer trop de threads
#        await asyncio.gather(*[get_node_from(from_depth+1,child_node,tree_depth,engine_depth,ompv,player,pmpv) for child_node in pgn_node.variations])
    for child_node in pgn_node.variations:
        await get_node_from(from_depth+1,child_node,tree_depth,engine_depth,ompv,player,pmpv)

if __name__ == '__main__':
    fen = input("FEN (empty for default) : ")
    if fen == "":
        fen = pgn.Game().board().fen()
    fen_name = input("FEN name : ")
    if fen_name !="":
        fen_name="_"+fen_name
    tree_depth = input("Tree depth (full moves) (empty for default 5) : ")
    if tree_depth == "":
        tree_depth = 5
    else:
        tree_depth = int(tree_depth)
    engine_depth = input("Engine depth (empty for default 20) : ")
    if engine_depth == "":
        engine_depth = 20
    else:
        engine_depth = int(engine_depth)
    color = input("White (w) or Black (b) : ")
    while not color in ["w","b"]:
        color = input("White (w) or Black (b) : ")
    if color == "w":
        player = chess.WHITE
    else:
        player = chess.BLACK
    opponent_moves = input("Moves for opponent (empty for default 2) : ")
    if opponent_moves == "":
        opponent_moves = 2
    else:
        opponent_moves = int(opponent_moves)
    player_moves = input("Moves for player (empty for default 1) : ")
    if player_moves == "":
        player_moves = 1
    else:
        player_moves = int(player_moves)
    pgn_filename = input("File name (empty for auto) : ")
    if pgn_filename == "":
        pgn_filename = "PGN files/AutoPGN_"+str(tree_depth)+"_"+str(engine_depth)+fen_name+"_"+chess.COLOR_NAMES[player]+"_"+str(opponent_moves)+"_"+str(player_moves)+".pgn"
    pgn_tree = getpgn(fen=fen,tree_depth=2*tree_depth,engine_depth=engine_depth,ompv=opponent_moves,player=player,pmpv=player_moves)
    with open(pgn_filename, "w", encoding="utf-8") as pgn_file:
        print(pgn_tree, file=pgn_file, end="\n\n")
