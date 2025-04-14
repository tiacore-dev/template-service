from .doc_route import doc_router


def register_routes(app):
    app.include_router(doc_router, prefix="/api/docs", tags=["Auth"])
