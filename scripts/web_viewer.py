#!/usr/bin/env python3
"""
三省六部制 — Web 可视化查看器
启动本地 Web 服务，在浏览器中展示 Agent 流程的象形树工作记录
"""

import json
import os
import sys
import time
import uuid
import argparse
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from urllib.parse import urlparse, parse_qs

# ============================================================
# 工作记录数据结构
# ============================================================

class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TreeNode:
    """象形树节点"""
    id: str
    name: str
    role: str
    status: str = "pending"
    content: str = ""
    timestamp: str = ""
    children: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "content": self.content,
            "timestamp": self.timestamp,
            "children": [c.to_dict() if isinstance(c, TreeNode) else c for c in self.children],
            "metadata": self.metadata,
        }


@dataclass
class WorkflowSession:
    """一次完整的工作流会话"""
    id: str
    instruction: str
    start_time: str
    tree: Optional[dict] = None
    end_time: str = ""
    status: str = "running"

    def to_dict(self):
        return {
            "id": self.id,
            "instruction": self.instruction,
            "start_time": self.start_time,
            "tree": self.tree,
            "end_time": self.end_time,
            "status": self.status,
        }


# ============================================================
# 全局工作记录存储
# ============================================================

class WorkflowStore:
    """工作记录存储（内存 + 文件持久化）"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: list[WorkflowSession] = []
        self._load()

    def _load(self):
        log_file = self.data_dir / "workflow_log.json"
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    data = json.load(f)
                self.sessions = [WorkflowSession(**s) for s in data]
            except Exception:
                self.sessions = []

    def _save(self):
        log_file = self.data_dir / "workflow_log.json"
        with open(log_file, "w") as f:
            json.dump([s.to_dict() for s in self.sessions], f, ensure_ascii=False, indent=2)

    def add_session(self, session: WorkflowSession):
        self.sessions.append(session)
        self._save()

    def update_session(self, session_id: str, tree: dict, status: str = "running", end_time: str = ""):
        for s in self.sessions:
            if s.id == session_id:
                s.tree = tree
                s.status = status
                if end_time:
                    s.end_time = end_time
                break
        self._save()

    def get_all(self):
        return [s.to_dict() for s in self.sessions]

    def get_latest(self):
        if self.sessions:
            return self.sessions[-1].to_dict()
        return None


# ============================================================
# 流程编排器（集成 Web 日志记录）
# ============================================================

class Department(Enum):
    LI_BU = "吏部"
    HU_BU = "户部"
    LI_BU2 = "礼部"
    BING_BU = "兵部"
    XING_BU = "刑部"
    GONG_BU = "工部"


DEPARTMENT_RULES = {
    Department.LI_BU: {"keywords": ["git", "ci/cd", "pipeline", "deploy", "项目管理", "版本控制", "协作", "排期", "branch", "merge", "release", "workflow"]},
    Department.HU_BU: {"keywords": ["统计", "分析", "预算", "成本", "依赖", "数据", "报表", "count", "metrics", "budget", "dependency", "评估"]},
    Department.LI_BU2: {"keywords": ["文档", "注释", "格式", "规范", "style", "lint", "doc", "comment", "format", "readme", "说明", "标准化"]},
    Department.BING_BU: {"keywords": ["安全", "漏洞", "测试", "部署", "security", "vulnerability", "test", "pentest", "扫描", "防护", "防火墙", "加密验证"]},
    Department.XING_BU: {"keywords": ["审计", "合规", "故障", "调试", "错误", "日志", "bug", "debug", "trace", "fix", "troubleshoot", "排查", "修复"]},
    Department.GONG_BU: {"keywords": ["编写", "开发", "实现", "功能", "代码", "api", "编码", "build", "implement", "create", "feature", "construct", "集成", "构建", "底层"]},
}

SENSITIVE_KEYWORDS = ["rm -rf", "delete all", "DROP TABLE", "truncate", "格式化", "清空", "删除全部", "root权限", "sudo rm", "chmod 777", "exec(", "eval("]


class WebOrchestrator:
    """带 Web 日志的三省六部编排器"""

    def __init__(self, store: WorkflowStore):
        self.store = store
        self.logger = logging.getLogger("三省六部制")

    def _classify(self, text: str) -> list[Department]:
        scores = {}
        desc_lower = text.lower()
        for dept, rules in DEPARTMENT_RULES.items():
            score = sum(1 for kw in rules["keywords"] if kw in desc_lower)
            scores[dept] = score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result = [dept for dept, score in ranked if score > 0]
        if not result:
            result = [Department.GONG_BU]
        return result[:2]

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def process_instruction(self, user_instruction: str) -> str:
        session_id = uuid.uuid4().hex[:8]
        session = WorkflowSession(
            id=session_id,
            instruction=user_instruction,
            start_time=self._now(),
        )
        self.store.add_session(session)

        # === 皇帝节点 ===
        emperor_node = TreeNode(
            id=f"{session_id}-emperor",
            name="皇帝",
            role="emperor",
            status="completed",
            content=f"下达指令：{user_instruction}",
            timestamp=self._now(),
        )

        # === 中书省：拟令 ===
        zhongshu_node = TreeNode(
            id=f"{session_id}-zhongshu",
            name="中书省",
            role="zhongshu",
            status="running",
            content="正在起草拟令...",
            timestamp=self._now(),
        )
        emperor_node.children.append(zhongshu_node)

        summary = f"皇帝旨意总结：{user_instruction[:200]}"
        departments = self._classify(user_instruction)
        dept_names = [d.value for d in departments]
        core_semantics = f"涉及部门：{', '.join(dept_names)}"

        zhongshu_node.status = "completed"
        zhongshu_node.content = f"拟令起草完成\n\n**指令总结**：{summary}\n**核心语义**：{core_semantics}\n**涉及部门**：{', '.join(dept_names)}"
        zhongshu_node.timestamp = self._now()

        # 更新树
        self.store.update_session(session_id, emperor_node.to_dict())

        # === 门下省：审核 ===
        menxia_node = TreeNode(
            id=f"{session_id}-menxia",
            name="门下省",
            role="menxia",
            status="running",
            content="正在审核拟令...",
            timestamp=self._now(),
        )
        zhongshu_node.children.append(menxia_node)

        # 安全审查
        issues = []
        all_text = f"{summary} {user_instruction}"
        for kw in SENSITIVE_KEYWORDS:
            if kw.lower() in all_text.lower():
                issues.append(f"安全风险：检测到敏感操作 '{kw}'")

        if issues:
            menxia_node.status = "rejected"
            menxia_node.content = "审核驳回\n\n" + "\n".join(f"- {i}" for i in issues) + "\n\n修改建议：请中书省根据以上问题重新草拟拟令"
            menxia_node.timestamp = self._now()
            self.store.update_session(session_id, emperor_node.to_dict(), status="rejected", end_time=self._now())
            return f"门下省驳回：{'; '.join(issues)}"

        menxia_node.status = "approved"
        menxia_node.content = "审核通过\n\n- 完整性：合格\n- 安全性：合格\n- 一致性：合格"
        menxia_node.timestamp = self._now()
        self.store.update_session(session_id, emperor_node.to_dict())

        # === 尚书省：分发执行 ===
        shangshu_node = TreeNode(
            id=f"{session_id}-shangshu",
            name="尚书省",
            role="shangshu",
            status="running",
            content="正在拆解任务并分发至六部...",
            timestamp=self._now(),
        )
        menxia_node.children.append(shangshu_node)
        self.store.update_session(session_id, emperor_node.to_dict())

        # 六部执行
        dept_colors = {
            "吏部": "#4FC3F7", "户部": "#81C784", "礼部": "#FFB74D",
            "兵部": "#E57373", "刑部": "#BA68C8", "工部": "#FFD54F",
        }

        task_results = []
        for i, dept in enumerate(departments):
            dept_node = TreeNode(
                id=f"{session_id}-dept-{i}",
                name=dept.value,
                role=f"dept-{dept.name.lower()}",
                status="running",
                content=f"正在执行任务...",
                timestamp=self._now(),
                metadata={"color": dept_colors.get(dept.value, "#90A4AE")},
            )
            shangshu_node.children.append(dept_node)
            self.store.update_session(session_id, emperor_node.to_dict())

            # 模拟执行
            time.sleep(0.1)
            dept_node.status = "completed"
            dept_node.content = f"{dept.value}执行完成\n\n任务：{user_instruction}\n状态：已完成"
            dept_node.timestamp = self._now()
            task_results.append(f"{dept.value}：已完成")

        shangshu_node.status = "completed"
        shangshu_node.content = f"尚书省汇总完成\n\n" + "\n".join(task_results) + "\n\n*以上结果已呈报皇帝，恭请圣裁*"
        shangshu_node.timestamp = self._now()

        self.store.update_session(session_id, emperor_node.to_dict(), status="completed", end_time=self._now())
        return "执行完成，结果已呈报皇帝"


# ============================================================
# Web 服务器
# ============================================================

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>三省六部制 — Agent 工作流可视化</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0a0e1a;--surface:#111827;--surface2:#1a2332;--border:#1e3a5f;
  --text:#e2e8f0;--text2:#94a3b8;--accent:#60a5fa;--accent2:#818cf8;
  --emperor:#fbbf24;--zhongshu:#60a5fa;--menxia:#34d399;--shangshu:#a78bfa;
  --libu:#4fc3f7;--hubu:#81c784;--libu2:#ffb74d;--bingbu:#e57373;--xingbu:#ba68c8;--gongbu:#ffd54f;
  --pending:#64748b;--running:#60a5fa;--approved:#34d399;--rejected:#f87171;--completed:#a78bfa;--failed:#ef4444;
}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;min-height:100vh;overflow-x:hidden}
.bg-glow{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}
.bg-glow::before{content:'';position:absolute;top:-20%;left:-10%;width:50%;height:50%;background:radial-gradient(circle,rgba(96,165,250,0.08) 0%,transparent 70%);animation:float1 20s ease-in-out infinite}
.bg-glow::after{content:'';position:absolute;bottom:-20%;right:-10%;width:50%;height:50%;background:radial-gradient(circle,rgba(167,139,250,0.08) 0%,transparent 70%);animation:float2 25s ease-in-out infinite}
@keyframes float1{0%,100%{transform:translate(0,0)}50%{transform:translate(5%,10%)}}
@keyframes float2{0%,100%{transform:translate(0,0)}50%{transform:translate(-5%,-10%)}}
.container{position:relative;z-index:1;max-width:1400px;margin:0 auto;padding:20px}
header{text-align:center;padding:40px 0 30px}
header h1{font-size:2.2rem;font-weight:700;background:linear-gradient(135deg,var(--emperor),var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:2px}
header p{color:var(--text2);margin-top:8px;font-size:0.95rem}
.controls{display:flex;gap:12px;justify-content:center;align-items:center;margin:20px 0;flex-wrap:wrap}
.controls input{background:var(--surface);border:1px solid var(--border);color:var(--text);padding:12px 18px;border-radius:12px;font-size:0.95rem;width:400px;max-width:100%;outline:none;transition:border-color .3s}
.controls input:focus{border-color:var(--accent)}
.controls button{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;padding:12px 28px;border-radius:12px;font-size:0.95rem;font-weight:600;cursor:pointer;transition:all .3s;letter-spacing:1px}
.controls button:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(96,165,250,0.3)}
.controls button:active{transform:translateY(0)}
.stats{display:flex;gap:16px;justify-content:center;margin:20px 0;flex-wrap:wrap}
.stat-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:16px 24px;text-align:center;min-width:120px;backdrop-filter:blur(10px)}
.stat-card .num{font-size:1.8rem;font-weight:700;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.stat-card .label{font-size:0.8rem;color:var(--text2);margin-top:4px}
.tree-container{margin-top:30px}
.session-card{background:var(--surface);border:1px solid var(--border);border-radius:20px;margin-bottom:20px;overflow:hidden;backdrop-filter:blur(10px);transition:all .3s}
.session-card:hover{border-color:rgba(96,165,250,0.3)}
.session-header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;cursor:pointer;border-bottom:1px solid var(--border);transition:background .3s}
.session-header:hover{background:var(--surface2)}
.session-header .left{display:flex;align-items:center;gap:12px}
.session-header .id-badge{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;padding:4px 12px;border-radius:8px;font-size:0.8rem;font-weight:600}
.session-header .instruction{font-weight:600;font-size:1rem}
.session-header .right{display:flex;align-items:center;gap:12px}
.session-header .time{color:var(--text2);font-size:0.85rem}
.session-body{padding:24px;display:none}
.session-body.open{display:block}
.tree-visual{position:relative}
.tree-node{position:relative;margin:8px 0;padding-left:40px}
.tree-node::before{content:'';position:absolute;left:16px;top:0;bottom:0;width:2px;background:var(--border)}
.tree-node:last-child::before{bottom:50%}
.tree-node::after{content:'';position:absolute;left:16px;top:24px;width:20px;height:2px;background:var(--border)}
.node-card{background:var(--surface2);border:1px solid var(--border);border-radius:14px;padding:16px 20px;transition:all .4s;position:relative;overflow:hidden}
.node-card::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;border-radius:4px 0 0 4px}
.node-card[data-role="emperor"]::before{background:var(--emperor)}
.node-card[data-role="zhongshu"]::before{background:var(--zhongshu)}
.node-card[data-role="menxia"]::before{background:var(--menxia)}
.node-card[data-role="shangshu"]::before{background:var(--shangshu)}
.node-card[data-role^="dept-"]::before{background:var(--accent)}
.node-card:hover{transform:translateX(4px);border-color:rgba(96,165,250,0.3);box-shadow:0 4px 20px rgba(0,0,0,0.3)}
.node-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.node-name{font-weight:700;font-size:1rem;display:flex;align-items:center;gap:8px}
.node-name .icon{font-size:1.2rem}
.node-status{padding:3px 10px;border-radius:8px;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px}
.node-status.pending{background:rgba(100,116,139,0.2);color:var(--pending)}
.node-status.running{background:rgba(96,165,250,0.2);color:var(--running);animation:pulse 2s infinite}
.node-status.approved{background:rgba(52,211,153,0.2);color:var(--approved)}
.node-status.rejected{background:rgba(248,113,113,0.2);color:var(--rejected)}
.node-status.completed{background:rgba(167,139,250,0.2);color:var(--completed)}
.node-status.failed{background:rgba(239,68,68,0.2);color:var(--failed)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.node-content{color:var(--text2);font-size:0.88rem;line-height:1.6;white-space:pre-wrap;word-break:break-word}
.node-time{color:var(--text2);font-size:0.75rem;margin-top:6px;opacity:0.7}
.node-children{margin-top:8px}
.empty-state{text-align:center;padding:60px 20px;color:var(--text2)}
.empty-state .icon{font-size:4rem;margin-bottom:16px;opacity:0.3}
.empty-state p{font-size:1.1rem;margin-bottom:8px}
.empty-state .hint{font-size:0.85rem;opacity:0.6}
.legend{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin:20px 0;padding:16px;background:var(--surface);border:1px solid var(--border);border-radius:14px}
.legend-item{display:flex;align-items:center;gap:6px;font-size:0.8rem;color:var(--text2)}
.legend-dot{width:10px;height:10px;border-radius:50%}
footer{text-align:center;padding:40px 0;color:var(--text2);font-size:0.8rem;opacity:0.5}
@media(max-width:768px){
  .controls input{width:100%}
  header h1{font-size:1.6rem}
  .stats{gap:8px}
  .stat-card{min-width:80px;padding:12px 16px}
  .stat-card .num{font-size:1.3rem}
}
</style>
</head>
<body>
<div class="bg-glow"></div>
<div class="container">
  <header>
    <h1>三省六部制 — Agent 工作流可视化</h1>
    <p>皇帝 → 中书省(拟令) → 门下省(审核) → 尚书省(分发) → 六部(执行) → 皇帝(裁决)</p>
  </header>

  <div class="controls">
    <input type="text" id="instruction" placeholder="皇帝下达指令..." />
    <button onclick="submitInstruction()">下达旨意</button>
  </div>

  <div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:var(--emperor)"></div>皇帝</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--zhongshu)"></div>中书省</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--menxia)"></div>门下省</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--shangshu)"></div>尚书省</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--libu)"></div>吏部</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--hubu)"></div>户部</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--libu2)"></div>礼部</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--bingbu)"></div>兵部</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--xingbu)"></div>刑部</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--gongbu)"></div>工部</div>
  </div>

  <div class="stats" id="stats">
    <div class="stat-card"><div class="num" id="stat-total">0</div><div class="label">总会话</div></div>
    <div class="stat-card"><div class="num" id="stat-completed">0</div><div class="label">已完成</div></div>
    <div class="stat-card"><div class="num" id="stat-rejected">0</div><div class="label">已驳回</div></div>
    <div class="stat-card"><div class="num" id="stat-running">0</div><div class="label">执行中</div></div>
  </div>

  <div class="tree-container" id="tree-container">
    <div class="empty-state">
      <div class="icon">&#x1F3DB;</div>
      <p>尚无工作记录</p>
      <div class="hint">输入指令后，Agent 流程将在此以象形树形式展示</div>
    </div>
  </div>

  <footer>三省六部制 — AI 协助开发 (MiMo-V2.5) | MIT License</footer>
</div>

<script>
const ROLE_ICONS={emperor:'&#x1F451;',zhongshu:'&#x1F4DC;',menxia:'&#x2696;',shangshu:'&#x1F3E0;',dept:'&#x2694;'};
const ROLE_NAMES={emperor:'皇帝',zhongshu:'中书省',menxia:'门下省',shangshu:'尚书省','dept-li_bu':'吏部','dept-hu_bu':'户部','dept-li_bu2':'礼部','dept-bing_bu':'兵部','dept-xing_bu':'刑部','dept-gong_bu':'工部'};

function renderNode(node,depth){
  if(!node)return '';
  const role=node.role||'';
  const icon=role.startsWith('dept-')?ROLE_ICONS.dept:(ROLE_ICONS[role]||'&#x1F4CB;');
  const name=ROLE_NAMES[role]||node.name||'未知';
  const statusClass=node.status||'pending';
  const statusText={pending:'待处理',running:'执行中',approved:'审核通过',rejected:'已驳回',completed:'已完成',failed:'失败'}[statusClass]||statusClass;
  let childrenHtml='';
  if(node.children&&node.children.length>0){
    childrenHtml='<div class="node-children">'+node.children.map(c=>renderNode(c,depth+1)).join('')+'</div>';
  }
  return `<div class="tree-node" style="padding-left:${depth>0?40:0}px">
    <div class="node-card" data-role="${role}">
      <div class="node-top">
        <div class="node-name"><span class="icon">${icon}</span>${name}</div>
        <span class="node-status ${statusClass}">${statusText}</span>
      </div>
      <div class="node-content">${escapeHtml(node.content||'')}</div>
      <div class="node-time">${node.timestamp||''}</div>
    </div>
    ${childrenHtml}
  </div>`;
}

function escapeHtml(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}

function renderSessions(sessions){
  const container=document.getElementById('tree-container');
  if(!sessions||sessions.length===0){
    container.innerHTML='<div class="empty-state"><div class="icon">&#x1F3DB;</div><p>尚无工作记录</p><div class="hint">输入指令后，Agent 流程将在此以象形树形式展示</div></div>';
    return;
  }
  let completed=0,rejected=0,running=0;
  sessions.forEach(s=>{if(s.status==='completed')completed++;else if(s.status==='rejected')rejected++;else if(s.status==='running')running++});
  document.getElementById('stat-total').textContent=sessions.length;
  document.getElementById('stat-completed').textContent=completed;
  document.getElementById('stat-rejected').textContent=rejected;
  document.getElementById('stat-running').textContent=running;

  let html='';
  sessions.reverse().forEach(s=>{
    const statusClass=s.status||'running';
    const statusText={pending:'待处理',running:'执行中',approved:'审核通过',rejected:'已驳回',completed:'已完成',failed:'失败'}[statusClass]||statusClass;
    const treeHtml=s.tree?renderNode(s.tree,0):'<div class="empty-state"><p>流程执行中...</p></div>';
    html+=`<div class="session-card">
      <div class="session-header" onclick="toggleSession(this)">
        <div class="left">
          <span class="id-badge">#${s.id}</span>
          <span class="instruction">${escapeHtml(s.instruction)}</span>
        </div>
        <div class="right">
          <span class="node-status ${statusClass}">${statusText}</span>
          <span class="time">${s.start_time||''}</span>
        </div>
      </div>
      <div class="session-body">${treeHtml}</div>
    </div>`;
  });
  container.innerHTML=html;
  // auto-open latest
  const first=container.querySelector('.session-body');
  if(first)first.classList.add('open');
}

function toggleSession(el){
  const body=el.nextElementSibling;
  body.classList.toggle('open');
}

async function loadSessions(){
  try{
    const r=await fetch('/api/sessions');
    const data=await r.json();
    renderSessions(data.sessions||[]);
  }catch(e){console.error('Failed to load sessions',e)}
}

async function submitInstruction(){
  const input=document.getElementById('instruction');
  const text=input.value.trim();
  if(!text)return;
  input.value='';
  try{
    const r=await fetch('/api/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({instruction:text})});
    const data=await r.json();
    loadSessions();
  }catch(e){console.error('Failed to submit',e)}
}

document.getElementById('instruction').addEventListener('keydown',e=>{if(e.key==='Enter')submitInstruction()});

// Auto-refresh every 3s
setInterval(loadSessions,3000);
loadSessions();
</script>
</body>
</html>"""


class WebHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""

    store: WorkflowStore = None
    orchestrator: WebOrchestrator = None

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self._send_html(HTML_PAGE)
        elif parsed.path == "/api/sessions":
            self._send_json({"sessions": self.store.get_all()})
        elif parsed.path == "/api/latest":
            self._send_json({"session": self.store.get_latest()})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/execute":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
                instruction = data.get("instruction", "").strip()
                if not instruction:
                    self._send_json({"error": "指令不能为空"}, 400)
                    return
                # Run in background thread
                def run():
                    self.orchestrator.process_instruction(instruction)
                t = threading.Thread(target=run, daemon=True)
                t.start()
                self._send_json({"status": "started"})
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logging.getLogger("web").debug(format % args)


def main():
    parser = argparse.ArgumentParser(description="三省六部制 — Web 可视化查看器")
    parser.add_argument("--port", type=int, default=8080, help="Web 服务端口 (默认: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="绑定地址 (默认: 0.0.0.0)")
    parser.add_argument("--data-dir", default=None, help="工作记录数据目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="[%(name)s] %(message)s")

    store = WorkflowStore(args.data_dir)
    orchestrator = WebOrchestrator(store)

    WebHandler.store = store
    WebHandler.orchestrator = orchestrator

    server = HTTPServer((args.host, args.port), WebHandler)
    print(f"\n  三省六部制 — Web 可视化查看器")
    print(f"  访问地址: http://localhost:{args.port}")
    print(f"  按 Ctrl+C 停止服务\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


if __name__ == "__main__":
    main()