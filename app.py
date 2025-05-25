import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# .envからAPIキーを読み込む
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Gemini APIキーが設定されていません。プロジェクトルートの.envファイルにGOOGLE_API_KEYを記載してください。")
    st.stop()

# Gemini APIの初期化
genai.configure(api_key=GOOGLE_API_KEY)

# ページ設定
st.set_page_config(
    page_title="事業プロセス分析＆ナッジ提案アプリ",
    page_icon="🎯",
    layout="wide"
)

# タイトル
st.title("事業プロセス分析＆ナッジ提案アプリ")

# 入力フォーム
with st.form("input_form"):
    project_name = st.text_input("事業名")
    target_action = st.text_input("目標行動")
    municipality = st.text_input("自治体名")
    submit_button = st.form_submit_button("分析開始")

if submit_button:
    if not all([project_name, target_action, municipality]):
        st.error("すべての項目を入力してください。")
        st.stop()

    prompt = f"""
    以下の情報をもとに、プロセスマップとナッジ案を作成してください。

    事業名: {project_name}
    目標行動: {target_action}
    自治体名: {municipality}

    出力形式：
    1. プロセスマップ（10ステップ程度）
    2. 摩擦ポイント
    3. 燃料ポイント
    4. EASTフレームワークに基づくナッジ案
    5. Mermaid形式のフローチャート（下記の例のように必ず出力してください）

    例：
    ```mermaid
    graph TD
        A[開始] --> B[ステップ1]
        B --> C[ステップ2]
        C --> D[ステップ3]
        D --> E[終了]
    ```
    """

    with st.spinner("Geminiで分析中..."):
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2048
                }
            )
            # Geminiの出力からMermaidコードブロックと見出し行を除去
            cleaned_text = re.sub(r"```mermaid[\s\S]+?```", "", response.text)
            cleaned_text = re.sub(r"\n?5\. Mermaid形式のフローチャート\n?", "", cleaned_text)
            st.subheader("分析結果")
            st.write(cleaned_text.strip())
        except Exception as e:
            import traceback
            st.error("APIリクエスト中にエラーが発生しました。")
            st.code(traceback.format_exc())

models = genai.list_models()
for m in models:
    print(m.name) 
