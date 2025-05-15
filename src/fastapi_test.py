from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>CoPri - Welcome</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { padding: 20px; background: #f0f0f0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>CoPri - Your Ultimate Assistant</h1>
                <div class="status">
                    <h2>System Status</h2>
                    <p>✅ Server is running</p>
                    <p>✅ Basic setup complete</p>
                </div>
            </div>
        </body>
    </html>
    """
