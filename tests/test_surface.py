from src.surface import BrowserSurface


surface = BrowserSurface()

try:
    surface.start()

    surface.navigate("http://127.0.0.1:5000")

    surface.type_by_label(
        "Member ID",
        "12345"
    )

    surface.click_by_role(
        "button",
        "Search Member"
    )

    balance = surface.read_css(
        "#savings-balance"
    )

    print("Savings balance:", balance)

    surface.screenshot(
        "evidence/playwright_test.png"
    )

finally:
    surface.close()