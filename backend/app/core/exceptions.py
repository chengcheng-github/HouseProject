from fastapi import HTTPException, status


class AppException(HTTPException):
    """自定义应用异常基类"""
    def __init__(self, code: int, msg: str):
        self.code = code
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail={"code": code, "msg": msg, "data": None}
        )


class BadRequestException(AppException):
    """请求参数错误"""
    def __init__(self, msg: str = "请求参数错误"):
        super().__init__(code=400, msg=msg)


class UnauthorizedException(AppException):
    """未授权访问"""
    def __init__(self, msg: str = "未授权访问"):
        super().__init__(code=401, msg=msg)


class ForbiddenException(AppException):
    """禁止访问"""
    def __init__(self, msg: str = "禁止访问"):
        super().__init__(code=403, msg=msg)


class NotFoundException(AppException):
    """资源不存在"""
    def __init__(self, msg: str = "资源不存在"):
        super().__init__(code=404, msg=msg)


class InternalServerError(AppException):
    """服务器内部错误"""
    def __init__(self, msg: str = "服务器内部错误"):
        super().__init__(code=500, msg=msg)