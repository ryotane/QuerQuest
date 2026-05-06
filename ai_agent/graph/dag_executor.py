from concurrent.futures import ThreadPoolExecutor


class DAGExecutor:

    def run(self, tasks, query, tools):

        results = []

        def exec_task(name):
            tool = tools.get(name)
            if not tool:
                return None
            return tool.run(query)

        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = [ex.submit(exec_task, t) for t in tasks]

            for f in futures:
                results.append(f.result())

        return results