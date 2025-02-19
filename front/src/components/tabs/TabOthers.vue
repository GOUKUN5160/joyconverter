<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faTwitter, faInstagram, faGithub } from '@fortawesome/free-brands-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

library.add(faTwitter, faInstagram, faGithub);
const VERSION = __APP_VERSION__;
const PLATFORM = ref("");
const CONFIG_PATH = ref("");
const EMAIL = "goukun5160@gmail.com";
const TWITTER = "@GOU_KUN5160";
const INSTAGRAM = "@gou_kun5160";
const GITHUB = "GOUKUN5160";

onMounted(() => {
  eel.get_platform()().then((result: string) => {
    PLATFORM.value = result;
  });
  eel.get_config_path()().then((result: string) => {
    CONFIG_PATH.value = result;
  });
});

const openConfigFolderOnFileApp = () => {
  eel.open_config_folder()();
};

const openProgramFolder = () => {
  eel.open_current_propgram_directory()();
};

const openStartUpFolder = () => {
  eel.open_startup_folder()();
};

</script>

<template>
  <v-main>
    <v-container fluid>
      <div style="text-align: center;">
        <h1>JoyConverter</h1>
        <h3>v{{ VERSION }}</h3>
      </div>
      <v-card class="mt-5">
        <v-card-title class="text-h6 text-md-h5 text-lg-h4">使用上の注意</v-card-title>
        <v-card-text>
          <div style="color: red;">
            ・<strong>異なるOS間でのプロファイルのインポートをしないでください。</strong>キーコードが異なるため、思わぬ動作を引き起こすことになります。<br>
            ・プロファイルをインポートするときは、<strong>自分が作ったものであるかを必ず確認</strong>してください。悪意あるアクションが仕込まれている可能性があります。<br>
            ・<strong>いかなる損害が発生したとしても開発者は一切の責任を負いません。</strong>
          </div>
        </v-card-text>
      </v-card>
      <v-card class="mt-5">
        <v-card-title class="text-h6 text-md-h5 text-lg-h4">よくありそうな質問</v-card-title>
        <v-card-text>
          <v-expansion-panels variant="accordion">
            <v-expansion-panel title="何のためのソフト？">
              <v-expansion-panel-text class="pt-2">
                「作業効率化を図るためにJoyConを片手デバイスとして操作したい」と思っている方のためのソフトです。<br>
                <strong>・分かりやすいUIデザイン</strong><br>
                <strong>・クロスプラットフォーム（Windows、Mac）</strong><br>
                <strong>・JoyConに特化</strong>（ゲーム用途での使用は想定されていません）<br>
                <strong>・完全無料</strong><br>
                ※キーコードの関係上OS間での設定ファイルの共有は現状サポートされていません。
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel title="JoyConが認識されません。">
              <v-expansion-panel-text>
                JoyConとの通信に失敗している可能性が高いです。接続しているJoyConの電源を全てOFFにし、1本だけ電源を入れて再度お試しください。<br>
                お使いの環境によっては、JoyConを複数本同時接続すると動作が不安定になる可能性があります。<br>
                JoyConをSwitchや他のPCなどに接続するとペアリングが切れるので、Bluetooth設定を削除してから再度ペアリングしてください。
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel title="バイブレーションの「非同期実行」って何ですか？">
              <v-expansion-panel-text>
                バイブレーションの終了を待たずに次の処理へ進んでしまうということです。バイブレーションの秒数にかかわらず一瞬で処理が終了します。<br>
                バイブレーションが終わるのを待ちたい場合（同期実行）、バイブレーションと同じ秒数だけ待機する処理を入れてください。
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel title="OS起動時に自動実行するにはどうすればいいですか？">
              <v-expansion-panel-text>
                <template v-if="PLATFORM == 'windows'">
                  このソフトのショートカットをスタートアップフォルダに入れてください。<br>
                  1. Shiftキーを押しながらexeファイルを右クリックし、「ショートカットの作成」を押します。<br>
                  2. できたショートカットをスタートアップフォルダに入れます。<br>
                  <v-btn @click="openProgramFolder()" color="primary" dark class="mr-5">ソフトの場所を開く</v-btn>
                  <v-btn @click="openStartUpFolder()" color="primary" dark>スタートアップフォルダを開く</v-btn>
                </template>
                <template v-if="PLATFORM == 'mac'">
                  「システム環境設定」を開き、検索バーに「ログイン項目」と入力してください。<br>
                  検索結果の「ログイン項目」を選択し、＋ボタンを押してこのソフトを追加してください。<br>
                </template>
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel title="アンインストール方法">
              <v-expansion-panel-text>
                <template v-if="PLATFORM == 'windows'">
                  このプログラムが保存されているフォルダと設定ファイルが保存されているフォルダを丸ごと削除してください。<br>
                </template>
                <template v-if="PLATFORM == 'mac'">
                  「アプリケーション」フォルダの中のJoyConverterを削除してください。設定まで削除したい場合は設定ファイルが保存されているフォルダも削除してください。<br>
                </template>
                設定ファイルは以下の場所に保存されています。<br>
                <strong>{{ CONFIG_PATH }}</strong><br>
                <v-btn @click="openProgramFolder()" color="primary" dark class="mr-5" v-if="PLATFORM == 'windows'">ソフトの場所を開く</v-btn>
                <v-btn @click="openConfigFolderOnFileApp()" color="primary" dark>設定ファイルの場所を開く</v-btn>
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel title="実装を見送った機能">
              <v-expansion-panel-text>
                ・UIの色をカスタムできる機能<br>
                ・アクション編集画面での並び替え機能<br>
                ・選択されなかったアクションの記憶<br>
                ・スタートアップ自動登録<br>
                ・多言語対応<br>
                ・プロコンをはじめとする他のコントローラーのサポート<br>
                ・加速度センサー、ARセンサー、NFCリーダーのデータを使ったアクション<br>
                ・LED表示をカスタマイズできるアクション<br>
                ・文章をタイピングするアクション<br>
                ・ブロックプログラミングを用いて、より高度な設定を行う機能<br>
                ・Pythonコードを書いて、より高度な設定を行う機能<br><br>
                <strong>要望があれば考えますが、今のところ実装の目途は立っていません。</strong>
              </v-expansion-panel-text>
            </v-expansion-panel>
            <v-expansion-panel title="開発者連絡先">
              <v-expansion-panel-text>
                <div class="mb-2">
                  <v-icon icon="mdi-email" class="mr-1"></v-icon>{{ EMAIL }}<br>
                </div>
                <div class="mb-2">
                  <font-awesome-icon icon="fa-brands fa-instagram" size="xl" class="mr-1"></font-awesome-icon>{{ INSTAGRAM }}<br>
                </div>
                <div class="mb-2">
                  <font-awesome-icon icon="fa-brands fa-twitter" size="xl" class="mr-1"></font-awesome-icon>{{ TWITTER }}<br>
                </div>
                <div class="mb-2">
                  <font-awesome-icon icon="fa-brands fa-github" size="xl" class="mr-1"></font-awesome-icon>{{ GITHUB }}<br><br>
                </div>
                <strong>感想、質問、バグの報告、追加してほしい機能などがありましたらお気軽にご連絡ください。</strong>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
      </v-card>
    </v-container>

  </v-main>
</template>
