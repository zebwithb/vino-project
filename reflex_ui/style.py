import reflex as rx


# Common styles for questions and answers.
shadow = "rgba(0, 0, 0, 0.15) 0px 2px 8px"
chat_margin = "20%"
message_style = dict(
    padding="1em",
    border_radius="5px",
    margin_y="1em",
    box_shadow=shadow,
    max_width="40em",
    display="inline-block",
)

# Set specific styles for questions and answers.
question_style = message_style | dict(
    margin_left=chat_margin,
    background_color=rx.color("gray", 4),
)
answer_style = message_style | dict(
    margin_right=chat_margin,
    background_color=rx.color("cyan", 8),
)

# Styles for the action bar.
input_style = dict(
    border_width="1px",
    padding="1em",
    box_shadow=shadow,
    width="40em",
)
button_style = dict(
    background_color=rx.color("accent", 10),
    box_shadow=shadow,
)

# Global styles for custom scrollbars
scrollbar_style = {
    # Webkit scrollbar styling (Chrome, Safari, Edge)
    "::-webkit-scrollbar": {
        "width": "6px",
        "height": "6px",
    },
    "::-webkit-scrollbar-track": {
        "background": "transparent",
    },
    "::-webkit-scrollbar-thumb": {
        "background": "#cbd5e1",
        "border-radius": "3px",
        "transition": "background 0.2s ease",
    },
    "::-webkit-scrollbar-thumb:hover": {
        "background": "#94a3b8",
    },
    "::-webkit-scrollbar-corner": {
        "background": "transparent",
    },
    # Firefox scrollbar styling
    "scrollbar-width": "thin",
    "scrollbar-color": "#cbd5e1 transparent",
}