from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helpers.config import get_settings
from routes.base import base_router
from routes.data import data_router
from routes.nlp import nlp_router
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectorDBFactory import VectorDBFactory
from stores.llm.template.template_parser import TemplateParser
from controllers.NlpController import NlpController
from models.enums.LLMEnum import LLMProvider
from models.enums.VectorDBEnum import VectorDBProvider


def create_app():
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="End-to-end RAG system: upload documents, embed them, query with LLM."
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(base_router)
    app.include_router(data_router, prefix="/api/v1/data")
    app.include_router(nlp_router, prefix="/api/v1/nlp")

    @app.on_event("startup")
    async def startup_event():
        settings = get_settings()

        # 1. Instantiate the factory
        llm_factory = LLMFactory(settings)

        # 2. Create the providers
        llm_client = llm_factory.create(LLMProvider.OPENAI)
        embed_client = llm_factory.create(LLMProvider.LOCAL_BGE)
        
        vector_db = VectorDBFactory.create(VectorDBProvider.QDRANT, settings)
        template_parser = TemplateParser(language="en")

        # 3. Assemble NlpController
        nlp_controller = NlpController(
            llm_client=llm_client,
            embed_client=embed_client,
            vector_db=vector_db,
            template_parser=template_parser
        )

        # 4. Store on app.state
        app.state.llm_client = llm_client
        app.state.embed_client = embed_client
        app.state.vector_db = vector_db
        app.state.template_parser = template_parser
        app.state.nlp_controller = nlp_controller

        print(f"{settings.APP_NAME} v{settings.APP_VERSION} started.")

    @app.on_event("shutdown")
    async def shutdown_event():
        print("Server shutting down.")

    return app


app = create_app()