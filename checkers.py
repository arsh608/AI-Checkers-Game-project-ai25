from enum import Enum
import copy

class Status(Enum):
    INVALID_MOVE = 'Invalid Move'
    CAPTURE_FIRST = 'Capture First'
    VALID_MOVE = 'Valid Move'
    CAPTURE_AGAIN = 'Capture Again'
    WAS_CAPTURE_MOVE = 'Was Capture Move'

class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [['_'] * 8 for _ in range(8)]
    
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Black squares
                    if row < 3:
                        self.board[row][col] = 'R'  # Red pieces
                    elif row > 4:
                        self.board[row][col] = 'B'  # Black pieces
                    else:
                        self.board[row][col] = 'X'  # Empty black square

    def __str__(self):
        return '\n'.join(' '.join(row) for row in self.board)
    
    def is_king(self, r, c):
        return self.board[r][c] in ('BK','RK')

    def move_piece(self, start_pos, end_pos, player):
        start_r, start_c = start_pos  # Now matches user_input's (col, row)
        end_r, end_c = end_pos

        # Check if starting cell has the correct piece
        valid_pieces = ('B','BK') if player=='B' else ('R','RK')

        if self.board[start_r][start_c] not in valid_pieces:
            return Status.INVALID_MOVE
        
        # Check if destination is empty
        if self.board[end_r][end_c] != 'X':
            return Status.INVALID_MOVE

        dr = end_r - start_r  
        dc = end_c - start_c 

        # Check move direction (regular pieces can only move forward)
        if not self.is_king(start_r, start_c):
            if (player == 'B' and dr >= 0) or (player == 'R' and dr <= 0): # Direction check (B=up, R=down)
                return Status.INVALID_MOVE  # Wrong direction

         # Simple diagonal move (non-capturing)
        if abs(dr) == 1 and abs(dc) == 1:
            # Only allow simple moves if no captures are available (forced capture rule)
            if self.has_available_captures(player): # Cannot force AI for capture
                return Status.CAPTURE_FIRST  # Must capture instead

            self.board[end_r][end_c] = self.board[start_r][start_c]
            self.board[start_r][start_c] = 'X'
            self.check_promotion(end_r, end_c)  # Promote to king if needed
            return Status.VALID_MOVE
        
        # Capture move (jump over opponent)
        if abs(dr) == 2 and abs(dc) == 2 and self.capture_move(start_pos, end_pos, player):
            # Check for Multi-Jump
            if self._can_capture_from_position(end_r, end_c, player):
                return Status.CAPTURE_AGAIN
        
            return Status.WAS_CAPTURE_MOVE

        return Status.INVALID_MOVE
    
    def capture_move(self, start_pos, end_pos, player):
        start_r, start_c = start_pos
        end_r, end_c = end_pos

        mid_r = (start_r + end_r) // 2
        mid_c = (start_c + end_c) // 2
        
        # Determine the opponent's piece
        opponent_pieces = ('R','RK') if player=='B' else ('B','BK')

        # Check if middle piece is opponent
        if self.board[mid_r][mid_c] not in opponent_pieces:
            return False

        # Perform the capture
        self.board[end_r][end_c] = self.board[start_r][start_c]
        self.board[start_r][start_c] = 'X'
        self.board[mid_r][mid_c] = 'X'
        self.check_promotion(end_r, end_c)  # Promote to king if needed
        return True

    def has_available_captures(self, player):
        """
        Check if the specified player has any available captures.
        Returns True if at least one capture exists, False otherwise.
        """
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                   
                # Skip if the piece doesn't belong to the player
                valid_pieces = ('B','BK') if player=='B' else ('R','RK')

                if self.board[r][c] not in valid_pieces:
                    continue
                
                # Check all possible capture directions
                if self._can_capture_from_position(r, c, player):
                    return True
        return False

    def _can_capture_from_position(self, r, c, player):
        """Helper to check if a piece at (r,c) can capture any opponent."""

        # Define movement directions based on piece type
        king_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        directions = king_directions if self.is_king(r,c) else (
            [(-1, -1), (-1, 1)] if player == 'B' else [(1, -1), (1, 1)]
        )
        
        # Check each direction for a valid capture
        for dr, dc in directions:
            jump_r, jump_c = r + dr, c + dc
            land_r, land_c = r + 2*dr, c + 2*dc
            
            # Check bounds
            if not (0 <= land_r < len(self.board) and 0 <= land_c < len(self.board[land_r])):
                continue

            # Determine the opponent's piece
            opponent_pieces = ('R','RK') if player=='B' else ('B','BK')

            # Check if jump is over an opponent and landing is empty
            if (self.board[jump_r][jump_c] in opponent_pieces and self.board[land_r][land_c] == 'X'):
                return True
            
        return False

    def get_valid_moves(self, r, c):
        """Returns a dictionary of valid moves for the piece at (r, c).
        Format: { (dest_r, dest_c): [(captured_r, captured_c)] }
        If move is not a capture, the list is empty.
        """
        piece = self.board[r][c]
        if piece not in ('B', 'R', 'BK', 'RK'):
            return {}

        player = 'B' if piece.startswith('B') else 'R'
        is_king = self.is_king(r, c)

        moves = {}
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else (
            [(-1, -1), (-1, 1)] if player == 'B' else [(1, -1), (1, 1)]
        )

        opponent_pieces = ('R', 'RK') if player == 'B' else ('B', 'BK')

        for dr, dc in directions:
            # Simple move
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8 and self.board[new_r][new_c] == 'X':
                # Only add if no captures are available (will be filtered later)
                moves[(new_r, new_c)] = []

            # Capture move
            mid_r, mid_c = r + dr, c + dc
            jump_r, jump_c = r + 2 * dr, c + 2 * dc
            if (
                0 <= jump_r < 8 and 0 <= jump_c < 8 and
                self.board[mid_r][mid_c] in opponent_pieces and
                self.board[jump_r][jump_c] == 'X'
            ):
                moves[(jump_r, jump_c)] = [(mid_r, mid_c)]

        # Enforce capture rule: only return capture moves if any exist
        capture_moves = {k: v for k, v in moves.items() if v}
        return capture_moves if capture_moves else moves


    def check_promotion(self, r, c):
        """Promote a piece to king if it reaches the farthest row."""
        piece = self.board[r][c]
        last_row = len(self.board) - 1  # Bottom row (0-indexed)

        if piece == 'B' and r == 0:      # Black reaches top row (promote to BK)
            self.board[r][c] = 'BK'
            return True
        elif piece == 'R' and r == last_row:  # Red reaches bottom row (promote to RK)
            self.board[r][c] = 'RK'
            return True
        return False
    
    def check_winner(self):
        """Check if the game has a winner by counting all pieces (including kings)."""
        black_count = 0
        red_count = 0
        
        for row in self.board:
            for piece in row:
                if piece in ('B','BK'):  # Counts both 'B' and 'BK'
                    black_count += 1
                elif piece in ('R','RK'):  # Counts both 'R' and 'RK'
                    red_count += 1
        
        if black_count == 0:
            return "Red Wins!"  # No black pieces left
        elif red_count == 0:
            return "Black Wins!"  # No red pieces left
        return None  # No winner yet
    
class AI_Algo:
    def __init__(self, board):
        """
        Initializes the AI algorithm with a game board.
        
        Parameters:
        board (object): The board object representing the checkers game state.
        """
        self.board = board
    # def evaluate_checkers(self, player):
    #     pawn_value = 100
    #     king_value = 150

    #     # Weights for different evaluation factors
    #     weights = {
    #         "material": 1.0,
    #         "mobility": 0.3,
    #         "center_control": 0.2,
    #         "promotion_potential": 0.4,
    #         "king_safety": 0.3,
    #         "threats": 0.5,
    #         "multi_jump": 0.4,
    #     }

    #     score = {
    #         "material": 0,
    #         "mobility": 0,
    #         "center_control": 0,
    #         "promotion_potential": 0,
    #         "king_safety": 0,
    #         "threats": 0,
    #         "multi_jump": 0,
    #     }

    #     center_squares = {
    #         (2, 3), (2, 4), (2, 5), (2, 6),
    #         (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
    #         (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
    #         (5, 3), (5, 4), (5, 5), (5, 6)
    #     }

    #     player_pieces, opponent_pieces = (
    #         (('R', 'RK'), ('B', 'BK')) if player == 'R' else (('B', 'BK'), ('R', 'RK'))
    #     )

    #     # Iterate over board
    #     for row in range(8):
    #         for col in range(8):
    #             piece = self.board.board[row][col]

    #             if piece not in player_pieces + opponent_pieces:
    #                 continue

    #             is_king = piece.endswith('K')
    #             is_player = piece in player_pieces
    #             forward_dir = -1 if player == 'B' else 1

    #             # Material
    #             if is_player:
    #                 score["material"] += king_value if is_king else pawn_value
    #             else:
    #                 score["material"] -= king_value if is_king else pawn_value

    #             # Center Control
    #             if (row, col) in center_squares:
    #                 delta = 15 if is_king else 10
    #                 score["center_control"] += delta if is_player else -delta

    #             # Promotion potential
    #             if not is_king:
    #                 prom_row = 0 if player == 'B' else 7
    #                 prom_distance = abs(prom_row - row)
    #                 delta = (7 - prom_distance) * 5
    #                 score["promotion_potential"] += delta if is_player else -delta

    #             # King safety (safe = back rows)
    #             if is_king:
    #                 if (player == 'B' and row == 0) or (player == 'R' and row == 7):
    #                     score["king_safety"] += 15 if is_player else -15

    #             # Mobility
    #             mobility = self.count_legal_moves(row, col, player if is_player else ('B' if player == 'R' else 'R'))
    #             score["mobility"] += mobility * (8 if is_king else 5) if is_player else -mobility * (8 if is_king else 5)

    #             # Capture & multi-jump potential
    #             directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else (
    #                 [(-1, -1), (-1, 1)] if piece in ('B',) else [(1, -1), (1, 1)]
    #             )
    #             opponent_set = set(opponent_pieces if is_player else player_pieces)

    #             jumps = self.find_jump_moves(row, col, opponent_set, directions)
    #             if jumps:
    #                 max_jumps = self.count_continuation_jumps(row, col, opponent_set, directions)
    #                 score["threats"] += (10 if is_player else -10)
    #                 score["multi_jump"] += max_jumps * (10 if is_player else -10)

    #     # Final weighted score
    #     total_score = sum(weights[key] * score[key] for key in score)
    #     return total_score

    def evaluate_checkers(self, player):
        pawn_value = 100
        king_value = 160

        weights = {
            "material": 1.0,
            "mobility": 0.4,
            "center_control": 0.3,
            "promotion_potential": 0.3,
            "king_safety": 0.4,
            "threats": 0.6,
            "multi_jump": 0.5,
            "vulnerability": 0.6,
            "clustering": 0.3,
            "edge_safety": 0.2,
            "tempo": 0.25,
        }

        score = {key: 0 for key in weights}

        center_squares = {(r, c) for r in range(2, 6) for c in range(2, 6)}
        edge_squares = {(r, c) for r in range(8) for c in [0, 7]} | {(0, c) for c in range(8)} | {(7, c) for c in range(8)}

        player_pieces, opponent_pieces = (
            (('R', 'RK'), ('B', 'BK')) if player == 'R' else (('B', 'BK'), ('R', 'RK'))
        )

        opponent = 'B' if player == 'R' else 'R'
        tempo_count = 0

        def in_bounds(r, c):
            return 0 <= r < 8 and 0 <= c < 8

        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if piece not in player_pieces + opponent_pieces:
                    continue

                is_king = piece.endswith('K')
                is_player = piece in player_pieces
                forward_dir = -1 if piece in ('B', 'BK') else 1

                # Material
                base_val = king_value if is_king else pawn_value
                score["material"] += base_val if is_player else -base_val

                # Center Control
                if (row, col) in center_squares:
                    score["center_control"] += (12 if is_king else 8) * (1 if is_player else -1)

                # Edge Safety
                if (row, col) in edge_squares:
                    score["edge_safety"] += 6 * (1 if is_player else -1)

                # Promotion Potential
                if not is_king:
                    target_row = 0 if piece.startswith('B') else 7
                    prom_distance = abs(target_row - row)
                    score["promotion_potential"] += (7 - prom_distance) * 4 * (1 if is_player else -1)

                # King Safety
                if is_king and (row == 0 or row == 7):
                    score["king_safety"] += 15 * (1 if is_player else -1)

                # Mobility
                mobility = self.count_legal_moves(row, col, player if is_player else opponent)
                mobility_weight = 8 if is_king else 5
                score["mobility"] += mobility * mobility_weight * (1 if is_player else -1)

                # Threats and Multi-Jump
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_king else (
                    [(-1, -1), (-1, 1)] if piece.startswith('B') else [(1, -1), (1, 1)]
                )

                enemy_set = set(opponent_pieces if is_player else player_pieces)
                jumps = self.find_jump_moves(row, col, enemy_set, directions)
                if jumps:
                    max_jumps = self.count_continuation_jumps(row, col, enemy_set, directions)
                    score["threats"] += 10 * (1 if is_player else -1)
                    score["multi_jump"] += max_jumps * 10 * (1 if is_player else -1)

                # Vulnerability (if adjacent to opponent and no backup)
                vulnerable = False
                for dr, dc in directions:
                    nr, nc = row + dr, col + dc
                    if in_bounds(nr, nc) and self.board.board[nr][nc] in enemy_set:
                        backup_r, backup_c = row - dr, col - dc
                        if not in_bounds(backup_r, backup_c) or self.board.board[backup_r][backup_c] not in player_pieces:
                            vulnerable = True
                            break
                if vulnerable:
                    score["vulnerability"] -= 15 if is_player else -15

                # Clustering (pieces near each other)
                cluster_count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = row + dr, col + dc
                        if in_bounds(nr, nc) and self.board.board[nr][nc] in player_pieces:
                            cluster_count += 1
                score["clustering"] += cluster_count * (2 if is_player else -2)

                # Tempo (advancing aggressively)
                if not is_king and is_player:
                    tempo_count += (row if player == 'R' else (7 - row))

        # Tempo advantage
        score["tempo"] += tempo_count * 0.5

        # Combine all weighted scores
        total_score = sum(weights[key] * score[key] for key in score)
        return total_score

    # def evaluate_checkers(self, player):
    #     """
    #     Evaluates the board position for the given player.
        
    #     Parameters:
    #     player (str): The player whose position is being evaluated ('R' or 'B').
        
    #     Returns:
    #     float: A score representing the player's advantage in the game based on material, mobility, and center control.
    #     """
    #     material_score = 0
    #     mobility_score = 0
    #     center_control_score = 0

    #     # Define piece values
    #     pawn_value = 100
    #     king_value = 150
        
    #     # Define mobility and center control weights
    #     pawn_mobility_weight = 5
    #     king_mobility_weight = 8  # More mobility weight for kings
    #     pawn_center_weight = 10
    #     king_center_weight = 15  # More control weight for kings
        
    #     # Define center squares (expanded center for checkers)
    #     center_squares = {
    #         (2, 3), (2, 4), (2, 5), (2, 6),
    #         (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
    #         (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
    #         (5, 3), (5, 4), (5, 5), (5, 6)
    #     }
        
    #     # Determine player and opponent pieces
    #     player_pieces, opponent_pieces = (
    #         (('R', 'RK'), ('B', 'BK')) if player == 'R' else (('B', 'BK'), ('R', 'RK'))
    #     )
    #     player_pawn, player_king = player_pieces
    #     opponent_pawn, opponent_king = opponent_pieces

    #     # Iterate through all board positions
    #     for row in range(8):
    #         for col in range(8):
    #             piece = self.board.board[row][col]

    #             # Material evaluation
    #             if piece == player_pawn:
    #                 material_score += pawn_value
    #             elif piece == player_king:
    #                 material_score += king_value
    #             elif piece == opponent_pawn:
    #                 material_score -= pawn_value
    #             elif piece == opponent_king:
    #                 material_score -= king_value
                
    #             # Mobility evaluation for both player & opponent
    #             mobility = self.count_legal_moves(row, col, player) if piece in player_pieces else (
    #                        self.count_legal_moves(row, col, 'B' if player == 'R' else 'R') if piece in opponent_pieces else 0)

    #             if piece == player_pawn:
    #                 mobility_score += mobility * pawn_mobility_weight
    #             elif piece == player_king:
    #                 mobility_score += mobility * king_mobility_weight
    #             elif piece == opponent_pawn:
    #                 mobility_score -= mobility * pawn_mobility_weight
    #             elif piece == opponent_king:
    #                 mobility_score -= mobility * king_mobility_weight
                
    #             # Center control evaluation with different weights
    #             if (row, col) in center_squares:
    #                 if piece == player_pawn:
    #                     center_control_score += pawn_center_weight
    #                 elif piece == player_king:
    #                     center_control_score += king_center_weight
    #                 elif piece == opponent_pawn:
    #                     center_control_score -= pawn_center_weight
    #                 elif piece == opponent_king:
    #                     center_control_score -= king_center_weight
        
    #     # Combine scores with weights
    #     total_score = (
    #         1.0 * material_score + 
    #         0.3 * mobility_score + 
    #         0.2 * center_control_score
    #     )
        
    #     return total_score

    def count_legal_moves(self, row, col, player):
        """
        Counts the total number of legal moves for a piece at a given position.
        
        Parameters:
        row (int): The row index of the piece.
        col (int): The column index of the piece.
        player (str): The player ('R' or 'B') whose moves are being counted.
        
        Returns:
        int: The total number of legal moves possible for the given piece.
        """
        
        # Determine the list of directions
        king_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        directions = king_directions if self.board.is_king(row, col) else (
            [(-1, -1), (-1, 1)] if player=='B' else [(1, -1), (1, 1)]
        )
        
        # Determine the opponent's piece
        opponent_pieces = ('R','RK') if player=='B' else ('B','BK')
        
        jump_moves = self.find_jump_moves(row, col, opponent_pieces, directions)
        
        if jump_moves:
            # Count all possible jump sequences (including multi-jumps)
            total = 0
            for jump_sequence in jump_moves:
                total += self.count_continuation_jumps(jump_sequence[0], jump_sequence[1], opponent_pieces, directions)
            return total
        else:
            # Count simple diagonal moves
            return self.count_simple_moves(row, col, directions)

    def find_jump_moves(self, row, col, opponent_pieces, directions):
        jumps = []
        
        for dr, dc in directions:
            jump_row, jump_col = row + dr, col + dc
            land_row, land_col = row + 2*dr, col + 2*dc
        
            if (0 <= land_row < 8 and 0 <= land_col < 8 and
                self.board.board[land_row][land_col] == 'X' and
                self.board.board[jump_row][jump_col] in opponent_pieces):
                jumps.append((land_row, land_col))
        
        return jumps

    def count_continuation_jumps(self, row, col, opponent_pieces, directions):
        """
        Counts the maximum number of continuation jumps possible from a given position,
        properly handling king pieces that can jump in multiple directions.

        Parameters:
        row (int): The row index of the piece.
        col (int): The column index of the piece.
        opponent_pieces (tuple): The opponent's regular and king pieces.
        directions (list): List of movement directions allowed for the piece.

        Returns:
        int: The maximum number of jumps possible in a sequence.
        """
        max_jumps = 0
        stack = [(row, col, 0, set())]  # (row, col, jump_count, visited)

        while stack:
            current_row, current_col, jumps, visited = stack.pop()
            current_pos = (current_row, current_col)
            
            # Skip if we've already been here with a higher or equal jump count
            if current_pos in visited:
                continue
                
            # Add current position to visited
            new_visited = set(visited)
            new_visited.add(current_pos)
            
            found_jump = False
            
            for dr, dc in directions:
                jump_row, jump_col = current_row + dr, current_col + dc
                land_row, land_col = current_row + 2 * dr, current_col + 2 * dc

                if (0 <= land_row < 8 and 0 <= land_col < 8 and
                    self.board.board[land_row][land_col] == 'X' and
                    self.board.board[jump_row][jump_col] in opponent_pieces and
                    (jump_row, jump_col) not in new_visited):  # Don't jump over same piece twice
                    
                    # Push the new position with incremented jump count
                    stack.append((land_row, land_col, jumps + 1, new_visited))
                    found_jump = True

            # If no more jumps from this position, update max_jumps
            if not found_jump:
                max_jumps = max(max_jumps, jumps)
        
        return max_jumps if max_jumps > 0 else 1

    def count_simple_moves(self, row, col, directions):
        """
        Finds simple diagonal moves for a piece when no jumps are available.
        
        Parameters:
        row (int): The row index of the piece.
        col (int): The column index of the piece.
        directions (list): List of movement directions allowed for the piece.
        
        Returns:
        int: The total number of simple diagonal moves possible.
        """
        total_moves = 0
        for dr, dc in directions:
            land_row, land_col = row + dr, col + dc
        
            if (0 <= land_row < 8 and 0 <= land_col < 8 and
                self.board.board[land_row][land_col] == 'X'):
                total_moves += 1

        return total_moves


    def get_legal_moves(self):
        legal_moves = [] # [[(start_pos),(end)]]
        opponent_pieces = ('B','BK')

        for r in range(8):
            for c in range(8):
                if self.board.board[r][c] in ('R', 'RK'): #  AI
                    # Determine the list of directions
                    king_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                    directions = king_directions if self.board.is_king(r, c) else [(1, -1), (1, 1)]

                    jump_moves = self.find_jump_moves(r, c, opponent_pieces, directions)
                    if jump_moves:
                        for jumps in jump_moves:
                            legal_moves.append([(r,c), jumps])
                    else:
                        simple_moves = self.get_simple_moves(r, c, directions)
                        
                        if simple_moves:
                            for moves in simple_moves:
                                legal_moves.append([(r,c), moves])
                    
        return legal_moves
                
    def get_simple_moves(self, r, c, directions):
        simple_moves = []
        for dr, dc in directions:
            land_row, land_col = r + dr, c + dc
        
            if (0 <= land_row < 8 and 0 <= land_col < 8 and
                self.board.board[land_row][land_col] == 'X'):
                simple_moves.append((land_row, land_col))

        return simple_moves

    def minimax(self, depth, is_maximizing, alpha=-float('inf'), beta=float('inf')):
        if depth == 0 or self.board.check_winner() is not None:
            return self.evaluate_checkers('R')  # Uses self.board

        legal_moves = self.get_legal_moves()  # Uses self.board
        
        if is_maximizing:
            max_eval = -float('inf')
            for move in legal_moves:
                board_copy = copy.deepcopy(self.board)
                self.apply_move_to_board(move, board_copy)
                eval_score = self.minimax(depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board_copy = copy.deepcopy(self.board)
                self.apply_move_to_board(move, board_copy)
                eval_score = self.minimax(depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
            
    def best_move(self, must_continue_from=None):
        legal_moves = self.get_legal_moves()

        if must_continue_from:
            legal_moves = [move for move in legal_moves if move[0] == must_continue_from]

        if not legal_moves or self.board.check_winner() is not None:
            return self.evaluate_checkers('R')

        next_move = None
        best_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        for move in legal_moves:
            board_copy = copy.deepcopy(self.board)
            self.apply_move_to_board(move, board_copy)
            original_board = self.board  # Save reference
            self.board = board_copy  # Temporarily replace
            score = self.minimax(depth=3, is_maximizing=False, alpha=alpha, beta=beta)
            self.board = original_board  # Restore
            
            if score > best_score:
                best_score = score
                next_move = move
            
            alpha = max(alpha, score)
            if beta <= alpha:
                break  # Beta cutoff

        return next_move

    def apply_move_to_board(self, move, board):
        """Apply the move to the given board (modifies the board in place)."""
        start_pos, end_pos = move
        board.board[end_pos[0]][end_pos[1]] = board.board[start_pos[0]][start_pos[1]]
        board.board[start_pos[0]][start_pos[1]] = 'X'

        # Handle jump move
        if abs(start_pos[0] - end_pos[0]) == 2:
            mid_row = (start_pos[0] + end_pos[0]) // 2
            mid_col = (start_pos[1] + end_pos[1]) // 2
            board.board[mid_row][mid_col] = 'X'

        # Handle King Promotion
        if not board.is_king(end_pos[0], end_pos[1]):
            if board.board[end_pos[0]][end_pos[1]] == 'R' and end_pos[0] == 7:
                board.board[end_pos[0]][end_pos[1]] = 'RK'
            elif board.board[end_pos[0]][end_pos[1]] == 'B' and end_pos[0] == 0:
                board.board[end_pos[0]][end_pos[1]] = 'BK'