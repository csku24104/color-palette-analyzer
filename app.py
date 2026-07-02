import streamlit as st
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def extract_colors(image, num_colors=5, exclude_bw=False):
    # 1. 計算量削減のため、画像をリサイズ (150x150程度で十分な精度が出ます)
    image = image.copy()
    image.thumbnail((150, 150))
    image = image.convert("RGB")
    
    # 2. 画像をnumpy配列に変換し、(ピクセル数, 3)の形にリシェイプ
    pixels = np.array(image).reshape(-1, 3)
    
    # 3. 白・黒の除外処理
    if exclude_bw:
        # 白: RGBすべてが240以上 / 黒: RGBすべてが15以下 (閾値は調整可能です)
        mask_white = np.all(pixels > 240, axis=1)
        mask_black = np.all(pixels < 15, axis=1)
        mask_valid = ~(mask_white | mask_black) # 白でも黒でもないピクセルを残す
        pixels = pixels[mask_valid]
        
        # もし除外した結果、ピクセルが指定色数未満になってしまった場合のフェイルセーフ
        if len(pixels) < num_colors:
            return None
            
    # 4. K-means法で色をクラスタリング
    # n_init="auto" はscikit-learnの警告を回避するため
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init="auto")
    kmeans.fit(pixels)
    
    # クラスタの中心（代表色）を整数化して返す
    colors = kmeans.cluster_centers_.astype(int)
    return colors

def display_palette(colors):
    """抽出した色をStreamlit上でカラーパレットとして綺麗に表示する関数"""
    cols = st.columns(len(colors))
    for i, col in enumerate(cols):
        # RGBをHexコード（16進数）に変換
        hex_color = '#{:02x}{:02x}{:02x}'.format(colors[i][0], colors[i][1], colors[i][2])
        with col:
            # HTMLを使って色付きの四角形を描画
            st.markdown(f'<div style="background-color: {hex_color}; height: 50px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 5px;"></div>', unsafe_allow_html=True)
            st.caption(hex_color)

def main():
    st.set_page_config(page_title="Color Palette Analyzer", layout="centered")
    st.title("🎨 Color Palette Analyzer")
    st.write("イラストをアップロードして、色彩設計をサポートするアプリです。")

    uploaded_file = st.file_uploader(
        "解析したいイラストを選択してください (対応形式: PNG, JPG, JPEG) \n\n※一度にアップロードできるイラストは1枚のみです"
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        if not file_name.endswith(('.png', '.jpg', '.jpeg')):
            st.error("❌ 対応していないファイル形式です。PNG, JPG, JPEGのいずれかをアップロードしてください。")
        else:
            try:
                image = Image.open(uploaded_file)
                st.subheader("アップロードされたイラスト")
                st.image(image, caption="解析対象の画像", use_container_width=True)
                st.success("✅ 画像の読み込みに成功しました！")
                
                st.divider() # 区切り線
                
                # 【新規追加】抽出設定のUI
                st.subheader("⚙️ 抽出設定")
                exclude_bw = st.checkbox("背景の白・黒を抽出から除外する")
                
                if st.button("代表色を抽出する", type="primary"):
                    with st.spinner("K-means法で色を分析中..."):
                        colors = extract_colors(image, num_colors=5, exclude_bw=exclude_bw)
                        
                        if colors is None:
                            st.warning("⚠️ 画像内の有効な色が少なすぎるため、抽出できませんでした（白・黒を除外しすぎた可能性があります）。")
                        else:
                            st.subheader("抽出されたカラーパレット")
                            display_palette(colors)
                
            except Exception as e:
                st.error("❌ 画像の読み込みに失敗しました。ファイルが破損している可能性があります。")
                st.caption(f"エラー詳細: {e}")

if __name__ == "__main__":
    main()