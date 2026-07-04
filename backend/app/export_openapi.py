"""Export FastAPI OpenAPI schema to stdout for contract drift checks."""
import json

if __name__ == "__main__":
    from app.main import app

    print(json.dumps(app.openapi(), indent=2))
