import asyncio
import chess
import chess.engine
import EngineSettings

asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())

class Mixin:
    
    analyzing=False
    analysis=None
    analyze_task = None

    async def start_analyze(self):
        self.analyzing = True
        self.button_analyze.configure(text="Stop",command=self.stop_analyze)
        self.transport, self.engine =\
            await chess.engine.popen_uci(EngineSettings.ENGINE_PATH,
                                         setpgrp=True)
        await self.engine.configure(
            {"Threads":EngineSettings.ENGINE_MAX_THREADS})
        while self.analyzing:
            self.changing = False
            self.analysis = await self.engine.analysis(
                self.chessboard,multipv=3)
            self.analyze_task = asyncio.create_task(self.analyze())
            await asyncio.gather(self.updater(),self.analyze_task)
        await self.engine.quit()
        self.analyze_task = None
        self.canvas.delete("analyze_arrow")
        self.button_analyze.configure(
            text="Analyze",
            command=lambda : asyncio.run(self.start_analyze()))
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
                        label=self.readable_score(
                            score.white(),info.get("depth"))
                        self.label_score.configure(text=label)
                        if score.is_mate():
                            await asyncio.sleep(0.5)
                        if not self.training:
                            moves_scores_list =\
                              [(info.get("pv")[0],
                                info.get("score").white().score())
                               for info in self.analysis.multipv]
                            bs=moves_scores_list[0][1]
                            self.draw_analyze_arrows(
                                [m for m,s in moves_scores_list
                                 if bs is None\
                                  or s is None\
                                  or abs(s-bs)<EngineSettings.MAX_CT_DIFF])
                except chess.engine.AnalysisComplete:
                    break
                except asyncio.CancelledError:
                    break
        self.analysis.stop()
        self.analysis = None

    def stop_analyze(self):
        self.analyze_task.cancel()
        self.analyzing = False

    def change_analyze(self):
        self.analyze_task.cancel()
        self.changing = True

    async def updater(self):
        while (self.analysis is not None)\
           or (self.analyzing and (not self.changing)):
            self.update()
            await asyncio.sleep(1/120)

    def readable_score(self,score,depth):
        val = score.score()
        if val is not None:
            if val >0:
                text="+"
            else:
                text=""
            text += str(val/100)
            depth = str(depth)
            return text+" (dep "+depth+")"
        mat = str(score.mate())
        return "Mate in "+mat

