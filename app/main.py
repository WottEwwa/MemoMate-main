import sys
import os
import uvicorn
from dotenv import load_dotenv
from app.fast_api_client import app

load_dotenv()


def main():
    fast_url = os.getenv("FAST_URL")
    fast_port = os.getenv("FAST_PORT")

    # Add the project root to the sys.path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    uvicorn.run(app, host=fast_url, port=int(fast_port))


if __name__ == '__main__':
    main()
