"""
求职面试准备 Agent
输入公司名 + 官网，生成以面试建议为核心的调研报告
"""

import os, re, json, urllib.request, urllib.error
from html.parser import HTMLParser
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder=".")


# ── 网页抓取 ───────────────────────────────────────────────────────

class TextExtractor(HTMLParser):
    SKIP = {"script","style","noscript","head","meta","link","nav","footer"}
    def __init__(self):
        super().__init__(); self._skip_tag = None; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP: self._skip_tag = tag
    def handle_endtag(self, tag):
        if tag == self._skip_tag: self._skip_tag = None
    def handle_data(self, data):
        if not self._skip_tag:
            t = data.strip()
            if len(t) > 20: self.parts.append(t)
    def get_text(self): return "\n".join(self.parts)


def fetch_text(url: str, max_chars=8765) -> str:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; InterviewPrepAgent/1.0)"
        })
        with urllib.request.urlopen(req, timeout=12) as r:
            charset = r.headers.get_content_charset() or "utf-8"
            html = r.read().decode(charset, errors="replace")
        p = TextExtractor(); p.feed(html)
        text = re.sub(r"\n{3,}", "\n\n", p.get_text())
        return text[:max_chars]
    except Exception:
        return ""


def collect_pages(base_url: str) -> dict:
    base = base_url.rstrip("/")
    candidates = {
        "主页": base,
        "about": f"{base}/about",
        "about-us": f"{base}/about-us",
        "culture": f"{base}/culture",
        "careers": f"{base}/careers",
        "values": f"{base}/values",
        "team": f"{base}/team",
        "blog": f"{base}/blog",
    }
    pages = {}
    for label, url in candidates.items():
        text = fetch_text(url, max_chars=3500)
        if len(text) > 200:
            pages[label] = text
        if len(pages) >= 5:
            break
    return pages


# ── Agent 核心 ─────────────────────────────────────────────────────

def run_agent(company: str, website: str, job_title: str) -> dict:
    client =  OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pages = collect_pages(website)
    if not pages:
        raise ValueError("无法抓取到该网站内容，请检查 URL 是否正确。")

    combined = ""
    for label, text in pages.items():
        combined += f"\n\n=== [{label}] ===\n{text}"

    job_context = f"应聘职位：{job_title}" if job_title else "（未指定职位）"

    prompt = f"""你是一位经验丰富的求职面试教练。

我正在准备面试"{company}"公司。{job_context}

以下是从该公司官网抓取的内容：
{combined[:12000]}

---

请基于公司官网内容，生成一份以**面试准备**为核心的报告。
请严格按以下 JSON 格式输出，不要输出任何其他内容：

{{
  "company_name": "公司全称",
  "one_liner": "一句话：公司是做什么的（15字以内）",
  "background": {{
    "industry": "所属行业",
    "founded": "成立时间（如官网未提及填'未知'）",
    "size": "公司规模（如官网未提及填'未知'）",
    "core_business": "核心业务简述（2-3句）",
    "recent_highlights": ["近期亮点或动态1", "近期亮点或动态2"]
  }},
  "culture_signals": [
    {{
      "trait": "文化特质名称（如：追求极致 / 扁平开放 / 用户至上）",
      "evidence": "从官网哪里体现的（具体依据）",
      "interview_angle": "面试时如何用这一点展示契合度"
    }}
  ],
  "interview_prep": {{
    "likely_questions": [
      {{
        "question": "高概率被问到的问题",
        "why_asked": "为什么这家公司会问这个",
        "answer_tip": "如何回答才能打动这家公司的面试官（结合公司文化）"
      }}
    ],
    "star_stories": [
      {{
        "theme": "建议准备的 STAR 故事主题",
        "reason": "为什么这个主题与该公司特别契合"
      }}
    ],
    "dos": ["面试中应该做的事1", "应该做的事2", "应该做的事3"],
    "donts": ["面试中应该避免的事1", "应该避免的事2"]
  }},
  "questions_to_ask": [
    {{
      "question": "你可以问面试官的问题",
      "intent": "这个问题传递了什么信号（展示你做了充分调研）"
    }}
  ]
}}

要求：
- likely_questions 至少 5 条，每条都要有针对性，不能是泛泛的通用问题
- culture_signals 至少 3 条，必须有官网原文依据
- star_stories 至少 3 个主题
- questions_to_ask 至少 3 条
- 所有建议必须结合该公司的具体文化和业务，不能是通用建议"""

    message = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.choices[0].message.content
    raw = re.sub(r"^```json\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)

    result = json.loads(raw)
    result["pages_scraped"] = list(pages.keys())
    return result


# ── 路由 ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/research", methods=["POST"])
def research():
    data     = request.get_json(force=True)
    company  = (data.get("company") or "").strip()
    website  = (data.get("website") or "").strip()
    job      = (data.get("job_title") or "").strip()

    if not company or not website:
        return jsonify({"error": "请填写公司名称和官网 URL"}), 400
    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    try:
        return jsonify(run_agent(company, website, job))
    except json.JSONDecodeError:
        return jsonify({"error": "GPT 返回格式异常，请重试"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"OpenAI API 错误：{e}"}), 500
    except Exception as e:
        return jsonify({"error": f"错误：{e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8765)