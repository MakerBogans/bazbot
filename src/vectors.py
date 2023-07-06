from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, ScoredPoint
from datetime import datetime
from discord import Message, TextChannel
from dataclasses import dataclass

@dataclass
class SearchHit:
    """Dataclass for search results."""
    score: float
    author_name: str
    author_id: int
    message: str
    channel: str
    date: datetime

class Vectinator:
    """Class for creating vector representations of text strings and saving them to Qdrant index."""

    def __init__(self, nuke: bool = False):
        # Best performing short-length embeddings model for retrieval tasks according to:
        # https://huggingface.co/spaces/mteb/leaderboard
        # model card: https://huggingface.co/ggrn/e5-small-v2
        self.model = SentenceTransformer("intfloat/e5-small-v2")
        self.qdrant = QdrantClient(host="localhost", port=6333, timeout=3.0)
        # Why can't this just be a list of string?!
        result = self.qdrant.get_collections()
        foundcollection = False
        for collection in result.collections:
            if collection.name == "posts":
                foundcollection = True
                break
        if nuke or not foundcollection:
            print('Creating collection, too bad if it existed before!')
            self.qdrant.recreate_collection(
                collection_name="posts",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def get_embeddings(self, text: str) -> list[float]:
        """Create a vector representation of a text string based on the embeddings model."""
        embeddings = self.model.encode(["passage: " + text], normalize_embeddings=True)
        return embeddings[0].tolist()

    def save_message(self, message: Message) -> None:
        """Upserts messages and vectors to Qdrant db. Takes a discord.Message class as input."""
        if not isinstance(message.channel, TextChannel):
            return
        # Ignore empty messages and short messages like 'lol'
        if message.content.strip() == "" or len(message.content) < 20: 
            return
        vector = self.get_embeddings(message.content)
        # This is similar to a row in a standard database
        point = PointStruct(
            id=message.id,
            vector=vector,
            payload={
                "aname": message.author.display_name,
                "aid": message.author.id,
                "msg": message.content,
                "channel": message.channel.name,
                "date": int(datetime.now().timestamp()),
            },
        )
        self.qdrant.upsert(collection_name="posts", points=[point])

    def search(self, query: str, topn: int = 20, threshold: float = 0.9) -> list[SearchHit]:
        """Search Qdrant index for similar messages. Returns a list of SearchHit data classes."""
        # The reason for prepending "query: " is that the model was trained on this, see model card
        vector = self.get_embeddings('query: ' + query)
        points: list[ScoredPoint] = self.qdrant.search(
            collection_name="posts",
            query_vector=vector,
            limit=topn,
            with_payload=True,
            score_threshold=threshold
        )
        results: list[SearchHit] = []
        for point in points:
            payload = point.payload
            if payload is None:
                continue
            results.append(SearchHit(
                score=point.score,
                author_name=payload['aname'],
                author_id=payload['aid'],
                message=payload['msg'],
                channel=payload['channel'],
                date=datetime.fromtimestamp(payload['date'])
            ))
        return results

