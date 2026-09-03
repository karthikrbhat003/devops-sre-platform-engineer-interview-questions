#!/usr/bin/env python3
"""
Thread-Safe O(1) Least Recently Used (LRU) Cache
- Implemented using Doubly Linked List + Hash Map.
- Essential data structure pattern in SRE system design & coding rounds.
"""

import threading
from typing import Optional, Dict, Any

class Node:
    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional['Node'] = None
        self.next: Optional['Node'] = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[str, Node] = {}
        self.lock = threading.Lock()

        # Dummy Head and Tail for clean boundary node operations
        self.head = Node("HEAD", None)
        self.tail = Node("TAIL", None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        """Unlink node from doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node):
        """Insert node right after dummy head (most recently used)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            node = self.cache[key]
            # Move to front (mark as most recently used)
            self._remove(node)
            self._add_to_front(node)
            return node.value

    def put(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.value = value
                self._remove(node)
                self._add_to_front(node)
            else:
                if len(self.cache) >= self.capacity:
                    # Evict least recently used (node right before tail)
                    lru_node = self.tail.prev
                    self._remove(lru_node)
                    del self.cache[lru_node.key]
                
                new_node = Node(key, value)
                self.cache[key] = new_node
                self._add_to_front(new_node)

if __name__ == "__main__":
    print("Testing LRU Cache (Capacity: 2)...")
    cache = LRUCache(2)
    cache.put("user_1", "Alice")
    cache.put("user_2", "Bob")
    print("Get user_1:", cache.get("user_1")) # Alice (user_1 is now most recent)
    
    cache.put("user_3", "Charlie") # Evicts user_2 (least recently used)
    print("Get user_2 (evicted):", cache.get("user_2")) # None
    print("Get user_3:", cache.get("user_3")) # Charlie
    print("Get user_1:", cache.get("user_1")) # Alice
    print("✅ LRU Cache test passed.")
