from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self) -> str:
        values = []
        for col in self.__table__.columns.keys():
            values.append(f"{col}={getattr(self, col)!r}")
            if len(values) >= getattr(self, "repr_cols_num", 3):
                break
        return f"<{self.__class__.__name__} {' '.join(values)}>"
