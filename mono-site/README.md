# MONO SELECT — 無料比較サイトのスターター

Astro + Pages CMS + GitHub + Cloudflare Pages 用。

## 公開手順
1. GitHubで新規リポジトリを作成し、このフォルダの**中身**をアップロードします。`.pages.yml` などドットで始まるファイルも含めます。
2. Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git でGitHubリポジトリを接続します。
3. Framework preset: Astro / Build command: `npm run build` / Build output directory: `dist` / Root directory: `/` と設定します。
4. 発行された `*.pages.dev` URLでサイトを確認します。
5. Pages CMS (https://pagescms.org/) にGitHubアカウントでログインし、リポジトリを選びます。記事コレクションが表示されたら「新規記事」を作成できます。
6. 記事を保存するとGitHubの変更をCloudflare Pagesがビルドし、公開します。`draft: true` は公開一覧に出ません。

## 公開前に必要なこと
- `astro.config.mjs` の `site` を本当の `https://<name>.pages.dev` に置き換える。
- `src/pages/about.astro` と `src/pages/privacy.astro` を実際の運営情報・利用サービスに合わせて完成させる。
- 広告リンクの利用条件・PR表記・画像利用権限を確認する。
- サンプル記事は公開前に編集するか削除する。
- Pages CMSのUIや設定仕様は更新されることがあるため、公式ドキュメントで確認する。

## ローカルで確認
`npm install` → `npm run dev`。ビルド確認は `npm run build`。
