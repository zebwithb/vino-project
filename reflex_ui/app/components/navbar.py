import reflex as rx
from app.states.state import State
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
    "inactive_height": "3vh",  # Further reduced to ensure no overlap with bottom border
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
    alt_text = text or f"Step {step_number}" if step_number else "Navigation icon"    # Common link styles - position relative for z-index layering
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
    
    if active_image_src and step_number is not None:        # Link with active/inactive states
        active_image_props = get_common_image_props(
            src=active_image_src,
            alt_text=alt_text,            
            height=NAVBAR_CONFIG["active_height"],
            width="100%",
            max_width="25vh",   
            )
        
        inactive_image_props = get_common_image_props(
            src=default_image_src,
            alt_text=alt_text,
            height="100%",  # Fill the full container height
            max_width="12vh",  # Slightly larger max width
            padding_x="1.5vh",  # Reduced padding for better fill
            padding_y="0.5vh"   # Add some vertical padding
        )
        
        # Determine border styles based on position
        left_border = get_border_style() if step_number == 1 else "none"
        right_border = get_border_style() if step_number == NAVBAR_CONFIG["step_count"] else "none"
          # Add separator border for inactive steps (except the last one)
        separator_border = "none"
        if step_number < NAVBAR_CONFIG["step_count"]:
            separator_border = f"1px solid {NAVBAR_CONFIG['border_color']}"
        
        return rx.link(
            rx.cond(
                State.current_step == step_number,
                # Active state: larger image, no extra borders
                rx.image(**active_image_props),
                # Inactive state: normal image
                rx.image(**inactive_image_props),
            ),
            **link_styles,
            on_click=State.set_current_step(step_number),
            padding_x="0",
            border_left=left_border,
            border_right=rx.cond(
                State.current_step == step_number,
                "none",  # Active step has no right border to allow seamless appearance
                rx.cond(
                    step_number < NAVBAR_CONFIG["step_count"],
                    separator_border,  # Add separator for inactive steps
                    right_border  # Right border only for last step
                )
            ),
            # Active state gets elevated appearance
            z_index=rx.cond(State.current_step == step_number, "10", "1"),
            box_shadow=rx.cond(
                State.current_step == step_number,
                "0 2px 8px rgba(59, 130, 246, 0.3)",
                "none"
            ),
        )
    elif default_image_src:
        # Image-only link
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
        text=STEP_DESCRIPTION.get(step_number, f"Step {step_number}")
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
        "top": "3vh",
        "z_index": "5",
        "width": "100%",
        "border_top": get_border_style(),
        "border_bottom": get_border_style(),
        "height": "6vh",
    }
      # Content container styles
    content_styles = {
        "width": "100%",
        "align_items": "center",
        "height": "6vh",
        "padding": "0vh",
        "justify_content": "center",
    }
      # Step container styles
    step_container_styles = {
        "justify": "between",
        "spacing": "0",
        "width": "70%",
        "height": "100%",  # Fill the full container height
        "align_items": "stretch",  # Stretch children to fill height
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