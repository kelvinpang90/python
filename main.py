import os
from fastapi import FastAPI
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


@app.post("/generate")
def generate(product: str):
    system_prompt = "你是TikTok马来西亚电商专家，精通中，英，马来文"
    prompt = f"""

产品：{product}

输出：
1. 标题（10个，英文）
2. 卖点（5个）
3. 标签（10个）
4. 视频脚本
5. 投放建议
"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return {"result": resp.choices[0].message.content}