from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')


class ResponseBase(BaseModel):
    """响应基类"""
    code: int
    msg: str
    data: Optional[T] = None


class SuccessResponse(ResponseBase, Generic[T]):
    """成功响应"""
    code: int = 200
    msg: str = "操作成功"


class ErrorResponse(ResponseBase):
    """错误响应"""
    pass


class PaginatedResponse(ResponseBase, Generic[T]):
    """分页响应"""
    data: dict


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 10
    
    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedData(BaseModel, Generic[T]):
    """分页数据"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int