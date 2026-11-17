"""Launch the Code Twin desktop application."""

from ui.app import CodeTwinApp


def main() -> None:
    """Start the desktop user interface."""
    CodeTwinApp().run()


if __name__ == "__main__":
    main()
