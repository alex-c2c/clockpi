from logging import Logger, getLogger

from sqlalchemy.orm import Mapped

from app import db

logger: Logger = getLogger(__name__)

class QueueModel(db.Model):
	__tablename__: str = "queue"

	id: Mapped[int]		= db.Column(db.Integer, primary_key=True)
	queue: Mapped[str]	= db.Column(db.String(), nullable=False)

	def __init__(self, queue: str):
		self.queue = queue

	def __repr__(self) -> str:
		return f"<Queue - queue:{self.queue}>"
		
	def get_queue(self) -> list[int]:
		return [int(id) for id in self.queue.split(",")]

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"queue": self.get_queue()
		}
