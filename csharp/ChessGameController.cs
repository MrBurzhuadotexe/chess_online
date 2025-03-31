using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class ChessGameController : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    private string recMessage;
    private bool wait = false; // Flag to wait for messages

    // Chess game variables
    private string[] currentEnemyPieces;
    private Vector2[] currentEnemyLocations;
    private string[] currentPlayerPieces;
    private Vector2[] currentPlayerLocations;
    private List<string> capturedPiecesEnemy = new List<string>();
    private List<string> capturedPiecesPlayer = new List<string>();
    private string winner = "";
    private bool gameOver = false;
    private int selection = 100; // Reset selection
    private const int fps = 30; // Frames per second

    // Server address
    private string serverAddress = "127.0.0.1";
    private int port = 8080; 

    void Start()
    {
        // Connect to server
        client = new TcpClient(serverAddress, port);
        stream = client.GetStream();
        Debug.Log("Connected to the server.");
        
        // Receive role
        byte[] roleBuffer = new byte[1];
        stream.Read(roleBuffer, 0, 1);
        char role = Convert.ToChar(roleBuffer[0]);

        // Initialize player roles based on received role
        if (role == 'b')
        {
            // Initialize black roles
            currentEnemyPieces = startPlayerPieces; // Set enemy pieces to player
            currentEnemyLocations = startPlayerLocations; // Set enemy locations
            currentPlayerPieces = startEnemyPieces; // Set player pieces to enemy
            currentPlayerLocations = startEnemyLocations; // Set player locations
        }
        else
        {
            // Initialize white roles
            currentEnemyPieces = startEnemyPieces;
            currentEnemyLocations = startEnemyLocations;
            currentPlayerPieces = startPlayerPieces;
            currentPlayerLocations = startPlayerLocations;
        }

        // Start the thread to listen for messages
        Thread receiveThread = new Thread(ReceiveMessages);
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    void Update()
    {
        // Main game loop logic
        if (recMessage != null)
        {
            HandleReceivedMessage();
            recMessage = null; // Reset received message
        }

        // Handle game drawing and logic
        Timer.Tick(fps);
        gl.DrawBoard();
        gl.DrawPieces(currentEnemyImages, currentPlayerImages);
        gl.DrawCaptured();
        gl.DrawCheck();

        if (selection != 100)
        {
            var validMoves = gl.CheckValidMoves();
            gl.DrawValid(validMoves);
        }

        HandleInput();
        if (!string.IsNullOrEmpty(winner))
        {
            gameOver = true;
            gl.DrawGameOver(); // Draw game over message
        }
    }

    void ReceiveMessages()
    {
        while (true)
        {
            byte[] buffer = new byte[1024];
            int bytesRead = stream.Read(buffer, 0, buffer.Length);
            recMessage = Encoding.UTF8.GetString(buffer, 0, bytesRead);
            wait = false; // Reset wait flag when a message is received
        }
    }

    void HandleReceivedMessage()
    {
        if (recMessage == "forfeit")
        {
            winner = "enemy"; // Set winner based on the forfeit
        }
        else
        {
            // Process the received move
            var messageData = JsonConvert.DeserializeObject<object[]>(recMessage);
            int playedFigure = (int)messageData[0];
            Vector2 clickCoords = new Vector2(7 - (float)messageData[1][0], 7 - (float)messageData[1][1]);
            currentEnemyLocations[playedFigure] = clickCoords; // Update enemy piece location

            // Check if an enemy captured a piece
            if (Array.Exists(currentPlayerLocations, location => location == clickCoords))
            {
                int capturedIndex = Array.IndexOf(currentPlayerLocations, clickCoords);
                capturedPiecesEnemy.Add(currentPlayerPieces[capturedIndex]); // Add to captured pieces
                if (currentPlayerPieces[capturedIndex] == "king")
                {
                    winner = "black"; // Black wins if king is captured
                }
                currentPlayerPieces[capturedIndex] = null; // Remove captured piece
                currentPlayerLocations[capturedIndex] = Vector2.zero; // Reset location of captured piece
            }
        }
    }

    void HandleInput()
    {
        // Implement input handling for mouse clicks and key presses
        // Check if the game has ended and key pressed
        if (Input.GetMouseButtonDown(0) && !gameOver && !wait)
        {
            Vector3 mousePosition = Camera.main.ScreenToWorldPoint(Input.mousePosition);
            int xCoord = Mathf.FloorToInt(mousePosition.x / 100);
            int yCoord = Mathf.FloorToInt(mousePosition.y / 100);
            Vector2 clickCoords = new Vector2(xCoord, yCoord);

            // Check for forfeit
            if (clickCoords.x == 8 && clickCoords.y == 8 || clickCoords.x == 9 && clickCoords.y == 8)
            {
                winner = "enemy"; // Set opponent as the winner
                SendMessage("forfeit");
            }

            // If clicking on player piece
            if (Array.Exists(currentPlayerLocations, location => location == clickCoords))
            {
                selection = Array.IndexOf(currentPlayerLocations, clickCoords); // Set selected piece
            }

            // Moving the piece to valid move location
            if (IsMoveValid(clickCoords) && selection != 100)
            {
                currentPlayerLocations[selection] = clickCoords; // Update player piece location
                SendToEnemy(clickCoords);
                selection = 100; // Reset selection
            }
        }

        // Handle Key Input for restarting the game
        if (gameOver && Input.GetKeyDown(KeyCode.Return))
        {
            gameOver = false; // Reset game over flag
            ResetGame(); // Reset game state and pieces
        }
    }

    void SendMessage(string message)
    {
        byte[] messageBytes = Encoding.UTF8.GetBytes(message);
        stream.Write(messageBytes, 0, messageBytes.Length);
    }

    void SendToEnemy(Vector2 clickCoords)
    {
        var message = JsonConvert.SerializeObject(new object[] { selection, clickCoords });
        SendMessage(message); // Send the move message to the server
        wait = true; // Set wait flag to wait for the server response
    }

    bool IsMoveValid(Vector2 clickCoords)
    {
        // Add logic to check if the clicked coordinates are in the valid moves list
        return currentPlayerLocations != null && currentPlayerLocations[selection] != Vector2.zero; // Placeholder
    }

    void ResetGame()
    {
        winner = ""; // Clear winner
        currentEnemyPieces = (string[])startEnemyPieces.Clone();
        currentEnemyLocations = (Vector2[])startEnemyLocations.Clone();
        currentPlayerPieces = (string[])startPlayerPieces.Clone();
        currentPlayerLocations = (Vector2[])startPlayerLocations.Clone();
        capturedPiecesEnemy.Clear(); // Reset captured pieces
        capturedPiecesPlayer.Clear();
        selection = 100; // Reset selection index
    }

    private void OnApplicationQuit()
    {
        // Close the stream and client when the application quits
        if (stream != null) stream.Close();
        if (client != null) client.Close();
    }
}
        
