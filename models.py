from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    DateTime, 
    UniqueConstraint
)
from db import Base


# constants
class SourceConst(Enum):
    REDDIT = "reddit"
    X = "x"

class TypeConst(Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"

class ContentCategory(str, Enum):
    FOOTBALL_MEME = "football_meme"
    NEWS = "news"


# models
class ChannelSubcription(Base):
    __tablename__= "channel_subscriptions"
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(255), unique=True, nullable=False)
    channel_name = Column(String(255))
    category = Column(String(100), nullable=True)
    added_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        """Return a serializable dict representation of the content."""
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "channel_id": self.channel_id,
            "category": self.category,
            "added_at": self.posted_at.isoformat() if self.posted_at else None,
        } 

    def __repr__(self):
        return f"<ChannelSubcription(id={self.id}, channel_id={self.channel_id}, channel_name={self.channel_name[:30]}...)>"


class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True)
    source_id = Column(String(100), unique=True, nullable=False)
    source = Column(String(50), default=SourceConst.REDDIT.value)
    title = Column(String(500))
    url = Column(String(500))
    type = Column(String(50), default=TypeConst.TEXT.value)
    posted = Column(Boolean, default=False)
    fetched_at = Column(DateTime, default=datetime.now)
    posted_at = Column(DateTime, nullable=True)
    priority = Column(Integer, default=0, index=True)

    __table_args__ = (
        UniqueConstraint("source_id", name="uq_source_id"),
    )

    def to_dict(self):
        """Return a serializable dict representation of the content."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "type": self.type,
            "posted": self.posted,
            "priority": self.priority,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
        }

    def __repr__(self):
        return f"<Content(id={self.id}, source={self.source}, title={self.title[:30]}..., priority={self.priority})>"
