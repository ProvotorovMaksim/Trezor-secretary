from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from settings import settings

class VectorDB:
    def __init__(self):
        # Подключение к Qdrant (локально или удаленно)
        self.client = QdrantClient(
            url=settings.QDRANT_URL,  # Например, "http://localhost:6333"
            api_key=settings.QDRANT_API_KEY if hasattr(settings, 'QDRANT_API_KEY') else None # type: ignore
        )
        
        # Модель для эмбеддингов (русская, легкая)
        self.encoder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        self.collection_name = "chat_history"
        self.vector_size = 384  # Размер вектора для MiniLM
        
        # Создаем коллекцию, если её нет
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Создает коллекцию в Qdrant, если она не существует"""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )
    
    def add_message(self, message_id: int, text: str, metadata: dict):
        """Добавляет сообщение в векторную БД"""
        vector = self.encoder.encode(text).tolist()
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=message_id,
                    vector=vector,
                    payload={"text": text, **metadata}
                )
            ]
        )
    
    def search_similar(self, query: str, limit: int = 3) -> list:
        """Ищет похожие сообщения по смыслу"""
        vector = self.encoder.encode(query).tolist()
        
        results = self.client.search( # type: ignore
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit
        )
        
        return [
            {
                "text": r.payload.get("text"),
                "score": r.score,
                "metadata": {k: v for k, v in r.payload.items() if k != "text"}
            }
            for r in results
        ]

# Глобальный экземпляр (или используйте Dependency Injection)
vector_db = VectorDB()
