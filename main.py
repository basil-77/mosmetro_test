from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

from models import Base, Teacher, Student

def main():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        maria = Teacher(name="Мария Ивановна", email="maria@school.ru")
        session.add(maria)

        python_course = maria.create_course("Программирование на Python", "Базовый курс по Python")
        session.add(python_course)

        ivan = Student(name="Иван Петров", email="ivan@student.ru")
        anna = Student(name="Анна Смирнова", email="anna@student.ru")
        ivan.enroll(python_course)
        anna.enroll(python_course)

        session.add_all([ivan, anna])
        session.flush() 

        lesson = maria.create_lesson(python_course, datetime.now(), "ООП в Python")
        ivan.attend_lesson(lesson)
        anna.attend_lesson(lesson)

        assignment = maria.create_assignment(python_course, "Реализовать класс «Книга»")
        ivan.submit_assignment(assignment.id, "class Book: pass")
        anna.submit_assignment(assignment.id, "class Book:\n    def __init__(self): pass")

        maria.grade_submission(ivan, assignment, 90)
        maria.grade_submission(anna, assignment, 100)

        session.commit()

        print("Студенты курса:")
        for s in python_course.students:
            print(f"- {s.name}")

        print("\nПрисутствовали на занятии:")
        for p in lesson.participants:
            print(f"- {p.name}")

        print("\nСданные задания и оценки:")
        for sid, (ans, grade) in assignment.submissions.items():
            student = session.get(Student, sid)
            print(f"- {student.name}: Оценка — {grade}, Ответ — {ans}")


if __name__ == "__main__":
    main()
