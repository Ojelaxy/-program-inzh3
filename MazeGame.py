import random
import tkinter as tk
from tkinter import messagebox


CELL_SIZE = 25
WALL_COLOR = "#1f2937"
PATH_COLOR = "#f9fafb"
PLAYER_COLOR = "#2563eb"
EXIT_COLOR = "#16a34a"
GRID_COLOR = "#d1d5db"
TRAP_ACTIVE_COLOR = "#ef4444"


class MazeGenerator:
    def __init__(self, rows, cols):
        self.rows = rows if rows % 2 == 1 else rows + 1
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.maze = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

    def generate(self):
        self._carve_passages(1, 1)
        self.maze[1][1] = 0
        self.maze[self.rows - 2][self.cols - 2] = 0
        return self.maze

    def _carve_passages(self, r, c):
        self.maze[r][c] = 0
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < self.rows - 1 and 1 <= nc < self.cols - 1 and self.maze[nr][nc] == 1:
                self.maze[r + dr // 2][c + dc // 2] = 0
                self._carve_passages(nr, nc)


class MazeGame:
    def __init__(self, rows=21, cols=21):
        self.rows = rows if rows % 2 == 1 else rows + 1
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.steps = 0
        self.traps_active = False
        self.reset()

    def reset(self):
        generator = MazeGenerator(self.rows, self.cols)
        self.maze = generator.generate()

        self.player_row = 1
        self.player_col = 1
        self.exit_row = self.rows - 2
        self.exit_col = self.cols - 2
        self.steps = 0
        self.traps_active = False

        self.trap_cells = self.generate_traps()

    def generate_traps(self):
        excluded = {
            (1, 1),
            (self.exit_row, self.exit_col),
            (1, 2),
            (2, 1),
            (self.exit_row, self.exit_col - 1),
            (self.exit_row - 1, self.exit_col),
        }

        free_cells = []
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.maze[r][c] == 0 and (r, c) not in excluded:
                    free_cells.append((r, c))

        trap_count = max(8, min(16, len(free_cells) // 12))
        if len(free_cells) < trap_count:
            trap_count = len(free_cells)

        return set(random.sample(free_cells, trap_count))

    def can_move(self, dr, dc):
        nr = self.player_row + dr
        nc = self.player_col + dc
        return 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] == 0

    def move(self, dr, dc):
        if not self.can_move(dr, dc):
            return "blocked"

        self.player_row += dr
        self.player_col += dc
        self.steps += 1

        if self.traps_active and (self.player_row, self.player_col) in self.trap_cells:
            return "dead"

        if self.is_winner():
            return "win"

        return "moved"

    def is_winner(self):
        return self.player_row == self.exit_row and self.player_col == self.exit_col

    def is_player_on_active_trap(self):
        return self.traps_active and (self.player_row, self.player_col) in self.trap_cells


class MazeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабиринт")
        self.resizable(False, False)
        self.configure(bg="#e5e7eb")

        self.game = MazeGame(21, 21)
        self.trap_timer_id = None

        self.create_menu()
        self.create_widgets()
        self.bind_keys()

        self.draw_maze()
        self.update_info()
        self.start_trap_cycle()

    def create_menu(self):
        menu_bar = tk.Menu(self)

        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.destroy)
        menu_bar.add_cascade(label="Игра", menu=game_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Помощь", command=self.show_help)
        help_menu.add_command(label="О программе", command=self.show_about)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menu_bar)

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#e5e7eb")
        main_frame.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(
            main_frame,
            width=self.game.cols * CELL_SIZE,
            height=self.game.rows * CELL_SIZE,
            bg="white",
            highlightthickness=1,
            highlightbackground="#9ca3af"
        )
        self.canvas.grid(row=0, column=0, rowspan=2, padx=(0, 12))

        side_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief="solid")
        side_frame.grid(row=0, column=1, sticky="n")

        tk.Label(
            side_frame,
            text="Лабиринт",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#111827"
        ).pack(pady=(12, 8))

        self.info_label = tk.Label(
            side_frame,
            text="",
            font=("Arial", 11),
            bg="#ffffff",
            fg="#374151",
            justify="left"
        )
        self.info_label.pack(padx=12, pady=8)

        tk.Button(
            side_frame,
            text="Новая игра",
            width=18,
            command=self.new_game,
            bg="#2563eb",
            fg="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=6)

        tk.Button(
            side_frame,
            text="Помощь",
            width=18,
            command=self.show_help,
            bg="#10b981",
            fg="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=6)

        tk.Button(
            side_frame,
            text="Выход",
            width=18,
            command=self.destroy,
            bg="#ef4444",
            fg="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=(6, 12))

        controls_frame = tk.LabelFrame(
            main_frame,
            text="Управление",
            bg="#ffffff",
            fg="#111827",
            font=("Arial", 10, "bold"),
            bd=1,
            relief="solid"
        )
        controls_frame.grid(row=1, column=1, sticky="n", pady=(10, 0))

        tk.Button(controls_frame, text="↑", width=5, command=lambda: self.try_move(-1, 0)).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(controls_frame, text="←", width=5, command=lambda: self.try_move(0, -1)).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(controls_frame, text="↓", width=5, command=lambda: self.try_move(1, 0)).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(controls_frame, text="→", width=5, command=lambda: self.try_move(0, 1)).grid(row=1, column=2, padx=5, pady=5)

    def bind_keys(self):
        self.bind_all("<KeyPress>", self.handle_keypress)

    def stop_trap_cycle(self):
        if self.trap_timer_id is not None:
            try:
                self.after_cancel(self.trap_timer_id)
            except Exception:
                pass
            self.trap_timer_id = None

    def handle_keypress(self, event):
        char = event.char.lower() if event.char else ""
        key = event.keysym.lower()

        if key == "up" or char in ("w", "ц"):
            self.try_move(-1, 0)
        elif key == "down" or char in ("s", "ы"):
            self.try_move(1, 0)
        elif key == "left" or char in ("a", "ф"):
            self.try_move(0, -1)
        elif key == "right" or char in ("d", "в"):
            self.try_move(0, 1)

    def start_trap_cycle(self):
        self.stop_trap_cycle()
        self.game.traps_active = False
        self.draw_maze()
        self.update_info()
        self.trap_timer_id = self.after(2000, self.toggle_traps)

    def toggle_traps(self):
        self.trap_timer_id = None
        self.game.traps_active = not self.game.traps_active
        self.draw_maze()
        self.update_info()

        if self.game.is_player_on_active_trap():
            messagebox.showerror(
                "Поражение",
                f"Опасная клетка стала красной под игроком.\n"
                f"Игра окончена.\n"
                f"Шагов сделано: {self.game.steps}"
            )
            self.new_game()
            return

        self.trap_timer_id = self.after(2000, self.toggle_traps)

    def draw_maze(self):
        self.canvas.delete("all")

        for r in range(self.game.rows):
            for c in range(self.game.cols):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                if self.game.maze[r][c] == 1:
                    color = WALL_COLOR
                else:
                    color = PATH_COLOR

                if (r, c) in self.game.trap_cells and self.game.traps_active:
                    color = TRAP_ACTIVE_COLOR

                if r == self.game.exit_row and c == self.game.exit_col:
                    color = EXIT_COLOR

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=GRID_COLOR
                )

        pr = self.game.player_row
        pc = self.game.player_col
        x1 = pc * CELL_SIZE + 4
        y1 = pr * CELL_SIZE + 4
        x2 = x1 + CELL_SIZE - 8
        y2 = y1 + CELL_SIZE - 8

        self.canvas.create_oval(x1, y1, x2, y2, fill=PLAYER_COLOR, outline="")

    def update_info(self):
        trap_state = "АКТИВНЫ" if self.game.traps_active else "безопасны"

        self.info_label.config(
            text=(
                f"Цель: дойти до зелёной клетки\n\n"
                f"Шагов сделано: {self.game.steps}\n"
                f"Опасные клетки: {trap_state}\n\n"
                f"Управление:\n"
                f"Стрелки / WASD"
            )
        )

    def try_move(self, dr, dc):
        result = self.game.move(dr, dc)

        if result == "blocked":
            return

        self.draw_maze()
        self.update_info()

        if result == "dead":
            self.stop_trap_cycle()
            messagebox.showerror(
                "Поражение",
                f"Вы наступили на красную клетку.\n"
                f"Игра окончена.\n"
                f"Шагов сделано: {self.game.steps}"
            )
            self.new_game()
            return

        if result == "win":
            self.stop_trap_cycle()
            messagebox.showinfo(
                "Победа",
                f"Вы прошли лабиринт!\n"
                f"Количество шагов: {self.game.steps}"
            )
            self.new_game()

    def new_game(self):
        self.game.reset()
        self.draw_maze()
        self.update_info()
        self.start_trap_cycle()

    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Помощь")
        help_window.resizable(False, False)
        help_window.configure(bg="#ffffff")

        text = (
            "Правила игры:\n\n"
            "1. Игрок начинает в левом верхнем углу лабиринта.\n"
            "2. Нужно дойти до зелёной клетки — это выход.\n"
            "3. Сквозь стены проходить нельзя.\n"
            "4. Некоторые клетки периодически становятся красными.\n"
            "5. Если наступить на красную клетку, игра заканчивается.\n\n"
            "Управление:\n"
            "- стрелки\n"
            "- WASD\n"
            "- кнопки справа в интерфейсе\n\n"
            "Меню:\n"
            "- Новая игра — создать новый лабиринт\n"
            "- Выход — закрыть приложение"
        )

        tk.Label(
            help_window,
            text="Справка по игре",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="#111827"
        ).pack(pady=(12, 8))

        tk.Label(
            help_window,
            text=text,
            justify="left",
            bg="#ffffff",
            fg="#374151",
            font=("Arial", 11)
        ).pack(padx=15, pady=10)

        tk.Button(
            help_window,
            text="Закрыть",
            command=help_window.destroy,
            bg="#2563eb",
            fg="white",
            relief="flat",
            cursor="hand2",
            width=14
        ).pack(pady=(0, 12))

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Игра «Лабиринт»\n\n"
            "Учебный GUI-проект на Python + Tkinter.\n"
            "Разработал Эндерс Глеб 4.407-1."
        )


if __name__ == "__main__":
    app = MazeApp()
    app.mainloop()