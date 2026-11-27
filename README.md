# Career Opportunity Skill

**简历驱动的求职辅导 Skill：从这份简历和约束出发，打开真实招聘页，给出能投的岗位、求职策略，以及一份可以保存的网页报告。**

An Agent Skill that turns a resume into a career-counselor report. A live run opens current postings and ranks the ones this person can apply to.

## 快速开始

在支持 Agent Skills 的客户端中安装：

```bash
npx skills add tongruizhang1097-crypto/career-opportunity-skill
```

也可以为 Codex 手动安装到默认技能目录（使用自定义 `CODEX_HOME` 时请相应调整路径）：

```bash
git clone https://github.com/tongruizhang1097-crypto/career-opportunity-skill.git ~/.codex/skills/find-career-opportunities
```

在能够读取附件、联网搜索和打开网页的 AI 助手中，上传简历，然后发送：

```text
使用 $find-career-opportunities，根据附件简历找现在能投的岗位，并生成可保存的网页报告。
```

可选补充城市、毕业时间、当前实习，以及愿意做和不愿意做的事。只给简历时，也会按明确标注的暂定场景继续，不要求先填完问卷。

## 默认交付

主交付是 **一份单文件 HTML 网页**。用浏览器直接打开，不需要本地服务器，也不加载外部样式或脚本。需要 PDF 时，在浏览器里打印并另存为 PDF；打印样式会把链接展开。本仓库不调用付费转换接口。环境里没有无头浏览器时，不因缺少 PDF 文件而停更报告。

同时保留 Markdown 报告、证据 CSV 和运行清单 JSON。CSV 是台账。判断和岗位旁边仍然要看到来源，不能只把链接放在 CSV 里。

## 可投岗位

实时或半实时报告必须有一步 **「找岗可投岗位」**：检索雇主官网和公司招聘系统，以及该市场真正在用的招聘板（中国大陆检索包含 BOSS直聘；有在招信息时包含 LinkedIn；在校生包含学校官方就业网），打开页面，剔除不符合的，再按固定顺序排出最多 10 个现在能投的岗位。

每个岗位都要在网页上、紧挨着推荐写明：

- 来源名称（雇主官网、招聘系统，或点名的招聘板）
- 可点击的一手链接
- 发布日期（页面没写就写没写）
- 截止日期（没有就写没有）
- 本次打开页面的时间

不足 10 个时，输出实际数量，并说明为什么更短。不得用已关闭广告、过期公告、届别不符的岗位，或这次打不开原文的转载来凑数。转载只能当线索，原文打开之后才能引用。

排序规则写在 Skill 和报告模板里，按这个顺序，不另做加权分：本轮一手核验仍在招、与简历里已经做成的工作是否契合、资格是否够得着、岗位成色、来源质量、新鲜程度和截止日期、仅当招聘原文写明时才看留用或转化。每一名用一两句话说明为什么是这个人，而不是一句通用的“匹配度高”。

## 来源与信任

实质判断和推荐岗位都要有一手来源。优先雇主官方页面，其次是公司招聘系统或具名招聘板。来源就放在对应的句子或岗位卡片下面。

报告区分三个时间：岗位或文章的发布日期、统计数据覆盖的时期、本次运行打开页面的时间。今天打开一个网页，不等于网页里的数字描述的是今天的市场。

| 状态 | 含义 |
| --- | --- |
| `live` | 本轮已核验市场来源，并披露抽样和数据限制。 |
| `partial` | 一部分来源本轮已核验，其他岗位、历史数据或材料仍无法确认。 |
| `offline` | 本轮没有核验在线市场来源。只做简历分析和待验证假设，不声称当前有在招岗位。 |

实时性指生成时重新核验的快照。它不覆盖全部市场，不保证广告对应未填的编制，也不会把岗位数量当成人才短缺。

## 报告里还有什么

- **能力与约束**：区分简历自述、已经做成的事、当前实习，以及这个人愿意和不愿意做的事。
- **求职策略**：现在投什么、先跳过什么、补哪一份作品、两条路怎么选、什么事实会改建议。
- **方向比较**：作为策略的辅助，不代替可投名单。
- **排除清单**：看过但没有推荐的岗位，以及关闭、未打开、届别不符或只有转载等原因。

## 运行要求

- 支持读取本地文件或附件的 AI 助手。
- 生成实时报告需要搜索和打开网页。本仓库不附带搜索服务或商业劳动力数据库。
- PDF / DOCX / 扫描件解析依赖客户端已有的文档和 OCR 能力。读不出来的部分必须标明。
- 可选 Python 3.9+。清单核验和测试只用标准库。

## 检查运行清单

在仓库或已安装 Skill 的根目录执行：

```bash
python3 scripts/audit_run.py /path/to/run-manifest.json
```

脚本检查时间戳、来源引用和研究状态。对写进 `recommended_jobs` 的岗位，还会检查一手链接、本次核验时间，以及已关闭或未核验的岗位有没有被标成当前推荐。少于 10 个时必须有 `shortfall_reason`。**它不联网、不验证页面正文，也不证明市场结论正确。**

从当前模板出发的 live / partial 运行要保留 `job_search` 和 `recommended_jobs`。完全没有这两个字段的旧清单只会收到警告，以免把本功能加入之前的元数据测试判失败。

执行自动测试：

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖跨时区时间、旧来源、搜索索引、已关闭岗位、离线降级、缺失链接、转载、届别不符和凑满 10 条等情景。测试使用虚构元数据，不包含真实个人简历。

## 文件结构

| 路径 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | 主工作流、找岗步骤与排序规则 |
| [agents/openai.yaml](agents/openai.yaml) | Skill 界面元数据和默认调用提示 |
| [references/resume-intake.md](references/resume-intake.md) | 简历、约束与缺失偏好 |
| [references/job-search.md](references/job-search.md) | 「找岗可投岗位」：检索、打开、筛选、排序 |
| [references/live-research.md](references/live-research.md) | 实时检索、三种研究状态与清单字段 |
| [references/evidence-protocol.md](references/evidence-protocol.md) | 可投名单与市场证据的口径 |
| [assets/report-template.html](assets/report-template.html) | 单文件网页报告模板（主交付） |
| [assets/report-template.md](assets/report-template.md) | Markdown 报告模板 |
| [assets/](assets/) | 能力画像、证据表和运行清单模板 |
| [scripts/audit_run.py](scripts/audit_run.py) | 运行清单元数据核验 |
| [tests/](tests/) | 可复现的离线自动测试 |

## 个人资料

公开仓库只保存通用流程、空模板和虚构测试。不要把真实简历、个人报告或运行记录提交到仓库。检索使用匿名化的任务、资历和地区词，不把整份简历或联系方式发给外部服务。

## English overview

Install the skill, attach a resume, and ask the agent to use `$find-career-opportunities`. It reads that person's evidence and constraints, opens employer and job-board pages in the same run, and writes a job-seeking strategy. The action section is a ranked list of at most 10 postings verified as open and eligible. A shorter list stays short, with the reason stated. Each claim and job shows the source name, URL, posting date, deadline, and the time the page was checked.

The primary file is a self-contained HTML page. Print it to PDF from the browser. A Markdown report, evidence CSV, and run manifest are written as well. Fresh browsing is required for a live report. Publication date, data period, and inspection time stay separate. Status is `live`, `partial`, or `offline`.

The optional Python auditor checks declared metadata, including first-hand URLs and check times on recommended jobs. It is not a crawler. The skill does not guarantee employment, a salary, or a blue-ocean career. It is domain-agnostic and does not embed a person's identity or resume.

## License

[MIT](LICENSE)
