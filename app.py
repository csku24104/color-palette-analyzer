import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px

def extract_colors(image, num_colors=5, exclude_bw=False):
    """
    K-means法を用いて画像から主要な色とその割合を抽出する
    """
    # 1. 計算量削減のため、画像をリサイズ
    image = image.copy()
    image.thumbnail((150, 150))
    
    # 2. 透過PNG対応: RGBAで読み込み
    image = image.convert("RGBA")
    pixels = np.array(image).reshape(-1, 4)
    
    # 3. 透過ピクセル（アルファ値が低い部分）を完全に除外
    mask_opaque = pixels[:, 3] > 200
    pixels = pixels[mask_opaque]
    
    # RGBのみを取り出す
    pixels = pixels[:, :3] 
    
    # 4. 白・黒の除外処理
    if exclude_bw:
        mask_white = np.all(pixels > 240, axis=1)
        mask_black = np.all(pixels < 15, axis=1)
        mask_valid = ~(mask_white | mask_black)
        pixels = pixels[mask_valid]
        
    # フェイルセーフ
    if len(pixels) < num_colors:
        return None, None
            
    # 5. K-means法で色をクラスタリング
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init="auto")
    kmeans.fit(pixels)
    
    # 代表色（クラスタの中心）
    colors = kmeans.cluster_centers_.astype(int)
    
    # 各色の割合を計算
    counts = np.bincount(kmeans.labels_)
    proportions = counts / counts.sum()
    
    return colors, proportions

def display_palette(colors):
    """抽出した色をパレットとして表示し、コードをコピー可能にする"""
    cols = st.columns(len(colors))
    for i, col in enumerate(cols):
        hex_color = '#{:02x}{:02x}{:02x}'.format(colors[i][0], colors[i][1], colors[i][2])
        with col:
            st.markdown(
                f'<div style="background-color: {hex_color}; height: 60px; border-radius: 8px; border: 2px solid #ddd; margin-bottom: 5px;"></div>', 
                unsafe_allow_html=True
            )
            # st.codeを使うことで、ワンクリックでコピー可能にする
            st.code(hex_color, language="")

def main():
    st.set_page_config(page_title="Color Palette Analyzer Pro", layout="centered")
    st.title("🎨 Color Palette Analyzer Pro")
    st.write("イラストの色彩設計をAIが分析し、パレットと構成比率を可視化します。")

    uploaded_file = st.file_uploader(
        "イラストをアップロード (PNG, JPG, JPEG) \n\n※一度に1枚のみ対応",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.subheader("🖼️ 解析対象")
            st.image(image, use_container_width=True)
            
            st.divider()
            
            # --- ⚙️ 抽出設定セクション ---
            st.subheader("⚙️ 抽出設定")
            col_cfg1, col_cfg2 = st.columns(2)
            
            with col_cfg1:
                # 【新規】色数スライダー
                num_colors = st.slider("抽出する色数", min_value=3, max_value=10, value=5)
            
            with col_cfg2:
                # 白黒除外チェック
                exclude_bw = st.checkbox("背景の白・黒を除外する", value=True)
            
            if st.button("✨ 色彩を分析する", type="primary", use_container_width=True):
                with st.spinner("AIが色彩をクラスタリング中..."):
                    colors, proportions = extract_colors(image, num_colors=num_colors, exclude_bw=exclude_bw)
                    
                    if colors is None:
                        st.warning("⚠️ 有効なピクセルが不足しています。除外設定を見直してください。")
                    else:
                        # --- 🎨 結果表示セクション ---
                        st.subheader("🎨 抽出されたカラーパレット")
                        display_palette(colors)
                        
                        # --- 📊 割合表示（円グラフ）セクション ---
                        st.subheader("📊 色彩構成比率")
                        
                        # Plotly用のデータ準備
                        hex_colors = ['#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2]) for c in colors]
                        df_plot = pd.DataFrame({
                            "Color": hex_colors,
                            "Ratio": proportions
                        })
                        
                        # 円グラフの作成
                        fig = px.pie(
                            df_plot, 
                            values="Ratio", 
                            names="Color",
                            color="Color",
                            color_discrete_map={c: c for c in hex_colors}, # グラフの色を実際の抽出色に合わせる
                            hole=0.4 # ドーナツチャートにする
                        )
                        fig.update_traces(textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.success("✅ 全ての分析が完了しました！")
                
        except Exception as e:
            st.error("❌ 画像の解析中にエラーが発生しました。")
            st.caption(f"Error: {e}")

if __name__ == "__main__":
    main()