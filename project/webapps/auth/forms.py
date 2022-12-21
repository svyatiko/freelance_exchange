from typing import List, Optional

from fastapi import Request


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username or not (self.username.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


class PasswordRecoveryForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.user: Optional[str] = None
        self.email: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")

    def is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.errors:
            return True
        return False


class ChangePasswordForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.old_pass: Optional[str] = None
        self.repeat_new_pass: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.old_pass = form.get("old_password")
        self.new_pass = form.get("new_password")
        self.repeat_new_pass = form.get("repeat_password")

    def is_valid(self):
        if not self.old_pass or not len(self.old_pass) >= 4:
            self.errors.append("Old password required")
        if not self.new_pass or not len(self.new_pass) >= 4:
            self.errors.append("New password required")
        if not self.repeat_new_pass or not len(self.repeat_new_pass) >= 4:
            self.errors.append("Repeat password required")
        if not self.errors:
            return True
        return False
