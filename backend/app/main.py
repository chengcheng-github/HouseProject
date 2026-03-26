import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.houses import router as house_router
from app.api.v1.endpoints.visits import router as visit_router
from app.api.v1.endpoints.users import router as user_router


# 创建FastAPI应用
app = FastAPI()


app.include_router(admin_router)
app.include_router(house_router)
app.include_router(visit_router)
app.include_router(user_router)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8089)