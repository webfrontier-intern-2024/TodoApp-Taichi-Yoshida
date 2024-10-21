from fastapi import FastAPI
from routers import controllers  # Todoルーターをインポート
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# ルーターを登録
app.include_router(controllers.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
