# Communication Module - Agent 通信与协作

from .messenger import AgentMessenger, Message, MessageType
from .knowledge_share import KnowledgeSharing, KnowledgePacket
from .group_chat import GroupChatManager, ChatRole
from .collaboration import AgentCollaboration, TaskType

__all__ = [
    'AgentMessenger',
    'Message',
    'MessageType',
    'KnowledgeSharing',
    'KnowledgePacket',
    'GroupChatManager',
    'ChatRole',
    'AgentCollaboration',
    'TaskType',
]
