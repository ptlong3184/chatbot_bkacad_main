from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
import os
import json

# Lấy credentials từ biến môi trường JSON
credentials_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Tạo Dialogflow session client
session_client = dialogflow.SessionsClient(credentials=credentials)

# ID của project trên Dialogflow
PROJECT_ID = "chatbottuyensinh-gphg"


app = FastAPI()

# Cho phép CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối MySQL
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Model cho request
class DialogflowRequest(BaseModel):
    query: str
    session_id: str

class EndSessionRequest(BaseModel):
    session_id: str

# Endpoint kiểm tra
@app.get("/")
def root():
    return {"message": "Chatbot API is running"}

# Endpoint gửi tin nhắn đến Dialogflow
@app.post("/dialogflow-proxy")
async def dialogflow_proxy(req: DialogflowRequest):
    user_query = req.query
    session_id = req.session_id

    if not user_query:
        raise HTTPException(status_code=400, detail="Missing query")

    try:
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(PROJECT_ID, session_id)

        text_input = dialogflow.TextInput(text=user_query, language_code="vi")
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        result = response.query_result
        fulfillment_text = result.fulfillment_text or "Xin lỗi, tôi chưa có thông tin phù hợp."

        # Lưu vào database
        turn_order = get_next_turn_order(session_id)
        save_turn(
            session_id,
            turn_order,
            user_query,
            result.intent.display_name if result.intent else "",
            result.parameters,
            fulfillment_text
        )

        return {"response": fulfillment_text}

    except Exception as e:
        return {"response": f"Đã xảy ra lỗi khi xử lý câu hỏi: {str(e)}"}

# Lưu lượt chat
def save_turn(session_id, turn_order, user_query, intent_name, parameters, bot_response):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT session_id FROM chatbot_sessions WHERE session_id = %s", (session_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO chatbot_sessions (session_id) VALUES (%s)", (session_id,))

        cursor.execute("""
            INSERT INTO chatbot_turns (session_id, turn_order, user_query, intent_name, parameters, bot_response)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session_id, turn_order, user_query, intent_name, str(parameters), bot_response))

        conn.commit()
    except Error as e:
        print(f"Lỗi khi lưu lượt chat: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Lấy lượt chat tiếp theo
def get_next_turn_order(session_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chatbot_turns WHERE session_id = %s", (session_id,))
        count = cursor.fetchone()[0]
        return count + 1
    except Error as e:
        print(f"Lỗi khi lấy số lượt chat: {e}")
        return 1
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
