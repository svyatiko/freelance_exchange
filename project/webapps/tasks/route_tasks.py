from typing import Optional

from fastapi import APIRouter, Depends, Request, responses, status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from apis.v1.route_login import get_current_user, get_current_user_from_token
from db.models.users import User_Account
from db.repository.tasks import (create_msg, create_new_task, list_msgs,
                                 list_tasks, retreive_task, search_task)
from db.session import get_db
from schemas.tasks import CreateTaskMsg, TaskCreate
from webapps.tasks.forms import TaskCreateForm, TaskMsgForm

templates = Jinja2Templates(directory="templates")
# include_in_schema=False -> чтобы не видеть в swagger entrypoint
router = APIRouter(include_in_schema=False)


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), msg: str = None):
    tasks = list_tasks(db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "tasks": tasks, "msg": msg}
    )


@router.get("/post-a-task/")
def create_task(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("tasks/create_task.html", {"request": request})


@router.post("/post-a-task/")
async def create_task(request: Request, db: Session = Depends(get_db)):
    form = TaskCreateForm(request)
    await form.load_data()

    if form.is_valid():
        try:
            token = request.cookies.get("access_token")
            if token is None:
                form.__dict__.get("errors").append(
                    "You might not be logged in, In case problem persists please contact us."
                )
                raise Exception

            scheme, param = get_authorization_scheme_param(token)
            current_user: User_Account = get_current_user_from_token(token=param, db=db)

            if current_user.user_role == "developer":
                form.__dict__.get("errors").append("Developer cannot create tasks")
                raise Exception

            form.price = int(form.price)
            task = TaskCreate(**form.__dict__)
            task = create_new_task(task=task, db=db, owner_id=current_user.id)

            return responses.RedirectResponse(
                f"/details/{task.id}", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            print(e)
            return templates.TemplateResponse("tasks/create_task.html", form.__dict__)
    return templates.TemplateResponse("tasks/create_task.html", form.__dict__)


@router.get("/details/{id}")
def task_detail(id: int, request: Request, db: Session = Depends(get_db)):
    task = retreive_task(id=id, db=db)
    msgs = list_msgs(db=db, task_id=id)
    user = get_current_user(request, db=db)

    user_obj = dict()
    if user:
        if user.user_role == "developer":
            is_user_msg = [i for i in msgs if i.dev_id == user.id]
            user_obj["is_user_msg_exists"] = True if is_user_msg else False
            user_obj["is_cust"] = False
        else:
            user_obj["is_user_msg_exists"] = True
            user_obj["is_cust"] = True
    else:
        user_obj["is_user_msg_exists"] = True
        user_obj["is_cust"] = False

    return templates.TemplateResponse(
        "tasks/detail.html",
        {"request": request, "task": task, "msgs": msgs, "user_obj": user_obj},
    )


@router.post("/details/{id}")
async def task_detail_msg(id: int, request: Request, db: Session = Depends(get_db)):
    form = TaskMsgForm(request)
    await form.load_data()
    task = retreive_task(id=id, db=db)
    user = get_current_user(request, db=db)

    if form.is_valid():
        try:
            msg_obj = CreateTaskMsg(msg=form.msg, dev_id=user.id, task_id=id)
            create_msg(msg_obj, db=db)

            return responses.RedirectResponse(
                f"/details/{task.id}", status_code=status.HTTP_302_FOUND
            )
        except Exception as e:
            return templates.TemplateResponse(
                "tasks/detail.html",
                {"request": request, "task": task, "errors": form.errors},
            )
    return templates.TemplateResponse(
        "tasks/detail.html", {"request": request, "task": task, "errors": form.errors}
    )


@router.get("/delete-task")
def show_tasks_to_delete(request: Request, db: Session = Depends(get_db)):
    tasks = list_tasks(db=db)
    return templates.TemplateResponse(
        "tasks/show_tasks_to_delete.html", {"request": request, "tasks": tasks}
    )


@router.get("/search/")
def search(
    request: Request, db: Session = Depends(get_db), query: Optional[str] = None
):
    tasks = search_task(query, db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "tasks": tasks}
    )
