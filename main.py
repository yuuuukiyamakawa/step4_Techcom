# API一覧

from fastapi import FastAPI, Request
from db_control import crud, GPT
from db_control.dbmodels import MenteeMaster, UserData, Mentoring, MentorMaster, Feedback
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'PUT'],
    allow_headers=['*'],
)


@app.get('/')
def read_root():
    return {'message': 'Hello World'}


# Home画面メンティーリスト取得API
@app.get("/mentor/{mentor_id}/home")
def get_mentee_list(mentor_id: int):
    result = crud.get_mentee_data(mentor_id)
    return result


# メンタリングスケジュールリスト取得API
@app.get("/mentor/{mentor_id}/mentoring_schedule")
def get_mentoring_list(mentor_id: int):
    result = crud.get_mentoring_data(mentor_id)
    return result


# 1on1開始のAPI
@app.get("/mentoring/{mentoring_id}")
def get_mentoring_info(mentoring_id: int):
    result = crud.get_mentoring_details(mentoring_id)
    return result


# 1on1履歴保存API
@app.put("/mentoring/{mentoring_id}")

# mtg_contentとmtg_memoの保存
async def save_mentoring_data(mentoring_id: int, request: Request):
    data = await request.json()
    # data = {
    #     "mtg_content": "11111",
    #     "mtg_memo": "1111",
    # }
    result = crud.update_data(mentoring_id, data)
    return result

# 話者分離 → 要約
async def process_after_meeting(mentoring_id: int, request: Request):
    data = await request.json()
    mtg_content = data['mtg_content']
    mtg_speaker_separation = await GPT.some_speaker_separation(mtg_content)
    mtg_content_summary = GPT.summary(mtg_speaker_separation)
    advise_to_mentor_for_mtg = GPT.advice(mtg_speaker_separation)
    data = {
        "mtg_content_speaker_identification": mtg_speaker_separation,
        "mtg_content_summary": mtg_content_summary,
        "advise_to_mentor_for_mtg": advise_to_mentor_for_mtg,
    }
    result = crud.update_data(mentoring_id, data)
    return result


# メンタースキルマップ取得API
@app.get("/mentor/{mentor_id}/skillmap/{FB_flg}")
def get_mentor_skill(mentor_id: int, FB_flg: bool):
    result = crud.get_feedback_data(mentor_id, FB_flg)
    return result


# 1on1履歴閲覧用API
    # @app.get("/mentor/{mentor_id}/history")
    # def read_mentoring_history(mentor_id: int,):
    #         model = 
    #     result = a
    #     return result


# 確認用
@app.get("/mentoring_list")
def get_mentoring_list():
    result = crud.get_mentoring_results()
    return result