import streamlit as st
from PIL import Image

def main():
    st.set_page_config(page_title="Color Palette Analyzer", layout="centered")
    st.title("🎨 Color Palette Analyzer")
    st.write("イラストをアップロードして、色彩設計をサポートするアプリです。")

    # 【UX改善】「1枚のみ」の注意書きを追加
    # 【欠陥回避】あえてtype引数を外して、StreamlitのUIバグ（×ボタンが隠れる欠陥）を徹底回避
    uploaded_file = st.file_uploader(
        "解析したいイラストを選択してください (対応形式: PNG, JPG, JPEG) \n\n※一度にアップロードできるイラストは1枚のみです"
    )

    if uploaded_file is not None:
        # ファイル名から拡張子を抽出してチェック（大文字・小文字を区別しない）
        file_name = uploaded_file.name.lower()
        if not file_name.endswith(('.png', '.jpg', '.jpeg')):
            # アップローダーの下部にエラーを出すため、×ボタンを絶対に隠さない
            st.error("❌ 対応していないファイル形式です。PNG, JPG, JPEGのいずれかをアップロードしてください。")
        else:
            try:
                # 破損チェックを兼ねた画像の読み込み
                image = Image.open(uploaded_file)
                
                # 【出力】プレビュー表示
                st.subheader("アップロードされたイラスト")
                st.image(image, caption="解析対象の画像", use_container_width=True)
                st.success("✅ 画像の読み込みに成功しました！主要機能「画像アップロード」の動作確認完了です。")
                
            except Exception as e:
                # 【エラー処理】ファイル自体が壊れている場合の例外ハンドリング
                st.error(f"❌ 画像の読み込みに失敗しました。ファイルが破損している可能性があります。")
                st.caption(f"エラー詳細: {e}")

if __name__ == "__main__":
    main()