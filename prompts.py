import os
from typing import List, Optional, Dict, Any

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# ------------------------------------------------------------------------------
# UNIVERSAL MATRIX STEP DEFINITIONS (Based on provided PDF)
# ------------------------------------------------------------------------------

# Define the core concepts and guiding questions for the first 6 steps
# These help the LLM understand the focus of each step.
UNIVERSAL_MATRIX_STEPS = {
    1: {
        "name": "Initial State / Starting Point",
        "concept": "The beginning of the process, the first atom or birth, the initial state. Possibility of existence.",
        "questions": [
            "What is the starting point or initial state of the process/project?",
            "What are the core components or sub-aspects of this initial point?",
            "How does it represent the possibility of existence or appearance for this project?",
        ]
    },
    2: {
        "name": "Connection / Awareness",
        "concept": "Two points with a connection and awareness of their presence. Possibility and probability of an event. Presence and self-awareness.",
        "questions": [
            "What follows the initial point? What key elements need to be connected?",
            "What is the relationship between these elements?",
            "How does this represent the core possibility and probability for the project's success?",
        ]
    },
    3: {
        "name": "Emergence / Triad / Initial Plan",
        "concept": "Result of the relationship between possibility and probability. Emergence of a third force. PLANNER DEFINITION STEP.",
        "questions": [
            "What emerges from the interaction of the elements defined in Step 2?",
            "Based on Steps 1 & 2, what is the initial triad of forces or key pillars for this project?",
            "Let's define the initial 6-step plan based on the Universal Matrix framework and our discussion so far. What are the key objectives/tasks for each of the 6 steps?",
        ]
    },
    4: {
        "name": "Manifestation / Plane",
        "concept": "The manifested result of the interaction of three forces. A plane reflecting different possibilities for development.",
        "questions": [
            "What is the manifested result of the interaction defined in Step 3 (the initial plan)?",
            "How does this create a 'plane' of possibilities for development?",
            "How can we refine the plan (Step 3 output) based on these possibilities?",
        ]
    },
    5: {
        "name": "Choice / Vector",
        "concept": "The center of the plane, source, stage of vector formation, true motive, choice of the most effective direction.",
        "questions": [
            "What is the central focus or 'true motive' within the possibilities from Step 4?",
            "What is the most effective direction or 'vector' for the project to take?",
            "How should we adjust the plan to align with this chosen vector?",
        ]
    },
    6: {
        "name": "Completion / Boundary",
        "concept": "A completed outer border, limitation of space, necessary for the realization of the event.",
        "questions": [
            "What defines the completed boundary or scope for this phase/project?",
            "How does this boundary limit options but enable realization?",
            "What are the final refinements to the plan based on these boundaries?",
        ]
    }
    # Steps 7-12 could be added here if needed later
}

# ------------------------------------------------------------------------------
# AUGMENTED PROMPT TEMPLATES
# ------------------------------------------------------------------------------

# --- System Prompts ---

BASE_SYSTEM_PROMPT = """You are VINO, an AI assistant guiding users through project definition and planning using the 6-step Universal Matrix framework.
Your goal is to help the user clarify their project step-by-step, leveraging provided document context and user input.
Always focus on the user's CURRENT STEP in the 6-step process.
Use the concepts and guiding questions for the current step to direct the conversation.
After Step 3, you will help the user define and refine a 6-step planner based on the Universal Matrix structure.
Be concise, clear, and action-oriented."""

STEP_SPECIFIC_SYSTEM_PROMPT_TEMPLATE = BASE_SYSTEM_PROMPT + """

CURRENT FOCUS: Step {current_step}: {step_name}
CONCEPT: {step_concept}
GUIDING QUESTIONS TO ADDRESS:
{step_questions}

Maintain awareness of the overall 6-step plan, especially when refining it after Step 3."""

PLANNER_SYSTEM_PROMPT = BASE_SYSTEM_PROMPT + """

CURRENT FOCUS: Step 3: Emergence / Initial Plan Definition
CONCEPT: {step_concept}
GUIDING QUESTIONS TO ADDRESS:
{step_questions}

Your primary goal now is to synthesize the information from Steps 1 and 2, along with any relevant context, to help the user create an initial draft of the 6-step planner. The planner should outline key goals or tasks for each of the 6 Universal Matrix steps as they apply to the user's project."""

# --- Human Prompt Snippets (to be assembled dynamically) ---

CONTEXT_SECTION_TEMPLATE = """--- Relevant Context for Step {current_step} ---
{step_context}
--- General Project Context ---
{general_context}"""

HISTORY_PLACEHOLDER = MessagesPlaceholder(variable_name="history") # Use MessagesPlaceholder for chat history

PLANNER_SECTION_TEMPLATE = """--- Current 6-Step Planner ---
{planner_state}"""

USER_INPUT_SECTION_TEMPLATE = """--- User's Request ---
User: {question}

--- Your Task ---
Address the user's request in the context of Step {current_step}. Use the guiding questions for this step. If the user asks to move on, confirm the current step's objectives are met and guide them to the next step. If in Step 3, focus on drafting the planner. If in Steps 4-6, focus on refining the planner based on the step's concept."""

# ------------------------------------------------------------------------------
# PROMPT SELECTION LOGIC
# ------------------------------------------------------------------------------

def get_universal_matrix_prompt(
    current_step: int,
    history: list, # Expecting list of BaseMessage objects (HumanMessage, AIMessage)
    question: str,
    step_context: str,
    general_context: str,
    planner_state: Optional[str] = None # String representation of the planner
) -> Optional[ChatPromptTemplate]:
    """
    Builds the appropriate ChatPromptTemplate based on the current step
    in the Universal Matrix process.

    Args:
        current_step: The current step number (1-6).
        history: The conversation history (list of Langchain message objects).
        question: The user's latest input.
        step_context: Context specifically retrieved for the current step.
        general_context: General context (e.g., from user documents).
        planner_state: The current state of the 6-step planner (optional).

    Returns:
        A ChatPromptTemplate instance or None if the step is invalid.
    """
    if not 1 <= current_step <= 6:
        print(f"Warning: Invalid step number {current_step}. Falling back.")
        # Fallback to a basic prompt if step is out of range
        return ChatPromptTemplate.from_messages([
            ("system", BASE_SYSTEM_PROMPT),
            HISTORY_PLACEHOLDER,
            ("human", "Context:\n{general_context}\n\nUser: {question}")
        ]).partial(general_context=general_context, question=question) # History added separately

    step_info = UNIVERSAL_MATRIX_STEPS[current_step]
    step_name = step_info["name"]
    step_concept = step_info["concept"]
    # Format guiding questions for readability in the prompt
    step_questions_formatted = "\n".join([f"- {q}" for q in step_info["questions"]])

    messages = []

    # 1. Add System Message
    if current_step == 3:
        system_prompt_content = PLANNER_SYSTEM_PROMPT.format(
            current_step=current_step,
            step_name=step_name,
            step_concept=step_concept,
            step_questions=step_questions_formatted
        )
    else:
        system_prompt_content = STEP_SPECIFIC_SYSTEM_PROMPT_TEMPLATE.format(
            current_step=current_step,
            step_name=step_name,
            step_concept=step_concept,
            step_questions=step_questions_formatted
        )
    messages.append(SystemMessage(content=system_prompt_content))

    # 2. Add History Placeholder
    messages.append(HISTORY_PLACEHOLDER) # history will be passed in the .invoke() call

    # 3. Construct Human Message Content
    human_content = CONTEXT_SECTION_TEMPLATE.format(
        current_step=current_step,
        step_context=step_context if step_context else "N/A",
        general_context=general_context if general_context else "N/A"
    )

    if planner_state and current_step >= 3: # Show planner from step 3 onwards
         human_content += "\n\n" + PLANNER_SECTION_TEMPLATE.format(planner_state=planner_state)

    human_content += "\n\n" + USER_INPUT_SECTION_TEMPLATE.format(
        question=question,
        current_step=current_step
    )
    messages.append(HumanMessage(content=human_content))

    # 4. Create the ChatPromptTemplate
    prompt_template = ChatPromptTemplate.from_messages(messages)

    return prompt_template

# ------------------------------------------------------------------------------
# EXAMPLE USAGE (Illustrative - integrate this into your main logic)
# ------------------------------------------------------------------------------
