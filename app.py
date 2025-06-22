from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import Error
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
import os
import json
import requests
from fastapi import UploadFile, File, Form, HTTPException
import openai
import base64
import os

# Lấy credentials từ biến môi trường JSON
credentials_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Tạo Dialogflow session client
session_client = dialogflow.SessionsClient(credentials=credentials)

# ID của project trên Dialogflow
PROJECT_ID = "chatbottuyensinh-gphg"

# Lấy OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

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
        host=os.getenv("DB_HOST").strip(),
        port=int(os.getenv("DB_PORT").strip()),
        user=os.getenv("DB_USER").strip(),
        password=os.getenv("DB_PASSWORD").strip(),
        database=os.getenv("DB_NAME").strip()
    )


# Model cho request
class DialogflowRequest(BaseModel):
    query: str
    session_id: str


class EndSessionRequest(BaseModel):
    session_id: str


def get_scholarship_info():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT score_range, amount FROM scholarship_info ORDER BY id ASC")
        result = cursor.fetchall()
        return result if result else None
    except Error as e:
        print(f"Lỗi truy vấn học bổng: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# Truy vấn học phí
def get_program_tuition_by_intent():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
                SELECT p.name AS program_name,
                       m.major_name,
                       p.duration,
                       t.fee_amount,
                       t.notes
                FROM programs p
                         LEFT JOIN majors_info m ON p.major_id = m.id
                         LEFT JOIN tuition_fees t ON t.program_id = p.id \
                """
        cursor.execute(query)
        result = cursor.fetchall()

        return result if result else None

    except Error as e:
        print(f"Lỗi truy vấn học phí: {e}")
        return None

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.get("/")
def root():
    return {"message": "Chatbot API is running"}


@app.post("/dialogflow-proxy")
async def dialogflow_proxy(req: DialogflowRequest):
    user_query = req.query
    session_id = req.session_id

    if not user_query:
        raise HTTPException(status_code=400, detail="Missing query")

    try:
        session = session_client.session_path(PROJECT_ID, session_id)

        text_input = dialogflow.TextInput(text=user_query, language_code="vi")
        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        result = response.query_result
        fulfillment_text = result.fulfillment_text or "Xin lỗi, tôi chưa có thông tin phù hợp."
        intent_name = result.intent.display_name if result.intent else ""

        if intent_name == "IKetThuc":
            mark_session_ended(session_id)

        if intent_name == "IHocPhi":
            tuition_data = get_program_tuition_by_intent()
            if tuition_data:
                fulfillment_text = "Thông tin học phí của một số chương trình:\n"
                for item in tuition_data:
                    fulfillment_text += f"- {item['program_name']} ({item['major_name']}): {item['fee_amount']} / năm. {item['notes'] or ''}\n"

        elif intent_name == "I_gia_tri_hoc_bong":
            data = get_scholarship_info()
            if data:
                fulfillment_text = "📚 Giá trị học bổng theo điểm thi:\n"
                for item in data:
                    fulfillment_text += f"- {item['score_range']}: {item['amount']} VNĐ\n"
        elif intent_name == "I_thoi_gian_thi_hoc_bong":
            fulfillment_text = "⏰ Thời gian tổ chức kỳ thi học bổng thường diễn ra vào tháng 6 hàng năm. Thí sinh vui lòng theo dõi fanpage chính thức của BKACAD để cập nhật chi tiết."

        elif intent_name == "I_thong_tin_chung_hoc_bong":
            fulfillment_text = (
                "🎓 BKACAD tổ chức kỳ thi Học bổng Sinh viên Tài năng hằng năm nhằm giúp các bạn học sinh lớp 12 "
                "và đã tốt nghiệp THPT trên toàn quốc có cơ hội tiếp cận chương trình đào tạo hiện đại, chuẩn quốc tế."
            )

        elif intent_name == "I_tuyensinh_thoigian_hoc_bong":
            fulfillment_text = (
                "📆 Kỳ thi học bổng nằm trong đợt tuyển sinh chính của BKACAD, thường tổ chức vào tháng 6 hoặc 7. "
                "Thông tin chi tiết sẽ được công bố sớm trên trang chính thức."
            )

        turn_order = get_next_turn_order(session_id)
        save_turn(
            session_id,
            turn_order,
            user_query,
            intent_name,
            result.parameters,
            fulfillment_text
        )

        return {"response": fulfillment_text}

    except Exception as e:
        return {"response": f"Đã xảy ra lỗi khi xử lý câu hỏi: {str(e)}"}


def save_turn(session_id, turn_order, user_query, intent_name, parameters, bot_response):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT session_id FROM chatbot_sessions WHERE session_id = %s", (session_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO chatbot_sessions (session_id) VALUES (%s)", (session_id,))

        cursor.execute("""
                       INSERT INTO chatbot_turns (session_id, turn_order, user_query, intent_name, parameters,
                                                  bot_response)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       """, (session_id, turn_order, user_query, intent_name, str(parameters), bot_response))

        conn.commit()
    except Error as e:
        print(f"Lỗi khi lưu lượt chat: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def get_next_turn_order(session_id):
    conn = None
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
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def mark_session_ended(session_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE chatbot_sessions SET is_ended = TRUE WHERE session_id = %s", (session_id,))
        conn.commit()
    except Error as e:
        print(f"Lỗi khi đánh dấu kết thúc phiên: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
