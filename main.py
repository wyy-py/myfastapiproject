from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from routes import auth, signup, materials

app = FastAPI()

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需指定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(signup.router, prefix="/signup")
app.include_router(materials.router, prefix="/api")
# 挂载静态文件目录
# app.mount("/cif_files", StaticFiles(directory="cif_data"), name="cif_files")


@app.get("/")
async def root():
    return {"message": "Welcome to the Materials Database API"}
