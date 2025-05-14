import psycopg2
from psycopg2.extras import execute_values
import numpy as np
from datetime import datetime
from config import DB_CONFIG

def get_db_connection():
    """Veritabanı bağlantısı oluşturur"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Veritabanı tablolarını oluşturur"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # pgvector uzantısını etkinleştir
        cur.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        
        # Konuşma geçmişi tablosu
        cur.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255),
            model_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            title VARCHAR(255)
        );''')
        
        # Mesajlar tablosu
        cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id),
            role VARCHAR(50),
            content TEXT,
            embedding vector(1536),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''')
        
        # Dosya içerikleri tablosu
        cur.execute('''
        CREATE TABLE IF NOT EXISTS file_contents (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255),
            content TEXT,
            embedding vector(1536),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''')
        
        conn.commit()
    except Exception as e:
        print(f"Veritabanı başlatma hatası: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def save_conversation(user_id: str, model_name: str, title: str = None) -> int:
    """Yeni bir konuşma kaydeder ve ID'sini döndürür"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO conversations (user_id, model_name, title) VALUES (%s, %s, %s) RETURNING id;',
            (user_id, model_name, title)
        )
        conversation_id = cur.fetchone()[0]
        conn.commit()
        return conversation_id
    finally:
        cur.close()
        conn.close()

def save_message(conversation_id: int, role: str, content: str, embedding: list = None):
    """Mesajı kaydeder"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO messages (conversation_id, role, content, embedding) VALUES (%s, %s, %s, %s);',
            (conversation_id, role, content, embedding)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def save_file_content(filename: str, content: str, embedding: list = None):
    """Dosya içeriğini kaydeder"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO file_contents (filename, content, embedding) VALUES (%s, %s, %s);',
            (filename, content, embedding)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_conversation_history(conversation_id: int):
    """Konuşma geçmişini getirir"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY created_at;',
            (conversation_id,)
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def search_similar_content(query_embedding: list, limit: int = 5):
    """Benzer içerikleri arar"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Mesajlarda ara
        cur.execute('''
            SELECT content, embedding <-> %s as distance
            FROM messages
            WHERE embedding IS NOT NULL
            UNION ALL
            SELECT content, embedding <-> %s as distance
            FROM file_contents
            WHERE embedding IS NOT NULL
            ORDER BY distance
            LIMIT %s;
        ''', (query_embedding, query_embedding, limit))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close() 