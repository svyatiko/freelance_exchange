from fastapi import (APIRouter, Depends, HTTPException, Request, responses,
                     status)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from apis.mail_sender import MailSender
from apis.utils import generate_password
from apis.v1.route_login import (get_current_user, get_current_user_from_token,
                                 login_for_access_token)
from db.repository.login import get_user
from db.repository.tasks import list_tasks
from db.repository.users import update_user_password_by_id
from db.session import get_db
from schemas.users import UserCreate
from webapps.auth.forms import LoginForm, PasswordRecoveryForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/login/")
def login(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db=db)
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "user": user}
    )


@router.post("/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    tasks = list_tasks(db=db)
    setattr(form, "tasks", tasks)
    setattr(form, "user", None)
    await form.load_data()
    if await form.is_valid():
        try:
            response = templates.TemplateResponse(
                "general_pages/homepage.html", form.__dict__
            )
            token_data = login_for_access_token(
                response=response, form_data=form, db=db
            )

            form.__dict__.update(msg="Login Successful")
            user = get_current_user_from_token(token_data["access_token"], db=db)
            setattr(form, "user", user)

            r = templates.TemplateResponse("general_pages/homepage.html", form.__dict__)
            updated_content_length = r.__dict__.get("raw_headers")[0]
            raw_headers = response.__dict__.get("raw_headers")
            raw_headers[0] = updated_content_length
            response.__dict__.update(raw_headers=raw_headers)
            response.__dict__.update(body=r.__dict__.get("body"))

            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or password")
            return templates.TemplateResponse("auth/login.html", form.__dict__)
    return templates.TemplateResponse("auth/login.html", form.__dict__)


@router.get("/pass_recovery/")
def password_recovery(request: Request):
    return templates.TemplateResponse(
        "auth/pass_recovery.html", {"request": request, "user": None}
    )


@router.post("/pass_recovery/")
async def password_recovery(request: Request, db: Session = Depends(get_db)):
    form = PasswordRecoveryForm(request)
    await form.load_data()
    if form.is_valid():
        try:
            user = get_user(form.email, db)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Email does not exist",
                )
            new_password = generate_password()
            print(user.__dict__)
            user_schem_obj = UserCreate(
                username=user.username,
                email=user.email,
                password=new_password,
                user_role=user.user_role,
            )
            update_status = update_user_password_by_id(user.id, user_schem_obj, db)
            if update_status:
                MailSender.send_msg(user.username, "cvity6692@gmail.com", new_password)
            return responses.RedirectResponse(
                "/login/", status_code=status.HTTP_302_FOUND
            )
        except HTTPException:
            form.__dict__.get("errors").append("Email does not exist")
            return templates.TemplateResponse("auth/pass_recovery.html", form.__dict__)
    return templates.TemplateResponse("auth/pass_recovery.html", form.__dict__)
