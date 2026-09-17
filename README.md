# 科研项目验收技能

维护者：[kuangjunwei1](https://github.com/kuangjunwei1)。

这是一个通用的项目材料审核技能，提供审核、替换、同步、提交整理四条流程，以及空白工作表结构和只读文件检查工具。

不附任何机构内部制度、指南原件、项目档案、签名印章或实际财务记录。使用时必须提供本项目适用的制度、合同/任务书、正式变更和模板；技能不预设金额门槛、时间、专家人数、盖章主体或字体要求，不出具专业审计意见。

## 使用

将本仓库完整保存为 `research-project-acceptance` 文件夹，放入目标工具配置的技能目录。在支持技能调用的环境中使用：

```text
使用 $research-project-acceptance，按我提供的制度与任务书审核正式目录。
完整阅读后给出问题位置、依据和建议；此次不修改文件。
```

```text
使用 $research-project-acceptance，只同步工作报告和自查表的论文清单。
按真实发表/录用状态统计，保留格式、历史意见和源文件，先备份再修改。
```

不同运行环境的安装目录、文档转换及权限可能不同；先确认技能已被发现，不将访问令牌写进文件。

## 文件

- `SKILL.md`：入口及任务分流。
- `references/`：规则建模、四类流程、命名方法。
- `assets/deliverables.md`：可选空白台账、证据矩阵和问题记录结构，并非官方报告模板。
- `scripts/inspect_materials.py`：只读清点和PDF物理页范围检查。
- `tests/`：离线功能/包结构测试及合成行为案例。
- `TEST_REPORT.md`：本公开版本的验证边界。

## 检查工具

```shell
python -m pip install pypdf
python scripts/inspect_materials.py inventory "正式资料目录"
python scripts/inspect_materials.py page-check "报告.pdf" --pages 2,4
```

工具向标准输出返回JSON，不创建、修改、移动或删除输入文件。返回码0表示清点或页范围检查完成，2表示读取失败、缺依赖、损坏或越界。重复和编号冲突只是候选问题，不自动删除。

PDF页存在不代表内容满足指标；Office元数据不是全文审阅或排版验证；旧二进制表格格式仅清点及计算哈希。目录链接/联接点跳过并报告。

## 测试

```shell
python -m pip install PyYAML pypdf python-docx
python -m unittest discover -s tests -v
```

Python 3.10+。测试使用临时合成文件，不需要业务数据或模型凭据。依赖安装可能联网。单元测试不执行模型，不证明每次业务判断、OCR或Office排版都正确。行为案例需独立运行并人工核验，不能仅因案例文件存在就称通过。

## 安全及范围

没有适用原文或证明不足时，应返回待核实范围，不宣布验收通过。原始签章及历史意见不应因内容调整被重新解释为新认可。发布代码前应检查全部可见历史、元数据、讨论及附件；不能仅清理最新版。

仓库公开不等于已授予特定开源许可；此版本未指定许可证。
