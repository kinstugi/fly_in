from graph_lib import Node, ZoneType, Edge


class InputProcessor:
    def __init__(self, file_path: str = ""):
        self.file_path = file_path
        self.nb_drones = 0
        self.start_hub_name = ''
        self.end_hub_name = ''
        self.nodes: set[Node] = set()
        self.edges: list[tuple[str, str, int]] = []
        self.process_file()

    def process_file(self):
        try:
            with open(self.file_path, 'r') as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line[0] == '#':
                        continue
                    s_vals = line.split(':')
                    if len(s_vals) != 2:
                        print("Error, bad line")
                        continue
                    if s_vals[0].lower() == "nb_drones":
                        self.nb_drones = int(s_vals[1])
                    elif "hub" in s_vals[0].lower():
                        hub = self.process_hub(s_vals[1])
                        if not hub:
                            continue
                        self.nodes.add(hub)
                        if s_vals[0].lower() == 'start_hub':
                            self.start_hub_name = hub.name
                        elif s_vals[0].lower() == "end_hub":
                            self.end_hub_name = hub.name
                    elif s_vals[0].lower() == "connection":
                        c_edge = self.process_connect(s_vals[1])
                        if not c_edge:
                            continue
                        self.edges.append(c_edge)
        except Exception as e:
            print(f"Error {e}")

    def process_hub(self, line: str) -> Node | None:
        vals = line.strip().split()
        if not vals or len(vals) < 3 or len(vals) > 4:
            return None
        g_name = vals[0]
        try:
            g_x = int(vals[1])
            g_y = int(vals[2])
        except Exception as e:
            print(f"Error {e}")
            return None
        meta_data = vals[3][1:-1]
        m_arr = meta_data.split()
        ret_obj = Node(g_name, g_x, g_y)
        for item in m_arr:
            r_arr = item.split('=')
            if len(r_arr) != 2:
                print("Error")
                continue
            self.handle_hub_metadata(r_arr[0], r_arr[1], ret_obj)
        return ret_obj

    def handle_hub_metadata(self, key_word: str, value: str, hub: Node):
        value = value.lower()

        if key_word.lower() == 'color':
            hub.color = value
        elif key_word.lower() == 'max_drones':
            try:
                hub.max_drones = int(value)
            except Exception as e:
                print(f"Error {e}")
        elif key_word.lower() == 'zone':
            if value == 'normal':
                hub.z_type = ZoneType.normal
            elif value == 'blocked':
                hub.z_type = ZoneType.blocked
            elif value == 'restricted':
                hub.z_type = ZoneType.restricted
            elif value == 'priority':
                hub.z_type = ZoneType.priority
            else:
                print("Error")

    def process_connect(self, line: str) -> None | tuple[str, str, int]:
        vals = line.strip().split()
        if len(vals) < 1 or len(vals) > 2:
            return None
        nd_group = vals[0].strip().split('-')
        if len(nd_group) != 2:
            print("Error")
            return None
        node_a, node_b = nd_group
        if len(vals) != 2:
            return node_a, node_b, 1
        meta_data = (vals[1].strip())[1:-1]
        if len(meta_data) != 2:
            print("Error")
            return None
        mx_cap = 1
        try:
            mx_cap = int(meta_data[1])
        except Exception as e:
            print(f"Error {e}")
        return node_a, node_b, mx_cap
