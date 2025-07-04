# PyRedis - A Redis-like In-Memory Database

This project is a simplified, multi-threaded, in-memory database server built with Python, inspired by Redis. It includes data persistence and can be accessed via a TCP client like `telnet`.

---

### **How to Run**

1.  **Clone the project using the following command in the terminal:**
    ```
    Git clone https://github.com/Deepak-19922001/PyRedis.git
    ```

2.  **Start the Server:**
    * Open a terminal in the project folder and run the following command:
    ```bash
    python main.py
    ```
    * The server will start and listen on `127.0.0.1:6380` by default.

3.  **Connect with a Client:**
    * Open a **new terminal window**.
    * Connect to the server using `telnet`:
    ```bash
    telnet 127.0.0.1 6380
    ```

4.  **Execute Commands:**
    * Once connected, you can type Redis commands directly into the terminal.
    ```
    SET name "deepak"
    GET name
    INCR counter
    KEYS *
    QUIT
    ```

---
