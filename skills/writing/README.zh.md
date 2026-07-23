# writing

[English](README.md)

**面向人类读者的写作**类 skill——包括体裁类（学术、博客/评论、宣传文案）
与载体类（LaTeX、Typst、Markdown 源码）。它们共享同一套基础：动笔前先明确
文章类型、作者、读者与预期效果；让读者能感受到一个具体的作者；核实每一处
引用；克制地修改。通用基线 skill `human-writing` 位于 `core` catalog。

```bash
npx skills add ryan-minato/skills --skill <skill-name>
```

## Skill 列表

| Skill | 说明 |
|---|---|
| [academic-writing](academic-writing/) | 以英文、中文或日文撰写和修改学术文本（论文、学位论文、报告）：在编辑/研究者/审稿人角色间切换，围绕论证主线规划结构，按可信度层级取用来源并用脚本核验引用，执行严格的语体规则，克制地修改。 |
| [blog-writing](blog-writing/) | 以英文、中文或日文撰写和改进带作者立场的博客、专栏与评论：先确认读者与作者形象，沿读者情绪与思想的变化规划结构并按重要性分配篇幅，保持立场锋利、节奏优先于防御性叙述，引用核实不了就不用。 |
| [copywriting](copywriting/) | 以英文、中文或日文撰写宣传文案（社媒帖文、广告与落地页文字、slogan）：先以甲方视角确定需求，围绕情绪与传播性，把唯一信息前置并追求密度，在媒介需要时允许结构让位于传播。 |
| [latex-authoring](latex-authoring/) | 编写、修改并整理 LaTeX 源码：语法查 class 文档、texdoc/CTAN 与 Overleaf Learn 而不是靠猜；利用单个换行不影响排版的特性，在逻辑断点（语义换行）折行；涵盖宏、连字符、label、宏包顺序等核心陷阱。 |
| [markdown-authoring](markdown-authoring/) | 面向特定渲染引擎编写 Markdown：先确定方言（GFM、GLFM、mkdocs、Docusaurus/MDX、Obsidian、聊天工具），再套用其换行/空行语义以及数学、mermaid、脚注、admonition 和 HTML 的写法；引擎未知时退回保守的 CommonMark 子集。 |
| [typst-authoring](typst-authoring/) | 编写和修改 Typst 源码：正文内置入门（markup/code/math 三模式、set/show 规则、include 与 import 的区别、模板模式），另附图表、表格、数学与参考文献速查表——Typst 足够冷门，凭感觉写出来的多半是伪装的 LaTeX。 |
