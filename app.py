import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px

def extract_colors(image, num_colors=5, exclude_bw=False):
    # 画像の縮小とRGBA変換
    image = image.copy()
    image.thumbnail((150, 150))
    image = image.convert("RGBA")
    pixels = np.array(image).reshape(-1, 4)
    
    # 透過ピクセルの除外
    mask_opaque = pixels[:, 3] > 200
    pixels = pixels[mask_opaque]
    pixels = pixels[:, :3] 
    
    # 白黒ピクセルの除外
    if exclude_bw:
        mask_white = np.all(pixels > 240, axis=1)
        mask_black = np.all(pixels < 15, axis=1)
        mask_valid = ~(mask_white | mask_black)
        pixels = pixels[mask_valid]
        
    # 色数不足の事前チェック
    if len(pixels) < num_colors or len(np.unique(pixels, axis=0)) < num_colors:
        return None, None
            
    # KMeansによるクラスタリング
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init="auto")
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    
    # 比率の計算（空のクラスタが発生した場合も長さを揃える）
    counts = np.bincount(kmeans.labels_, minlength=num_colors)
    
    # 空のグループ(0件)ができてしまったら失敗として扱う
    if 0 in counts:
        return None, None
        
    proportions = counts / counts.sum()
    
    return colors, proportions

def display_palette(colors):
    cols = st.columns(len(colors))
    for i, col in enumerate(cols):
        hex_color = '#{:02x}{:02x}{:02x}'.format(colors[i][0], colors[i][1], colors[i][2])
        with col:
            st.markdown(
                f'<div style="background-color: {hex_color}; height: 60px; border-radius: 8px; border: 2px solid #ddd; margin-bottom: 5px;"></div>', 
                unsafe_allow_html=True
            )
            st.code(hex_color, language="")

def main():
    # ページ設定とGoogle翻訳のお節介ブロック
    st.set_page_config(page_title="Color Palette Analyzer Pro", layout="centered")
    st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)
    
    st.title("🎨 Color Palette Analyzer Pro")
    st.write("イラストの色彩設計をAIが分析し、パレットと構成比率を可視化します。")

    # ファイルアップローダー
    uploaded_file = st.file_uploader(
        "イラストをアップロード (PNG, JPG, JPEG) \n\n※一度に1枚のみ対応"
    )

    if uploaded_file is not None:
        
        # 拡張子チェック
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ['png', 'jpg', 'jpeg']:
            st.error("❌ PNG, JPG, JPEG以外のファイルです。対応している画像をアップロードしてください。")
            return
            
        # 読み込みエラー（破損チェック）
        try:
            image = Image.open(uploaded_file)
            image.verify() # 破損チェック
            image = Image.open(uploaded_file) # verify後に再読み込み
        except Exception:
            st.error("❌ 画像の読み込みに失敗しました。ファイルが破損している可能性があります。")
            return

        st.subheader("🖼️ 解析対象")
        st.image(image, use_container_width=True)
        st.success("✅ 画像の読み込みに成功しました！")
        
        st.divider()
        
        st.subheader("⚙️ 抽出設定")
        col_cfg1, col_cfg2 = st.columns(2)
        with col_cfg1:
            num_colors = st.slider("抽出する色数", min_value=3, max_value=10, value=5)
        with col_cfg2:
            exclude_bw = st.checkbox("背景の白・黒を除外する", value=True)
        
        if st.button("✨ 色彩を分析する", type="primary", use_container_width=True):
            with st.spinner("AIが色彩をクラスタリング中..."):
                try:
                    colors, proportions = extract_colors(image, num_colors=num_colors, exclude_bw=exclude_bw)
                    
                    if colors is None:
                        st.warning("⚠️ 有効なピクセルが不足しています。画像内の色数が少ないか、除外設定を見直してください。")
                    else:
                        st.subheader("🎨 抽出されたカラーパレット")
                        display_palette(colors)
                        
                        st.subheader("📊 色彩構成比率")
                        hex_colors = ['#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2]) for c in colors]
                        df_plot = pd.DataFrame({"Color": hex_colors, "Ratio": proportions})
                        
                        fig = px.pie(
                            df_plot, values="Ratio", names="Color", color="Color",
                            color_discrete_map={c: c for c in hex_colors}, hole=0.4
                        )
                        fig.update_traces(textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                        st.success("✅ 全ての分析が完了しました！")
                except Exception as e:
                    st.error("❌ 画像の解析中に予期せぬエラーが発生しました。")
                    st.caption(f"Error: {e}")

if __name__ == "__main__":
    main()