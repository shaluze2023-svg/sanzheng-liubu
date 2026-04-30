#!/usr/bin/env python3
"""
三省六部制 — 六部 API 协调脚本
负责尚书省的任务分发和六部执行结果汇总
"""

import json
import os
import sys
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ============================================================
# 六部定义
# ============================================================

class Department(Enum):
    """六部枚举"""
    LI_BU = "吏部"       # 项目管理、版本控制、团队协作
    HU_BU = "户部"       # 事务性数据处理、成本核算
    LI_BU2 = "礼部"      # 文档与代码规范、风格检查
    BING_BU = "兵部"     # 安全性分析（防御型）、测试部署
    XING_BU = "刑部"     # 合规性审计、错误溯源、调试
    GONG_BU = "工部"     # 代码编写、功能构建、算法实现


# 任务关键词到部门的映射规则
DEPARTMENT_RULES = {
    Department.LI_BU: {
        "keywords": ["git", "ci/cd", "pipeline", "deploy", "项目管理", "版本控制",
                      "协作", "排期", "branch", "merge", "release", "workflow"],
        "description": "项目管理、版本控制、团队协作与资源调度",
    },
    Department.HU_BU: {
        "keywords": ["统计", "分析", "预算", "成本", "依赖", "数据", "报表",
                      "count", "metrics", "budget", "dependency", "评估"],
        "description": "事务数据统计和成本评估",
    },
    Department.LI_BU2: {
        "keywords": ["文档", "注释", "格式", "规范", "style", "lint", "doc",
                      "comment", "format", "readme", "说明", "标准化"],
        "description": "代码规范审查和文档说明撰写",
    },
    Department.BING_BU: {
        "keywords": ["安全", "漏洞", "测试", "部署", "security", "vulnerability",
                      "test", "pentest", "扫描", "防护", "防火墙", "加密验证"],
        "description": "自动化的安全与部署任务",
    },
    Department.XING_BU: {
        "keywords": ["审计", "合规", "故障", "调试", "错误", "日志", "bug",
                      "debug", "trace", "fix", "troubleshoot", "排查", "修复"],
        "description": "告警分析、合规审计与故障调试",
    },
    Department.GONG_BU: {
        "keywords": ["编写", "开发", "实现", "功能", "代码", "api", "编码",
                      "build", "implement", "create", "feature", "construct",
                      "集成", "构建", "底层"],
        "description": "开发工作的核心逻辑实现",
    },
}


# ============================================================
# 数据结构
# ============================================================

@dataclass
class TaskUnit:
    """可执行的任务单元"""
    id: str
    description: str
    department: Department
    priority: int = 0  # 0=低, 1=中, 2=高, 3=紧急
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"  # pending/running/completed/failed
    result: Optional[str] = None


@dataclass
class Edict:
    """拟令（中书省产出）"""
    id: str
    source: str  # 皇帝旨意
    core_semantics: str
    summary: str
    steps: list[str]
    notes: list[str]
    review_status: str = "pending"  # pending/approved/rejected
    review_reason: Optional[str] = None


@dataclass
class ExecutionReport:
    """尚书省执行汇总报告"""
    edict_id: str
    tasks: list[TaskUnit]
    overall_status: str = "pending"
    summary: Optional[str] = None


# ============================================================
# 任务分类器
# ============================================================

class TaskClassifier:
    """根据任务描述自动分类到合适的部门"""

    @staticmethod
    def classify(task_description: str) -> list[Department]:
        """将任务描述匹配到最合适的部门（可多部门）"""
        scores: dict[Department, int] = {}
        desc_lower = task_description.lower()

        for dept, rules in DEPARTMENT_RULES.items():
            score = 0
            for kw in rules["keywords"]:
                if kw in desc_lower:
                    score += 1
            scores[dept] = score

        # 按得分排序，取前2个（支持跨部门协同）
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = [dept for dept, score in ranked if score > 0]

        # 如果没有匹配到任何部门，默认分配给工部（通用执行）
        if not result:
            result = [Department.GONG_BU]

        return result[:2]  # 最多跨2个部门


# ============================================================
# 门下省 — 审核复核
# ============================================================

class MenXiaReviewer:
    """门下省审核器：对拟令进行二次审核，拥有驳回权"""

    # 安全敏感关键词
    SENSITIVE_KEYWORDS = [
        "rm -rf", "delete all", "DROP TABLE", "truncate",
        "格式化", "清空", "删除全部", "root权限",
        "sudo rm", "chmod 777", "exec(", "eval(",
    ]

    def review_edict(self, edict: Edict) -> tuple[str, Optional[str]]:
        """审核拟令，返回 (状态, 驳回理由)"""
        issues = []

        # 1. 完整性审查
        if not edict.summary:
            issues.append("拟令缺少总结说明")
        if not edict.steps:
            issues.append("拟令缺少执行步骤")

        # 2. 安全审查
        all_text = f"{edict.summary} {' '.join(edict.steps)}"
        for kw in self.SENSITIVE_KEYWORDS:
            if kw.lower() in all_text.lower():
                issues.append(f"安全风险: 检测到敏感操作 '{kw}'")

        # 3. 一致性审查
        if not edict.core_semantics:
            issues.append("拟令缺少核心语义标签")

        if issues:
            reason = "门下省驳回理由:\n" + "\n".join(f"  - {i}" for i in issues)
            reason += "\n修改建议: 请中书省根据以上问题重新草拟拟令"
            return "rejected", reason

        return "approved", None


# ============================================================
# 中书省 — 决策起草
# ============================================================

class ZhongShuDrafter:
    """中书省起草器：对用户指令进行总结、筛选、重述，形成拟令"""

    def draft_edict(self, user_instruction: str, edict_counter: int = 1) -> Edict:
        """将用户指令转化为拟令"""
        summary = f"皇帝旨意总结: {user_instruction[:200]}"
        classifier = TaskClassifier()
        departments = classifier.classify(user_instruction)
        dept_names = [d.value for d in departments]
        core_semantics = f"涉及部门: {', '.join(dept_names)}"
        steps = [user_instruction]

        notes = []
        for kw in MenXiaReviewer.SENSITIVE_KEYWORDS:
            if kw.lower() in user_instruction.lower():
                notes.append(f"指令包含敏感关键词: {kw}")

        return Edict(
            id=f"E{edict_counter}",
            source="皇帝旨意",
            core_semantics=core_semantics,
            summary=summary,
            steps=steps,
            notes=notes,
        )


# ============================================================
# 尚书省 — 任务分发与汇总
# ============================================================

class ShangShuExecutor:
    """尚书省执行器：接收审核通过的拟令，拆分任务，分发六部，汇总结果"""

    def __init__(self, config: dict):
        self.config = config
        self.classifier = TaskClassifier()
        self.logger = logging.getLogger("尚书省")

    def decompose_edict(self, edict: Edict) -> list[TaskUnit]:
        """将拟令拆解为任务单元"""
        tasks = []
        for i, step in enumerate(edict.steps):
            departments = self.classifier.classify(step)
            primary_dept = departments[0]

            task = TaskUnit(
                id=f"{edict.id}-T{i+1}",
                description=step,
                department=primary_dept,
                priority=1,
            )
            tasks.append(task)
        return tasks

    def dispatch_to_department(self, task: TaskUnit) -> str:
        """将任务分发到对应部门执行"""
        dept_name = task.department.value
        api_config = self.config.get("departments", {}).get(task.department.name, {})
        model = api_config.get("model", "default")

        result = f"[{dept_name}] 已接收任务 {task.id}: {task.description}\n"
        result += f"  使用模型: {model}\n"
        result += f"  执行状态: 已完成"

        task.status = "completed"
        task.result = result
        return result

    def execute_edict(self, edict: Edict) -> ExecutionReport:
        """执行完整拟令流程"""
        tasks = self.decompose_edict(edict)

        for task in tasks:
            self.dispatch_to_department(task)

        report = ExecutionReport(
            edict_id=edict.id,
            tasks=tasks,
            overall_status="completed",
        )

        # 生成汇总报告
        summary_lines = [f"## 尚书省执行汇总 — 拟令 #{edict.id}"]
        summary_lines.append(f"\n**来源**: {edict.source}")
        summary_lines.append(f"**核心语义**: {edict.core_semantics}")
        summary_lines.append(f"\n### 任务执行明细")

        for task in tasks:
            dept = task.department.value
            summary_lines.append(f"- **{dept}** [{task.id}]: {task.description} -> {task.status}")

        summary_lines.append(f"\n### 执行结果汇总")
        for task in tasks:
            if task.result:
                summary_lines.append(task.result)

        summary_lines.append(f"\n---")
        summary_lines.append(f"*以上结果已呈报皇帝，恭请圣裁*")

        report.summary = "\n".join(summary_lines)
        return report


# ============================================================
# 完整流程编排
# ============================================================

class SanZhengLiuBuOrchestrator:
    """三省六部制完整流程编排器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.zhongshu = ZhongShuDrafter()
        self.menxia = MenXiaReviewer()
        self.shangshu = ShangShuExecutor(self.config)
        self.edict_counter = 0
        self.logger = logging.getLogger("三省六部制")

    def _load_config(self, config_path: Optional[str]) -> dict:
        """加载配置"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)

        # 默认配置
        return {
            "zhongshu": {"model": "claude-4-6-opus", "temperature": 0.3},
            "menxia": {"model": "claude-4-6-opus", "temperature": 0.2},
            "shangshu": {"model": "claude-4-6-opus", "temperature": 0.4},
            "departments": {
                "LI_BU": {"model": "claude-4-6-opus", "temperature": 0.3},
                "HU_BU": {"model": "claude-4-6-opus", "temperature": 0.3},
                "LI_BU2": {"model": "claude-4-6-opus", "temperature": 0.2},
                "BING_BU": {"model": "claude-4-6-opus", "temperature": 0.2},
                "XING_BU": {"model": "claude-4-6-opus", "temperature": 0.3},
                "GONG_BU": {"model": "claude-4-6-opus", "temperature": 0.4},
            },
        }

    def process_instruction(self, user_instruction: str) -> str:
        """处理完整的皇帝指令流程"""
        self.edict_counter += 1
        self.logger.info(f"=== 三省六部制流程启动 === 指令 #{self.edict_counter}")

        # Phase 1: 中书省草拟
        edict = self.zhongshu.draft_edict(user_instruction, self.edict_counter)

        # Phase 2: 门下省审核
        review_status, review_reason = self.menxia.review_edict(edict)
        edict.review_status = review_status
        edict.review_reason = review_reason

        if review_status == "rejected":
            output = f"## 门下省驳回通知\n\n"
            output += f"**拟令编号**: {edict.id}\n"
            output += f"**审核状态**: 驳回\n\n"
            output += review_reason
            output += f"\n\n---\n*恭请皇帝圣裁，是否调整指令后重新下达*"
            return output

        # Phase 3: 尚书省执行
        report = self.shangshu.execute_edict(edict)
        return report.summary or "执行完成，但无汇总报告"


# ============================================================
# CLI 入口
# ============================================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="三省六部制 — 多角色代理协调器")
    parser.add_argument("instruction", help="皇帝指令内容")
    parser.add_argument("--config", help="配置文件路径", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(name)s] %(message)s")

    orchestrator = SanZhengLiuBuOrchestrator(args.config)
    result = orchestrator.process_instruction(args.instruction)
    print(result)


if __name__ == "__main__":
    main()