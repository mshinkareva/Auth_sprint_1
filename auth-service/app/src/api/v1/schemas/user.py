from src.models.utils import ModelWithConf


class UserSignUp(ModelWithConf):
    login: str
    password: str
    email: str
    first_name: str
    last_name: str
