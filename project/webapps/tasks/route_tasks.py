from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, responses, status
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from apis.v1.route_login import get_current_user, get_current_user_from_token
from db.models.users import User_Account
from db.repository.tasks import (create_msg, create_new_task, list_msgs, my_tasks,set_finish_status_in_task,set_close_status_in_task,my_closed_tasks,
                                 list_tasks, retreive_task, search_task)
from db.session import get_db
from schemas.tasks import CreateTaskMsg, TaskCreate
from webapps.tasks.forms import TaskCreateForm, TaskMsgForm
from db.repository.tasks import set_dev_in_task

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
async def home(request: Request, db: Session = Depends(get_db), msg: str = None):
    tasks = list_tasks(db=db)
    user = get_current_user(request, db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html",
        {"request": request, "tasks": tasks, "msg": msg, "user": user},
    )


@router.get("/post-a-task/")
def create_task(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db=db)
    return templates.TemplateResponse(
        "tasks/create_task.html", {"request": request, "user": user}
    )


@router.get("/logout/")
def logout(response: Response):
    response = responses.RedirectResponse("/", status_code=302)
    response.delete_cookie(key="access_token")
    return response


@router.post("/post-a-task/")
async def create_task(request: Request, db: Session = Depends(get_db)):
    form = TaskCreateForm(request)
    setattr(form, "user", user)
    user = get_current_user(request, db=db)
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
        if user.id == task.customer_id:
            user_obj["is_user_msg_exists"] = True
            user_obj["is_cust"] = True
    else:
        user_obj["is_user_msg_exists"] = True
        user_obj["is_cust"] = False

    return templates.TemplateResponse(
        "tasks/detail.html",
        {
            "request": request,
            "task": task,
            "msgs": msgs,
            "user": user,
            "user_obj": user_obj,
        },
    )

@router.get("/details/{task_id}/choose_dev/{dev_id}")
def choose_dev(dev_id: int, task_id:int, request: Request, db: Session = Depends(get_db)):
    print(dev_id, task_id)
    ok = set_dev_in_task(task_id, dev_id, db)
    if ok:
        return responses.RedirectResponse(
            f"/my-tasks/", status_code=status.HTTP_302_FOUND
        )
    else: 
        return responses.RedirectResponse(
            f"/details/{task_id}", status_code=status.HTTP_302_FOUND
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
                {"request": request, "task": task, "errors": form.errors, "user": user},
            )
    return templates.TemplateResponse(
        "tasks/detail.html",
        {"request": request, "task": task, "errors": form.errors, "user": user},
    )


@router.get("/my-tasks")
def show_tasks_to_delete(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db=db)
    print(user.id)
    tasks = my_tasks(user.id, db=db)
    if user is None:
        return responses.RedirectResponse(
            "/", status_code=status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        "tasks/show_tasks_to_delete.html", {"request": request, "tasks": tasks, 'user': user}
    )


@router.get('/go-to-task/{id}')
def redirect_task(id: int, request: Request, db: Session = Depends(get_db)):
    task = retreive_task(id=id, db=db)
    if task.dev_id is None:
        print("task.dev_id is None")
        return responses.RedirectResponse(f'/details/{id}', status_code=status.HTTP_302_FOUND)
    else:
        return responses.RedirectResponse(f'/my_tasks/{id}', status_code=status.HTTP_302_FOUND)


@router.get('/my_tasks/{id}')
def show_task(id: int, request: Request, db: Session = Depends(get_db)):
    task = retreive_task(id=id, db=db)
    user = get_current_user(request, db=db)
    print("INNNNNNNNNN")
    return templates.TemplateResponse("tasks/show_task.html", {'request': request, "task": task, 'user': user})

@router.get('/finish_task/{task_id}')
def finish_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    set_finish_status_in_task(task_id, db)
    user = get_current_user(request, db=db)
    tasks = my_tasks(user.id, db)
    return templates.TemplateResponse(
        "tasks/show_tasks_to_delete.html", {"request": request, "tasks": tasks, 'user': user}
    )

@router.get('/close_task/{task_id}')
def close_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    set_close_status_in_task(task_id, db)
    user = get_current_user(request, db=db)
    tasks = my_tasks(user.id, db)
    return templates.TemplateResponse(
        "tasks/show_tasks_to_delete.html", {"request": request, "tasks": tasks, 'user': user}
    )
    
@router.get('/profile')
def profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db=db)
    task_inf = dict()
    closed_tasks = my_closed_tasks(user.id, db=db)
    task_inf['count_closed_tasks'] = len(closed_tasks)
    return templates.TemplateResponse(
        "users/profile.html", {"request": request, 'user': user, "task_inf":task_inf}
    )    


@router.get("/search/")
def search(
    request: Request, db: Session = Depends(get_db), query: Optional[str] = None
):
    user = get_current_user(request, db=db)
    tasks = search_task(query, db=db)
    return templates.TemplateResponse(
        "general_pages/homepage.html",
        {"request": request, "tasks": tasks, "user": user},
    )
