#!/usr/bin/env python3
"""
Web Search MCP Server
基于bocha.cn API的网页搜索MCP服务
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests
from mcp.server import Server
from mcp.types import Tool, TextContent


# bocha API配置
BOCHA_API_URL = "https://api.bocha.cn/v1/web-search"
BOCHA_API_KEY = "sk-8770b49c06864f178072ea845cfb95f9"  # 从环境变量读取更安全


class BochaSearchClient:
    """bocha搜索客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = BOCHA_API_URL
    
    def search(self, query: str, summary: bool = True, count: int = 10) -> Dict[str, Any]:
        """
        执行网页搜索
        
        Args:
            query: 搜索关键词
            summary: 是否返回摘要
            count: 返回结果数量
            
        Returns:
            API响应的JSON数据
        """
        payload = {
            "query": query,
            "summary": summary,
            "count": count
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"搜索请求失败: {str(e)}",
                "data": None
            }


def format_search_results(results: Dict[str, Any]) -> str:
    """格式化搜索结果为可读文本"""
    if "error" in results:
        return f"搜索出错: {results['error']}"
    
    if not results or "data" not in results:
        return "未找到相关结果"
    
    data = results.get("data", {})
    web_pages = data.get("webPages", {}).get("value", [])
    
    if not web_pages:
        return "未找到相关网页结果"
    
    formatted = []
    formatted.append(f"找到 {len(web_pages)} 个相关结果:\n")
    
    for i, page in enumerate(web_pages, 1):
        title = page.get("name", "无标题")
        url = page.get("url", "")
        snippet = page.get("snippet", "无摘要")
        summary_text = page.get("summary", "")
        
        formatted.append(f"{i}. {title}")
        formatted.append(f"   链接: {url}")
        formatted.append(f"   摘要: {snippet}")
        if summary_text:
            formatted.append(f"   详细: {summary_text}")
        formatted.append("")
    
    return "\n".join(formatted)


# 创建MCP Server
app = Server("web-search")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="web_search",
            description="搜索网页信息，获取最新网络资讯",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "count": {
                        "type": "integer",
                        "description": "返回结果数量(1-10)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    },
                    "summary": {
                        "type": "boolean",
                        "description": "是否返回详细摘要",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """调用工具"""
    if name == "web_search":
        query = arguments.get("query", "")
        count = arguments.get("count", 5)
        summary = arguments.get("summary", True)
        
        if not query:
            return [TextContent(type="text", text="错误: 搜索关键词不能为空")]
        
        # 创建搜索客户端
        api_key = os.environ.get("BOCHA_API_KEY", BOCHA_API_KEY)
        client = BochaSearchClient(api_key)
        
        # 执行搜索
        results = client.search(query, summary=summary, count=count)
        
        # 格式化结果
        formatted_text = format_search_results(results)
        
        return [TextContent(type="text", text=formatted_text)]
    
    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    """主入口"""
    # 从stdin/stdout运行MCP服务
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())