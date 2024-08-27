
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('OPEN_API_KEY')


# 話者分離
def some_speaker_separation(mtg_content):

    message = (
        '＃依頼'
        'あなたは｛＃役割｝です。次の｛＃ルール｝を必ず守り、｛＃形式｝の形式でデータを出力してください。対象となるデータは｛＃参照｝を使用してください。'
        '＃役割'
        'あなたは議事録作成担当者です。'
        '＃ルール'
        '・この会議は、メンターとメンティーの２名で行われています。'
        '・どちらが話をしているか、話者を特定して下さい。'
        '＃形式'
        '・「メンター：」と「メンティー：」で話者分離を行う。'
        '＃参照'
        f'{mtg_content}'
    )

    client = OpenAI(api_key = API_KEY)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return completion.choices[0].message.content


# 要約
def summary(mtg_speaker_separation):

    message = (
        '＃依頼'
        'あなたは｛＃役割｝です。次の｛＃ルール｝を必ず守り、｛＃形式｝の形式でデータを出力してください。対象となるデータは｛＃参照｝を使用してください。'
        '＃役割'
        'あなたは議事録要約担当者です。'
        '＃ルール'
        '・会議の内容を要約してください。'
        '＃形式'
        '・「サマリー：」として、100文字以内での要約。「詳細：」として、400文字以内で要約。'
        '＃参照'
        f'{mtg_speaker_separation}'
    )

    client = OpenAI(api_key = API_KEY)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return completion.choices[0].message.content


# メンターへのアドバイス作成
def advice(mtg_speaker_separation):

    message = (
        '＃依頼'
        'あなたは｛＃役割｝です。次の｛＃ルール｝を必ず守り、｛＃形式｝の形式でデータを出力してください。対象となるデータは｛＃参照｝を使用してください。'
        '＃役割'
        'あなたは会議の仕方に関してアドバイスを行う者です。'
        '＃ルール'
        '・メンターに対してアドバイスをしてください。'
        '・次回の会議に向けて、「改善点」と「良かった点」をアドバイスしてください。'
        '・アドバイスがなければ、「なし」としてください。'
        '＃形式'
        '・「改善点：」は200文字以内で箇条書き。「良かった点：」は200文字以内で箇条書き。'
        '＃参照'
        f'{mtg_speaker_separation}'
    )

    client = OpenAI(api_key = API_KEY)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return completion.choices[0].message.content