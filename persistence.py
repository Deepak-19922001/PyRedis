import json
from collections import deque

def save_to_disk(filename, db_instance):
    with db_instance._lock:
        print(f"INFO: Saving to database: {filename}...")
        serializable_data = {}
        for k, v in db_instance._data.items():
            serializable_data[k] = list(v) if isinstance(v, deque) else v
        try:
            with open(filename, "w") as f:
                json.dump({
                    'data': serializable_data,
                    'expirations': db_instance._expirations
                }, f)
            print("INFO: Saved successfully.")
        except IOError as e:
            print(f"ERROR: Failed to save to database: {e}")

def load_from_disk(filename, db_instance):
    try:
        with open(filename, "r") as f:
            persisted_state = json.load(f)
            loaded_data = persisted_state.get('data', {})
            with db_instance._lock:
                for k, v in loaded_data.items():
                    db_instance._data[k] = deque(v) if isinstance(v, list) else v
                db_instance._expirations = persisted_state.get('expirations', {})
                print(f"INFO: Database loaded from {filename}.")
    except FileNotFoundError:
        print(f"INFO: Database file {filename} not found.")
    except (json.JSONDecodeError, TypeError) as e:
        print(f"ERROR: Failed to load database from {filename}: {e}")