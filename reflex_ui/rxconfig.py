import reflex as rx

config = rx.Config(
    app_name="app",
    tailwind={
        "theme": {"extend": {}},
        "plugins": ["@tailwindcss/typography"],
    },
)
