from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Integer, ForeignKey
from typing import List


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Loop(db.Model):
    __tablename__ = "loops"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    persons: Mapped[List["Person"]] = relationship(back_populates="loop")
    
class Person(db.Model):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    loop_id: Mapped[str] = mapped_column(ForeignKey("loops.id"))
    loop: Mapped[Loop] = relationship(back_populates="persons")

    name: Mapped[str]
    email: Mapped[str]
    avoids: Mapped[List["Person"]] = relationship(
        secondary="avoid_assoc_table",
        primaryjoin = "Person.id == PersonAvoid.person_id",
        secondaryjoin = "Person.id == PersonAvoid.avoid_person_id",
        backref = "avoided_by"
    )

# that's kind of a m2m join table
class PersonAvoid(db.Model):
    __tablename__ ="avoid_assoc_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    # person: Mapped["Person"] = relationship()
    avoid_person_id: Mapped[int] = mapped_column(ForeignKey("persons.id"))
    # avoid_person: Mapped["Person"] = relationship()



