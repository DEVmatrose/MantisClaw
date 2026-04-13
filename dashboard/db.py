import aiosqlite
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chats.db"


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    return db


async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id          TEXT PRIMARY KEY,
            title       TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL,
            system_prompt TEXT,
            model       TEXT,
            metadata    TEXT
        );

        CREATE TABLE IF NOT EXISTS messages (
            id              TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role            TEXT NOT NULL,
            content         TEXT NOT NULL,
            created_at      TEXT NOT NULL,
            tokens_used     INTEGER,
            model           TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conv
            ON messages(conversation_id, created_at);
    """)
    await db.commit()
    await db.close()


async def create_conversation(title: str = "", model: str = "", system_prompt: str = "") -> dict:
    db = await get_db()
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    if not title:
        title = f"Chat {now[:16]}"
    await db.execute(
        "INSERT INTO conversations (id, title, created_at, updated_at, model, system_prompt) VALUES (?,?,?,?,?,?)",
        (conv_id, title, now, now, model, system_prompt),
    )
    await db.commit()
    await db.close()
    return {"id": conv_id, "title": title, "created_at": now, "updated_at": now, "model": model}


async def list_conversations() -> list[dict]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT id, title, created_at, updated_at, model FROM conversations ORDER BY updated_at DESC"
    )
    await db.close()
    return [dict(r) for r in rows]


async def get_conversation(conv_id: str) -> dict | None:
    db = await get_db()
    row = await db.execute_fetchall(
        "SELECT * FROM conversations WHERE id = ?", (conv_id,)
    )
    await db.close()
    return dict(row[0]) if row else None


async def get_messages(conv_id: str) -> list[dict]:
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
        (conv_id,),
    )
    await db.close()
    return [dict(r) for r in rows]


async def add_message(conv_id: str, role: str, content: str, model: str = "", tokens: int = 0) -> dict:
    db = await get_db()
    msg_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    await db.execute(
        "INSERT INTO messages (id, conversation_id, role, content, created_at, tokens_used, model) VALUES (?,?,?,?,?,?,?)",
        (msg_id, conv_id, role, content, now, tokens, model),
    )
    await db.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id)
    )
    await db.commit()
    await db.close()
    return {"id": msg_id, "role": role, "content": content, "created_at": now}


async def delete_conversation(conv_id: str):
    db = await get_db()
    await db.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
    await db.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    await db.commit()
    await db.close()
