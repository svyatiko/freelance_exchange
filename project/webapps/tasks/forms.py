from typing import List, Optional

from fastapi import Request


class TaskCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.title: Optional[str] = None
        self.sphere: Optional[str] = None
        self.stack: Optional[str] = None
        self.description: Optional[str] = None
        self.payment_type: Optional[str] = None
        self.price: Optional[int] = None
        self.git_link: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        # print(form)
        self.title = form.get("title")
        self.sphere = form.get("sphere")
        self.stack = form.get("stack")
        self.description = form.get("description")
        self.payment_type = form.get("payment_type")
        self.price = form.get("price")
        self.git_link = form.get("git_link")

    def is_valid(self):
        if not self.title or not len(self.title) >= 4:
            self.errors.append("A valid title is required")
        if not self.stack or not len(self.stack) >= 1:
            self.errors.append("Add technologies used")
        if not self.description or not len(self.description) >= 20:
            self.errors.append("Description too short(minimum 20 characters)")
        if not self.git_link or not (self.git_link.__contains__("https://github.com/")):
            self.errors.append("Valid Url is required e.g https://github.com/")
        if not self.price or not (self.price.isnumeric()):
            self.errors.append("Price field must contain only numbers")
        if not self.errors:
            return True
        return False


class TaskMsgForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.msg: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.msg = form.get("msg")
        print("===========", self.msg)

    def is_valid(self):
        if not self.msg or len(self.msg) <= 4:
            self.errors.append("Your msg is short")
        if not self.errors:
            return True
        return False
