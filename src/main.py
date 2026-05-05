from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helpers.config import get_settings
from routes.base import base_router
from routes.data import data_router
from routes.nlp import nlp_router
from stores.llm.LLMFactory import LLMFactory
# from stores.vectordb.VectorDBFactory import VectorDBFactory
# from stores.llm.template.template_parser import TemplateParser
# from controllers.NlpController import NlpController
from models.enums.LLMEnum import LLMProvider

def create_app():

    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="End-to-end RAG system: upload documents, embed them, query with LLM."
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],        # restrict this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(base_router)
    app.include_router(data_router)
    app.include_router(nlp_router)

    @app.on_event("startup")
    async def startup_event():

        settings = get_settings()

        # Instantiate the factory with the configuration (Dependency Injection)
        llm_factory = LLMFactory(settings)
        
        # Create the providers using the factory instance
        llm_client = llm_factory.create(LLMProvider.OPENAI)
        embed_client = llm_factory.create(LLMProvider.LOCAL_BGE)

        # vector_db = VectorDBFactory.create("qdrant", settings)
        # template_parser = TemplateParser(language="en")

        # Assemble NlpController with all dependencies
        # nlp_controller = NlpController(
        #     llm_client=llm_client,
        #     embed_client=embed_client,
        #     vector_db=vector_db,
        #     template_parser=template_parser
        # )
        
        # Store on app.state so routes can access via request.app.state
        app.state.llm_client = llm_client
        app.state.embed_client = embed_client
        # app.state.vector_db = vector_db
        # app.state.template_parser = template_parser
        # app.state.nlp_controller = nlp_controller
        
        print(f"{settings.APP_NAME} v{settings.APP_VERSION} started.")
        print("Provider startup not yet wired — complete Phase 3 first.")

    @app.on_event("shutdown")
    async def shutdown_event():
        print("Server shutting down.")

    return app


# Create the app instance (uvicorn looks for this variable)
app = create_app()
