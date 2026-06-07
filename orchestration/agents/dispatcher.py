from agent_framework import Executor, WorkflowContext, handler


class Dispatcher(Executor):

    def __init__(self, id="workflow-dispatcher"):
        self.content_safety = None
        super().__init__(id)

    @handler
    async def handle(self, document_content: str, ctx: WorkflowContext[str]):

        # validate the document is safe using contenty safety

        await ctx.send_message(document_content)
