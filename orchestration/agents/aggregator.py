import json
from uuid import uuid4
from agent_framework import Executor, handler, AgentExecutorResponse, WorkflowContext
from orchestration.agents.state import AggregatedReview, StateMap


class Aggregator(Executor):

    @handler
    async def aggregate_messages(
        self,
        messages: list[AgentExecutorResponse],
        ctx: WorkflowContext[AgentExecutorResponse],
    ):
        aggregation = {}

        for message in messages:
            print(f"Collecting messages from agent {message.executor_id}")

            aggregation[message.executor_id] = (
                message.agent_response.messages[0].contents[0].to_dict()
            )

        ea_review = json.loads(
            aggregation.get(StateMap.enterprise_architecture_reviewer.name, {}).get("text", "")
        )
        iq_review = json.loads(
            aggregation.get(StateMap.internal_iq_advisor.name, {}).get("text", "")
        )

        final_review = AggregatedReview(
            ea_score=ea_review.get("score", 0),
            iq_score=iq_review.get("score", 0),
            overall_score=round(
                (ea_review.get("score", 0) * 4 + iq_review.get("score", 0) * 6) / 10
            ),
            findings=ea_review.get("findings", []) + iq_review.get("findings"),
            recommendations=ea_review.get("recommendations", [])
            + iq_review.get("recommendations", []),
            conflicts=[],
        )

        await ctx.send_message(final_review.model_dump_json())
