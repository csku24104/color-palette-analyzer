# イラスト色彩自動解析アプリ (Color Palette Analyzer)

イラスト制作における色彩設計の悩みを解決し、客観的なデータに基づいて配色を最適化・ストックできるWebアプリケーションです。

---

## 1. Miro要件マップ（アプリ概要）

| 観点 | 内容 |
| :--- | :--- |
| **目的** | イラスト制作における色彩設計 of 悩み（バランスの悪さや色の偏り）を解決し、客観的なデータに基づいて配色を最適化・研究する。 |
| **利用者** | イラストレーター、デジタルペイント初心者。作品のブラッシュアップ中や、配色に行き詰まった際に使用する。 |
| **入力** | イラスト画像ファイル（jpg, png）、パレットのタイトル（テキスト）。 |
| **出力** | 主要な5色のカラーパレット、各色の構成比グラフ、カラーコード一覧、保存済みパレット一覧。 |
| **主要機能** | 1. 画像のドラッグ＆ドロップ機能<br>2. K-means法による5色の代表色抽出機能<br>3. 各色の面積比率の算出とグラフ表示機能<br>4. カラーコードのクリップボードへの一括コピー機能<br>5. 解析したパレットの保存・一覧参照・名前の更新・削除（CRUD機能） |
| **非目標** | 色の心理的意味のAIによる解釈、画像全体の自動色調補正（自動修正）、複雑なレイヤー解析。 |
| **受け入れ基準**| ・画像をアップロード後、3秒以内にカラーパレットと構成比グラフが正しく描画されること。<br>· カラーコードの一括コピーボタンが正常に機能すること。<br>· 保存したパレットのCRUD操作が正常に行えること。 |

---

## 2. 要件定義書（機能・非機能要求一覧）

### 機能要求（Functional Requirements）
* ユーザーが画像をドラッグ＆ドロップしてアップロードできること。
* システムが自動で画像を解析し、代表5色とそれぞれの構成比率（％）を算出すること。
* 算出された比率を直感的なグラフ（棒グラフまたは円グラフ）で表示すること。
* 抽出したカラーコードをワンクリックで一括コピーできること。
* 解析結果に任意の名前をつけて保存、一覧からの確認、編集、削除ができること。

### 非機能要求（Non-Functional Requirements）
* **性能**: 画像アップロード完了から、カラーパレットおよび構成比グラフの描画完了まで**3秒以内**で処理すること。高解像度画像は内部で自動リサイズして高速化を図る。
* **セキュリティ**: アップロードできる拡張子を `jpg`, `jpeg`, `png` に限定すること。画像ファイルはサーバー等に永続保存せずメモリ上で即時破棄すること。
* **ユーザビリティ**: デザイナーが直感的に使えるよう、一般的なカラーピッカーUIを踏襲すること。
* **保守性**: コードは「前処理」「解析」「描画」「CRUD処理」をそれぞれ独立した関数（モジュール）に分解して実装すること。データは単純なJSON形式等で永続化すること。

---

## 3. COSMIC CFP（機能規模）の見積もり

本アプリケーションの規模をCOSMIC機能規模測定法に基づき見積もります。

* **外部入力 (Entry: 2 CFP)**: 画像のアップロード操作、パレット保存時の名称入力
* **外部出力 (Exit: 3 CFP)**: カラーパレットの描画、構成比グラフの描画、一括コピーの出力
* **読み込み/書き込み (Read/Write: 4 CFP)**: パレットデータの保存(W)、一覧の参照(R)、名称の更新(W)、パレットの削除(W)
* **合計機能規模**: **約 30 ~ 35 CFP** (4週間で個人開発可能な適切な規模感)

---

## 4. 開発環境・使用言語

次週の実装に向けて、以下の軽量かつ高速に開発が可能な環境を採用します。

* **利用言語**: Python 3.10+
* **フレームワーク**: Streamlit (Web UI UI構築用)
* **主要ライブラリ**: 
  * OpenCV / Pillow (画像前処理用)
  * scikit-learn (K-means法によるクラスタリング解析用)
  * Plotly / Matplotlib (構成比グラフ描画用)

---

## 5. アプリケーションの起動方法（動かし方）

### ① 必要ライブラリのインストール
ターミナルで以下のコマンドを実行し、必要なパッケージをインストールします。
```bash
pip install streamlit opencv-python Pillow scikit-learn plotly
```

### ② アプリケーションの起動
リポジトリのルートディレクトリで以下のコマンドを実行し、ローカルサーバーを起動します。
```bash
streamlit run app.py
```
起動後、ブラウザで http://localhost:8501 に自動アクセスされ、アプリが利用可能になります。

---

## 6. 設計図（Mermaid記法による4種の図面）

### ① ユースケース図風
```mermaid
flowchart LR
    subgraph アクター
        User((ユーザー<br>イラストレーター / 初心者))
    end
    subgraph イラスト色彩自動解析アプリ
        UC1(1. 画像をアップロードする)
        UC2(2. 色彩を自動解析する)
        UC3(3. カラーコードを一括コピーする)
        UC4(4. パレットを命名して保存する)
        UC5(5. 保存済みパレットを管理する)
        UC2_1(5色の代表色を抽出)
        UC2_2(面積比率のグラフを表示)
        UC5_1(パレット一覧を参照)
        UC5_2(パレット名を更新)
        UC5_3(パレットを削除)
    end
    User --> UC1
    User --> UC3
    User --> UC4
    User --> UC5
    UC1 -.->|include| UC2
    UC2 -.->|include| UC2_1
    UC2 -.->|include| UC2_2
    UC5 -.->|include| UC5_1
    UC5_2 -.->|extend| UC5
    UC5_3 -.->|extend| UC5
```

### ② クラス図
```mermaid
classDiagram
    direction TB
    class PaletteApp {
        <<Boundary>>
        +main() void
        +render_main_page() void
        +render_history_page() void
    }
    class ImageProcessor {
        <<Service>>
        -max_resize_dim : int
        +preprocess_image(uploaded_file: File) ndarray
        +extract_theme_colors(img_data: ndarray, num_colors: int) Tuple~List, List~
        +rgb_to_hex(rgb_color: List~int~) string
    }
    class PaletteRepository {
        <<Service>>
        -storage_path : string
        +create(palette: SavedPalette) bool
        +read_all() List~SavedPalette~
        +update(palette_id: string, new_name: string) bool
        +delete(palette_id: string) bool
    }
    class SavedPalette {
        <<Entity>>
        +palette_id : string
        +palette_name : string
        +hex_codes : List~string~
        +percentages : List~float~
        +created_at : string
        +get_formatted_codes() string
    }
    PaletteApp "1" --> "1" ImageProcessor : 利用
    PaletteApp "1" --> "1" PaletteRepository : 利用
    PaletteRepository "1" ..> "*" SavedPalette : 操作 (JSON/DB永続化)
```

### ③ シーケンス図
```mermaid
sequenceDiagram
    autonumber
    actor User as ユーザー(イラストレーター)
    participant UI as PaletteApp (UI画面)
    participant Ctrl as ImageProcessor (コントローラ)
    participant Model as PaletteRepository (モデル/JSON)

    Note over User, Model: 【色彩解析フェーズ】
    User->>UI: 画像をドラッグ＆ドロップ
    activate UI
    UI->>Ctrl: preprocess_image(画像ファイル)
    activate Ctrl
    Ctrl-->>UI: 前処理済み画像データ
    deactivate Ctrl
    UI->>Ctrl: extract_theme_colors(画像データ, 5)
    activate Ctrl
    Ctrl->>Ctrl: K-means法によるクラスタリング計算
    Ctrl-->>UI: 代表5色(RGB/HEX), 構成比率(%)
    deactivate Ctrl
    UI-->>User: カラーパレット＆構成比グラフを3秒以内に描画
    deactivate UI

    Note over User, Model: 【パレット保存フェーズ（条件分岐）】
    User->>UI: パレット名を入力
    alt パレット名が未入力の場合
        UI-->>User: 「パレット名を入力してください」とエラー警告
    else パレット名が入力され、保存ボタンを押した場合
        User->>UI: 「保存ボタン」をクリック
        activate UI
        UI->>UI: SavedPalette(インスタンス)を生成
        UI->>Model: create(saved_palette)
        activate Model
        Model->>Model: JSONファイルへデータを書き込み永続化
        alt 書き込み成功
            Model-->>UI: True (成功)
            UI-->>User: 「パレットを保存しました！」と成功メッセージを表示
        else 書き込み失敗
            Model-->>UI: False (失敗)
            UI-->>User: 「保存に失敗しました」とエラーメッセージを表示
        end
        deactivate Model
        deactivate UI
    end
```

### ④ 状態遷移図
```mermaid
stateDiagram-v2
    [*] --> 未生成 : アプリ起動 / 初期状態
    state 未生成 {
        [*] --> 待機中
        待機中 --> 解析中 : 画像のアップロード (トリガー: File Upload)
        解析中 --> 解析完了 : K-means法による5色・比率抽出完了
        解析完了 --> 待機中 : 新しい画像の再アップロード / クリア
    }
    未生成 --> 一時オブジェクト状態 : 保存ボタンのクリック(トリガー: Save Button Clicked)
    state 一時オブジェクト状態 {
        [*] --> バリデーション中
        バリデーション中 --> エラー状態 : パレット名が空、または不正な文字
        エラー状態 --> バリデーション中 : パレット名を修正して再試行
    }
    一時オブジェクト状態 --> 永続化状態 (JSON保存済み) : バリデーション成功(トリガー: File Write Success)
    state 永続化状態 (JSON保存済み) {
        [*] --> 参照可能状態 (一覧表示)
        参照可能状態 (一覧表示) --> 編集モード : 「名前を変更」を選択
        編集モード --> 参照可能状態 (一覧表示) : 新しい名前を確定 (トリガー: Update Clicked)
    }
    永続化状態 (JSON保存済み) --> 削除処理状態 : 「削除」ボタンのクリック(トリガー: Delete Button Clicked)
    削除処理状態 --> [*] : メモリおよびJSONファイルからデータ消去 / 終了状態
```
    
