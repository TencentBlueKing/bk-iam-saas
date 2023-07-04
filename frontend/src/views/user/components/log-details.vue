<template>
  <div>
    <div class="link-btn">
      <bk-link class="link" theme="primary" href="https://bk.tencent.com/docs/document/6.0/160/8402" target="_blank">同步失败排查指引</bk-link>
    </div>
    <div>
      <div ref="logEditor" style="margin-left: 30px;">
        <textarea
          ref="logDetailCode"
          v-model="value"
          placeholder="日志详情"
          class="codesql"
        />
      </div>
    </div>
  </div>
</template>
<script>
  import CodeMirror from 'codemirror';
  import 'codemirror/lib/codemirror.css';
  import 'codemirror/mode/javascript/javascript';
  import 'codemirror/addon/edit/matchbrackets.js';
  import 'codemirror/addon/comment/continuecomment.js';
  import 'codemirror/addon/comment/comment.js';
  import 'codemirror/theme/icecoder.css';
  export default {
    name: 'LogDetails',
    props: {
      value: {
        type: String,
        required: true,
        default: () => ''
      },
      width: {
        type: String,
        default: () => '660'
      },
      height: {
        type: String,
        default: () => '400'
      }
    },
    data () {
      return {
        // value: '',
        editor: null
      };
    },
    computed: {
      newVal () {
        if (this.editor) {
          return this.editor.getValue();
        }
        return '';
      }
    },
    watch: {
      newVal () {
        this.$emit('input', this.editor.getValue());
      }
    },
    mounted () {
      this.$nextTick(() => {
        this.editor = CodeMirror.fromTextArea(this.$refs.logDetailCode, {
          matchBrackets: true,
          autoCloseBrackets: true,
          mode: 'application/ld+json',
          theme: 'icecoder',
          lineWrapping: true,
          readOnly: true
        });
        setTimeout(() => {
          this.editor.setValue(this.value);
        }, 300);
        this.editor.setSize(this.width, this.height);
      });
    }
  };
</script>
<style scoped>
    .link-btn{
        margin: 20px 0 20px 580px;
    }
</style>
