import reflex as rx
from app.states.chat_state import ChatState, AlignmentOption


def alignment_radio_option(
    option: AlignmentOption,
) -> rx.Component:
    return rx.el.label(
        rx.el.input(
            type="radio",
            name="alignment_option",
            checked=ChatState.selected_alignment == option,
            on_change=lambda val: ChatState.set_selected_alignment(
                option
            ),
            class_name="mr-1.5 accent-sky-500",
            default_value=option,
        ),
        rx.el.span(
            option,
            class_name="text-sm text-slate-700 font-medium",
        ),
        class_name="flex items-center cursor-pointer",
    )


def input_area() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon(
                    "box-select", size=16, class_name="mr-2"
                ),
                "Prompt Toolbox",
                on_click=ChatState.toggle_prompt_toolbox,
                class_name="px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 flex items-center whitespace-nowrap",
            ),
            rx.el.div(
                rx.foreach(
                    ChatState.alignment_options,
                    alignment_radio_option,
                ),
                class_name="flex flex-wrap items-center gap-x-4 gap-y-2",
            ),
            class_name="flex flex-col sm:flex-row items-center gap-3 mb-3 px-4 pt-3",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.textarea(
                    default_value=ChatState.input_message,
                    placeholder="Ask Vino AI...",
                    on_change=ChatState.set_input_message,
                    class_name="flex-grow p-3 bg-white border border-slate-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-sky-400 min-h-[60px] max-h-40 text-slate-800 placeholder-slate-400 text-sm",
                ),
                class_name="flex items-end gap-2 px-4",
            ),
            rx.el.div(
                rx.upload.root(
                    rx.el.div(
                        rx.icon(
                            "plus",
                            size=18,
                            class_name="text-slate-600 group-hover:text-sky-500 transition-colors",
                        ),
                        class_name="p-2.5 rounded-lg border border-slate-300 hover:border-sky-400 cursor-pointer group flex items-center justify-center bg-white hover:bg-slate-50",
                    ),
                    id="chat_file_upload",
                    on_drop=ChatState.handle_upload(
                        rx.upload_files(
                            upload_id="chat_file_upload"
                        )
                    ),
                    class_name="flex-shrink-0",
                ),
                rx.el.button(
                    rx.icon(
                        "info", size=16, class_name="mr-1.5"
                    ),
                    "Explain",
                    on_click=ChatState.toggle_explain,
                    class_name=rx.cond(
                        ChatState.explain_active,
                        "px-3 py-2 text-sm font-medium text-white bg-sky-500 border border-sky-500 rounded-lg hover:bg-sky-600 flex items-center transition-colors",
                        "px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 flex items-center transition-colors",
                    ),
                ),
                rx.el.button(
                    rx.icon(
                        "square_m",
                        size=16,
                        class_name="mr-1.5",
                    ),
                    "Tasks",
                    on_click=ChatState.toggle_tasks,
                    class_name=rx.cond(
                        ChatState.tasks_active,
                        "px-3 py-2 text-sm font-medium text-white bg-sky-500 border border-sky-500 rounded-lg hover:bg-sky-600 flex items-center transition-colors",
                        "px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 flex items-center transition-colors",
                    ),
                ),
                rx.el.button(
                    rx.cond(
                        ChatState.processing,
                        rx.icon(
                            "loader-circle",
                            class_name="animate-spin",
                            size=20,
                        ),
                        rx.icon("send-horizontal", size=20),
                    ),
                    type="submit",
                    disabled=ChatState.processing
                    | (
                        ChatState.input_message.strip()
                        == ""
                        & ~ChatState.explain_active
                        & ~ChatState.tasks_active
                        & (
                            ChatState.uploaded_file_name
                            == ""
                        )
                    ),
                    class_name="p-2.5 bg-sky-500 text-white rounded-lg hover:bg-sky-600 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0 ml-auto",
                ),
                class_name="flex items-center gap-2 px-4 mt-2",
            ),
            rx.cond(
                ChatState.uploaded_file_name != "",
                rx.el.div(
                    rx.el.span(
                        f"File: {ChatState.uploaded_file_name}",
                        class_name="text-xs text-slate-600",
                    ),
                    rx.el.button(
                        rx.icon(
                            "x",
                            size=12,
                            class_name="text-slate-500 hover:text-red-500",
                        ),
                        on_click=ChatState.clear_uploaded_file,
                        class_name="p-1 rounded hover:bg-slate-200",
                        type="button",
                    ),
                    class_name="flex items-center justify-between gap-2 px-4 mt-2 py-1 bg-slate-100 border border-slate-200 rounded-md text-xs",
                ),
            ),
            on_submit=ChatState.send_message_from_input,
            reset_on_submit=False,
            class_name="w-full",
        ),
        rx.cond(
            ChatState.messages.length() > 0,
            rx.el.button(
                rx.icon(
                    "trash-2", size=14, class_name="mr-1"
                ),
                "Clear Chat",
                on_click=ChatState.clear_messages,
                class_name="mt-3 mb-1 text-xs text-slate-500 hover:text-red-500 flex items-center self-center transition-colors",
            ),
        ),
        class_name="sticky bottom-0 left-0 right-0 py-3 bg-slate-100/90 backdrop-blur-md border-t border-slate-200 flex flex-col",
    )