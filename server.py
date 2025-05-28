from fastmcp import FastMCP
from typing import Optional
from urllib.parse import urlparse, urlunparse
import markdownify
import readabilipy.simple_json
from protego import Protego
import httpx
import asyncio
import nest_asyncio

# FastMCPサーバーを作成
mcp = FastMCP("Fetch MCP Server")

# nest_asyncioを適用してネストしたイベントループを許可
nest_asyncio.apply()

# デフォルトのUser-Agent
DEFAULT_USER_AGENT_AUTONOMOUS = "ModelContextProtocol/1.0 (Autonomous; +https://github.com/modelcontextprotocol/servers)"

def extract_content_from_html(html: str) -> str:
    """HTMLコンテンツをMarkdown形式に変換します"""
    ret = readabilipy.simple_json.simple_json_from_html_string(
        html, use_readability=True
    )
    if not ret["content"]:
        return "<e>Page failed to be simplified from HTML</e>"
    content = markdownify.markdownify(
        ret["content"],
        heading_style=markdownify.ATX,
    )
    return content

def get_robots_txt_url(url: str) -> str:
    """指定されたウェブサイトURLのrobots.txt URLを取得します"""
    parsed = urlparse(url)
    robots_url = urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
    return robots_url

async def check_may_autonomously_fetch_url(url: str, user_agent: str, proxy_url: Optional[str] = None) -> None:
    """robots.txtファイルに従ってURLが取得可能かチェックします"""
    robot_txt_url = get_robots_txt_url(url)
    
    async with httpx.AsyncClient(proxies=proxy_url) as client:
        try:
            response = await client.get(
                robot_txt_url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
            )
        except httpx.HTTPError:
            raise Exception(f"Failed to fetch robots.txt {robot_txt_url} due to a connection issue")
        
        if response.status_code in (401, 403):
            raise Exception(f"When fetching robots.txt ({robot_txt_url}), received status {response.status_code} so assuming that autonomous fetching is not allowed")
        elif 400 <= response.status_code < 500:
            return
        
        robot_txt = response.text
    
    processed_robot_txt = "\n".join(
        line for line in robot_txt.splitlines() if not line.strip().startswith("#")
    )
    robot_parser = Protego.parse(processed_robot_txt)
    if not robot_parser.can_fetch(str(url), user_agent):
        raise Exception(f"The sites robots.txt ({robot_txt_url}), specifies that autonomous fetching of this page is not allowed")

async def fetch_url_content(
    url: str, 
    user_agent: str, 
    force_raw: bool = False, 
    proxy_url: Optional[str] = None
) -> tuple[str, str]:
    """URLを取得してLLMで使用可能な形式でコンテンツを返します"""
    async with httpx.AsyncClient(proxies=proxy_url) as client:
        try:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
                timeout=30,
            )
        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch {url}: {e!r}")
        
        if response.status_code >= 400:
            raise Exception(f"Failed to fetch {url} - status code {response.status_code}")

        page_raw = response.text

    content_type = response.headers.get("content-type", "")
    is_page_html = (
        "<html" in page_raw[:100] or "text/html" in content_type or not content_type
    )

    if is_page_html and not force_raw:
        return extract_content_from_html(page_raw), ""

    return (
        page_raw,
        f"Content type {content_type} cannot be simplified to markdown, but here is the raw content:\n",
    )

async def _fetch_async(
    url: str,
    max_length: int = 5000,
    start_index: int = 0,
    raw: bool = False,
    ignore_robots_txt: bool = False,
    proxy_url: Optional[str] = None
) -> str:
    """非同期版のfetch関数"""
    if not url:
        raise ValueError("URL is required")

    user_agent = DEFAULT_USER_AGENT_AUTONOMOUS
    
    # robots.txtチェック（無視しない場合）
    if not ignore_robots_txt:
        try:
            await check_may_autonomously_fetch_url(url, user_agent, proxy_url)
        except Exception as e:
            return f"Error: {str(e)}"

    try:
        content, prefix = await fetch_url_content(
            url, user_agent, force_raw=raw, proxy_url=proxy_url
        )
    except Exception as e:
        return f"Error fetching URL: {str(e)}"
    
    original_length = len(content)
    if start_index >= original_length:
        content = "<e>No more content available.</e>"
    else:
        truncated_content = content[start_index : start_index + max_length]
        if not truncated_content:
            content = "<e>No more content available.</e>"
        else:
            content = truncated_content
            actual_content_length = len(truncated_content)
            remaining_content = original_length - (start_index + actual_content_length)
            # コンテンツが切り詰められた場合の続きを取得する案内
            if actual_content_length == max_length and remaining_content > 0:
                next_start = start_index + actual_content_length
                content += f"\n\n<e>Content truncated. Call the fetch tool with a start_index of {next_start} to get more content.</e>"
    
    return f"{prefix}Contents of {url}:\n{content}"

@mcp.tool()
def fetch(
    url: str,
    max_length: int = 5000,
    start_index: int = 0,
    raw: bool = False,
    ignore_robots_txt: bool = False,
    proxy_url: Optional[str] = None
) -> str:
    """
    インターネットからURLを取得し、そのコンテンツをマークダウンとして抽出します。

    Args:
        url: 取得するURL
        max_length: 返す最大文字数 (デフォルト: 5000)
        start_index: この文字インデックスからコンテンツを開始 (デフォルト: 0)
        raw: HTMLコンテンツを簡略化せずに取得 (デフォルト: False)
        ignore_robots_txt: robots.txtの制限を無視 (デフォルト: False)
        proxy_url: プロキシURL (オプション)
    """
    try:
        # 現在のイベントループを取得
        loop = asyncio.get_running_loop()
        # 新しいタスクとして実行
        task = loop.create_task(_fetch_async(url, max_length, start_index, raw, ignore_robots_txt, proxy_url))
        return loop.run_until_complete(task)
    except RuntimeError:
        # イベントループが実行されていない場合（通常のスクリプト実行時）
        return asyncio.run(_fetch_async(url, max_length, start_index, raw, ignore_robots_txt, proxy_url))
    except Exception as e:
        # nest_asyncioを使用してネストしたイベントループで実行
        try:
            return asyncio.run(_fetch_async(url, max_length, start_index, raw, ignore_robots_txt, proxy_url))
        except Exception as nested_e:
            return f"Error executing fetch: {str(e)} | Nested error: {str(nested_e)}"

@mcp.tool()
def fetch_simple(url: str) -> str:
    """
    シンプルなURL取得（デフォルト設定で5000文字まで）
    
    Args:
        url: 取得するURL
    """
    return fetch(url=url, max_length=5000, start_index=0, raw=False, ignore_robots_txt=False)

@mcp.tool()
def fetch_raw(url: str, max_length: int = 5000) -> str:
    """
    生のHTMLコンテンツを取得（マークダウン変換なし）
    
    Args:
        url: 取得するURL
        max_length: 返す最大文字数 (デフォルト: 5000)
    """
    return fetch(url=url, max_length=max_length, start_index=0, raw=True, ignore_robots_txt=False)

@mcp.tool()
def fetch_ignore_robots(url: str, max_length: int = 5000) -> str:
    """
    robots.txtを無視してURL取得
    
    Args:
        url: 取得するURL
        max_length: 返す最大文字数 (デフォルト: 5000)
    """
    return fetch(url=url, max_length=max_length, start_index=0, raw=False, ignore_robots_txt=True)

if __name__ == "__main__":
    # SSE transport で起動
    mcp.run(transport="sse", host="0.0.0.0", port=8000)