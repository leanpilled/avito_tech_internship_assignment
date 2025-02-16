from fastapi import FastAPI
from aioinject.ext.fastapi import AioInjectMiddleware

from api.auth import router as auth_router
from api.transaction import router as transaction_router
from api.deal import router as deal_router
from api.info import router as info_router
from di.container import container
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        root_path="/api",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AioInjectMiddleware, container=container)
    app.include_router(transaction_router)
    app.include_router(auth_router)
    app.include_router(deal_router)
    app.include_router(info_router)
    return app

app = create_app()
