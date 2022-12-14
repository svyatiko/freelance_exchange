from sqlalchemy.orm import Session

from db.models.tasks import Task, Task_msg
from schemas.tasks import CreateTaskMsg, TaskCreate


def create_new_task(task: TaskCreate, db: Session, owner_id: int):
    task_object = Task(**task.dict(), customer_id=owner_id)
    db.add(task_object)
    db.commit()
    db.refresh(task_object)
    return task_object


def create_msg(msg: CreateTaskMsg, db: Session):
    msg_obj = Task_msg(**msg.dict())
    db.add(msg_obj)
    db.commit()
    db.refresh(msg_obj)


def list_msgs(db: Session, task_id: int):
    msgs = db.query(Task_msg).filter(Task_msg.task_id == task_id).all()
    return msgs


def retreive_task(id: int, db: Session):
    item = db.query(Task).filter(Task.id == id).first()
    return item


def list_tasks(db: Session):
    tasks = db.query(Task).filter(Task.task_status == "dev not selected").all()
    return tasks


# def update_task_by_id(id: int, task: TaskCreate, db: Session, owner_id):
#     existing_task = db.query(Task).filter(Task.id == id)
#     print("=================", existing_task.first())
#     if not existing_task.first():
#         return 0
#     # task.__dict__.update(owner_id=owner_id)
#     existing_task.update(task.__dict__)
#     db.commit()
#     return 1


# def delete_task_by_id(id: int, db: Session, owner_id):
#     existing_task = db.query(Task).filter(Task.id == id)
#     if not existing_task.first():
#         return 0
#     existing_task.delete(synchronize_session=False)
#     db.commit()
#     return 1


def search_task(query: str, db: Session):
    tasks = db.query(Task).filter(Task.title.contains(query))
    return tasks
