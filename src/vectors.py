from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, grpc
from qdrant_client.models import PointStruct, Distance, VectorParams
from datetime import datetime
from discord import Message, TextChannel
class Vectinator:
    """Class for creating vector representations of text strings and saving them to Qdrant index."""
    def __init__(self):
        # Best performing short-length embeddings model for retrieval tasks according to:
        # https://huggingface.co/spaces/mteb/leaderboard
        # model card: https://huggingface.co/ggrn/e5-small-v2
        self.model = SentenceTransformer('intfloat/e5-small-v2')
        self.qdrant = QdrantClient(host="localhost", port=6333, timeout=3.0)
        result = self.qdrant.get_collections()
        if "posts" not in result.collections:
            self.qdrant.recreate_collection(
                collection_name="posts",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def get_embeddings(self, text: str) -> list[float]:
        """Create a vector representation of a text string based on the embeddings model."""
        embeddings = self.model.encode(['passage: '+text], normalize_embeddings=True)
        return embeddings[0].tolist()
    
    def save_message(self, message: Message) -> None:
        """Save message to Qdrant index. Takes a discord.Message class as input."""
        if not isinstance(message.channel, TextChannel):
            return
        vector = self.get_embeddings(message.content)
        point = PointStruct(
            id=1,
            vector=vector,
            payload={
                "aname": message.author.display_name,
                "aid": message.author.id,
                "msg": message.content,
                "channel": message.channel.name,
                "date": int(datetime.now().timestamp())
            }
        )
        self.qdrant.upsert(
            collection_name="posts",
            points=[point]
        )
 
