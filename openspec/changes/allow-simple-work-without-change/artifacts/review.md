# 独立审核轮次

- Active change: `allow-simple-work-without-change`
- 已批准范围：12个源/测试文件及本 change 的规划和证据；详见 `review-inputs.json`。
- 完整审核：第1轮已完成，REVIEW_STATUS: FINDINGS（F1、F2 阻断），报告在 `review-full-result.md`。
- 阻断修复：README 旧指南改为快速通道/正式分支，主路由 Assess Profile First 收进正式分支；回归断言已加（41/41 GREEN，`repair-red*.log`、`repair-green*.log`）。
- 定向复核：1轮已完成，REVIEW_STATUS: CLEAN（F1、F2 均已修复，无新增阻断），报告在 `review-focused-result.md`。
- 验证：Node 41/41（修复前 RED 2→1 失败、修复后 GREEN，见 repair 日志）；基线（Node 39/39、Python 16/16、OpenSpec strict、安装54项）仍有效；定向复核确认纯文本修复不需要重跑 Python/安装比对。
- NOT RUN：默认LSP（biome不可用）、四宿主新会话端到端执行、全局安装与外部gate行为。
- 审核输入：`review-inputs.json` 的12项SHA256；相对本次实施前字节的增量为 `review-input.patch`。HEAD仅提供提交来源，不能认证未提交材料。
- 预算：不叠加 `code-reviewer`；仅一次 focused 覆盖 F1/F2 与修复差异，不重新征集全范围建议。
