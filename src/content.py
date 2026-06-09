"""
LinkedList educational content for the short video.
Each section drives one slide in the final video.
"""

SECTIONS = [
    {
        "type": "title",
        "heading": "Python\nLinked Lists",
        "on_screen_text": "Data Structures Series",
        "narration": "",
        "duration": 3.0,
    },
    {
        "type": "text",
        "heading": "What is a Linked List?",
        "body": "A chain of nodes where each node\nstores a value and a pointer\nto the next node.",
        "on_screen_text": "Nodes connected by pointers",
        "narration": "A linked list is a chain of nodes. Each node stores a value and a pointer to the next node in the sequence.",
        "duration": 5.0,
    },
    {
        "type": "text",
        "heading": "Node Structure",
        "body": "• data  — stores the value\n• next  — points to next node\n• last node's next = None",
        "on_screen_text": "Two fields: data + next",
        "narration": "Every node has two fields: data holds the value, and next points to the following node. The last node's next is None.",
        "duration": 4.5,
    },
    {
        "type": "code",
        "heading": "1. Node Class",
        "body": (
            "class Node:\n"
            "    def __init__(self, data):\n"
            "        self.data = data\n"
            "        self.next = None"
        ),
        "on_screen_text": "data + next = None by default",
        "narration": "Here's the Node class. The constructor takes data and stores it, then sets next to None by default.",
        "duration": 5.0,
    },
    {
        "type": "code",
        "heading": "2. LinkedList + append()",
        "body": (
            "class LinkedList:\n"
            "    def __init__(self):\n"
            "        self.head = None\n"
            "\n"
            "    def append(self, data):\n"
            "        node = Node(data)\n"
            "        if not self.head:\n"
            "            self.head = node\n"
            "            return\n"
            "        cur = self.head\n"
            "        while cur.next:\n"
            "            cur = cur.next\n"
            "        cur.next = node"
        ),
        "on_screen_text": "Walk to tail → link new node",
        "narration": "The LinkedList tracks the head node. append creates a new node, then walks to the tail and links it in. If the list is empty, the new node becomes the head.",
        "duration": 7.0,
    },
    {
        "type": "code",
        "heading": "3. print_list()",
        "body": (
            "    def print_list(self):\n"
            "        cur = self.head\n"
            "        while cur:\n"
            "            print(cur.data, end=' -> ')\n"
            "            cur = cur.next\n"
            "        print('None')"
        ),
        "on_screen_text": "Follow next until None",
        "narration": "print_list starts at the head and follows each next pointer, printing values along the way until it reaches None.",
        "duration": 5.0,
    },
    {
        "type": "code",
        "heading": "Usage",
        "body": (
            "ll = LinkedList()\n"
            "name=\"Mehdi\"\n"
            "ll.append(1)\n"
            "ll.append(2)\n"
            "ll.append(3)\n"
            "ll.print_list()\n"
            "# 1 -> 2 -> 3 -> None"
        ),
        "on_screen_text": "O(n) append · O(n) traversal",
        "narration": "We create a linked list, append one, two, and three, then call print_list. The output shows each node connected by arrows, ending in None.",
        "duration": 5.0,
    },
    {
        "type": "text",
        "heading": "When to Use",
        "body": "✓  Frequent insertions / deletions\n✓  Dynamic, unknown size\n✗  Fast random access needed\n✗  Cache-friendly iteration",
        "on_screen_text": "Best for queues, stacks, dynamic lists",
        "narration": "Linked lists shine when you need fast insertions or a dynamic size. Avoid them when random access or cache performance matters.",
        "duration": 5.0,
    },
]
