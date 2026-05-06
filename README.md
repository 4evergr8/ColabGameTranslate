# ColabGameTranslate 🎮✨

本工具基于 Mtool 生成的 `ManualTransFile.json` 进行翻译管理，使用LLM进行翻译,支持上下文参考😊。

## 特性 🌟

- 旧版本翻译自动同步（避免重复翻译相同文本） 🔄


## 使用方法 📝

请先使用 **Mtool** 提取游戏文本，生成 `ManualTransFile.json` 并上传至GoogleDrive根目录。
* 点击<a href="https://colab.research.google.com/github/4evergr8/ColabGameTranslate/blob/main/笔记本.ipynb" target="_blank">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="80">
</a>在Colab中打开项目
* 选择GPU运行时，点击全部运行，并允许访问云盘文件
* 等待翻译完成


### 注意事项 ⚠️
- 项目仍在测试，如遇 bug 欢迎提交 Issue 🐛
- 暂不支持本地运行


pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu