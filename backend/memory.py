import sqlite3
import os


# --------------------------------------------------
# Database configuration
# --------------------------------------------------

DATABASE_DIR = "database"
DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "memory.db"
)


# --------------------------------------------------
# Get database connection
# --------------------------------------------------

def get_connection():
    os.makedirs(DATABASE_DIR, exist_ok=True)

    return sqlite3.connect(DATABASE_PATH)


# --------------------------------------------------
# Initialize memory database
# --------------------------------------------------

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# Save memory
# --------------------------------------------------

def save_memory(key, value):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO memories (key, value)
        VALUES (?, ?)
        ON CONFLICT(key)
        DO UPDATE SET
            value = excluded.value,
            updated_at = CURRENT_TIMESTAMP
    """, (key, value))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "key": key,
        "value": value
    }


# --------------------------------------------------
# Get memory
# --------------------------------------------------

def get_memory(key):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT key, value, created_at, updated_at
        FROM memories
        WHERE key = ?
    """, (key,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return {
            "success": False,
            "message": f"No memory found for key: {key}"
        }

    return {
        "success": True,
        "key": row[0],
        "value": row[1],
        "created_at": row[2],
        "updated_at": row[3]
    }


# --------------------------------------------------
# List all memories
# --------------------------------------------------

def list_memories():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, key, value, created_at, updated_at
        FROM memories
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    memories = []

    for row in rows:

        memories.append({
            "id": row[0],
            "key": row[1],
            "value": row[2],
            "created_at": row[3],
            "updated_at": row[4]
        })

    return memories


# --------------------------------------------------
# Delete memory
# --------------------------------------------------

def delete_memory(key):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE key = ?
    """, (key,))

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    if deleted == 0:
        return {
            "success": False,
            "message": f"No memory found for key: {key}"
        }

    return {
        "success": True,
        "message": f"Memory '{key}' deleted."
    }


# --------------------------------------------------
# Initialize database when module loads
# --------------------------------------------------

initialize_database()


# --------------------------------------------------
# Test memory system
# --------------------------------------------------

if __name__ == "__main__":

    print("Testing TaskPilot memory...\n")

    # Save
    result = save_memory(
        "interview",
        "Python interview tomorrow"
    )

    print("Saved:")
    print(result)

    # Get
    result = get_memory("interview")

    print("\nRetrieved:")
    print(result)

    # List
    result = list_memories()

    print("\nAll memories:")

    for memory in result:
        print(memory)

    # Update
    print("\nUpdating memory...")

    result = save_memory(
        "interview",
        "Python interview tomorrow at 10 AM"
    )

    print(result)

    # Retrieve updated memory
    print("\nUpdated memory:")

    print(get_memory("interview"))