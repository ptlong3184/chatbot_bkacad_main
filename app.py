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


def get_major_info_by_keyword(keyword: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT major_name, description
                FROM majors_info
                WHERE major_name LIKE %s
                   OR description LIKE %s \
                """
        like_kw = f"%{keyword}%"
        cursor.execute(query, (like_kw, like_kw))
        major = cursor.fetchone()

        if major:
            return f"Ngành {major['major_name']}:\n{major['description']}"
        else:
            return "Không tìm thấy thông tin ngành học phù hợp."

    except Error as e:
        print(f"Lỗi khi tìm ngành học: {e}")
        return "Đã xảy ra lỗi khi tìm ngành học."
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def get_all_majors():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT major_name, description FROM majors_info")
        majors = cursor.fetchall()
        if not majors:
            return "Hiện tại chưa có thông tin ngành học."

        response = "Các ngành đào tạo tại BKACAD:\n"
        for m in majors:
            response += f"- {m['major_name']}: {m['description']}\n"
        return response

    except Error as e:
        print(f"Lỗi truy vấn ngành học: {e}")
        return "Đã xảy ra lỗi khi truy vấn ngành học."
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def get_vieclam_info_by_intent(intent_name: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT content FROM vieclam_info WHERE category = %s"
        cursor.execute(query, (intent_name,))
        result = cursor.fetchone()

        return result["content"] if result else "Hiện chưa có thông tin việc làm cho yêu cầu này."

    except Error as e:
        print(f"Lỗi truy vấn việc làm: {e}")
        return "Đã xảy ra lỗi khi truy vấn thông tin việc làm."

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# Truy vấn học phí
# def get_program_tuition_by_intent():
#     try:
#         conn = get_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         query = """
#                 SELECT p.name AS program_name,
#                        m.major_name,
#                        p.duration,
#                        t.fee_amount,
#                        t.notes
#                 FROM programs p
#                          LEFT JOIN majors_info m ON p.major_id = m.id
#                          LEFT JOIN tuition_fees t ON t.program_id = p.id \
#                 """
#         cursor.execute(query)
#         result = cursor.fetchall()
#
#         return result if result else None
#
#     except Error as e:
#         print(f"Lỗi truy vấn học phí: {e}")
#         return None
#
#     finally:
#         if conn and conn.is_connected():
#             cursor.close()
#             conn.close()


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

        suggestions = []

        if intent_name == "IKetThuc":
            mark_session_ended(session_id)


        elif intent_name == "I_gia_tri_hocbong":

            data = get_scholarship_info()

            if data:

                fulfillment_text = "📚 Giá trị học bổng theo điểm thi:\n"

                for item in data:
                    fulfillment_text += f"- {item['score_range']}: {item['amount']} VNĐ\n"

            suggestions = [

                "Làm sao để đăng ký học bổng?",

                "Hồ sơ học bổng cần những gì?",

                "Có cần học sinh giỏi không?",

                "Học sinh nghèo có được học bổng không?",

                "Có cần hoạt động ngoại khóa không?",

                "Giải thưởng đạt được có giúp xin học bổng không?",

                "Đăng ký học bổng ở đâu?",

                "Thời gian đăng ký học bổng là khi nào?",

                "Có kỳ thi học bổng riêng không?"

            ]

            return {

                "response": fulfillment_text,

                "suggestions": suggestions

            }

        elif intent_name == "I_loai_hocbong":
            suggestions = [
                "Điều kiện xét học bổng là gì?",
                "Cần những giấy tờ gì để đăng ký học bổng?",
                "Làm sao để đăng ký học bổng?",
                "Hoàn cảnh gia đình có ảnh hưởng đến học bổng không?",
                "Có cần tham gia hoạt động ngoại khóa không?",
                "Học lực bao nhiêu thì đủ điều kiện học bổng?",
                "Giải thưởng nào được chấp nhận khi xét học bổng?",
                "Nộp hồ sơ học bổng ở đâu?",
                "Hạn đăng ký học bổng là khi nào?"
            ]

            return {
                "response": fulfillment_text,
                "suggestions": suggestions
            }

        elif intent_name == "I_tuyensinh_hocphi_theo_hocbong":
            suggestions = [
                "Học bổng có làm giảm học phí không?",
                "Cần điều kiện gì để được học bổng?",
                "Nếu học lực yếu thì có được học bổng không?",
                "Sau khi có học bổng thì học phí còn bao nhiêu?",
                "Học bổng có áp dụng cho năm sau không?",
                "Học bổng có bao gồm ký túc xá không?",
                "Có thể kết hợp nhiều loại học bổng không?",
                "Nộp học bổng ở đâu?",
                "Khi nào có kết quả học bổng?"
            ]

            return {
                "response": fulfillment_text,
                "suggestions": suggestions
            }



        elif intent_name == "I_danhsach_nganhhoc":
            fulfillment_text = get_all_majors()
            suggestions = [
                "Ngành Lập trình",
                "Ngành Thiết kế đồ họa",
                "Ngành Quản trị mạng",
                "Ngành Marketing"
            ]

        elif intent_name == "I_laptrinh_lagi":
            suggestions = [
                "Học lập trình có khó không?",
                "Học lập trình cần kỹ năng gì?",
                "Ra trường làm gì?",
                "Ngành này có phù hợp với nữ không?",
                "Nên chọn lập trình hay quản trị mạng?",
                "Nếu không giỏi toán thì nên chọn ngành nào?",
                "Nếu học tốt toán thì nên chọn ngành nào?",
                "So sánh lập trình và quản trị mạng",
                "So sánh lập trình và thiết kế đồ họa"
            ]

            # ✅ Return ngay tại đây nếu đã có response và suggestions
            return {
                "response": fulfillment_text,
                "suggestions": suggestions
            }

        elif intent_name == "I_thietkedohoa_lagi":
            suggestions = [
                "Ngành thiết kế đồ họa có khó không?",
                "Cần kỹ năng gì để học thiết kế?",
                "Ngành này có phù hợp với tôi không?",
                "Ra trường làm nghề gì?",
                "Dùng công cụ nào trong ngành này?",
                "So sánh thiết kế và lập trình",
                "So sánh thiết kế và marketing",
                "Tôi vẽ tốt thì nên chọn ngành này không?",
                "Tôi vẽ chưa tốt thì nên chọn ngành này không?"
            ]
            return {
                "response": fulfillment_text,
                "suggestions": suggestions
            }

        elif intent_name == "I_quantrimang_lagi":
            suggestions = [
                "Học ngành này có khó không?",
                "Cần kỹ năng gì để học quản trị mạng?",
                "Ngành này có phù hợp với tôi không?",
                "Ra trường làm việc gì?",
                "Dùng công cụ nào trong ngành này?",
                "So sánh lập trình và quản trị mạng",
                "Nên học lập trình hay quản trị mạng?",
                "Tôi không giỏi toán nên học ngành này không?",
                "Tôi học giỏi toán thì chọn ngành này không?"
            ]
            return {
                "response": fulfillment_text,
                "suggestions": suggestions
            }
        elif intent_name == "I_marketing_la_gi":
            suggestions = [
                "Học ngành này có khó không?",
                "Cần kỹ năng gì để học Marketing?",
                "Tôi có phù hợp với ngành này không?",
                "Ra trường làm nghề gì?",
                "Dùng công cụ gì trong ngành Marketing?",
                "So sánh Marketing và thiết kế đồ họa",
                "Tôi nên chọn thiết kế hay marketing?",
                "Nếu tôi không giỏi giao tiếp nên học ngành này không?",
                "Nếu tôi giao tiếp tốt thì nên chọn ngành này không?"
            ]
            return {
                "response": fulfillment_text,
                "suggestions": suggestions
            }





        elif intent_name.startswith("I_vieclam_ho_tro"):
            fulfillment_text = get_vieclam_info_by_intent(intent_name.replace("I_", "").lower())

        # Lưu lượt chat
        turn_order = get_next_turn_order(session_id)
        save_turn(
            session_id,
            turn_order,
            user_query,
            intent_name,
            result.parameters,
            fulfillment_text
        )

        return {
            "response": fulfillment_text,
            "suggestions": suggestions
        }

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
