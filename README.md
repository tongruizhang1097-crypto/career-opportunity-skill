# Career Opportunity Skill

**简历驱动的职业机会研究 Skill：上传简历，结合本次联网证据，生成职业方向、能力差距与验证计划。**

An Agent Skill that turns a resume into an evidence-linked career opportunity report using fresh market research on every live run.

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
使用 $find-career-opportunities，根据附件简历生成实时职业机会报告。
```

可选补充目标地区、入场时间、收入和工作条件。仅提供简历时，也会先按明确标注的暂定场景开展分析，不要求填写完整问卷。

## 报告内容

- **能力画像**：区分简历自述、项目证据、研究兴趣与未核实能力。
- **职业机会比较**：从现有能力寻找相邻任务，同时从产业变化寻找新增的付费需求。
- **市场与个人双重判断**：分别评估需求增长、合格人才供给、个人进入成本、时间窗口、岗位回报和能力迁移空间。
- **当前岗位证据**：记录企业、岗位层级、要求、来源与本次核验时间。
- **行动验证计划**：把学习和项目投入对应到真实任务，说明成功信号、反证及下一步决策。

文件生成能力可用时，默认交付 Markdown 报告、证据 CSV 和运行清单 JSON；PDF / Word 输出取决于客户端能力和用户请求。

## 实时性如何处理

每次实时报告都重新检索，并区分来源的**发布时间、数据覆盖时期、本次核验时间**。打开今天的网页，不等于网页中的统计描述今天的市场。

| 状态 | 含义 |
| --- | --- |
| `live` | 本轮已核验市场来源，并披露抽样和数据限制。 |
| `partial` | 一部分来源本轮已核验，其他岗位、历史数据或材料仍无法确认。 |
| `offline` | 本轮没有核验在线市场来源，只提供简历分析和待验证假设。 |

实时性指生成时重新核验的信息快照。它不提供完整市场覆盖，不保证广告对应未填补编制，也不会把岗位数量或申请人数直接当成人才短缺证据。

## 运行要求

- 支持读取本地文件或附件的 AI 助手。
- 生成实时市场报告需要搜索及网页读取能力；本仓库不附带搜索服务或商业劳动力数据库。
- PDF / DOCX / 扫描件解析依赖客户端已有的文档和 OCR 能力；无法读取的内容必须明确标注。
- 可选 Python 3.9+：运行清单核验与测试只使用标准库。

## 检查运行清单

在仓库或已安装 Skill 的根目录执行：

```bash
python3 scripts/audit_run.py /path/to/run-manifest.json
```

脚本检查时间戳、来源引用、实时状态以及当前岗位推荐是否具备声明的本轮核验依据。**它不联网、不验证来源内容，也不证明市场结论正确。**

执行自动测试：

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖跨时区时间、旧来源、搜索索引、已关闭岗位、离线降级、缺失来源、重复引用和滞后统计等情景。测试使用虚构元数据，不包含真实个人简历。

## 文件结构

| 路径 | 用途 |
| --- | --- |
| [SKILL.md](SKILL.md) | 主工作流与触发说明 |
| [agents/openai.yaml](agents/openai.yaml) | Skill 界面元数据和默认调用提示 |
| [references/resume-intake.md](references/resume-intake.md) | 简历提取、证据边界与缺失偏好处理 |
| [references/live-research.md](references/live-research.md) | 每次运行的实时检索和来源状态规则 |
| [references/evidence-protocol.md](references/evidence-protocol.md) | 市场数据、供需与比较口径 |
| [assets/](assets/) | 报告、能力画像、证据表和运行清单模板 |
| [scripts/audit_run.py](scripts/audit_run.py) | 运行清单元数据核验 |
| [tests/](tests/) | 可复现的离线自动测试 |

## 个人资料

公开仓库只保存通用流程、空模板和虚构测试。不要将真实简历、个人报告或运行记录提交到仓库。Skill 要求使用匿名化能力、任务和地区词进行公开搜索，不将整份简历或联系方式发给外部服务。

## English overview

Install the skill, attach a resume, and ask your agent to use `$find-career-opportunities`. The agent extracts evidenced capabilities, researches adjacent and emerging work, and compares market attractiveness with personal entry advantage. It produces conditional recommendations, attributable evidence, capability gaps, and practical validation experiments.

Fresh browsing is required for a live report. Each run separates publication dates, observation periods, and inspection timestamps, and declares `live`, `partial`, or `offline` coverage. The optional Python auditor checks declared metadata only; it is not a crawler or a truth verifier. The skill does not guarantee a blue-ocean career, employment, or a particular salary.

The workflow is domain-agnostic. It does not embed a particular user's identity, resume, research specialty, or private reports.

## License

[MIT](LICENSE)
