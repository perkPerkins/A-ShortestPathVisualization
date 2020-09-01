import pygame
import colors
from queue import PriorityQueue

WIDTH = 600
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")


class Node:
    def __init__(self, row, col, cube_width):
        self.row = row
        self.col = col
        self.x = row * cube_width
        self.y = col * cube_width
        self.color = colors.WHITE
        self.neighbors = []
        self.width = cube_width

    def find_neighbors(self, graph):
        if self.row < len(graph) - 1 and graph[self.row + 1][self.col].color is not colors.BLACK:
            self.neighbors.append(graph[self.row + 1][self.col])
        if self.row > 0 and graph[self.row - 1][self.col].color is not colors.BLACK:
            self.neighbors.append(graph[self.row - 1][self.col])
        if self.col < len(graph) - 1 and graph[self.row][self.col + 1].color is not colors.BLACK:
            self.neighbors.append(graph[self.row][self.col + 1])
        if self.col > 0 and graph[self.row][self.col - 1].color is not colors.BLACK:
            self.neighbors.append(graph[self.row][self.col - 1])
        if self.col > 0 and self.row > 0 and graph[self.row - 1][self.col - 1].color is not colors.BLACK:
            self.neighbors.append(graph[self.row - 1][self.col - 1])
        if self.col > 0 and self.row < len(graph) - 1 and graph[self.row + 1][self.col - 1].color is not colors.BLACK:
            self.neighbors.append(graph[self.row + 1][self.col - 1])
        if self.col < len(graph) - 1 and self.row < len(graph) - 1 and graph[self.row + 1][self.col + 1].color is not colors.BLACK:
            self.neighbors.append(graph[self.row + 1][self.col + 1])
        if self.col > len(graph) - 1 and self.row > 0 and graph[self.row - 1][self.col + 1].color is not colors.BLACK:
            self.neighbors.append(graph[self.row - 1][self.col + 1])

    def update_color(self, color):
        self.color = color

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for y in range(rows):
        grid.append([])
        for x in range(width):
            grid[y].append(Node(y, x, gap))
    return grid


def draw_grid(rows, width):
    square = width // rows
    for row in range(rows):
        pygame.draw.line(screen, colors.BLACK, (0, square * row), (width, square * row), 1)
    for col in range(rows):
        pygame.draw.line(screen, colors.BLACK, (square * col, 0), (square * col, width), 1)


def draw(grid, rows, width):
    screen.fill(colors.BLACK)
    for row in grid:
        for node in row:
            node.draw(screen)
    draw_grid(rows, width)
    pygame.display.update()


def draw_colors(grid, width, rows, start_and_finish):
    try:
        pos = pygame.mouse.get_pos()
        row = pos[0] // (width // rows)
        column = pos[1] // (width // rows)
        if len(start_and_finish) < 2:
            if len(start_and_finish) == 0:
                grid[row][column].color = colors.BLUE
                start_and_finish.append(grid[row][column])
            else:
                if grid[row][column].color is not colors.BLUE:
                    grid[row][column].color = colors.PURPLE
                    start_and_finish.append(grid[row][column])
        else:
            if grid[row][column].color is colors.WHITE:
                grid[row][column].color = colors.BLACK
        print("Click ", pos, "Grid coordinates: ", row, column)
    except (AttributeError, IndexError):
        pass
    return start_and_finish


def manhattan_dist(start_node, end_node):
    return abs(start_node.col - end_node.col) + abs(start_node.row - end_node.row)


def show_path(parent, node, grid, width, rows):
    node = parent.get(node)
    while node is not None:
        node.color = colors.GOLD
        node = parent[node]
        draw(grid, rows, width)


def cost_to_neighbor(node, neighbor):
    # if neighbor is diagonal from current node, cost to that node is sqrt(2) bc 1^2 + 1^2 = c^2. c^2 = 2, c = 1.4
    if abs(node.row - neighbor.row) + abs(node.col - neighbor.col) == 2:
        return 1.4
    return 1


def a_star_algorithm(start, end, grid, width, rows):
    count = 0
    open_nodes = PriorityQueue()
    open_nodes.put((0, count, start))
    open_node_hash = {start: True}
    parent = {start: None}
    start_to_current = {spot: float("inf") for row in grid for spot in row}
    start_to_current[start] = 0
    while not open_nodes.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        node = open_nodes.get()[2]
        open_node_hash.pop(node)
        node.find_neighbors(grid)

        if node == end:
            end.color = colors.GOLD
            show_path(parent, node, grid, width, rows)
            return True

        for neighbor in node.neighbors:

            new_cost = start_to_current[node] + cost_to_neighbor(node, neighbor)
            if new_cost < start_to_current[neighbor]:
                parent[neighbor] = node
                start_to_current[neighbor] = new_cost
                if neighbor not in open_node_hash:
                    count += 1
                    priority = manhattan_dist(neighbor, end) + new_cost
                    open_node_hash[neighbor] = True
                    open_nodes.put((priority, count, neighbor))
                    neighbor.color = colors.RED
        draw(grid, rows, width)

        if node != start:
            node.color = colors.BLUE
    return False


def main(width):
    rows = 30
    grid = make_grid(rows, width)
    pygame.init()
    done = False
    mouse_press_locked = False
    clock = pygame.time.Clock()
    start_and_finish = []
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif pygame.mouse.get_pressed()[0]:
                if not mouse_press_locked:
                    start_and_finish = draw_colors(grid, width, rows, start_and_finish)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    mouse_press_locked = True
                    a_star_algorithm(start_and_finish[0], start_and_finish[1], grid, width, rows)
                elif event.key == pygame.K_c:
                    mouse_press_locked = False
                    start_and_finish.clear()
                    grid = make_grid(rows, width)
        clock.tick(120)
        draw(grid, rows, width)


main(WIDTH)
