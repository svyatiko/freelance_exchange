from fastapi import APIRouter, Depends, Request, responses, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apis.v1.route_login import get_current_user
from db.repository.users import create_new_user
from db.session import get_db
from schemas.users import UserCreate
from webapps.users.forms import UserCreateForm

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/register/")
def register(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db=db)
    return templates.TemplateResponse(
        "users/register.html", {"request": request, "user": user}
    )


@router.post("/register/")
async def register(request: Request, db: Session = Depends(get_db)):
    form = UserCreateForm(request)
    setattr(form, "user", None)
    await form.load_data()
    if await form.is_valid():
        user = UserCreate(
            username=form.username,
            email=form.email,
            password=form.password,
            user_role=form.user_role,
        )
        try:
            user = create_new_user(user=user, db=db)
            return responses.RedirectResponse(
                "/login/?msg=Successfully-Registered", status_code=status.HTTP_302_FOUND
            )
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicate username or emails")
            return templates.TemplateResponse("users/register.html", form.__dict__)
    return templates.TemplateResponse("users/register.html", form.__dict__)
