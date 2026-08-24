import pygame
from graph_lib import StaticGraph


class SimVisualizer:
    _SCALE_FACTOR = 100
    _RAD = 25

    def __init__(self, s_graph: StaticGraph, output: str):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.s_graph = s_graph
        self.drone_movements = output

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill("purple")
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def draw(self) -> None:
        self._draw_static_graph()

    def _draw_static_graph(self) -> None:
        for node in self.s_graph.graph:
            pygame.draw.circle(
                self.screen, 
                'white', 
                (
                    self._SCALE_FACTOR*node.x + 120, 
                    self._SCALE_FACTOR*node.y + 300
                ), 
                15
            )
