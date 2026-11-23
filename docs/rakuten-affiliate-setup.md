# 楽天公式API連携（MONO SELECT）

この仕組みは**A8.net経由ではなく楽天アフィリエイト直接**の成果対象リンクを、楽天市場商品検索API（2026-07-01）から取得します。A8のIDやリンクは流用しません。

## 必要な初期設定
1. https://webservice.rakuten.co.jp/ で楽天ウェブサービスのアプリを登録し、Application ID と Access Key を取得。アプリの利用サイトとして https://mono-select.pages.dev/ を登録し、利用条件を確認。
2. 楽天アフィリエイトの **Affiliate ID** を取得。楽天ウェブサービスのアプリIDとは異なります。
3. GitHubリポジトリ Settings → Secrets and variables → Actions → New repository secret で以下を設定。
   - RAKUTEN_APPLICATION_ID
   - RAKUTEN_ACCESS_KEY
   - RAKUTEN_AFFILIATE_ID
4. GitHub Settings → Actions → General でワークフローのPR作成権限を確認。必要なら「Allow GitHub Actions to create and approve pull requests」を有効にする。
5. Actions → Rakuten affiliate product links → Run workflow を押して初回テスト。成功するとレビュー用PRが作成されます。

毎日09:15 JSTに再取得します。GitHub Actionsのscheduleは遅延する場合があります。**承認・マージまでは公開されません。**

対象商品は `scripts/rakuten-topics.json` に追加します。型番 `mustContain` で一致する商品のみ掲載し、検索結果に適切な商品がなければリンクを作りません。API認証エラーでも既存ページは上書きしません。

APIレスポンスの価格は取得時点の情報で、メーカー公式仕様の検証ではありません。商品紹介文は実機レビューと混同しないようにしてください。

公式仕様：https://webservice.rakuten.co.jp/documentation/ichiba-item-search
