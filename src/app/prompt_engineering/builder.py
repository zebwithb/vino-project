# Contains the get_universal_matrix_prompt function
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

# Assuming the __init__.py in this package makes these available,
# or adjust imports as needed:
from .matrix_definitions import UNIVERSAL_MATRIX_STEPS
from .templates import (
    BASE_SYSTEM_PROMPT,
    STEP_SPECIFIC_SYSTEM_PROMPT_TEMPLATE,
    PLANNER_SYSTEM_PROMPT,
    CONTEXT_SECTION_TEMPLATE,
    HISTORY_PLACEHOLDER,
    PLANNER_SECTION_TEMPLATE,
    USER_INPUT_SECTION_TEMPLATE
)

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
        ]).partial(general_context=general_context, question=question)

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