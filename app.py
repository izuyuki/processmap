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
            st.subheader("分析結果")
            st.write(response.text)

            # Graphviz部分だけ抽出して表示
            graphviz_match = re.search(r"```graphviz\s*([\s\S]+?)```", response.text)
            if graphviz_match:
                st.subheader("プロセスフロー図（Graphviz形式）")
                st.graphviz_chart(graphviz_match.group(1))
            else:
                # Mermaid記法があればGraphvizに変換して表示（日本語・分岐・ラベル対応）
                mermaid_match = re.search(r"```mermaid\s*([\s\S]+?)```", response.text)
                if mermaid_match:
                    mermaid_code = mermaid_match.group(1)
                    graphviz_code = "digraph G {\n"
                    for line in mermaid_code.splitlines():
                        # A[ノード名] -- ラベル --> B[ノード名];
                        m2 = re.match(r'\s*([A-Za-z0-9_]+)\[(.*?)\]\s*--\s*(.*?)\s*-->\s*([A-Za-z0-9_]+)\[(.*?)\];', line)
                        # A[ノード名] --> B[ノード名];
                        m1 = re.match(r'\s*([A-Za-z0-9_]+)\[(.*?)\]\s*--?>\s*([A-Za-z0-9_]+)\[(.*?)\];', line)
                        # B{ノード名} -- ラベル --> C[ノード名];
                        m4 = re.match(r'\s*([A-Za-z0-9_]+)\{(.*?)\}\s*--\s*(.*?)\s*-->\s*([A-Za-z0-9_]+)\[(.*?)\];', line)
                        # B{ノード名} --> C[ノード名];
                        m3 = re.match(r'\s*([A-Za-z0-9_]+)\{(.*?)\}\s*--?>\s*([A-Za-z0-9_]+)\[(.*?)\];', line)
                        if m2:
                            from_label = m2.group(2)
                            edge_label = m2.group(3)
                            to_label = m2.group(5)
                            graphviz_code += f'    "{from_label}" -> "{to_label}" [label="{edge_label}"];\n'
                        elif m1:
                            from_label = m1.group(2)
                            to_label = m1.group(4)
                            graphviz_code += f'    "{from_label}" -> "{to_label}";\n'
                        elif m4:
                            from_label = m4.group(2)
                            edge_label = m4.group(3)
                            to_label = m4.group(5)
                            graphviz_code += f'    "{from_label}" -> "{to_label}" [label="{edge_label}"];\n'
                        elif m3:
                            from_label = m3.group(2)
                            to_label = m3.group(4)
                            graphviz_code += f'    "{from_label}" -> "{to_label}";\n'
                    graphviz_code += "}"
                    st.subheader("プロセスフロー図（自動変換Graphviz）")
                    st.code(graphviz_code, language="text")
                    st.graphviz_chart(graphviz_code)
                else:
                    st.info("Graphviz形式またはMermaid形式のフローチャートが見つかりませんでした。")
        except Exception as e:
            import traceback
            st.error("APIリクエスト中にエラーが発生しました。")
            st.code(traceback.format_exc())

models = genai.list_models()
for m in models:
    print(m.name) 
