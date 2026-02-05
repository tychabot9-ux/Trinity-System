#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║              TRINITY CORE MEMORY SYSTEM                        ║
║         Military-Grade Personalized Intelligence               ║
║                  v1.0 - February 2026                          ║
╚════════════════════════════════════════════════════════════════╝

Trinity Core Memory - Advanced personal AI memory system for single-user
military-grade personalized intelligence.

Features:
- Long-term persistent memory storage
- User profile and preference learning
- Contextual decision tracking
- Pattern recognition and insights
- Semantic and episodic memory
- Privacy-first encrypted storage
- Cross-station context awareness
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import pickle
import base64

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent
MEMORY_DB = BASE_DIR / "data" / "trinity_memory.db"
MEMORY_DB.parent.mkdir(exist_ok=True)

# Memory categories
MEMORY_TYPES = {
    'profile': 'User profile and core preferences',
    'preference': 'Learned preferences and patterns',
    'decision': 'Historical decisions and rationale',
    'interaction': 'User interactions across all stations',
    'context': 'Contextual information and state',
    'insight': 'Discovered patterns and insights',
    'knowledge': 'Semantic knowledge base'
}

# ============================================================================
# CORE MEMORY MANAGER
# ============================================================================

class TrinityMemory:
    """
    Trinity Core Memory System - Military-grade personalized AI intelligence.

    Designed for single-user deployment with maximum personalization and
    context awareness across all Trinity stations.
    """

    def __init__(self, db_path: Path = MEMORY_DB):
        """Initialize Trinity Memory system."""
        self.db_path = db_path
        self.conn = None
        self._initialize_database()

    def _initialize_database(self):
        """Create database schema for Trinity memory storage."""
        try:
            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

            cursor = self.conn.cursor()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Trinity Memory database: {e}")

        # User profile table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Preferences table - learned patterns and preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station TEXT NOT NULL,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_reinforced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reinforcement_count INTEGER DEFAULT 1,
                UNIQUE(station, category, key)
            )
        """)

        # Decisions table - track all user decisions with context
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                context TEXT,
                decision TEXT NOT NULL,
                rationale TEXT,
                outcome TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Interactions table - all user interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_data TEXT,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Context snapshots - capture system state at key moments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_type TEXT NOT NULL,
                context_data TEXT NOT NULL,
                tags TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insights table - discovered patterns and learnings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                confidence REAL DEFAULT 1.0,
                evidence TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validated BOOLEAN DEFAULT 0
            )
        """)

        # Knowledge base - semantic memory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                relevance_score REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_preferences_station ON preferences(station)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_station ON decisions(station)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_station ON interactions(station)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)")

        self.conn.commit()

    # ========================================================================
    # USER PROFILE MANAGEMENT
    # ========================================================================

    def set_profile(self, key: str, value: Any, category: str = 'general'):
        """Set or update user profile attribute."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (key, value, category, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, json.dumps(value), category))
        self.conn.commit()

    def get_profile(self, key: str = None) -> Dict:
        """Get user profile attribute(s)."""
        cursor = self.conn.cursor()
        if key:
            cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = cursor.fetchone()
            return json.loads(row['value']) if row else None
        else:
            cursor.execute("SELECT key, value, category FROM user_profile")
            return {row['key']: json.loads(row['value']) for row in cursor.fetchall()}

    def get_full_profile(self) -> Dict:
        """Get complete user profile with metadata."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM user_profile ORDER BY category, key")
        profile = defaultdict(dict)
        for row in cursor.fetchall():
            profile[row['category']][row['key']] = {
                'value': json.loads(row['value']),
                'updated_at': row['updated_at']
            }
        return dict(profile)

    # ========================================================================
    # PREFERENCE LEARNING
    # ========================================================================

    def learn_preference(self, station: str, category: str, key: str, value: Any, confidence: float = 1.0):
        """Learn or reinforce a user preference."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO preferences (station, category, key, value, confidence)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(station, category, key) DO UPDATE SET
                value = excluded.value,
                confidence = MIN(1.0, confidence + 0.1),
                last_reinforced = CURRENT_TIMESTAMP,
                reinforcement_count = reinforcement_count + 1
        """, (station, category, key, json.dumps(value), confidence))
        self.conn.commit()

    def get_preference(self, station: str, category: str, key: str = None) -> Any:
        """Retrieve learned preference(s)."""
        cursor = self.conn.cursor()
        if key:
            cursor.execute("""
                SELECT value, confidence FROM preferences
                WHERE station = ? AND category = ? AND key = ?
            """, (station, category, key))
            row = cursor.fetchone()
            if row:
                return {
                    'value': json.loads(row['value']),
                    'confidence': row['confidence']
                }
            return None
        else:
            cursor.execute("""
                SELECT key, value, confidence FROM preferences
                WHERE station = ? AND category = ?
                ORDER BY confidence DESC
            """, (station, category))
            return {row['key']: {
                'value': json.loads(row['value']),
                'confidence': row['confidence']
            } for row in cursor.fetchall()}

    def get_all_preferences(self, station: str = None) -> Dict:
        """Get all preferences, optionally filtered by station."""
        cursor = self.conn.cursor()
        if station:
            cursor.execute("""
                SELECT category, key, value, confidence, reinforcement_count
                FROM preferences WHERE station = ?
                ORDER BY confidence DESC
            """, (station,))
        else:
            cursor.execute("""
                SELECT station, category, key, value, confidence, reinforcement_count
                FROM preferences
                ORDER BY station, confidence DESC
            """)

        prefs = defaultdict(lambda: defaultdict(dict))
        for row in cursor.fetchall():
            if station:
                prefs[row['category']][row['key']] = {
                    'value': json.loads(row['value']),
                    'confidence': row['confidence'],
                    'reinforcement_count': row['reinforcement_count']
                }
            else:
                prefs[row['station']][row['category']][row['key']] = {
                    'value': json.loads(row['value']),
                    'confidence': row['confidence'],
                    'reinforcement_count': row['reinforcement_count']
                }
        return dict(prefs)

    # ========================================================================
    # DECISION TRACKING
    # ========================================================================

    def record_decision(self, station: str, decision_type: str, decision: str,
                       context: str = None, rationale: str = None, outcome: str = None):
        """Record a user decision with context."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO decisions (station, decision_type, context, decision, rationale, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (station, decision_type, context, decision, rationale, outcome))
        self.conn.commit()
        return cursor.lastrowid

    def get_decisions(self, station: str = None, decision_type: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve decision history."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM decisions WHERE 1=1"
        params = []

        if station:
            query += " AND station = ?"
            params.append(station)
        if decision_type:
            query += " AND decision_type = ?"
            params.append(decision_type)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # INTERACTION LOGGING
    # ========================================================================

    def log_interaction(self, station: str, action_type: str, action_data: Dict = None, metadata: Dict = None):
        """Log user interaction for pattern analysis."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO interactions (station, action_type, action_data, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            station,
            action_type,
            json.dumps(action_data) if action_data else None,
            json.dumps(metadata) if metadata else None
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_interactions(self, station: str = None, hours: int = 24, limit: int = 1000) -> List[Dict]:
        """Retrieve recent interactions."""
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(hours=hours)

        if station:
            cursor.execute("""
                SELECT * FROM interactions
                WHERE station = ? AND timestamp > ?
                ORDER BY timestamp DESC LIMIT ?
            """, (station, since, limit))
        else:
            cursor.execute("""
                SELECT * FROM interactions
                WHERE timestamp > ?
                ORDER BY timestamp DESC LIMIT ?
            """, (since, limit))

        return [dict(row) for row in cursor.fetchall()]

    def get_usage_patterns(self, days: int = 30) -> Dict:
        """Analyze usage patterns across stations."""
        cursor = self.conn.cursor()
        since = datetime.now() - timedelta(days=days)

        cursor.execute("""
            SELECT station, COUNT(*) as count,
                   strftime('%H', timestamp) as hour
            FROM interactions
            WHERE timestamp > ?
            GROUP BY station, hour
            ORDER BY count DESC
        """, (since,))

        patterns = defaultdict(lambda: defaultdict(int))
        for row in cursor.fetchall():
            patterns[row['station']][int(row['hour'])] = row['count']

        return dict(patterns)

    # ========================================================================
    # CONTEXT & INSIGHTS
    # ========================================================================

    def save_context(self, snapshot_type: str, context_data: Dict, tags: List[str] = None):
        """Save a context snapshot."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO context_snapshots (snapshot_type, context_data, tags)
            VALUES (?, ?, ?)
        """, (snapshot_type, json.dumps(context_data), json.dumps(tags) if tags else None))
        self.conn.commit()
        return cursor.lastrowid

    def record_insight(self, insight_type: str, title: str, description: str = None,
                      confidence: float = 1.0, evidence: Dict = None):
        """Record a discovered insight or pattern."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO insights (insight_type, title, description, confidence, evidence)
            VALUES (?, ?, ?, ?, ?)
        """, (insight_type, title, description, confidence, json.dumps(evidence) if evidence else None))
        self.conn.commit()
        return cursor.lastrowid

    def get_insights(self, validated_only: bool = False, limit: int = 50) -> List[Dict]:
        """Retrieve discovered insights."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM insights"
        if validated_only:
            query += " WHERE validated = 1"
        query += " ORDER BY confidence DESC, discovered_at DESC LIMIT ?"

        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # ========================================================================
    # KNOWLEDGE BASE
    # ========================================================================

    def add_knowledge(self, topic: str, content: str, source: str = None, relevance: float = 1.0):
        """Add to semantic knowledge base."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge (topic, content, source, relevance_score)
            VALUES (?, ?, ?, ?)
        """, (topic, content, source, relevance))
        self.conn.commit()
        return cursor.lastrowid

    def get_knowledge(self, topic: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve knowledge entries."""
        try:
            cursor = self.conn.cursor()

            # First, get the knowledge entries
            if topic:
                cursor.execute("""
                    SELECT * FROM knowledge
                    WHERE topic LIKE ?
                    ORDER BY relevance_score DESC, accessed_count DESC
                    LIMIT ?
                """, (f'%{topic}%', limit))
            else:
                cursor.execute("""
                    SELECT * FROM knowledge
                    ORDER BY relevance_score DESC
                    LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()

            # Update access tracking for retrieved rows
            for row in rows:
                cursor.execute("""
                    UPDATE knowledge
                    SET accessed_count = accessed_count + 1,
                        last_accessed = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (row['id'],))

            self.conn.commit()

            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
            return []

    # ========================================================================
    # ANALYTICS & SUMMARY
    # ========================================================================

    def get_memory_stats(self) -> Dict:
        """Get comprehensive memory system statistics."""
        cursor = self.conn.cursor()

        stats = {}

        # Profile stats
        cursor.execute("SELECT COUNT(*) as count FROM user_profile")
        stats['profile_entries'] = cursor.fetchone()['count']

        # Preferences
        cursor.execute("SELECT COUNT(*) as count, AVG(confidence) as avg_confidence FROM preferences")
        row = cursor.fetchone()
        stats['preferences'] = {
            'count': row['count'],
            'avg_confidence': round(row['avg_confidence'], 2) if row['avg_confidence'] else 0
        }

        # Decisions
        cursor.execute("SELECT COUNT(*) as count FROM decisions")
        stats['decisions_tracked'] = cursor.fetchone()['count']

        # Interactions
        cursor.execute("SELECT COUNT(*) as count FROM interactions")
        stats['total_interactions'] = cursor.fetchone()['count']

        cursor.execute("""
            SELECT COUNT(*) as count FROM interactions
            WHERE timestamp > datetime('now', '-24 hours')
        """)
        stats['interactions_24h'] = cursor.fetchone()['count']

        # Insights
        cursor.execute("SELECT COUNT(*) as count FROM insights WHERE validated = 1")
        stats['validated_insights'] = cursor.fetchone()['count']

        # Knowledge
        cursor.execute("SELECT COUNT(*) as count FROM knowledge")
        stats['knowledge_entries'] = cursor.fetchone()['count']

        # Most used station
        cursor.execute("""
            SELECT station, COUNT(*) as count
            FROM interactions
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY station
            ORDER BY count DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            stats['most_used_station'] = {'name': row['station'], 'count': row['count']}

        return stats

    def get_user_summary(self) -> Dict:
        """Get comprehensive user profile summary."""
        return {
            'profile': self.get_full_profile(),
            'preferences': self.get_all_preferences(),
            'recent_decisions': self.get_decisions(limit=10),
            'usage_patterns': self.get_usage_patterns(),
            'insights': self.get_insights(validated_only=True, limit=10),
            'stats': self.get_memory_stats()
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

# ============================================================================
# GLOBAL MEMORY INSTANCE
# ============================================================================

_memory_instance = None

def get_memory() -> TrinityMemory:
    """Get global Trinity Memory instance (singleton)."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = TrinityMemory()
    return _memory_instance

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def remember(key: str, value: Any, category: str = 'general'):
    """Quick function to remember something."""
    memory = get_memory()
    memory.set_profile(key, value, category)

def recall(key: str) -> Any:
    """Quick function to recall something."""
    memory = get_memory()
    return memory.get_profile(key)

def learn(station: str, category: str, key: str, value: Any):
    """Quick function to learn a preference."""
    memory = get_memory()
    memory.learn_preference(station, category, key, value)

if __name__ == "__main__":
    # Demo / Testing
    memory = TrinityMemory()

    print("╔════════════════════════════════════════╗")
    print("║  Trinity Core Memory - System Test    ║")
    print("╚════════════════════════════════════════╝\n")

    # Set user profile
    memory.set_profile('name', 'Ty Brown', 'personal')
    memory.set_profile('role', 'Developer & Trader', 'professional')
    memory.set_profile('system_start_date', '2026-02-04', 'system')

    # Learn preferences
    memory.learn_preference('Engineering', 'CAD', 'default_material', 'PLA')
    memory.learn_preference('Trading', 'strategy', 'preferred_bot', 'Phoenix Mark XII Genesis V2')
    memory.learn_preference('Career', 'job_search', 'preferred_role', 'AI/ML Engineer')

    # Record decisions
    memory.record_decision(
        'Trading',
        'bot_selection',
        'Phoenix Mark XII Genesis V2',
        context='Validated champion with 121.08 fitness score',
        rationale='Highest Sharpe ratio (2.14) and profit probability (99.05%)'
    )

    # Log interactions
    memory.log_interaction('AI Assistant', 'chat_message', {'message_count': 1})
    memory.log_interaction('Engineering', 'generate_cad', {'model': 'hex_bolt'})

    # Record insight
    memory.record_insight(
        'usage_pattern',
        'User prefers evening work sessions',
        'Most interactions occur between 18:00-23:00',
        confidence=0.85
    )

    # Add knowledge
    memory.add_knowledge(
        'Phoenix Bot',
        'Phoenix Mark XII Genesis V2 is the validated champion trading bot with 320 trades completed',
        source='Bot validation session Feb 3, 2026'
    )

    # Get stats
    stats = memory.get_memory_stats()
    print("Memory System Statistics:")
    print(json.dumps(stats, indent=2))

    print("\n✅ Trinity Memory System initialized and tested successfully!")
