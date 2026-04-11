from enum import StrEnum
from typing import Iterable
from sqlmodel import Field, Session, SQLModel, create_engine, select
from qqchan.config import config
import time


class TargetType(StrEnum):
    PRIVATE = "private"
    GROUP = "group"


class Target(SQLModel, table=True):
    id: str = Field(primary_key=True)
    type: TargetType
    target_id: int = Field(index=True, description="目标id，可以是群号或QQ号")
    registrant: int = Field(index=True, description="注册者QQ号")
    created_at: int = Field(default_factory=lambda: int(time.time()))
    deleted_at: int = Field(default=0)

    @classmethod
    def get_target_by_id(cls, id: str) -> "Target":
        with get_session() as session:
            target = session.get(Target, id)
        if target is None:
            raise KeyError
        if target.deleted_at != 0:
            raise KeyError
        return target

    @classmethod
    def get_targets_by_target_id(cls, target_id: int, registrant_id: int | None = None) -> Iterable["Target"]:
        sql = (
            select(Target)
                .where(Target.target_id == target_id)
                .where(Target.deleted_at == 0)
        )
        if registrant_id is not None:
            sql = sql.where(Target.registrant == registrant_id)

        with get_session() as session:
            targets = session.exec(sql).all()
        return targets
    
    @classmethod
    def get_targets_by_registrant(cls, registrant_id: int) -> Iterable["Target"]:
        sql = (
            select(Target)
                .where(Target.registrant == registrant_id)
                .where(Target.deleted_at == 0)
        )
        with get_session() as session:
            targets = session.exec(sql).all()
        return targets

    def register(self) -> "Target":
        with get_session() as session:
            session.add(self)
            session.commit()
            session.refresh(self)
        return self

    def save(self) -> "Target":
        with get_session() as session:
            session.add(self)
            session.commit()
            session.refresh(self)
        return self

    def delete(self):
        self.deleted_at = int(time.time())
        self.save()
    



engine = create_engine(config.DATABASE_URL)
SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
