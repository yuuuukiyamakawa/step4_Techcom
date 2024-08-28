# ORM（SQLalchemy）によるデータ規則と構成

from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import  ForeignKey, VARCHAR, Integer, DATE, TIME
import datetime, time


class Base(DeclarativeBase):
    pass


class MentorMaster(Base):
    __tablename__ = 'MentorMaster'
    id :Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_code :Mapped[str] = mapped_column(ForeignKey("UserData.employee_code"))
    login_id :Mapped[str] = mapped_column(VARCHAR(32))

    mentees :Mapped['MenteeMaster'] = relationship(back_populates="mentor")
    user_data :Mapped['UserData'] = relationship(back_populates="mentor")


class MenteeMaster(Base):
    __tablename__ = 'MenteeMaster'
    id :Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_code :Mapped[str] = mapped_column(ForeignKey("UserData.employee_code"))
    login_id :Mapped[str] = mapped_column(VARCHAR(32))
    mentor_id :Mapped[int] = mapped_column(ForeignKey("MentorMaster.id"))

    mentor :Mapped['MentorMaster'] = relationship(back_populates="mentees")
    user_data :Mapped['UserData'] = relationship(back_populates="mentee")
    mentorings :Mapped['Mentoring'] = relationship(back_populates="mentee")


class UserData(Base):
    __tablename__ = 'UserData'
    employee_code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(8))
    gender: Mapped[str]
    birth_date: Mapped[datetime.date] = mapped_column(DATE)
    department: Mapped[str]
    position: Mapped[str]
    employment_type: Mapped[str]
    join_date: Mapped[datetime.date] = mapped_column(DATE)
    workplace: Mapped[str]
    career: Mapped[str]
    # mentoring_record_id: Mapped[int]

    mentor :Mapped['MentorMaster'] = relationship(back_populates="user_data")
    mentee :Mapped['MenteeMaster'] = relationship(back_populates="user_data")  # 同じクラス内に同一名称のデータは使えない


class Mentoring(Base):
    __tablename__ = 'Mentoring'  # クラスの名前と同一は不可
    id :Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mentee_id :Mapped[int] = mapped_column(ForeignKey("MenteeMaster.id"))
    mtg_date :Mapped[int] = mapped_column(DATE)
    mtg_start_time :Mapped[datetime.time] = mapped_column(TIME)
    mtg_time :Mapped[datetime.time] = mapped_column(TIME)
    request_to_mentor_for_attitude :Mapped[str] = mapped_column(VARCHAR(100))
    request_to_mentor_for_content :Mapped[str] = mapped_column(VARCHAR(100))
    advise_to_mentor_for_mtg :Mapped[Optional[str]] = mapped_column(VARCHAR(500))  # nullable=True
    mtg_content :Mapped[Optional[str]] # nullable=True
    mtg_content_summary :Mapped[Optional[str]] = mapped_column(VARCHAR(500))  # nullable=True
    mtg_memo :Mapped[Optional[str]] # nullable=True
    mtg_content_speaker_identification :Mapped[Optional[str]] # nullable=True
    pre_advise_to_mentor_for_mtg :Mapped[Optional[str]] = mapped_column(VARCHAR(500))  # nullable=True
    pre_mtg_content_summary :Mapped[Optional[str]] = mapped_column(VARCHAR(500))  # nullable=True

    feedbacks :Mapped['Feedback'] = relationship(back_populates="mentoring")
    mentee :Mapped['MenteeMaster'] = relationship(back_populates="mentorings")


class Feedback(Base):
    __tablename__ = 'Feedback'
    id :Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mentoring_id :Mapped[int] = mapped_column(ForeignKey("Mentoring.id"))
    listening_score :Mapped[int]
    questioning_score :Mapped[int]
    feedbacking_score :Mapped[int]
    empathizing_score :Mapped[int]
    motivating_score :Mapped[int]
    coaching_score :Mapped[int]
    teaching_score :Mapped[int]
    analyzing_score :Mapped[int]
    inspiration_score :Mapped[int]
    vision_score :Mapped[int]
    mentee_feedback_flg :Mapped[bool]

    mentoring :Mapped['Mentoring'] = relationship(back_populates="feedbacks")


# 型定義の参考：https://zenn.dev/re24_1986/articles/8520ac3f9a0187