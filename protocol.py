def process_command(request_str, db):
    if not request_str:
        return None
    parts = request_str.split()
    command = parts[0].upper()
    args = parts[1:]
    response = None
    try:
        if command == "PING":
            response = "PONG"
        elif command == "GET" and len(args) == 1:
            response = db.get(args[0])
        elif command == "SET" and len(args) >= 2:
            expiry = None
            if len(args) == 4 and args[2].upper() == 'EX':
                expiry = int(args[3])
            response = db.set(args[0], args[1], expiry_seconds=expiry)
        elif command == "DEL" and len(args) >= 1:
            response = db.delete(args)
        elif command == "EXISTS" and len(args) >= 1:
            response = db.exists(args)
        elif command == "INCR" and len(args) == 1:
            response = db.incr_decr(args[0], 1)
        elif command == "DECR" and len(args) == 1:
            response = db.incr_decr(args[0], -1)
        elif command == "KEYS" and len(args) == 1:
            response = db.keys(args[0])
        elif command == "FLUSHDB" and len(args) == 0:
            response = db.flushdb()
        elif command == "HSET" and len(args) == 3:
            response = db.hset(args[0], args[1], args[2])
        elif command == "HGET" and len(args) == 2:
            response = db.hget(args[0], args[1])
        elif command == "LPUSH" and len(args) >= 2:
            response = db.lpush(args[0], *args[1:])
        elif command == "RPUSH" and len(args) >= 2:
            response = db.rpush(args[0], *args[1:])
        elif command == "LPOP" and len(args) == 1:
            response = db.lpop(args[0])
        elif command == "RPOP" and len(args) == 1:
            response = db.rpop(args[0])
        elif command == "LRANGE" and len(args) == 3:
            response = db.lrange(args[0], int(args[1]), int(args[2]))
        elif command == "RRANGE" and len(args) == 3:
            response = db.rrange(args[0], int(args[1]), int(args[2]))
        elif command == "QUIT":
            response = "QUIT"
        else:
            response = f"ERR: Unknown or wrong number of arguments for '{command}'"
    except (ValueError, IndexError) as e:
        response = f"ERR: Invalid arguments for command {command}: {e}"

    return format_response(response)


def format_response(response_data):
    if response_data is None:
        return b"(nil)\n"
    if response_data == "QUIT":
        return b"QUIT"  # Special signal
    if isinstance(response_data, str) and response_data.startswith("ERR"):
        return f"({response_data})\n".encode('utf-8')
    if isinstance(response_data, str):
        return f"{response_data}\n".encode('utf-8')
    if isinstance(response_data, int):
        return f"(integer) {response_data}\n".encode('utf-8')
    if isinstance(response_data, list):
        resp_str = f"*{len(response_data)}\n"
        for item in response_data:
            item_str = str(item)
            resp_str += f"${len(item_str)}\r\n{item_str}\r\n"
        return resp_str.encode('utf-8')
    return f"{response_data}\n".encode('utf-8')
