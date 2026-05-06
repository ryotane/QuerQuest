import requests


class Tool:

    def run(self, query: str):

        # ノイズ除去
        if "### Task:" in query:
            return {"ok": False, "result": ""}

        url = "http://localhost:8888/search"

        params = {
            "q": query,
            "format": "json"
        }

        try:
            res = requests.get(url, params=params, timeout=5)
            data = res.json()

            # 🔥 DEBUG①（SearXNGの生レスポンス）
            print("\n===== DEBUG RAW SearXNG =====")
            print(data)

            results = data.get("results", [])

            if not results:
                print("⚠️ 検索結果ゼロ")
                return {"ok": False, "result": ""}

            cleaned = []
            seen = set()

            for r in results:
                title = r.get("title", "")
                content = r.get("content", "")
                link = r.get("url", "")

                if link in seen:
                    continue
                seen.add(link)

                text = (title + content)
                if not text.strip():
                    continue

                cleaned.append({
                    "title": title,
                    "content": content,
                    "url": link
                })

            output = []
            for r in cleaned[:5]:
                output.append(
                    f"{r['title']}\n{r['content']}\n{r['url']}"
                )

            result_text = "\n\n".join(output)

            # 🔥 DEBUG②（整形後）
            print("\n===== DEBUG FORMATTED =====")
            print(result_text)

            return {
                "ok": True,
                "result": result_text
            }

        except Exception as e:
            print("❌ WebTool Exception:", e)
            return {"ok": False, "result": str(e)}