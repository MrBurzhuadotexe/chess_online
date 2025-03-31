using System.Collections.Generic;
using UnityEngine;


public class ChessGame : MonoBehaviour
{
    private const int WIDTH = 1000;
    private const int HEIGHT = 900;

    // Initialize chess pieces and their starting positions
    private string[] startEnemyPieces = { "rook", "knight", "bishop", "king", "queen", "bishop", "knight", "rook", 
                                          "pawn", "pawn", "pawn", "pawn", "pawn", "pawn", "pawn", "pawn" };

    private Vector2[] startEnemyLocations = { new Vector2(7, 0), new Vector2(6, 0), new Vector2(5, 0), new Vector2(4, 0),
                                              new Vector2(3, 0), new Vector2(2, 0), new Vector2(1, 0), new Vector2(0, 0),
                                              new Vector2(7, 1), new Vector2(6, 1), new Vector2(5, 1), new Vector2(4, 1),
                                              new Vector2(3, 1), new Vector2(2, 1), new Vector2(1, 1), new Vector2(0, 1) };

    private Vector2[] startPlayerLocations = { new Vector2(0, 7), new Vector2(1, 7), new Vector2(2, 7), new Vector2(3, 7),
                                               new Vector2(4, 7), new Vector2(5, 7), new Vector2(6, 7), new Vector2(7, 7),
                                               new Vector2(0, 6), new Vector2(1, 6), new Vector2(2, 6), new Vector2(3, 6),
                                               new Vector2(4, 6), new Vector2(5, 6), new Vector2(6, 6), new Vector2(7, 6) };

    private string[] startPlayerPieces = { "rook", "knight", "bishop", "king", "queen", "bishop", "knight", "rook", 
                                            "pawn", "pawn", "pawn", "pawn", "pawn", "pawn", "pawn", "pawn" };
    // Reference to the game objects
    public GameObject[] enemyImages;
    public GameObject[] playerImages;

    // Game state variables
    private Vector2[] currentEnemyLocations;
    private Vector2[] currentPlayerLocations;
    private string[] currentEnemyPieces;
    private string[] currentPlayerPieces;
    private List<string> capturedPiecesEnemy = new List<string>();
    private List<string> capturedPiecesPlayer = new List<string>();
    private int selection = -1; // Index of selected piece (initially none)
    private List<Vector2[]> playerOptions = new List<Vector2[]>(); // Valid move options for selected piece

    private void OnGUI()
    {
        DrawBoard();
        DrawPieces();
        DrawCaptured();
        if (IsKingInCheck())
        {
            DrawCheck();
        }
        if (IsGameOver())
        {
            DrawGameOver();
        }
    }

    void LoadImages()
    {
        // Load images as Sprites (you need to have them in the Resources folder or similar in Unity)
        blackQueen = Resources.Load<Sprite>("assets/images/black queen");
        blackKing = Resources.Load<Sprite>("assets/images/black king");
        blackRook = Resources.Load<Sprite>("assets/images/black rook");
        blackBishop = Resources.Load<Sprite>("assets/images/black bishop");
        blackKnight = Resources.Load<Sprite>("assets/images/black knight");
        blackPawn = Resources.Load<Sprite>("assets/images/black pawn");

        whiteQueen = Resources.Load<Sprite>("assets/images/white queen");
        whiteKing = Resources.Load<Sprite>("assets/images/white king");
        whiteRook = Resources.Load<Sprite>("assets/images/white rook");
        whiteBishop = Resources.Load<Sprite>("assets/images/white bishop");
        whiteKnight = Resources.Load<Sprite>("assets/images/white knight");
        whitePawn = Resources.Load<Sprite>("assets/images/white pawn");
    }

    void DrawBoard()
    {
        for (int i = 0; i < 32; i++)
        {
            int column = i % 4;
            int row = i / 4;
            // Draw board squares
            Color squareColor = (row % 2 == 0) ? Color.lightGray : Color.gray;
            GUI.backgroundColor = squareColor;
            GUI.Box(new Rect(600 - (column * 200), row * 100, 100, 100), GUIContent.none);
        }

        // Draw the bottom panel
        GUI.backgroundColor = Color.gray;
        GUI.Box(new Rect(0, 800, 1000, 100), GUIContent.none);
        GUI.backgroundColor = Color.black;
        GUI.Box(new Rect(0, 800, 1000, 100), GUIContent.none);
        GUI.Box(new Rect(800, 0, 200, 900), GUIContent.none);
        
        // Game status
        string[] statusText = {
            "White: Select a Piece to Move!",
            "White: Select a Destination!",
            "Black: Select a Piece to Move!",
            "Black: Select a Destination!"
        };
        
        // Draw grid lines
        for (int i = 0; i < 9; i++)
        {
            DrawLine(new Vector2(0, 100 * i), new Vector2(800, 100 * i)); // Horizontal
            DrawLine(new Vector2(100 * i, 0), new Vector2(100 * i, 800)); // Vertical
        }
        GUI.Label(new Rect(810, 830, 100, 20), "FORFEIT");
    }

    void DrawLine(Vector2 start, Vector2 end)
    {
        GUI.color = Color.black;
        UnityEngine.Graphics.DrawLine(start, end);
    }

    void DrawPieces()
    {
        // Draw enemy pieces
        for (int i = 0; i < currentEnemyPieces.Length; i++)
        {
            int index = System.Array.IndexOf(pieceList, currentEnemyPieces[i]);
            Vector2 position = currentEnemyLocations[i];
            GameObject pieceImage = enemyImages[index];
            pieceImage.transform.position = new Vector2(position.x * 100 + (currentEnemyPieces[i] == "pawn" ? 22 : 10),
                                                          position.y * 100 + (currentEnemyPieces[i] == "pawn" ? 30 : 10));
        }

        // Draw player pieces
        for (int i = 0; i < currentPlayerPieces.Length; i++)
        {
            int index = System.Array.IndexOf(pieceList, currentPlayerPieces[i]);
            Vector2 position = currentPlayerLocations[i];
            GameObject pieceImage = playerImages[index];
            pieceImage.transform.position = new Vector2(position.x * 100 + (currentPlayerPieces[i] == "pawn" ? 22 : 10),
                                                          position.y * 100 + (currentPlayerPieces[i] == "pawn" ? 30 : 10));

            // Draw rectangle highlighting selected piece
            if (selection == i)
            {
                DrawHighlight(new Vector2(currentPlayerLocations[i].x * 100 + 1, currentPlayerLocations[i].y * 100 + 1));
            }
        }
    }

    void DrawHighlight(Vector2 position)
    {
        GUI.color = Color.blue;
        GUI.Box(new Rect(position.x, position.y, 100, 100), GUIContent.none);
    }

    void DrawCaptured()
    {
        // Draw captured pieces for the enemy
        for (int i = 0; i < capturedPiecesEnemy.Count; i++)
        {
            string capturedPiece = capturedPiecesEnemy[i];
            int index = System.Array
// Get the index of the captured piece
            int index = System.Array.IndexOf(pieceList, capturedPiece);
            // Draw the captured piece for the enemy
            GUI.DrawTexture(new Rect(825, 5 + 50 * i, 45, 45), smallBlackImages[index]);
        }

        // Draw captured pieces for the player
        for (int i = 0; i < capturedPiecesPlayer.Count; i++)
        {
            string capturedPiece = capturedPiecesPlayer[i];
            int index = System.Array.IndexOf(pieceList, capturedPiece);
            // Draw the captured piece for the player
            GUI.DrawTexture(new Rect(925, 5 + 50 * i, 45, 45), smallWhiteImages[index]);
        }
    }

    // Draw a flashing rectangle around the king if it is in check
    void DrawCheck()
    {
        if (System.Array.Exists(currentEnemyPieces, piece => piece == "king"))
        {
            int kingIndex = System.Array.IndexOf(currentEnemyPieces, "king");
            Vector2 kingLocation = currentEnemyLocations[kingIndex];
            for (int i = 0; i < playerOptions.Count; i++)
            {
                if (playerOptions[i].Contains(kingLocation))
                {
                    GUI.color = Color.red;
                    GUI.Box(new Rect(kingLocation.x * 100 + 1, kingLocation.y * 100 + 1, 100, 100), GUIContent.none);
                }
            }
        }
    }

    // Draw the game over message
    void DrawGameOver()
    {
        GUI.color = Color.black;
        GUI.Box(new Rect(200, 200, 400, 70), GUIContent.none);
        GUI.Label(new Rect(210, 210, 400, 30), $"{winner} won the game!", "label");
        GUI.Label(new Rect(210, 240, 400, 30), "Press ENTER to Restart!", "label");
    }

    // Check if the king of the player is in check
    bool IsKingInCheck()
    {
        // Logic to check if the king is in check
        // Use similar logic to the original Python implementation
        // Return true if king is in check, else return false
        return false; // Placeholder
    }

    // Check if the game is over
    bool IsGameOver()
    {
        // Logic to determine if the game is over
        // This can be based on the state of the game, e.g., if a king has been captured
        return false; // Placeholder
    }

    // Check possible moves for a piece
    List<Vector2> CheckOptions(string[] pieces, Vector2[] locations)
    {
        List<Vector2> allMoves = new List<Vector2>(); // List of all moves
        for (int i = 0; i < pieces.Length; i++)
        {
            Vector2 location = locations[i];
            string piece = pieces[i];

            List<Vector2> movesList = new List<Vector2>();
            switch (piece)
            {
                case "pawn":
                    movesList = CheckPawn(location);
                    break;
                case "rook":
                    movesList = CheckRook(location);
                    break;
                case "knight":
                    movesList = CheckKnight(location);
                    break;
                case "bishop":
                    movesList = CheckBishop(location);
                    break;
                case "queen":
                    movesList = CheckQueen(location);
                    break;
                case "king":
                    movesList = CheckKing(location);
                    break;
            }
            allMoves.AddRange(movesList); // Add moves to all moves list
        }
        return allMoves; // Return all possible moves
    }

    List<Vector2> CheckQueen(Vector2 position)
    {
        List<Vector2> movesList = new List<Vector2>();
        movesList.AddRange(CheckBishop(position));
        movesList.AddRange(CheckRook(position));
        return movesList;
    }

    List<Vector2> CheckBishop(Vector2 position)
    {
        List<Vector2> movesList = new List<Vector2>();
        Vector2[] directions = { new Vector2(1, -1), new Vector2(-1, -1), new Vector2(1, 1), new Vector2(-1, 1) };

        foreach (var direction in directions)
        {
            for (int chain = 1; chain < 8; chain++)
            {
                Vector2 target = position + (direction * chain);
                if (IsValidMove(target))
                {
                    movesList.Add(target);
                    if (IsEnemyPiece(target)) break; // Stop if an enemy piece is found
                }
                else
                {
                    break; // Stop if friend piece or out of bounds
                }
            }
        }
        return movesList;
    }
 List<Vector2> CheckRook(Vector2 position)
    {
        List<Vector2> movesList = new List<Vector2>();
        Vector2[] directions = { Vector2.up, Vector2.down, Vector2.left, Vector2.right };

        foreach (var direction in directions)
        {
            for (int chain = 1; chain < 8; chain++)
            {
                Vector2 target = position + (direction * chain);
                if (IsValidMove(target))
                {
                    movesList.Add(target);
                    if (IsEnemyPiece(target)) break; // Stop if an enemy piece is found
                }
                else
                {
                    break; // Stop if friend piece or out of bounds
                }
            }
        }
        return movesList;
    }

    List<Vector2> CheckKnight(Vector2 position)
    {
        List<Vector2> movesList = new List<Vector2>();
        Vector2[] knightMoves = { new Vector2(1, 2), new Vector2(1, -2), new Vector2(2, 1), new Vector2(2, -1),
                                  new Vector2(-1, 2), new Vector2(-1, -2), new Vector2(-2, 1), new Vector2(-2, -1) };

        foreach (var move in knightMoves)
        {
            Vector2 target = position + move;
            if (IsValidMove(target))
            {
                movesList.Add(target); // Valid knight move
            }
        }
        return movesList;
    }

    List<Vector2> CheckKing(Vector2 position)
    {
        List<Vector2> movesList = new List<Vector2>();
        Vector2[] targets = { new Vector2(1, 0), new Vector2(1, 1), new Vector2(1, -1), new Vector2(-1, 0), 
                              new Vector2(-1, 1), new Vector2(-1, -1), new Vector2(0, 1), new Vector2(0, -1) };
        foreach (var target in targets)
        {
            Vector2 potentialMove = position + target;
            if (IsValidMove(potentialMove))
            {
                movesList.Add(potentialMove); // Valid king move
            }
        }
        return movesList;
    }

    List<Vector2> CheckPawn(Vector2 position)
    {
        List<Vector2> movesList = new List<Vector2>();
        
        // Move forward
        Vector2 forward = position + new Vector2(0, -1);
        if (IsValidMove(forward))
        {
            movesList.Add(forward); // Single step forward
            // Check for double step from start position
            if (position.y == 6) // Assuming last row is 6 for White
            {
                Vector2 doubleForward = position + new Vector2(0, -2);
                if (IsValidMove(doubleForward))
                    movesList.Add(doubleForward); // Double step forward
            }
        }

        // Capture moves
        Vector2 captureRight = position + new Vector2(1, -1);
        Vector2 captureLeft = position + new Vector2(-1, -1);
        if (IsEnemyPiece(captureRight))
            movesList.Add(captureRight); // Capture right
        if (IsEnemyPiece(captureLeft))
            movesList.Add(captureLeft); // Capture left

        return movesList;
    }

    // Helper functions to validate moves
    bool IsValidMove(Vector2 position)
    {
        return position.x >= 0 && position.x <= 7 && position.y >= 0 && position.y <= 7 &&
               !IsFriendPiece(position);
    }

    bool IsEnemyPiece(Vector2 position)
    {
        return System.Array.Exists(currentEnemyLocations, loc => loc == position);
    }

    bool IsFriendPiece(Vector2 position)
    {
        return System.Array.Exists(currentPlayerLocations, loc => loc == position);
    }

    // Sample message to indicate game over status
    public void SetGameOver(string winner)
    {
        // Implement logic to end the game and display the winner
        this.winner = winner;
        gameOver = true;
    }
}
