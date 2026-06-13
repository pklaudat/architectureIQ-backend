from agent_framework import WorkflowBuilder, Agent, ChatOptions, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatClient
from orchestration.agents import models as model
from orchestration.agents.dispatcher import Dispatcher
from orchestration.agents.aggregator import Aggregator
from utils import prompt_content
from orchestration.agents.state import *


def review_workflow():

    chat_client = OpenAIChatClient(model=model.DISPATCHER_MODEL)

    dispatcher = Dispatcher(id="review_dispatcher")

    architecture_facts_extractor = Agent(
        client=chat_client,
        id="architecture_facts_extractor",
        # name="Architecture Facts Extractor",
        instructions=prompt_content(name="ARCHITECTURE_FACTS"),
        default_options=ChatOptions(response_format=ArchitectureFacts),
    )

    enterprise_arch_reviewer = Agent(
        client=chat_client,
        id="enterprise_architecture_reviewer",
        # name="Enterprise Architect Reviewer",
        instructions=prompt_content(name="EA_REVIEWER"),
        default_options=ChatOptions(response_format=EAReview),
        tools=[
            MCPStreamableHTTPTool(
                name="Microsoft Learn MCP",
                url="https://learn.microsoft.com/api/mcp",
                approval_mode="never_require",
                request_timeout=30,
                description="Microsoft Learn official MCP server.",
            )
        ],
    )

    internal_iq_advisor = Agent(
        client=chat_client,
        id="internal_iq_advisor",
        # name="Internal IQ Adivisor",
        instructions=prompt_content(name="IQ_REVIEWER"),
        default_options=ChatOptions(response_format=IQReview),
    )

    aggregator = Aggregator(id="aggregator")

    curator = Agent(
        client=chat_client,
        id="review_curator",
        # name="ReviewCurator",
        instructions=prompt_content(name="CURATOR"),
        default_options=ChatOptions(response_format=ReviewResult),
    )

    return (
        WorkflowBuilder(
            name="Enterp Architecture Advisor",
            description="Workflow to generate recommendations upon Architecture Docs",
            start_executor=dispatcher,
        )
        .add_edge(source=dispatcher, target=architecture_facts_extractor)
        .add_fan_out_edges(
            source=architecture_facts_extractor,
            targets=[enterprise_arch_reviewer, internal_iq_advisor],
        )
        .add_fan_in_edges(
            sources=[enterprise_arch_reviewer, internal_iq_advisor], target=aggregator
        )
        .add_edge(source=aggregator, target=curator)
    ).build()
