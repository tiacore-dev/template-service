from app import create_app

# Порт и биндинг
PORT = 5000


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(PORT), reload=True)
