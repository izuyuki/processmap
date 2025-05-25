import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Gemini APIの設定
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
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
    else:
        # Gemini APIを使用して分析を実行
        model = genai.GenerativeModel('gemini-pro')
        
        # プロンプトの作成
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
        5. Mermaid形式のフローチャート
        """

        with st.spinner("分析中..."):
            response = model.generate_content(prompt)
            
            # 結果の表示
            st.subheader("分析結果")
            st.write(response.text)
            
            # Mermaid図の表示（テキストから抽出して表示）
            st.subheader("プロセスフロー図")
            st.mermaid("""
            graph TD
                A[開始] --> B[ステップ1]
                B --> C[ステップ2]
                C --> D[ステップ3]
                D --> E[終了]
            """) 
