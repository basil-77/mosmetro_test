import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

student_course = Table(
    'student_course', Base.metadata,
    Column('student_id', String, ForeignKey('students.id')),
    Column('course_id', String, ForeignKey('courses.id'))
)

class Student(Base):
    __tablename__ = 'students'
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    email = Column(String)
    submissions = Column(JSON, default=dict)

    courses = relationship("Course", secondary=student_course, back_populates="students")
    lessons = relationship("Lesson", secondary="student_lesson", back_populates="participants")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.submissions is None:
            self.submissions = {}

    def enroll(self, course):
        self.courses.append(course)

    def submit_assignment(self, assignment_id, answer):
        self.submissions[assignment_id] = answer

    def attend_lesson(self, lesson):
        self.lessons.append(lesson)

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    email = Column(String)
    courses = relationship("Course", back_populates="teacher")

    def create_course(self, name, description):
        return Course(name=name, description=description, teacher=self)

    def create_lesson(self, course, dt, topic):
        lesson = Lesson(datetime=dt, topic=topic, course=course)
        course.lessons.append(lesson)
        return lesson

    def create_assignment(self, course, description):
        assignment = Assignment(description=description, course=course)
        course.assignments.append(assignment)
        return assignment

    def grade_submission(self, student, assignment, grade):
        assignment.submissions[student.id] = (student.submissions.get(assignment.id), grade)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    description = Column(Text)

    teacher_id = Column(String, ForeignKey("teachers.id"))
    teacher = relationship("Teacher", back_populates="courses")

    students = relationship("Student", secondary=student_course, back_populates="courses")
    lessons = relationship("Lesson", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(String, primary_key=True, default=generate_uuid)
    datetime = Column(DateTime)
    topic = Column(String)
    course_id = Column(String, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="lessons")
    participants = relationship("Student", secondary="student_lesson", back_populates="lessons")

student_lesson = Table(
    'student_lesson', Base.metadata,
    Column('student_id', String, ForeignKey('students.id')),
    Column('lesson_id', String, ForeignKey('lessons.id'))
)

class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(String, primary_key=True, default=generate_uuid)
    description = Column(Text)
    course_id = Column(String, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="assignments")
    submissions = Column(JSON, default=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.submissions is None:
            self.submissions = {}