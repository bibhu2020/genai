import sqlite3

def setup_db():
    # Connect to SQLite (or create it)
    conn = sqlite3.connect('/home/azureuser/projects/srescripts/pocs/genai/_data/chat_history.db')
    c = conn.cursor()

    # Create a table for storing chat history
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Call this to initialize the database
setup_db()
