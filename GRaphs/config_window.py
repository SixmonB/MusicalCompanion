import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QFrame, QLabel, QScrollArea

class ParameterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Composer Ants")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.graphs = []

        form_layout = QFormLayout()
        # Load button
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_parameters)
        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save_parameters)
        form_layout.addRow(self.load_btn, save_btn)

        # BPM
        self.bpm_edit = QLineEdit()
        self.bpm_edit.setText("120")
        form_layout.addRow("BPM:", self.bpm_edit)

        # Evaporation rate
        self.evap_rate = QLineEdit()
        self.evap_rate.setText("10")
        form_layout.addRow("Evaporation rate (%/s)", self.evap_rate)

        # User
        self.add_user_btn = QPushButton("+")
        self.add_user_btn.clicked.connect(self.add_user)
        form_layout.addRow(QLabel("user"), self.add_user_btn)
        user_frame = QFrame()
        user_frame.setProperty("grouping_frame", True)
        self.user_layout = QFormLayout(user_frame)
        self.user = None
        form_layout.addRow(user_frame)

        # Graphs edit
        add_graph_btn = QPushButton("+")
        add_graph_btn.clicked.connect(self.add_graph)
        form_layout.addRow(QLabel("Graphs"), add_graph_btn)
        graphs_frame = QFrame()
        graphs_frame.setProperty("grouping_frame", True)
        graphs_frame
        graphs_layout = QVBoxLayout(graphs_frame)
        self.graphs_frame = graphs_frame
        self.graphs_layout = graphs_layout
        form_layout.addRow(self.graphs_frame)

        self.central_widget.setStyleSheet("QFrame[grouping_frame=\"true\"] { border: 2px solid black; }")
        self.central_widget.setLayout(form_layout)

        self.setFixedSize(720,1280)

    def add_user(self):
        self.add_user_btn.setText("-")
        self.add_user_btn.clicked.connect(self.remove_user)
        graph = QLineEdit("0")
        port = QLineEdit("0")
        channel = QLineEdit("0")
        self.user_layout.addRow("graph index", graph)
        self.user_layout.addRow("port", port)
        self.user_layout.addRow("channel", channel)
        self.user = {
            "graph": graph,
            "port": port,
            "channel": channel,
        }

    def remove_user(self):
        clear_layout(self.user_layout)
        self.user = None
        self.add_user_btn.setText("+")
        self.add_user_btn.clicked.connect(self.add_user)

    def add_graph(self):
        graph_idx = len(self.graphs)

        # graph editing frame
        graph_edit_frame = QFrame()
        graph_edit_frame.setProperty("grouping_frame", True)
        frame_layout = QVBoxLayout(graph_edit_frame)
        graph_edit = QWidget()
        layout = QFormLayout()

        # path edit
        path_edit = QLineEdit()
        layout.addRow("path", path_edit)

        # number of composers
        nb_composers = QLineEdit()
        layout.addRow("# of composers", nb_composers)

        # musicians
        ants_frame = QFrame()
        ants_frame.setProperty("grouping_frame", True)
        ants_layout = QVBoxLayout(ants_frame)
        add_ant_btn = QPushButton("+")
        add_ant_btn.clicked.connect(lambda _:self.add_musician(graph_idx))
        layout.addRow(QLabel("musicians"), add_ant_btn)
        layout.addRow(ants_frame)

        graph_edit.setLayout(layout)
        frame_layout.addWidget(graph_edit)
        self.graphs_layout.insertWidget(self.graphs_layout.count()-1, graph_edit_frame)
        self.graphs.append({
            "musicians_layout": ants_layout,
            "musicians": [],
            "path": path_edit,
            "nb_composers": nb_composers,
            "ants": [],
        })

    def add_musician(self, idx):
        musician_edit_frame = QFrame()
        musician_edit_frame.setProperty("grouping_frame", True)
        frame_layout = QVBoxLayout(musician_edit_frame)
        musician_edit = QWidget()
        layout = QFormLayout(musician_edit)

        port = QLineEdit()
        layout.addRow("port", port)
        channel = QLineEdit()
        layout.addRow("channel", channel)
        frame_layout.addWidget(musician_edit)
        self.graphs[idx]["musicians_layout"].insertWidget(self.graphs[idx]["musicians_layout"].count()-1, musician_edit_frame)
        self.graphs[idx]["musicians"].append({
            "port": port,
            "channel": channel,
        })

    def load_parameters(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Parameters", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "r") as file:
                data = json.load(file)
                self.bpm_edit.setText(str(data["bpm"]))
                self.evap_rate.setText(data["decay_factor"])
                self.reset()
                for i, graph_data in enumerate(data["graphs"]):
                    self.add_graph()
                    self.graphs[i]["path"].setText(graph_data["path"])
                    self.graphs[i]["nb_composers"].setText(str(graph_data.get("nb_composers", 0)))
                    for j, musician_data in enumerate(graph_data.get("musicians", [])):
                        self.add_musician(i)
                        self.graphs[i]["musicians"][j]["port"].setText(str(musician_data["port"]))
                        self.graphs[i]["musicians"][j]["channel"].setText(str(musician_data["channel"]))
                    if "user" in graph_data.keys():
                        print("user!", graph_data["user"]["port"])
                        self.add_user()
                        self.user["graph"].setText(str(i))
                        self.user["port"].setText(str(graph_data["user"]["port"]))
                        self.user["channel"].setText(str(graph_data["user"]["channel"]))
                
    def reset(self):
        for graph in self.graphs:
            clear_layout(graph["musicians_layout"])
        clear_layout(self.graphs_layout)
        clear_layout(self.user_layout)
        self.user = None
        self.graphs = []

    def save_parameters(self):
        data = {
            "bpm": self.bpm_edit.text(),
            "decay_factor": self.evap_rate.text(),
            "graphs": [],
        }

        for graph in self.graphs:
            graph_data = {
                "path": graph["path"].text(),
                "nb_composers": int(graph["nb_composers"].text()),
                "musicians": [],
            }
            for musician in graph["musicians"]:
                musician_data = {
                    "port": int(musician["port"].text()),
                    "channel": int(musician["channel"].text()),
                }
                graph_data["musicians"].append(musician_data)
                
            data["graphs"].append(graph_data)

        print(self.user)
        if self.user is not None:
            index = int(self.user["graph"].text())
            data["graphs"][index]["user"] = {
                "port": int(self.user["port"].text()),
                "channel": int(self.user["channel"].text())
            }

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Save Parameters", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
            print("Parameters saved successfully.")
            sys.exit()


def get_layout_widgets(layout):
    return list(map(lambda i:layout.itemAt(i).widget(), range(layout.count())))

def clear_layout(layout):
    for i in reversed(range(layout.count())):
        item=layout.takeAt(i)
        if item.widget():
            item.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParameterWindow()
    window.show()
    sys.exit(app.exec_())
