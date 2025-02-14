import openai

# テキストが人を傷つける可能性があるか判定する
# OpenAI クライアントの作成（APIキーを設定）
openai_api_key = "sk-xxxxx"

client = openai.OpenAI(api_key=openai_api_key)

def generate_response(child_statement: str, response: str, language="Japanese") -> bool | str:
    
    
    prompt = f"""
    以下の文章は {language} で書かれています。

    子供の発言:
    {child_statement}
    
    声掛け:
    {response}
    
    この声掛けを100字以内の、小学生にわかるレベルの、より前向きで適切な言葉に言い換えてください。
    言語は {language} で、言い換えること。もし日本語であれば小学校3年生までの漢字を使うこと。また、言い換えた言葉のみを出力すること。

    """
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは優しいカウンセラーです。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    result = completion.choices[0].message.content.strip()
    
    if result.lower() == "false":
        return False
    return result



def is_hurtful_text(text, language="ja"):
    """
    指定されたテキストが人を傷つける可能性がある場合は True を返し、
    そうでない場合は False を返す。

    :param text: 判定したい文章 (str)
    :param language: 解析する言語 (str) (例: "ja", "en", "fr", "es", "uk")
    :return: True (傷つける可能性あり) / False (傷つける可能性なし)
    """
    prompt = f"""
    以下の文章が人を傷つけるものであるか判定してください。
    使用する言語: {language}

    判定基準:
    1. 人種、性別、国籍、宗教、性的指向、障害などに対する攻撃的な表現が含まれている。
    2. 個人やグループを侮辱したり、脅迫したりする内容がある。
    3. いじめやハラスメントにつながる可能性がある。
    4. 子供の自尊心を傷つける可能性がある。
    5. 子供のメンタルヘルスを悪化させる可能性がある。
    6．子供を馬鹿にしたり、無視したりする内容がある。
    7. その他、嫌味や人を傷つける可能性があると判断される内容が含まれている。

    文章: "{text}"

    上記の基準に該当する場合は True、該当しない場合は False と出力してください。
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは文章の内容を判定するAIです。"},
            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content.strip()

    return result.lower() == "true"



# テキストを翻訳する
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    指定した言語から別の言語へ翻訳する関数 (openai>=1.0.0)
    
    :param text: 翻訳したいテキスト
    :param source_lang: 翻訳前の言語
    :param target_lang: 翻訳後の言語
    :return: 翻訳後のテキスト
    """
    prompt = f"Return only the translated text with no additional explanation. Translate the following text from {source_lang} to {target_lang}:\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional translator who accurately translates."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


##print(str(is_hurtful_text("あなたはとてもいい人ですね")))
#print(translate_text("それはとてもつらかったね。そういう時は周りの大人に相談するといいよ。", "Japanese", "Ukrainian"))


# 使用例
if __name__ == "__main__":
    child_statement = "今日は勉強がはかどらなかった。"
    response = "早く死ねばいいのに"
    language = "Japanese"

    print(is_hurtful_text(response, language))
    print(generate_response(child_statement, response, language))
