import sys 
import time 
import tempfile 
import mido 
import PyQt6
from pathlib import Path 
from dataclasses import dataclass 
from PyQt6.QtWidgets import ( QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, 
                             QApplication, QWidget, QVBoxLayout, QGridLayout,
                              QPushButton, QLabel, QSpinBox, QSlider, QFileDialog, QMessageBox )
from PyQt6.QtCore import Qt, QTimer 
from PyQt6.QtGui import QColor, QPalette 


# ---
# Sequencer data model 
# --- 
@dataclass 
class Config: 
    rows: int = 12 
    cols: int = 16 
    base_midi_note: int = 60 
    tempo: int = 120 
    tick_per_beat: int = 480 
    note_length_steps: int = 1 

class Sequencer: 
    def __init__(self, cfg: Config):
        self.cfg = cfg 
        self.grid = [[False]*cfg.cols for _ in range(cfg.rows)]
    
    def toggle(self,row,col):
        self.grid[row][col] = not self.grid[row][col]

    def set(self,row,col,value:bool):
        self.grid[row][col] = value 

    def clear(self): 
        self.grid = [[False]*self.cfg.cols for _ in range(self.cfg.rows)]

# ---
# Map row to MIDI note 
# ---
    def row_to_midi(row,cfg:Config):
        return cfg.base_midi_note + (cfg.rows - 1 - row) 
    
# ---
# GUI 
# ---
class PianoRoll(QWidget): 
    def __init__(self, seq: Sequencer):
        super().__init__()
        self.seq = seq 
        self.cfg = seq.cfg 
        self.setWindowTitle("GemSEQ")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
# controls 
        self.controls_layout = QHBoxLayout()
        self.layout.addLayout(self.controls_layout)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.on_play)
        self.controls_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.on_stop)
        self.controls_layout.addWidget(self.stop_btn)

        self.export_btn = QPushButton("Export MIDI")
        self.export_btn.clicked.connect(self.on_export)
        self.controls_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.on_clear)
        self.controls_layout.addWidget(self.clear_btn)

        self.controls_layout.addStretch() 

# tempo control 
        self.controls_layout.addWidget(QLabel("BPM"))
        self.tempo_spin = QSpinBox() 
        self.tempo_spin.setRange(30,300)
        self.tempo_spin.setValue(self.cfg.tempo)
        self.tempo_spin.valueChanged.connect(self.on_tempo_change)
        self.controls_layout.addWidget(self.steps_spin)

# grid 
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_widget.setLayout(self.grid_layout)
        self.layout.addWidget(self.grid_widget)

# cells reference 
        self.cells = [[None]*self.cfg.cols for _ in range(self.cfg.rows)]
        self.__init__grid()

# playback state 
        self.playing = False 
        self.current_step = 0 
        self.step_timer = QTimer() 
        self.step_timer.timeout.connect(self._advance_step)
        self.realtime_port = None 

    def _init_grid(self):
        for r in range(self.cfg.rows):
            note_lbl = QLabel(str(row_to_midi(r, self.cfg)))
            note_lbl.setFixedWidth(40)
            self.grid_layout.addWidget(note_lbl, r, 0)

            for c in range(self.cfg.cols):
                btn = QPushButton("")
                btn.setFixedSize(28,28)
                btn.setCheckable(True)
                btn.setStyleSheet(self._cell_style(False))
                btn.clicked.connect(self._makes_cell_handler(r,c,btn))
                self.grid_layout.addWidget(btn, r, c+1)
                self.cells[r][c] = btn

    def _make_cell_handler(self, r, c, btn):
        def handler():
            self.seq.toggle(r,c)
            state = self.seq.grid[r][c]
            btn.setStyleSheet(self._cell_style(state))
        return handler 

    def _cell_style(self, active:bool):
        if active: 
            return "background-color: rgb(0,170,0); border: 1px solid black;"
        else:
            return "background-color: rgb(240,240,240); border: 1px solid #aaa"
        
    def on_tempo_change(self, val):
        self.cfg.tempo = val 

    def on_steps_change(self,val):
        old_cols = self.cfg.cols 
        if val == old_cols: 
            return 
        self.cfg.cols = val 
        for r in range(self.cfg.rows):
            row = self.seq.grid[r]
            if len(row) < val:
                row.extend([False]*(val-len(row)))
            else:
                del row[val:]
        for r in range(self.cfg.rows):
            for c in range(old_cols):
                widget = self.cells[r][c]
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)
            self.cells = [[None]*self.cfg.cols for _ in range(self.cfg.rows)]
            for r in range(self.cfg.rows):
                for c in range(self.cfg.cols):
                    btn = QPushButton("")
                    btn.setFixedSize(28,28)
                    btn.setCheckable(True)
                    state = self.seq.grid[r][c]
                    btn.setChecked(state)
                    btn.setStyleSheet(self._cell_style(state))
                    btn.clicked.connect(self._make_cell_handler(r,c,btn))
                    self.grid_layout.addWidget(btn,r,c+1)
                    self.cells[r][c] = btn 

        def on_clear(self):
            self.seq.clear()
            for r in range(self.cfg.rows):
                for c in range(self.cfg.cols):
                    btn = self.cells[r][c]
                    btn.setChecked(False)
                    btn.setStyleSheet(self._cell_style(False))

        def _build_midi_file(self, filename: str):
            mid = mido.MidiFile(ticks_per_beat=self.cfg.ticks_per_beat)
            track = mido.MidiTrack()
            mid.tracks.append(track)
            tempo = mido.bpm2tempo(self.cfg.tempo)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
            step_ticks = int(self.cfg.ticks_per_beat * (4/ (self.cfg.cols)))
            step_ticks = int(self.cfg.ticks_per_beat * 4 / self.cfg.cols)
            events = [] 
            for c in range(self.cfg.cols): 
                abs_tick = c * step_ticks
                for r in range(self.cfg.rows):
                    if self.seq.grid[r][c]:
                        note = row_to_midi(r, self.cfg)
                        vel = 100 
                        events.append((abs_tick, mido.Message('note_on', note=note, velocity=vel)))
                        off_tick = abs_tick + self.cfg.note_lenght_steps * step_ticks 
                        events.append((off_tick, mido.Message('note_off', note=note, velocity=0)))
                    events.sort(key=lambda x: x[0])
                    last_tick = 0 
                    for abs_tick, msg in events: 
                        delta = abs_tick - last_tick 
                        msg.time = max(0, int(delta))
                        track.append(msg)
                        last_tick = abs_tick 
                    mid.save(filename)
                    return filename 
            
            def on_export(self):
                path, _ = QFileDialog.getSaveFilename(self, "Export MIDI", "sequence.mid", "MIDI files (*.mid *.midi)")
                if not path: 
                    return 
                try: 
                    self._build_midi_file(path)
                    QMessageBox.information(self, "Exported", f"MIDI exported to:\n{path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to export MIDI:\n{e}")
# ---
# Playback
# ---
def on_play(self):
        if self.playing:
            return
        self.playing = True
        self.current_step = 0

        step_dur = (4 * 60.0 / self.cfg.tempo) / self.cfg.cols
        self.step_interval_ms = int(step_dur * 1000)
        try:
            self.realtime_port = mido.open_output()  # tries to open default port (requires rtMidi or similar)
            print("Realtime MIDI output opened:", self.realtime_port.name)
        except Exception as e:
# fallback: write a MIDI file to temp location and ask user to play it with external player
            self.realtime_port = None
            tmp = Path(tempfile.gettempdir()) / "mini_daw_sequence.mid"
            try:
                self._build_midi_file(str(tmp))
                QMessageBox.information(self, "No realtime port", f"No realtime MIDI output available.\nExported MIDI to:\n{tmp}\n\nLoad it in a DAW or play with a MIDI player.")
            except Exception as ee:
                QMessageBox.critical(self, "Playback failed", f"Could not play or export MIDI:\n{ee}")
 # start stepping
        if self.realtime_port:
            self.active_off_events = []  # list of (absolute_step_index, note)
            self.step_timer.start(self.step_interval_ms)
        else:
            self.playing = False

def _advance_step(self):
    if not self.playing:
         return
    c = self.current_step 
    to_off = [ev for ev in self.active_off_events if ev[0] == c]
    for (_, note) in to_off:
        try:
            self.realtime_port.send(mido.Message('note_off', note=note, velocity=0))
        except Exception: 
                pass 
    self.active_off_events = [ev for ev in self.active_off_events if ev[0] != c]

    for r in range(self.cfg.rows):
        if self.seq.grid[r][c]:
            note = row_to_midi(r, self.cfg)
            try:
                self.realtime_port.send(mido.Message('note_on', note=note, velocity=100))
            except Exception:
                pass 
            off_step = (c + self.cfg.note_length_steps) % max(1, self.cfg.cols)
            self.active_off_events.append((off_step, note))
    for r in range(self.cfg.rows):
        for col in range(self.cfg.cols):
            btn = self.cells[r][col] 
            if col == c: 
                btn.setStyleSheet("background-color: rgb(0,200,0); border: 1px solid black")
            else: 
                btn.setStyleSheet("background-color: rgb(200,200,200); border 1px solid black")
        else: 
            btn.setStyleSheet(self._cell_style(self.seq.grid[r][col]))
        self.current_step = (self.current_step + 1) % self.cfg.cols 

    def on_stop(self):
        if self.step_timer.isActive():
            self.step_timer.stop()
        if self.realtime_port:
            try:
                for r in range(self.cfg.rows):
                    for c in range(self.cfg.cols):
                        if self.sew.grid[r][c]:
                            note= row_to_midi(r, self.cfg)
                            self.realtime_port.send(mido.Message('note_off', note=note, velocity=0))
            except Exception: 
                    pass 
        self.playing = False 
        for r in range(self.cfg.rows):
            for c in range(self.cfg.cols):
                btn = self.cells[r][c]
                btn.setStyleSheet(self._cell_style(self.seq.grid[r][c]))

    def main():
        app = QApplication(sys.argv)
        cfg = Config(rows=12, cols=16, base_midi_note=60, tempo=120)
        seq = Sequencer(cfg)
        w = PianoRoll(seq) 
        w.resize(800,400) 
        w.show()
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

        