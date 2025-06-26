import reflex as rx
from app.states.chat_state import ChatState
from typing import Optional

# Configuration constants
NAVBAR_CONFIG = {
    "step_count": 6,
    "step_width": "25vh",
    "step_height": "6h",  # Match navbar height
    "border_color": "#7a7a7a",
    "background_color": "#f0f0f0",
    "step_color": "white",
    "active_height": "10vh",  # Slightly smaller than navbar to avoid overflow
    "inactive_height": "5.1vh",  # Further reduced to ensure no overlap with bottom border
    "first_step_height": "1vh"  # Reasonable size for first step
}

STEP_DESCRIPTION = {
    1: "Step 1: A Dot",
    2: "Step 2: A Line",
    3: "Step 3: A Triangle",
    4: "Step 4: A Quadranle",
    5: "Step 5: A Quadranle With A Dot",
    6: "Step 6: A Hexagon",
}

def get_border_style() -> str:
    """Returns consistent border styling."""
    return f"0.5px solid {NAVBAR_CONFIG['border_color']}"

def get_common_image_props(src: str, alt_text: str, height: str, **kwargs) -> dict:
    """Returns common image properties to reduce repetition."""
    base_props = {
        "src": src,
        "alt": alt_text,
        "fit": "contain",
        "background_color": NAVBAR_CONFIG["step_color"],
        "height": height,
        "width": "100%",
    }
    return base_props | kwargs

def navbar_link(
    url: str, 
    default_image_src: str, 
    active_image_src: Optional[str] = None, 
    step_number: Optional[int] = None, 
    text: Optional[str] = None
) -> rx.Component:
    """Creates a navbar link with active/inactive states for navigation steps."""
    inactive_height = NAVBAR_CONFIG["first_step_height"] if step_number == 1 else NAVBAR_CONFIG["inactive_height"]
    # Conditional width for steps 2 and 3 when inactive
    inactive_max_width = "6vh" if step_number in [2, 3] else "12vh"
    alt_text = text or f"Step {step_number}" if step_number else "Navigation icon"
    
    # Common link styles
    link_styles = {
        "href": url,
        "height": "5.8vh",  # Fill the full navbar height
        "width": NAVBAR_CONFIG["step_width"],
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "background_color": NAVBAR_CONFIG["step_color"],
        "position": "relative",
    }
    
    if step_number is not None:
        # Base SVG image properties for inactive state
        base_image_props = get_common_image_props(
            src=default_image_src,
            alt_text=alt_text,
            height=inactive_height,
            width=inactive_max_width,
        )
        
        # Create the inactive SVG image
        inactive_svg_image = rx.image(**base_image_props)
        
        active_height = "1.5vh" if step_number == 1 else "7vh"
        active_width = "10vh" if step_number in [2, 3] else "15vh"
        active_image_props = get_common_image_props(
            src=default_image_src,
            alt_text=alt_text,
            height=active_height,
            width=active_width,
        )
        
        # Create the active SVG image
        active_svg_image = rx.image(**active_image_props)
        
        left_border = get_border_style() if step_number == 1 else "none"
        right_border = get_border_style() if step_number == NAVBAR_CONFIG["step_count"] else "none"
        
        separator_border = "none"
        if step_number < NAVBAR_CONFIG["step_count"]:
            separator_border = f"1px solid {NAVBAR_CONFIG['border_color']}"
        
        return rx.link(
            rx.cond(
                ChatState.current_step_display == step_number,
                # Active state
                rx.box(
                    active_svg_image,
                    background_color="white",
                    border_radius="1.2vh",
                    padding="1vh",
                    box_shadow="0 2px 8px rgba(0, 0, 0, 0.1)",
                    border="1px solid #7a7a7a",
                    width="100%",
                    height="7vh",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                # Inactive state
                inactive_svg_image,
            ),
            **link_styles,
            # Commented out to prevent conflicts with backend step progression logic
            # on_click=State.set_current_step(step_number),
            padding_x="0",
            border_left=rx.cond(
                ChatState.current_step_display == step_number,
                "none",
                left_border
            ),
            border_right=rx.cond(
                ChatState.current_step_display == step_number,
                "none",
                rx.cond(
                    ChatState.current_step_display == step_number + 1,
                    "none",
                    rx.cond(
                        step_number < NAVBAR_CONFIG["step_count"],
                        separator_border,
                        right_border
                    )
                )
            ),
            z_index=rx.cond(ChatState.current_step_display == step_number, "10", "1"),
        )
    elif default_image_src:
        image_props = get_common_image_props(
            src=default_image_src,
            alt_text=alt_text,
            height=inactive_height,
            max_width="20vh",
            padding_x="3vh",
            box_sizing="border-box"
        )
        
        return rx.link(
            rx.image(**image_props),
            **link_styles,
        )
    else:
        return rx.link(
            rx.text(text, size="4", weight="medium"), 
            href=url
        )


def create_step_link(step_number: int) -> rx.Component:
    """Creates a step link with the standard naming convention."""
    return navbar_link(
        url="/#", 
        default_image_src=f"/step{step_number}.svg", 
        active_image_src=None,
        step_number=step_number, 
        text=STEP_DESCRIPTION.get(step_number, f"Step {step_number}")
    )

def navbar() -> rx.Component:
    """Renders the navigation bar with step indicators."""
    step_links = [create_step_link(i) for i in range(1, NAVBAR_CONFIG["step_count"] + 1)]
    
    print(f"Navbar: Rendering navbar component")
    
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    *step_links,
                    justify="between",
                    spacing="0",
                    width="70%",
                    height="100%",
                    align="stretch",
                ),
                width="100%",
                align="center",
                height="6vh",
                padding="0vh",
                justify="center",
            ),
        ),
        bg="#f0f0f0",
        padding="0",
        position="fixed",
        top="3vh",
        z_index="5",
        width="100%",
        border_top=get_border_style(),
        border_bottom=get_border_style(),
        height="6vh",
    )