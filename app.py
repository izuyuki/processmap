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
    以下の情報を基に、事業プロセスとナッジ提案を作成してください：

    事業名: {project_name}
    目標行動: {target_action}
    自治体名: {municipality}

    以下の形式で出力してください：

    1. プロセスマップ（10ステップ程度）
    2. 摩擦ポイントの特定
    3. 燃料ポイントの特定
    4. EASTフレームワークに基づくナッジ提案
    5. Mermaid形式のフローチャート（必ず```mermaid ...```で囲んでください）
    """

    with st.spinner("Geminiで分析中..."):
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            st.subheader("分析結果")
            st.write(response.text)

            # Mermaid部分だけ抽出して表示
            mermaid_match = re.search(r"```mermaid\\s*([\\s\\S]+?)```", response.text)
            if mermaid_match:
                st.subheader("プロセスフロー図")
                st.mermaid(mermaid_match.group(1))
            else:
                st.info("Mermaid形式のフローチャートが見つかりませんでした。")
        except Exception as e:
            import traceback
            st.error("APIリクエスト中にエラーが発生しました。")
            st.code(traceback.format_exc())

models = genai.list_models()
for m in models:
    print(m.name) 
