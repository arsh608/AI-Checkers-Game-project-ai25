import pygame as pg
import sys
from checkers import Board, Status, AI_Algo


class GameRenderer:
    def __init__(self):
        pg.init()

        # Set dynamic screen size
        self.WIDTH, self.HEIGHT = 600, 600

        # Calculate cell size
        self.CELL_WIDTH = self.WIDTH // 8
        self.CELL_HEIGHT = self.HEIGHT // 8

        # Thickness of the border
        BORDER_WIDTH = 3

        # Initialize Pygame window
        self.SCREEN = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        pg.display.set_caption("Checkers!")

        # Load Images
        self.BOARD = pg.image.load("assets/Board.jpg")
        self.B_KING = pg.image.load("assets/Black_King.png")
        self.B_PIECE = pg.image.load("assets/Black_Piece.png")
        self.R_KING = pg.image.load("assets/Red_King.png")
        self.R_PIECE = pg.image.load("assets/Red_Piece.png")

        # Transform images to fit size
        self.BOARD = pg.transform.scale(self.BOARD, (self.WIDTH, self.HEIGHT))
        self.B_PIECE = pg.transform.scale(self.B_PIECE, (self.CELL_WIDTH, self.CELL_HEIGHT))
        self.R_PIECE = pg.transform.scale(self.R_PIECE, (self.CELL_WIDTH, self.CELL_HEIGHT))
        self.B_KING = pg.transform.scale(self.B_KING, (self.CELL_WIDTH, self.CELL_HEIGHT))
        self.R_KING = pg.transform.scale(self.R_KING, (self.CELL_WIDTH, self.CELL_HEIGHT))

    # Render Board
    def render_board(self, board, highlight_move=None):
        self.SCREEN.fill((0,0,0))
        self.SCREEN.blit(self.BOARD, (0, 0))  # Draw the board image
        if highlight_move:
            for move in highlight_move:
                r, c = move
                highlight_rect = pg.Rect(
                    c * self.CELL_WIDTH, 
                    r * self.CELL_HEIGHT, 
                    self.CELL_WIDTH, 
                    self.CELL_HEIGHT
                )
                pg.draw.rect(self.SCREEN, (255, 255, 120, 200), highlight_rect, 10)  # Yellow border

        for i in range(8):
            for j in range(8):
                if board.board[i][j] == 'B':  # Render 'Black Piece'
                    img_rect = self.B_PIECE.get_rect(center=(
                        j * self.CELL_WIDTH + self.CELL_WIDTH // 2, # X-coordinate (center of column)
                        i * self.CELL_HEIGHT + self.CELL_HEIGHT // 2 # Y-coordinate (center of row)
                    ))
                    self.SCREEN.blit(self.B_PIECE, img_rect)
                elif board.board[i][j] == 'R':  # Render 'Red Piece'
                    img_rect = self.R_PIECE.get_rect(center=(
                        j * self.CELL_WIDTH + self.CELL_WIDTH // 2, # X-coordinate (center of column)
                        i * self.CELL_HEIGHT + self.CELL_HEIGHT // 2 # Y-coordinate (center of row)
                    ))
                    self.SCREEN.blit(self.R_PIECE, img_rect)
                elif board.board[i][j] == 'BK':  # Render 'Black King'
                    img_rect = self.B_KING.get_rect(center=(
                        j * self.CELL_WIDTH + self.CELL_WIDTH // 2, # X-coordinate (center of column)
                        i * self.CELL_HEIGHT + self.CELL_HEIGHT // 2 # Y-coordinate (center of row)
                    ))
                    self.SCREEN.blit(self.B_KING, img_rect)
                elif board.board[i][j] == 'RK':  # Render 'Red King'
                    img_rect = self.R_KING.get_rect(center=(
                        j * self.CELL_WIDTH + self.CELL_WIDTH // 2, # X-coordinate (center of column)
                        i * self.CELL_HEIGHT + self.CELL_HEIGHT // 2 # Y-coordinate (center of row)
                    ))
                    self.SCREEN.blit(self.R_KING, img_rect)

        pg.display.update()  # Refresh the screen with new visuals

    # Display Winner
    def display_winner(self, winner):
        font = pg.font.Font(None, 60)  # Load default font with size 60
        text = font.render(winner, True, (255, 0, 0))  # Render text in red
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))  # Center the text

        self.SCREEN.blit(text, text_rect)  # Draw text on the screen
        pg.display.update()  # Refresh the display
        pg.time.delay(2000)  # Give time to see the message


    # Display Invalid Move
    def display_status(self, msg):
        font = pg.font.Font(None, 60)  # Load default font with size 60
        text = font.render(msg, True, (255, 0, 0))  # Render text in red
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))  # Center the text

        self.SCREEN.blit(text, text_rect)  # Draw text on the screen
        pg.display.update()  # Refresh the display
        pg.time.delay(100)

    def animate_piece_move(self, board, piece_type, start_pos, end_pos):
        start_x = start_pos[1] * self.CELL_WIDTH + self.CELL_WIDTH // 2
        start_y = start_pos[0] * self.CELL_HEIGHT + self.CELL_HEIGHT // 2
        end_x = end_pos[1] * self.CELL_WIDTH + self.CELL_WIDTH // 2
        end_y = end_pos[0] * self.CELL_HEIGHT + self.CELL_HEIGHT // 2

        if piece_type == 'B':
            image = self.B_PIECE
        elif piece_type == 'R':
            image = self.R_PIECE
        elif piece_type == 'BK':
            image = self.B_KING
        elif piece_type == 'RK':
            image = self.R_KING
        else:
            return

        frames = 15
        for frame in range(frames):
            t = frame / frames
            current_x = start_x + (end_x - start_x) * t
            current_y = start_y + (end_y - start_y) * t

            self.render_board(board)  # Redraw full board in the background
            img_rect = image.get_rect(center=(int(current_x), int(current_y)))
            self.SCREEN.blit(image, img_rect)

            pg.display.update()
            pg.time.delay(15)  # Control animation speed


class Game():
    def __init__(self):
        self.board = Board()
        self.renderer = GameRenderer()
        self.ai = AI_Algo(self.board)
        self.to_move = 'B'

    def reset_game(self):
        self.board.reset()
        self.to_move = 'B'
        self.renderer.render_board(self.board)

    def user_input(self):
        mouse_c, mouse_r = pg.mouse.get_pos()
        col, row = mouse_c // self.renderer.CELL_WIDTH, mouse_r // self.renderer.CELL_HEIGHT
        return (row, col)

    def game_loop(self):
        clock = pg.time.Clock()
        self.reset_game()
        move_in_progress = False
        start_pos = None
        highlight_moves = []

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()  
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:  
                        self.reset_game()
                        move_in_progress = False
                        start_pos = None

                if event.type == pg.MOUSEBUTTONDOWN:
                    if not move_in_progress:
                        start_pos = self.user_input()
                        move_in_progress = True
                        piece = self.board.board[start_pos[0]][start_pos[1]]
                        
                        if piece and piece.startswith('B'):
                            highlight_moves = self.board.get_valid_moves(start_pos[0], start_pos[1])
                        
                        self.renderer.render_board(self.board,highlight_moves)
                    else:
                        end_pos = self.user_input()
                        moving_piece = self.board.board[start_pos[0]][start_pos[1]]
                        user_status = self.board.move_piece(start_pos, end_pos, self.to_move)

                        if user_status in (Status.VALID_MOVE, Status.WAS_CAPTURE_MOVE, Status.CAPTURE_AGAIN):
                            self.renderer.animate_piece_move(self.board, moving_piece, start_pos, end_pos)
                            highlight_moves = []
                        
                        if user_status == Status.VALID_MOVE or user_status == Status.WAS_CAPTURE_MOVE:
                            # Switch turn to AI ('R')
                            self.to_move = 'R'
                            self.renderer.render_board(self.board)
                            
                            # Check if player ('B') won
                            winner = self.board.check_winner()
                            if winner is not None:
                                self.renderer.display_winner(winner)
                                self.reset_game()
                                continue  # Skip AI move if game ended
                            
                            # AI's turn (with forced captures)
                            ai_move = self.ai.best_move()  # Get initial AI move
                            while ai_move:  # Loop while AI has valid moves
                                start_ai, end_ai = ai_move
                                ai_status = self.board.move_piece(start_ai, end_ai, 'R')
                                self.renderer.render_board(self.board)  # Update display
                                
                                # Check if AI won
                                winner = self.board.check_winner()
                                if winner is not None:
                                    self.renderer.display_winner(winner)
                                    self.reset_game()
                                    break
                                
                                # Check if AI can capture again from the new position
                                if (ai_status==Status.CAPTURE_AGAIN) and self.board._can_capture_from_position(end_ai[0], end_ai[1], 'R'):
                                    # Restrict next move to this piece's position
                                    ai_move = self.ai.best_move(must_continue_from=end_ai)
                                else:
                                    break  # No more captures, exit loop
                            
                            # Switch back to player ('B') if game hasn't ended
                            if self.board.check_winner() is None:
                                self.to_move = 'B'
                        
                        elif user_status == Status.CAPTURE_FIRST:
                            self.renderer.display_status(Status.CAPTURE_FIRST.value)
                            highlight_moves = []
                        
                        elif user_status == Status.CAPTURE_AGAIN:
                            move_in_progress = False
                            start_pos = None  # Reset to allow player to select same piece again
                            continue  # Skip turn switch
                        
                        elif user_status == Status.INVALID_MOVE:
                            self.renderer.display_status(Status.INVALID_MOVE.value)
                            highlight_moves = []
                        
                        move_in_progress = False
                        start_pos = None


            # Render the board and any selection indicators
            self.renderer.render_board(self.board,highlight_moves)
            
            clock.tick(60)  # Cap at 60 FPS

# Run Game
if __name__ == "__main__":
    game = Game()
    game.game_loop()