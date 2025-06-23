import reflex as rx
from app.states.state import State
from typing import Optional

# Configuration constants
NAVBAR_CONFIG = {
    "step_count": 6,
    "step_width": "25em",
    "step_height": "3.8em",
    "border_color": "#222221",
    "background_color": "white",
    "active_height": "8em",
    "inactive_height": "4em",
    "first_step_height": "0.5em"
}

def get_border_style() -> str:
    """Returns consistent border styling."""
    return f"1px solid {NAVBAR_CONFIG['border_color']}"

def get_common_image_props(src: str, alt_text: str, height: str, **kwargs) -> dict:
    """Returns common image properties to reduce repetition."""
    base_props = {
        "src": src,
        "alt": alt_text,
        "fit": "contain",
        "background_color": NAVBAR_CONFIG["background_color"],
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
    active_height = NAVBAR_CONFIG["first_step_height"] if step_number == 1 else NAVBAR_CONFIG["inactive_height"]
    alt_text = text or f"Step {step_number}" if step_number else "Navigation icon"
    
    # Common link styles
    link_styles = {
        "href": url,
        "height": NAVBAR_CONFIG["step_height"],
        "width": NAVBAR_CONFIG["step_width"],
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "background_color": NAVBAR_CONFIG["background_color"],
    }
    
    if active_image_src and step_number is not None:
        # Link with active/inactive states
        active_image_props = get_common_image_props(
            src=active_image_src,
            alt_text=alt_text,
            height=NAVBAR_CONFIG["active_height"]
        )
        
        inactive_image_props = get_common_image_props(
            src=default_image_src,
            alt_text=alt_text,
            height=active_height,
            max_width="10em",
            padding_x="3em"
        )
        
        return rx.link(
            rx.cond(
                State.active_step == step_number,
                rx.image(**active_image_props),
                rx.image(**inactive_image_props),
            ),
            **link_styles,
            on_click=State.set_active_step(step_number),
            padding_x="0",
            border_left=get_border_style(),
            border_right=get_border_style(),
        )
    elif default_image_src:
        # Image-only link
        image_props = get_common_image_props(
            src=default_image_src,
            alt_text=alt_text,
            height=active_height,
            max_width="20em",
            padding_x="3em",
            border_left=get_border_style(),
            border_right=get_border_style(),
            box_sizing="border-box"
        )
        
        return rx.link(
            rx.image(**image_props),
            **link_styles,
        )
    else:
        # Text-only link
        return rx.link(
            rx.text(text, size="4", weight="medium"), 
            href=url
        )


def create_step_link(step_number: int) -> rx.Component:
    """Creates a step link with the standard naming convention."""
    return navbar_link(
        url="/#", 
        default_image_src=f"/step{step_number}.svg", 
        active_image_src=f"/step{step_number}_active.png", 
        step_number=step_number, 
        text=f"Step {step_number}"
    )

def navbar() -> rx.Component:
    """Renders the navigation bar with step indicators."""
    # Generate step links dynamically
    step_links = [create_step_link(i) for i in range(1, NAVBAR_CONFIG["step_count"] + 1)]
    
    # Navbar container styles
    navbar_styles = {
        "bg": NAVBAR_CONFIG["background_color"],
        "padding": "0",
        "position": "fixed",
        "top": "2em",
        "z_index": "5",
        "width": "100%",
        "border_top": get_border_style(),
        "border_bottom": get_border_style(),
        "height": "4em",
    }
    
    # Content container styles
    content_styles = {
        "width": "100%",
        "align_items": "center",
        "height": "4em",
        "padding": "-0.2em",
        "justify_content": "center",
    }
    
    # Step container styles
    step_container_styles = {
        "justify": "between",
        "spacing": "0",
        "width": "70%",
    }
    
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(*step_links, **step_container_styles),
                **content_styles,
            ),
        ),
        **navbar_styles,
    )