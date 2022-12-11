from fastapi import APIRouter
from fastapi import Request,Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# from db.repository.jobs import list_jobs
# from db.session import get_db

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)

# @router.get("/")
# async def home(request: Request, db: Session = Depends(get_db)):
#     tasks = list_tasks(db=db)
#     return templates.TemplateResponse(
#         "general_pages/homepage.html", {"requst": request, "tasks": tasks}
#     )
    
@router.get("/")
async def home(request: Request):
	return templates.TemplateResponse("general_pages/homepage.html",{"request":request})
	