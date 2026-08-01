from graph_lib import Node


class InputProcessor:
    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.nb_drones = 0

    def process_file(self):
        try:
            with open(self.file_path, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    s_vals = line.split(':')
                    if len(s_vals) != 2:
                        print("Error, bad line")
                        continue
                    if s_vals[0].lower() == "nb_drones":
                        self.nb_drones = int(s_vals[1])
        except Exception as e:
            print(f"Error {e}")

    def process_hub(self, line: str) -> Node | None:
        vals = line.strip().split()
        if not vals or len(vals) < 3:
            return None
        g_name = vals[0]
        try:
            g_x = int(vals[1])
            g_y = int(vals[2])
        except Exception as e:
            print(f"Error {e}")
            return None
        return Node(g_name, g_x, g_y)
