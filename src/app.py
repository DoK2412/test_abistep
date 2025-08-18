import os
import uvicorn


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError




from database.connection import JobDb
from database.table_diagrams import USERS_TABLE, WALLET_TABLE, TRANSACTION_TABLE

from service.router import router_api
from path import TEST

from contextlib import asynccontextmanager


from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await JobDb().create_pool()
    async with JobDb() as pool:
        await pool.execute(USERS_TABLE)
        await pool.execute(WALLET_TABLE)
        await pool.execute(TRANSACTION_TABLE)
    yield
    await JobDb().close_pool()


app = FastAPI(
    lifespan=lifespan,
    title="Сервис переводов",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["DNT", "X-CustomHeader", "Keep-Alive", "User-Agent", "X-Requested-With", "If-Modified-Since", "Cache-Control", "Content-Type", "x-tz-offset", "Authorization"],
)

app.include_router(router_api)

@app.get(TEST, tags=["monitoring"])
async def test():
    return JSONResponse(status_code=200, content={"answer": "Сервис в рабочем состоянии"})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"answer": "Ошибка валидации параметров", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"answer": "Произошла ошибка."},
    )

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST"), port=int(os.getenv("PORT")))