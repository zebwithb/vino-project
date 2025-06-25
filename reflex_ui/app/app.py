import reflex as rx
from app.states.chat_state import ChatState # Ensure ChatState is accessible
from app.components.chat_interface import input_area # Import the input_area
from app.components.navbar import navbar

# Placeholder for a component that would display the chat messages
def message_display_area() -> rx.Component:
    return rx.vstack(
        rx.foreach(
            ChatState.messages,
            lambda message: rx.box(
                rx.text(message["text"]),
                # Add styling based on message["is_ai"]
                align_self=rx.cond(message["is_ai"], "start", "end"),
                bg=rx.cond(message["is_ai"], "gray.100", "blue.100"),
                padding="0.5rem",
                border_radius="lg",
                max_width="70%",
            ),
        ),
        align_items="stretch",
        spacing="1",
        padding="1rem",
        width="100%",
        flex_grow="1", # Allows this area to take available space
        overflow_y="auto", # Make messages scrollable
    )

def vino_chat_page() -> rx.Component:
    """
    A page that displays the chat interface.
    """
    return rx.box(
        rx.vstack(
            navbar(), # Navigation bar component
            message_display_area(),  # Your component to display messages
            input_area(),            # The input area from your chat_interface.py
            spacing="0",
            align_items="stretch",
            width="100%",
            height="100vh", 
            bg="white"
        ),
        width="50%",
        height="100vh",
        margin="0 auto",
        bg="white"
    )
    
app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(
            rel="preconnect",
            href="https://fonts.googleapis.com",
        ),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            crossorigin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
  # Ensure ChatState is the default or accessible
app.add_page(vino_chat_page, route="/")  # Add the chat page to the app
# To make this page accessible, you would add it to your app 
# in c:\Users\Kuype\source\repos\vino-project\reflex_ui\app\app.py:
#
# import reflex as rx
# from app.states.chat_state import ChatState
# from .pages.my_chat_page import vino_chat_page # Assuming you save the above as my_chat_page.py
#
# app = rx.App(state=ChatState) # Ensure ChatState is the default or accessible
# app.add_page(vino_chat_page, route="/vino-chat")
# # app.compile() # if not already done