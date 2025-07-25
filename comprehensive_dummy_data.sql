-- 総合擬似データ投入スクリプト

-- 0. 既存データの全クリア (PostgreSQL版)
-- TRUNCATEはテーブルのデータを空にし、RESTART IDENTITYで連番(SERIAL)をリセット、CASCADEで依存関係を処理します。
TRUNCATE TABLE Clinics, Institutions, Doctors, Concerns, Procedures, Concern_Procedure_Links, Clinic_Treatments RESTART IDENTITY CASCADE;


-- 1. お悩みカテゴリ (Concerns) の登録
INSERT INTO Concerns (name) VALUES
('たるみ'), ('クマ'), ('輪郭・フェイスライン'), ('目'), ('鼻'), ('バスト・豊胸'),
('脂肪'), ('シミ・そばかす・肝斑・くすみ'), ('毛穴・ニキビ・ニキビ跡'),
('多汗症・ワキガ'), ('脱毛'), ('婦人科形成'), ('男性美容');

-- 2. 施術 (Procedures) の登録
INSERT INTO Procedures (name, description, demerits) VALUES
('HIFU（高密度焦点式超音波治療）', '超音波エネルギーで皮膚の深層に熱を与え、コラーゲン生成を促しリフトアップさせます。', '施術中に痛みを感じることがあり、稀に火傷や神経損傷のリスクがあります。'),
('RF治療（高周波治療）', '高周波で皮膚深部を加熱し、コラーゲン収縮と再生成を促して肌を引き締めます。', '複数回の施術が必要な場合が多く、稀に火傷や色素沈着のリスクがあります。'),
('糸リフト', '医療用の糸を皮下に挿入し、たるみを物理的に引き上げます。', '引きつれ感や違和感、内出血のリスク。効果は永続的ではありません。'),
('フェイスリフト', '余分な皮膚を切除し、SMAS筋膜を引き上げる根本的なたるみ治療です。', 'ダウンタイムが長く、腫れや内出血が強く出ます。傷跡が残る可能性があります。'),
('経結膜脱脂', '下まぶたの裏側から余分な眼窩脂肪を除去し、目の下の膨らみを改善します。', '脂肪を取りすぎると凹むリスクや、術後に腫れや内出血が出ることがあります。'),
('ハムラ法', '眼窩脂肪を移動させて目の下のたるみと膨らみを同時に改善する手術です。', '腫れや内出血が強く出ます。稀に外反（アカンベー状態）のリスクがあります。'),
('ヒアルロン酸注入', 'ヒアルロン酸を注入し、シワや凹みを改善したり、ボリュームを出したりします。', '効果は一時的です。注入量が多すぎると不自然になるリスクや、血管閉塞のリスクがあります。'),
('脂肪注入', '自身の脂肪を吸引し、必要な部位に注入してボリュームを補います。', '脂肪の生着率に個人差があり、しこりや石灰化のリスクがあります。'),
('レーザートーニング', '低出力のレーザーを均一に照射し、メラニンを穏やかに破壊して肝斑や色素沈着を改善します。', '複数回の治療が必要で、稀に白斑化のリスクがあります。'),
('エラボトックス', 'エラの筋肉（咬筋）にボトックスを注入し、筋肉の働きを抑制して小顔効果をもたらします。', '効果は一時的です。注入量が多すぎると噛む力が弱まることがあります。'),
('埋没法', '医療用の糸でまぶたを留め、二重のラインを形成します。', '糸が取れて元に戻る可能性があり、感染のリスクがあります。'),
('切開法', 'まぶたを切開し、半永久的な二重のラインを形成します。', 'ダウンタイムが長く、傷跡が残る可能性があり、修正が困難な場合があります。'),
('プロテーゼ隆鼻術', '鼻筋にプロテーゼを挿入し、鼻を高くします。', '感染やプロテーゼのずれ、皮膚が薄くなるなどのリスクがあります。'),
('脂肪豊胸', '自身の脂肪を吸引・注入してバストアップを図ります。', '脂肪の生着率に個人差があり、しこりや石灰化のリスクがあります。'),
('シリコン豊胸', 'シリコンバッグを挿入し、大幅なバストアップが可能です。', '感染、被膜拘縮、破損のリスクがあり、定期的な検診が必要です。'),
('脂肪吸引', 'カニューレで直接脂肪を吸引し、部分痩せを実現します。', 'ダウンタイムが長く、皮膚の凹凸やたるみが生じるリスクがあります。'),
('医療レーザー脱毛', '強力なレーザーで毛根を破壊し、半永久的な脱毛効果を得ます。', '痛みを感じることがあり、複数回の施術が必要です。稀に火傷のリスクがあります。');

-- 3. クリニック (Clinics) と所属機関 (Institutions) の登録
INSERT INTO Clinics (clinic_name) VALUES
('銀座プレミア美容クリニック'), ('新宿スキン＆ビューティー'), ('表参道ウェルネス整形'), ('渋谷メディカルスクエア'), ('池袋トータルケアクリニック'),
('品川ビューティーラボ'), ('上野中央クリニック'), ('立川スキンクリニック'), ('横浜美容外科'), ('大宮ビューティーデザイン'),
('千葉中央美容クリニック'), ('恵比寿プライベート形成外科'), ('六本木ヒルズビューティークリニック'), ('秋葉原メンズ美容'), ('日本橋エイジングケア');
INSERT INTO Institutions (name) SELECT clinic_name FROM Clinics;

-- 4. 医師 (Doctors) の登録
INSERT INTO Doctors (name, is_specialist, institution_id) VALUES
('佐藤 健介', TRUE, 1), ('鈴木 綾子', FALSE, 1), ('高橋 直人', TRUE, 1), ('田中 美咲', TRUE, 2), ('伊藤 沙織', FALSE, 2),
('渡辺 雄太', TRUE, 3), ('山本 恵子', FALSE, 3), ('中村 聡', TRUE, 4), ('小林 由紀', FALSE, 4), ('加藤 浩', TRUE, 4),
('吉田 誠', TRUE, 5), ('山田 久美子', FALSE, 5), ('佐々木 翼', TRUE, 6), ('山口 真理', FALSE, 6), ('松本 拓也', TRUE, 7),
('井上 菜々', FALSE, 7), ('木村 大輔', TRUE, 8), ('林 愛美', FALSE, 8), ('斎藤 圭', TRUE, 9), ('清水 智子', TRUE, 9),
('岡田 亮', FALSE, 10), ('長谷川 直樹', TRUE, 10), ('森田 あゆみ', FALSE, 11), ('岡崎 隼人', TRUE, 11), ('石川 香織', FALSE, 12),
('原田 剛', TRUE, 12), ('藤田 陽子', TRUE, 13), ('小川 裕樹', FALSE, 13), ('後藤 麻衣', TRUE, 14), ('前田 賢一', FALSE, 14),
('橋本 結衣', TRUE, 15), ('石井 瑞希', FALSE, 15), ('阿部 俊介', TRUE, 1), ('遠藤 遥', FALSE, 2), ('西村 和彦', TRUE, 3),
('福田 涼子', FALSE, 4), ('三浦 翔平', TRUE, 5), ('竹内 美穂', FALSE, 6), ('吉川 健太', TRUE, 7), ('中島 優子', FALSE, 8),
('岩崎 拓海', TRUE, 9), ('金子 絵里', FALSE, 10), ('野口 宗介', TRUE, 11), ('安田 夏美', FALSE, 12), ('高田 潤', TRUE, 13),
('大塚 玲奈', FALSE, 14), ('杉山 幸助', TRUE, 15), ('宮崎 栞', FALSE, 1), ('内藤 航', TRUE, 2), ('関根 千夏', TRUE, 3);

-- 5. お悩みと施術の関連付け (Concern_Procedure_Links)
INSERT INTO Concern_Procedure_Links (concern_id, procedure_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4),
(2, 5), (2, 6), (2, 7), (2, 8), (2, 9),
(3, 10), (3, 4), (3, 17),
(4, 11), (4, 12), (4, 5), (4, 6),
(5, 13), (5, 7),
(6, 14), (6, 15),
(7, 17), (7, 1), (7, 2),
(8, 9),
(11, 17);

-- 6. クリニック取扱施術 (Clinic_Treatments) の登録
INSERT INTO Clinic_Treatments (clinic_id, procedure_id, price, price_details, equipment_or_material, our_notes) VALUES
(1, 1, 29800, '全顔', 'ウルセラ', '最高峰HIFUで結果重視の方に。'),
(1, 11, 50000, '2点留め', '標準プラン', '院長による丁寧なカウンセリングが人気。'),
(1, 13, 300000, 'I型プロテーゼ', 'シリコン', '安心の10年保証付き。'),
(2, 1, 19800, '初回限定価格', 'ダブロゴールド', '最新機器によるスピーディーな施術。'),
(2, 10, 25000, '両側', 'ボトックスビスタ®', '定期的な注入で小顔をキープ。'),
(2, 17, 98000, '全身5回コース', 'ジェントルマックスプロ', '2種のレーザーでどんな肌質にも対応。'),
(3, 3, 120000, '片側4本', 'テスリフト', '持続性の高い糸を使用。'),
(3, 14, 600000, 'コンデンスリッチ豊胸', '自身の脂肪', '定着率が高く自然な仕上がり。'),
(4, 2, 45000, '顔全体', 'サーマクールFLX', 'RF治療の代表格。'),
(4, 12, 250000, '全切開', 'マイクロサージャリー', '傷跡が目立ちにくいと評判。'),
(5, 5, 150000, '両目', '経結膜脱脂', '腫れを最小限に抑える工夫あり。'),
(5, 16, 200000, '腹部全体', 'VASER Lipo', 'デザイン性の高い脂肪吸引。'),
(6, 6, 400000, '両目', '裏ハムラ法', '皮膚を切らないためダウンタイムが短い。'),
(6, 7, 49800, '1cc', 'ジュビダームビスタ ボリューマ', '鼻筋をシャープに見せる効果。'),
(7, 1, 25000, '全顔400ショット', 'ウルトラフォーマー3', '痛みが少なく初心者におすすめ。'),
(7, 4, 800000, 'ミニリフト', 'SMAS法', '傷跡が耳の後ろに隠れる。'),
(8, 11, 39800, '3点留め', 'ナチュラルプラン', '学生割引あり。'),
(8, 17, 120000, 'VIO含む全身5回', 'ソプラノチタニウム', '痛みが少なく日焼け肌もOK。'),
(9, 15, 700000, 'モティバ 250cc', 'モティバ', '自然な動きと感触を追求。'),
(9, 3, 98000, 'ミントリフト', 'PCL糸', 'リフトアップ効果が高い。'),
(10, 10, 19800, '初回限定', 'コアトックス®', 'アレルギー反応が出にくいとされる。'),
(10, 9, 8000, '1回', 'ピコトーニング', '肝斑治療にも効果的。'),
(11, 1, 22000, '頬＋あご下', 'ソノクイーン', '細かい部位への照射も可能。'),
(11, 7, 30000, '両目の下', 'レスチレンリフトリド', '実績のあるヒアルロン酸。'),
(12, 16, 150000, '二の腕', 'ボディジェット', '脂肪へのダメージが少ない。'),
(13, 2, 80000, '顔全体', 'ボルニューマ', '最新のモノポーラRF。'),
(14, 10, 30000, '男性向け強力プラン', 'ボトックス（アラガン社製）', '発達した咬筋にアプローチ。'),
(15, 4, 1200000, 'フルフェイスリフト', '拡大SMAS法', '持続性を最重視した術式。');

-- 新テーブル: Concern_Subcategories
-- 各サブカテゴリ（例：黒クマ、赤クマ、青クマ）の詳細を格納
CREATE TABLE Concern_Subcategories (
    subcategory_id SERIAL PRIMARY KEY,
    concern_id INT NOT NULL, -- 親となるConcernへの外部キー
    name VARCHAR(255) NOT NULL,
    short_description VARCHAR(500), -- 患者が理解しやすい簡単な説明
    long_description TEXT, -- 詳細な説明
    image_url TEXT, -- サブカテゴリを示す画像（例：クマの種類の比較画像）
    FOREIGN KEY (concern_id) REFERENCES Concerns(concern_id)
);

-- 新テーブル: Concern_Subcategory_Procedure_Links
-- サブカテゴリと施術の関連付け
CREATE TABLE Concern_Subcategory_Procedure_Links (
    link_id SERIAL PRIMARY KEY,
    subcategory_id INT NOT NULL,
    procedure_id INT NOT NULL,
    FOREIGN KEY (subcategory_id) REFERENCES Concern_Subcategories(subcategory_id),
    FOREIGN KEY (procedure_id) REFERENCES Procedures(procedure_id),
    UNIQUE (subcategory_id, procedure_id) -- 重複登録防止
);

-- 既存の Concern_Procedure_Links テーブルは、
-- 今回の変更でサブカテゴリを持たない汎用的な悩みと施術の紐付けとして残すか、
-- 全て Concern_Subcategory_Procedure_Links に移行するかを検討します。
-- 全て移行する場合は、Concern_Procedure_Links は削除またはリネームを推奨します。
-- 例として、今回は `Concern_Procedure_Links` はそのまま残し、
-- クマのような詳細な分類が必要な場合に `Concern_Subcategory_Procedure_Links` を使用する方針とします。

-- クマのサブカテゴリの擬似データ挿入例
-- まず、"クマ" の concern_id を取得
-- SELECT concern_id FROM Concerns WHERE name = 'クマ'; -- 例: id=2

INSERT INTO Concern_Subcategories (concern_id, name, short_description, long_description, image_url) VALUES
(2, '黒クマ', '目の下のたるみや膨らみが原因で影ができるクマ。上を向いたり、軽く引っ張ると影が薄くなる特徴があります。', '加齢やコラーゲン減少により眼窩脂肪が突出したり、頬がたるむことで影ができ、黒く見えるクマです。目の下の膨らみが特徴で、上を向くと影が薄くなる傾向があります。', '/static/images/black_bear.png'),
(2, '赤クマ', '目の下の皮膚が薄く、眼輪筋や眼窩脂肪が透けて赤っぽく見えるクマ。', '目の下の皮膚が薄い方に多く見られ、その下の眼輪筋や眼窩脂肪が透けて赤みがかって見えるクマです。特に目の下を引っ張っても色の変化があまり見られないのが特徴です。', '/static/images/red_bear.png'),
(2, '青クマ', '血行不良が原因で、目の下が青っぽく見えるクマ。睡眠不足や疲労が原因となることが多いです。', '寝不足やストレス、目の酷使による血行不良が主な原因で、毛細血管が透けて青っぽく見えるクマです。目の下を引っ張ると色が少し薄くなることがあります。', '/static/images/blue_bear.png');

-- クマの種類と施術の関連付けの擬似データ挿入例
-- 事前に concern_subcategories と procedures のIDを確認してください
INSERT INTO Concern_Subcategory_Procedure_Links (subcategory_id, procedure_id) VALUES
-- 黒クマ (例: subcategory_id = 1) に関連する施術
((SELECT subcategory_id FROM Concern_Subcategories WHERE name = '黒クマ'), (SELECT procedure_id FROM Procedures WHERE name = '経結膜脱脂')),
((SELECT subcategory_id FROM Concern_Subcategories WHERE name = '黒クマ'), (SELECT procedure_id FROM Procedures WHERE name = 'ハムラ法')),
((SELECT subcategory_id FROM Concern_Subcategories WHERE name = '黒クマ'), (SELECT procedure_id FROM Procedures WHERE name = '脂肪注入')),
-- 赤クマ (例: subcategory_id = 2) に関連する施術
((SELECT subcategory_id FROM Concern_Subcategories WHERE name = '赤クマ'), (SELECT procedure_id FROM Procedures WHERE name = '脂肪注入')),
((SELECT subcategory_id FROM Concern_Subcategories WHERE name = '赤クマ'), (SELECT procedure_id FROM Procedures WHERE name = 'ヒアルロン酸注入')),
-- 青クマ (例: subcategory_id = 3) に関連する施術
((SELECT subcategory_id FROM Concern_Subcategories WHERE name = '青クマ'), (SELECT procedure_id FROM Procedures WHERE name = 'ヒアルロン酸注入')),
((SELECT subcategory_id FROM Concern_Subcategories WHERE name = '青クマ'), (SELECT procedure_id FROM Procedures WHERE name = 'レーザートーニング'));


-- Concern_Procedure_Links または Concern_Subcategory_Procedure_Links にseverity_levelを追加
ALTER TABLE Concern_Procedure_Links ADD COLUMN severity_level VARCHAR(50);
ALTER TABLE Concern_Subcategory_Procedure_Links ADD COLUMN severity_level VARCHAR(50);
-- '軽度', '中程度', '重度', '全般' などの文字列で管理
-- またはINT型で 1:軽度, 2:中程度, 3:重度 のように管理し、ソートを容易にする

-- たるみ（concern_id=1）の施術データ更新例
-- HIFU: 軽度〜中程度
UPDATE Concern_Procedure_Links SET severity_level = '軽度〜中程度' WHERE concern_id = 1 AND procedure_id = (SELECT procedure_id FROM Procedures WHERE name = 'HIFU（高密度焦点式超音波治療）');
-- RF治療: 軽度〜中程度
UPDATE Concern_Procedure_Links SET severity_level = '軽度〜中程度' WHERE concern_id = 1 AND procedure_id = (SELECT procedure_id FROM Procedures WHERE name = 'RF治療（高周波治療）');
-- 糸リフト: 中程度〜重度
UPDATE Concern_Procedure_Links SET severity_level = '中程度〜重度' WHERE concern_id = 1 AND procedure_id = (SELECT procedure_id FROM Procedures WHERE name = '糸リフト');
-- フェイスリフト: 重度
UPDATE Concern_Procedure_Links SET severity_level = '重度' WHERE concern_id = 1 AND procedure_id = (SELECT procedure_id FROM Procedures WHERE name = 'フェイスリフト');