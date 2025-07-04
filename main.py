import argparse
import sys

from database import PyRedisDB
from persistence import load_from_disk, save_to_disk
from server import Server


def main():
    parser = argparse.ArgumentParser(description="A Redis-like in-memory database server.")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind the server to.')
    parser.add_argument('--port', type=int, default=6380, help='Port to listen on.')
    parser.add_argument('--db-file', type=str, default='pyredis.db.json', help='File to persist the database.')
    args = parser.parse_args()

    db = PyRedisDB()
    load_from_disk(args.db_file, db)
    server = Server(args.host, args.port, db)
    try:
        server.start()
    finally:
        save_to_disk(args.db_file, db)
        server.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()

