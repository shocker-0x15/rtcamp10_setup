# ルール・実行環境・提出物仕様

## はじめに
このファイルではレイトレ合宿10のルールや提出物の仕様を説明しています。\
**各自熟読をお願いします。**

ざっくり変更点：

- 静止画を提出可能としました。部門は分かれていません！
- 今年はCPU・GPUインスタンスともにシングルインスタンス構成となりました。
- 制限時間は256秒です。
- プレゼン資料には使用した主要なライブラリや3Dデータの出処を明記すること。


## 各仕様・ルール

### 提出物
提出物の仕様は以下の構造とします。`<root directory>` をzipファイルに圧縮したものを提出してください。

```
<root directory> ... 名前は参加者名とインスタンスタイプから name_(cpu|gpu) とする
├─ run.ps1 ............ 実行開始スクリプト
├─ fps.txt ............ [動画提出の場合のみ] 動画ファイルのfpsの数字だけを書き込む
├─ requirements.txt ... [Optional] Pythonのrequirements.txt
├─ ***.exe ............ 実行ファイル
├─ ***.pdf or pptx .... レンダラー紹介スライド
└─ etc ................ アセット
```

- zipファイルの上限サイズは1GiB(=1024MiB)です。
- 動画を提出する場合は `fps.txt` にフレームレートの数字だけを書き込んでください。フレームレートは最低10、最高60とします。
- 動画の時間は最低3秒、最高10秒とします。fpsの仕様とあわせると、最低で30枚、最高で600枚の画像出力を行うことになります。
- Pythonに依存していて何らかのライブラリが必要な場合は [requirements.txt](https://note.nkmk.me/python-pip-install-requirements/) を同梱してください。
- レンダラー紹介のプレゼンは一人5分です。
  - レンダラー名を入れてください。
  - 作品に対する本人の貢献度合いをフェアに判断するため使用した主要なライブラリや3Dデータの出処について明記してください。

### 実行環境

EC2インスタンスは以下のいずれか：
| インスタンスタイプ | 料金<br/>USD/h/inst | CPU | System Mem | GPU | GPU Mem | ストレージ | インスタンスストア |
| - | - | - | - | - | - | - | - |
| [g5.xlarge](https://aws.amazon.com/jp/ec2/instance-types/g5/) | 1.643 | AMD EPYC 7R32<br>4 vCPU | 16 GiB | [NVIDIA A10G](https://www.nvidia.com/ja-jp/data-center/products/a10-gpu/) | 16 GiB | EBS | 250 GiB NVMe SSD |
| [c7i.metal-48xl](https://aws.amazon.com/jp/ec2/instance-types/c7i/) | 19.6176 | Intel Xeon Scalable<br/>[Sapphire Rapids](https://www.intel.co.jp/content/www/jp/ja/products/docs/processors/xeon-accelerated/4th-gen-xeon-scalable-processors.html)<br>192 vCPU | 384 GiB | N/A | N/A | EBS | N/A |

- OSはWindows Server 2022 Baseを使います。
- python 3.11.4がインストールされています。\
  pythonライブラリとしては数値計算用にnumpy, scipy、画像処理にPillow、SSH操作用にparamikoをインストールしています。
- GPUインスタンスはDirectX 12, Vulkan, OptiX 8.0が動作するドライバー、CUDA 12.5がインストールされています。
- GPUインスタンスはインスタンスストア付きではありますが、特に要望がない限り設定しません。

### 実行

提出物内の `<root directory>` をホームディレクトリに配置します。すなわち `run.ps1` は次の絶対パスに配置されることになります。\
`C:\Users\Administrator\<root directory>\run.ps1`

- 画像出力は.pngまたは.jpgで000.png, 001.png, ...と0開始、3桁の連番で `<root directory>` に出力してください。\
  静止画の場合は000.png/jpgを最終結果として採用します。
- ウィンドウやダイアログを出さないでください。
- キーボードやマウスの操作を要求せずに自動でレンダリングしてください。
- 制限時間内(**256秒**)に自動で終了するようにしてください。
- エラーは標準出力か標準エラー出力かログファイルに出力してください。
- インターネット接続をしないで下さい。

### プレゼン・採点・結果発表
1. 現地の本戦の時間枠で全作品を参加者みんなで同時視聴します。
1. 参加者それぞれが自身の作品とレンダラーについてプレゼンを行います。
1. 当日の夜の間にお互いの提出作品の採点を行います。
   - 提出作品は各自のPCなどで何度でも閲覧できるようになっています。
   - 採点は10点満点で行います。採点基準は特にありませんが、順位かぶりを避けるため1点から10点までダイナミックレンジをできるだけ使い切ることを推奨しています。
   - 採点対象には自分の作品も含まれています。自由に採点してください。
1. 本戦翌日に結果発表を行います!!!
