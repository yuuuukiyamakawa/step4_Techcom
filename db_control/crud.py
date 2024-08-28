# main.pyで使用する関数

import pandas as pd
from datetime import datetime
import json
from .dbmodels import MenteeMaster, UserData, Mentoring, MentorMaster, Feedback
import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv


# 認証書の取得
base_path = os.path.dirname(os.path.abspath(__file__))
ssl_cert_path = os.path.join(base_path, 'DigiCertGlobalRootG2.crt.pem')

load_dotenv()
HOST = os.getenv('HOST')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')


# DB接続情報
config = {
    'host': HOST,
    'user': USER,
    'password': PASSWORD,
    'database': DATABASE,
    'port': '3306',
    'connection_timeout': 10, 
}
print(config)


# Home画面メンティーリスト用
def get_mentee_data(mentor_id):
    conn = None
    result_json = None

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
        cursor = conn.cursor()

        query = """
            SELECT MenteeMaster.id, UserData.name, UserData.birth_date, UserData.gender, UserData.join_date
            FROM MenteeMaster
            LEFT JOIN UserData ON MenteeMaster.employee_code = UserData.employee_code
            WHERE MenteeMaster.mentor_id = %s
        """
        cursor.execute(query, (mentor_id,))
        df = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])

        cursor.close()

        # 年齢データの作成
        today = datetime.today()
        df['birth_date'] = pd.to_datetime(df['birth_date'])
        df['join_date'] = pd.to_datetime(df['join_date'])

        df['age'] = df['birth_date'].apply(lambda x: (int(today.strftime('%Y%m%d')) - int(x.strftime('%Y%m%d'))) // 10000)

        # 入社年数データの作成
        df['working_years'] = df['join_date'].apply(lambda x: (int(today.strftime('%Y%m%d')) - int(x.strftime('%Y%m%d'))) // 10000 + 1)

        # データの抽出
        df = df[['id', 'name', 'age', 'gender', 'working_years']]
        result_json = df.to_json(orient='records', force_ascii=False)  # orient='records'で、各行が個別のJSONオブジェクトとしてリストに格納されるように指定。force_ascii=Falseで、非ASCII文字（日本語など）をそのまま使用。
        result_json = json.loads(result_json)  # json形式にパース

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        result_json = None  # エラーが発生した場合はNoneを返す

    finally:
        # 接続が確立されている場合のみクローズ
        if conn is not None:
            conn.close()

    return result_json


# メンタリングスケジュールリスト用
def get_mentoring_data(mentor_id):
    conn = None
    result_json = None

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
        cursor = conn.cursor()
        
        query = """
            SELECT MenteeMaster.id AS mentee_id, Mentoring.id AS mentoring_id, UserData.name, 
                   UserData.birth_date, UserData.gender, UserData.join_date,
                   Mentoring.mtg_date, Mentoring.mtg_start_time, 
                   Mentoring.request_to_mentor_for_attitude, Mentoring.request_to_mentor_for_content,
                   Mentoring.pre_advise_to_mentor_for_mtg
            FROM MenteeMaster
            LEFT JOIN UserData ON MenteeMaster.employee_code = UserData.employee_code
            LEFT JOIN Mentoring ON MenteeMaster.id = Mentoring.mentee_id
            WHERE MenteeMaster.mentor_id = %s
            AND Mentoring.mtg_content IS NULL
            AND Mentoring.mtg_date IS NOT NULL
        """
        
        cursor.execute(query, (mentor_id,))
        df = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])
        cursor.close()

        # 日付データ形式の変換
        df['mtg_date'] = pd.to_datetime(df['mtg_date']).dt.strftime('%Y/%m/%d')

        # 時間データ形式の変換
        df['mtg_start_time'] = pd.to_timedelta(df['mtg_start_time']).apply(lambda x: (datetime.min + x).strftime('%H:%M'))

        # 年齢データの作成
        today = datetime.today()
        df['age'] = df['birth_date'].apply(lambda x: (int(today.strftime('%Y%m%d')) - int(x.strftime('%Y%m%d'))) // 10000)

        # 入社年数データの作成
        df['working_years'] = df['join_date'].apply(lambda x: (int(today.strftime('%Y%m%d')) - int(x.strftime('%Y%m%d'))) // 10000 + 1)

        # 必要な列のみ抽出
        df = df[['mentoring_id', 'mentee_id', 'name', 'age', 'gender', 'working_years',
                 'mtg_date', 'mtg_start_time', 'request_to_mentor_for_attitude', 
                 'request_to_mentor_for_content', 'pre_advise_to_mentor_for_mtg']]
        df = df.sort_values('mtg_date', ascending=True)

        # 結果をJSON形式に変換
        result_json = df.to_json(orient='records', force_ascii=False)
        result_json = json.loads(result_json)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        result_json = None  # エラーが発生した場合はNoneを返す

    finally:
        # 接続が確立されている場合のみクローズ
        if conn is not None:
            conn.close()

    return result_json


# メンタリング開始時の情報取得
def get_mentoring_details(mentoring_id):
    conn = None  # connを初期化
    result_json = None

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
        cursor = conn.cursor()

        query = """
            SELECT MenteeMaster.id, UserData.name, UserData.birth_date, UserData.gender, UserData.join_date,
                   Mentoring.id AS mentoring_id, Mentoring.mtg_date, Mentoring.mtg_start_time,
                   Mentoring.request_to_mentor_for_attitude, Mentoring.request_to_mentor_for_content,
                   Mentoring.pre_advise_to_mentor_for_mtg, Mentoring.pre_mtg_content_summary
            FROM MenteeMaster
            LEFT JOIN UserData ON MenteeMaster.employee_code = UserData.employee_code
            LEFT JOIN Mentoring ON MenteeMaster.id = Mentoring.mentee_id
            WHERE Mentoring.id = %s
        """

        cursor.execute(query, (mentoring_id,))
        df = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])
        cursor.close()

        # 日付データ形式の変換
        df['mtg_date'] = pd.to_datetime(df['mtg_date']).dt.strftime('%Y/%m/%d')

        # 時間データ形式の変換
        df['mtg_start_time'] = pd.to_timedelta(df['mtg_start_time']).apply(lambda x: (datetime.min + x).strftime('%H:%M'))

        # 年齢データの作成
        today = datetime.today()
        df['age'] = df['birth_date'].apply(lambda x: (int(today.strftime('%Y%m%d')) - int(x.strftime('%Y%m%d'))) // 10000)

        # 入社年数データの作成
        df['working_years'] = df['join_date'].apply(lambda x: (int(today.strftime('%Y%m%d')) - int(x.strftime('%Y%m%d'))) // 10000 + 1)

        # 必要な列だけを抽出
        df = df[['id', 'name', 'age', 'gender', 'working_years', 'mentoring_id', 'mtg_date', 
                 'mtg_start_time', 'request_to_mentor_for_attitude', 'request_to_mentor_for_content', 
                 'pre_advise_to_mentor_for_mtg', 'pre_mtg_content_summary']]
        df = df.sort_values('mtg_date', ascending=True)

        # 結果をJSON形式に変換
        result_json = df.to_json(orient='records', force_ascii=False)
        result_json = json.loads(result_json)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        result_json = None  # エラーが発生した場合はNoneを返す

    finally:
        # 接続が確立されている場合のみクローズ
        if conn is not None:
            conn.close()

    return result_json


# メンタリング結果の保存
def update_data(mentoring_id, data):
    conn = None

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")

        cursor = conn.cursor()

        # 更新クエリを作成
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"""
            UPDATE Mentoring
            SET {set_clause}
            WHERE id = %s
        """

        # 更新する値をリストとして準備
        values = list(data.values())
        values.append(mentoring_id)

        try:
            cursor.execute(query, values)
            conn.commit()
            print("保存完了")
            return "保存完了"

        except mysql.connector.Error as err:
            print("更新に失敗しました:", err)
            conn.rollback()
            return "保存失敗"

        finally:
            cursor.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("ユーザー名かパスワードに問題があります")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("データベースが存在しません")
        else:
            print(err)
        return "保存失敗"

    finally:
        if conn is not None:
            conn.close()


# メンタースキルマップ
def get_feedback_data(mentor_id, FB_flg):
    conn = None
    result_json = None

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")

        cursor = conn.cursor()

        # SQLクエリを作成
        query = """
            SELECT MentorMaster.id AS mentor_id, UserData.name, Mentoring.id AS mentoring_id, Mentoring.mtg_date,
                   Feedback.listening_score, Feedback.questioning_score, Feedback.feedbacking_score, 
                   Feedback.empathizing_score, Feedback.motivating_score, Feedback.coaching_score, 
                   Feedback.teaching_score, Feedback.analyzing_score, Feedback.inspiration_score, 
                   Feedback.vision_score, Feedback.mentee_feedback_flg
            FROM Feedback
            LEFT JOIN Mentoring ON Feedback.mentoring_id = Mentoring.id
            LEFT JOIN MenteeMaster ON Mentoring.mentee_id = MenteeMaster.id
            LEFT JOIN MentorMaster ON MenteeMaster.mentor_id = MentorMaster.id
            LEFT JOIN UserData ON MentorMaster.employee_code = UserData.employee_code
            WHERE MenteeMaster.mentor_id = %s
            AND Feedback.mentee_feedback_flg = %s
        """

        try:
            cursor.execute(query, (mentor_id, FB_flg))
            df = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])

            # 日付データ形式の変換
            df['mtg_date'] = df['mtg_date'].apply(lambda x: x.strftime('%Y/%m/%d') if pd.notnull(x) else None)

            # トータルスコアの作成
            score_columns = ['listening_score', 'questioning_score', 'feedbacking_score', 'empathizing_score',
                             'motivating_score', 'coaching_score', 'teaching_score', 'analyzing_score',
                             'inspiration_score', 'vision_score']
            df['total_score'] = df[score_columns].sum(axis=1)

            # データの抽出
            df = df[['mentor_id', 'name', 'mentoring_id', 'mtg_date'] + score_columns + ['total_score', 'mentee_feedback_flg']]

            # 結果をJSON形式に変換
            result_json = df.to_json(orient='records', force_ascii=False)
            result_json = json.loads(result_json)

        except mysql.connector.Error as err:
            print("データ取得に失敗しました:", err)
            result_json = None

        finally:
            cursor.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("ユーザー名かパスワードに問題があります")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("データベースが存在しません")
        else:
            print(err)
        result_json = None

    finally:
        if conn is not None:
            conn.close()

    return result_json


# 確認用
def get_mentoring_results():
    conn = None
    result_json = None

    try:
        conn = mysql.connector.connect(**config)
        print("Connection established")
        cursor = conn.cursor()

        query = """
            SELECT MenteeMaster.id, UserData.name, UserData.birth_date, UserData.gender, UserData.join_date,
                   Mentoring.id AS mentoring_id, Mentoring.mtg_date, Mentoring.mtg_start_time,
                   Mentoring.request_to_mentor_for_attitude, Mentoring.request_to_mentor_for_content,
                   Mentoring.mtg_content, Mentoring.mtg_content_summary, Mentoring.mtg_memo,
                   Mentoring.mtg_content_speaker_identification, Mentoring.pre_advise_to_mentor_for_mtg,
                   Mentoring.pre_mtg_content_summary
            FROM MenteeMaster
            LEFT JOIN UserData ON MenteeMaster.employee_code = UserData.employee_code
            LEFT JOIN Mentoring ON MenteeMaster.id = Mentoring.mentee_id
        """

        cursor.execute(query)
        df = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])
        cursor.close()

        # 日付データ形式の変換
        df['mtg_date'] = pd.to_datetime(df['mtg_date'], errors='coerce').dt.strftime('%Y/%m/%d').fillna('')

        # 時間データ形式の変換
        df['mtg_start_time'] = pd.to_timedelta(df['mtg_start_time'], errors='coerce').apply(lambda x: str(x).split()[-1] if pd.notnull(x) else '')

        # 年齢データの作成
        today = datetime.today()
        df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
        df['age'] = df['birth_date'].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)) if pd.notnull(x) else '')

        # 入社年数データの作成
        df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce')
        df['working_years'] = df['join_date'].apply(lambda x: today.year - x.year + ((today.month, today.day) >= (x.month, x.day)) if pd.notnull(x) else '')

        # 必要な列だけを抽出
        df = df[['mentoring_id', 'id', 'name', 'age', 'gender', 'working_years', 'mtg_date', 
                 'mtg_start_time', 'request_to_mentor_for_attitude', 'request_to_mentor_for_content', 
                 'mtg_content', 'mtg_content_summary', 'mtg_memo', 'mtg_content_speaker_identification',
                 'pre_advise_to_mentor_for_mtg', 'pre_mtg_content_summary']]
        df = df.sort_values('mtg_date', ascending=True)

        # 結果をJSON形式に変換
        result_json = df.to_json(orient='records', force_ascii=False)
        result_json = json.loads(result_json)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        result_json = None

    finally:
        # 接続が確立されている場合のみクローズ
        if conn is not None:
            conn.close()

    return result_json
