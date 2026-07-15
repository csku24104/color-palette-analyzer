import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
import json
import os
import uuid
import time # 【追加】待機処理用
from datetime import datetime

# ==========================================
# 💾 データ保存・管理用ロジック (CRUD)
# ==========================================
PALETTE_FILE = "palettes.json"

def load_palettes():
    """【Read】JSONファイルからパレット一覧を読み込む"""
    if not os.path.exists(PALETTE_FILE):
        return []
    with open(PALETTE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_palette_data(name, hex_colors, proportions):
    """【Create】新しいパレットをJSONファイルに保存する"""
    palettes = load_palettes()
    new_palette = {
        "id": str(uuid.uuid4()),
        "name": name,
        "colors": hex_colors,
        "proportions": proportions.tolist() if isinstance(proportions, np.ndarray) else proportions,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    palettes.append(new_palette)
    with open(PALETTE_FILE, "w", encoding="utf-8") as f:
        json.dump(palettes, f, indent=4, ensure_ascii=False)
    return True

def update_palette_name(palette_id, new_name):
    """【Update】指定したパレットの名前を更新する"""
    palettes = load_palettes()
    for p in palettes:
        if p["id"] == palette_id:
            p["name"] = new_name
            break
    with open(PALETTE_FILE, "w", encoding="utf-8") as f:
        json.dump(palettes, f, indent=4, ensure_ascii=False)

def delete_palette(palette_id):
    """【Delete】指定したパレットを削除する"""
    palettes = load_palettes()
    palettes = [p for p in palettes if p["id"] != palette_id]
    with open(PALETTE_FILE, "w", encoding="utf-8") as f:
        json.dump(palettes, f, indent=4, ensure_ascii=False)

# ==========================================
# 🎨 画像解析用ロジック
# ==========================================
def extract_colors(image, num_colors=5, exclude_bw=False):
    image = image.copy()
    image.thumbnail((150, 150))
    image = image.convert("RGBA")
    pixels = np.array(image).reshape(-1, 4)
    
    mask_opaque = pixels[:, 3] > 200
    pixels = pixels[mask_opaque]
    pixels = pixels[:, :3] 
    
    if exclude_bw:
        mask_white = np.all(pixels > 240, axis=1)
        mask_black = np.all(pixels < 15, axis=1)
        mask_valid = ~(mask_white | mask_black)
        pixels = pixels[mask_valid]
        
    if len(pixels) < num_colors or len(np.unique(pixels, axis=0)) < num_colors:
        return None, None
            
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init="auto")
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    
    counts = np.bincount(kmeans.labels_, minlength=num_colors)
    if 0 in counts:
        return None, None
        
    proportions = counts / counts.sum()
    return colors, proportions

def display_palette(colors_hex):
    """カラーコードのリストを元にパレットを描画する"""
    cols = st.columns(len(colors_hex))
    for i, hex_color in enumerate(colors_hex):
        with cols[i]:
            st.markdown(
                f'<div style="background-color: {hex_color}; height: 60px; border-radius: 8px; border: 2px solid #ddd; margin-bottom: 5px;"></div>', 
                unsafe_allow_html=True
            )
            st.code(hex_color, language="")

# ==========================================
# 🖥️ 画面描画用関数（UI）
# ==========================================
def render_analysis_page():
    """解析モードの画面"""
    st.title("🎨 Color Palette Analyzer Pro")
    st.write("イラストの色彩設計をAIが分析し、パレットと構成比率を可視化します。")

    if "extracted_colors_rgb" not in st.session_state:
        st.session_state.extracted_colors_rgb = None
        st.session_state.extracted_proportions = None

    uploaded_file = st.file_uploader("イラストをアップロード (PNG, JPG, JPEG) \n\n※一度に1枚のみ対応")

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ['png', 'jpg', 'jpeg']:
            st.error("❌ PNG, JPG, JPEG以外のファイルです。対応している画像をアップロードしてください。")
            return
            
        try:
            image = Image.open(uploaded_file)
            image.verify()
            image = Image.open(uploaded_file)
        except Exception:
            st.error("❌ 画像の読み込みに失敗しました。ファイルが破損している可能性があります。")
            return

        st.subheader("🖼️ 解析対象")
        st.image(image, use_container_width=True)
        
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
                        st.session_state.extracted_colors_rgb = None
                    else:
                        st.session_state.extracted_colors_rgb = colors
                        st.session_state.extracted_proportions = proportions
                        st.success("✅ 全ての分析が完了しました！")
                except Exception as e:
                    st.error("❌ 画像の解析中に予期せぬエラーが発生しました。")
                    st.caption(f"Error: {e}")

        if st.session_state.extracted_colors_rgb is not None:
            colors_rgb = st.session_state.extracted_colors_rgb
            proportions = st.session_state.extracted_proportions
            hex_colors = ['#{:02x}{:02x}{:02x}'.format(c[0], c[1], c[2]) for c in colors_rgb]
            
            st.subheader("🎨 抽出されたカラーパレット")
            display_palette(hex_colors)
            
            st.subheader("📊 色彩構成比率")
            df_plot = pd.DataFrame({"Color": hex_colors, "Ratio": proportions})
            fig = px.pie(
                df_plot, values="Ratio", names="Color", color="Color",
                color_discrete_map={c: c for c in hex_colors}, hole=0.4
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.subheader("💾 パレットを保存")

            st.info("💡 【お知らせ】ホスティングの仕様上、保存・編集したパレットデータはアプリがスリープするとリセット（揮発）されます。デモ用としてお楽しみください。", icon="ℹ️")
            
            with st.form("save_palette_form"):
                palette_name = st.text_input("パレット名を入力", placeholder="例：メインキャラクター配色")
                submitted = st.form_submit_button("このパレットを保存する")
                if submitted:
                    if palette_name.strip() == "":
                        st.error("❌ パレット名を入力してください。")
                    else:
                        save_palette_data(palette_name, hex_colors, proportions)
                        st.success(f"✅ パレット「{palette_name}」を保存しました！サイドバーの「保存済みパレット」から確認できます。")

def render_history_page():
    """保存済みパレット管理画面"""
    st.title("📂 保存済みパレット一覧")
    palettes = load_palettes()
    
    if not palettes:
        st.info("保存されたパレットはまだありません。「🎨 解析モード」で画像を解析してパレットを保存してください。")
        return
        
    for p in reversed(palettes):
        with st.container():
            st.subheader(f"🏷️ {p['name']}")
            st.caption(f"保存日時: {p.get('created_at', '不明')} | 色数: {len(p['colors'])}色")
            
            display_palette(p['colors'])
            
            # 管理メニュー（更新・削除）
            col_upd, col_del = st.columns([3, 1])
            
            # 【変更点1】名前更新時の待機処理
            with col_upd:
                with st.expander("📝 名前を変更する"):
                    new_name = st.text_input("新しい名前", value=p['name'], key=f"txt_{p['id']}")
                    if st.button("更新", key=f"upd_{p['id']}"):
                        if new_name.strip():
                            update_palette_name(p['id'], new_name.strip())
                            st.success("✅ 名前を更新しました！")
                            time.sleep(1) # メッセージを1秒間表示してからリロード
                            st.rerun()
                        else:
                            st.error("名前を入力してください。")
                            
            # 【変更点2】削除の確認UI
            with col_del:
                with st.expander("🗑️ 削除する"):
                    st.warning("本当に削除しますか？")
                    if st.button("はい、削除します", key=f"del_confirm_{p['id']}", type="primary"):
                        delete_palette(p['id'])
                        st.rerun()
            
            st.divider()

def main():
    st.set_page_config(page_title="Color Palette Analyzer Pro", layout="centered", page_icon="🎨")
    st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)
    
    st.sidebar.title("メニュー")
    mode = st.sidebar.radio("", ["🎨 解析モード", "📂 保存済みパレット"])

    st.sidebar.markdown("---")
    st.sidebar.caption("※デモ環境のため、保存データは一定時間でリセットされます")
    
    if mode == "🎨 解析モード":
        render_analysis_page()
    else:
        render_history_page()

if __name__ == "__main__":
    main()