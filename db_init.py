import sqlite3

def init_users_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # 检查 total_tokens 列是否存在
    c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'total_tokens' not in columns:
        # 如果 total_tokens 列不存在，添加它
        c.execute("ALTER TABLE users ADD COLUMN total_tokens INTEGER DEFAULT 0")
        print("Added total_tokens column to users table")
    
    # 创建用户表（如果不存在）
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  password TEXT,
                  total_tokens INTEGER DEFAULT 0)''')
    
    conn.commit()
    conn.close()

def init_chat_history_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  timestamp TEXT,
                  role TEXT,
                  content TEXT)''')
    conn.commit()
    conn.close()

def init_assistants_db():
    conn = sqlite3.connect('assistants.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assistants
                 (id TEXT PRIMARY KEY,
                  name TEXT,
                  instructions TEXT,
                  model TEXT)''')
    conn.commit()
    conn.close()

def init_all_dbs():
    init_users_db()
    init_chat_history_db()
    init_assistants_db()

if __name__ == "__main__":
    init_all_dbs()
