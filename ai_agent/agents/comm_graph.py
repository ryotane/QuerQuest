class CommunicationGraph:

    def exchange(self, question, agents_output):

        messages = []

        for agent, output in agents_output.items():

            messages.append({
                "from": agent,
                "message": str(output)[:200]
            })

        # simplified consensus
        consensus = "agree" if len(messages) > 1 else "single"

        return {
            "messages": messages,
            "consensus": consensus
        }