1. 各種Windows設定
   - Dark Mode
   - ゴミ箱削除確認
   - ファイル拡張子
   - 隠しファイル表示
   - VSCode
   - Python拡張
2. semiauto_set_up.ps1を実行
3. 不要ファイル削除
4. EC2のインスタンス一覧から
   1. アクション > イメージとテンプレート > イメージを作成
   2. イメージ名と説明を入力、「再起動しない」にはチェックをいれない、「終了時に削除」はチェックそのまま
   3. イメージを作成をクリック。
5. EC2のAMIの欄にイメージが表示される。
   10分ほど待つと利用可能ステータスになる。
6. この時点で元のインスタンスは終了して良い。
7. AMIを選択し、「AMIからインスタンスを起動」をクリック。
   - 元と同じインスタンスタイプやネットワーク設定を選択
8. 起動したインスタンスにRDP
   - 元のインスタンスと同じパスワードでつながる。
   1. スタートメニューから
      Amazon Web Services > Amazon EC2Launch settings
   2. Administrator password settingsがRandom (retrieve from console)になっていることを確認。
   3. Shutdown with Sysprepをクリック
      You have unsaved changes...というダイアログが出るがシャットダウン。
      この後このインスタンスは起動しないこと。
9. 4-5を再度起動中のインスタンスに対して実施。
10. AMIからインスタンスを起動する。
    Windowsのパスワード復号には10分弱待つ必要があった。

AMIの削除
1. AMI一覧からAMIを選択し「AMIを登録解除」
2. EBS > スナップショットから関連するスナップショットを削除。

AMIの公開
1, AMI一覧からAMIを選択し「AMI許可を編集」
2. AMIの可用性をパブリックに変更。

userdata.xmlの実行結果格納場所
C:\Windows\System32\config\systemprofile\AppData\Local\Temp\