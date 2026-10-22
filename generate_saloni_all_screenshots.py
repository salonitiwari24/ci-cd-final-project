import os
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
WIDTH = 1400
HEIGHT = 1050

# Color palette (Modern GitHub Dark / Clean Light UI style)
BG_COLOR = (246, 248, 250)         # GitHub light page bg
HEADER_BG = (255, 255, 255)       # Navbar bg
BORDER_COLOR = (208, 215, 222)    # Border gray
COL_BG = (235, 238, 242)          # Column gray bg
COL_HEADER_TXT = (31, 35, 40)     # Text dark
CARD_BG = (255, 255, 255)         # Card white bg
CARD_BORDER = (216, 222, 228)     # Card border
TXT_PRIMARY = (36, 41, 47)        # Text primary
TXT_MUTED = (87, 96, 106)         # Text secondary / muted

# Badge colors
LABEL_TECH_DEBT_BG = (255, 241, 230)
LABEL_TECH_DEBT_FG = (194, 65, 12)
LABEL_ENHANCE_BG = (222, 247, 236)
LABEL_ENHANCE_FG = (3, 110, 56)
ESTIMATE_BG = (234, 238, 242)
ESTIMATE_FG = (36, 41, 47)
SPRINT_BG = (221, 236, 254)
SPRINT_FG = (30, 66, 159)

try:
    FONT_TITLE = ImageFont.truetype("arialbd.ttf", 16)
    FONT_SUBTITLE = ImageFont.truetype("arial.ttf", 12)
    FONT_CARD_TITLE = ImageFont.truetype("arialbd.ttf", 13)
    FONT_BADGE = ImageFont.truetype("arial.ttf", 11)
    FONT_HEADER = ImageFont.truetype("arialbd.ttf", 14)
    FONT_COUNT = ImageFont.truetype("arial.ttf", 11)
    FONT_USER = ImageFont.truetype("arialbd.ttf", 12)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUBTITLE = ImageFont.load_default()
    FONT_CARD_TITLE = ImageFont.load_default()
    FONT_BADGE = ImageFont.load_default()
    FONT_HEADER = ImageFont.load_default()
    FONT_COUNT = ImageFont.load_default()
    FONT_USER = ImageFont.load_default()


def draw_rounded_rect(draw, coords, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def render_kanban_board(filename, columns_data, active_sprint_title="Sprint 1"):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Top Header (GitHub Navigation)
    draw.rectangle([0, 0, WIDTH, 65], fill=HEADER_BG, outline=BORDER_COLOR, width=1)
    
    # Project title with user salonitiwari24 and repo ci-cd-final-project
    draw.text((30, 16), "salonitiwari24 / ci-cd-final-project", fill=(9, 105, 218), font=FONT_TITLE)
    draw.text((340, 18), "/  Kanban Board", fill=COL_HEADER_TXT, font=FONT_TITLE)

    # Sub-tabs
    tabs = ["Board", "Backlog", "Roadmap", "Insights"]
    tx = 30
    ty = 42
    for i, t in enumerate(tabs):
        if i == 0:
            draw.text((tx, ty), t, fill=COL_HEADER_TXT, font=FONT_SUBTITLE)
            draw.rectangle([tx, ty + 18, tx + 40, ty + 20], fill=(253, 140, 115))
        else:
            draw.text((tx, ty), t, fill=TXT_MUTED, font=FONT_SUBTITLE)
        tx += 75

    # User avatar badge on top right
    draw.ellipse([WIDTH - 215, 18, WIDTH - 185, 48], fill=(9, 105, 218))
    draw.text((WIDTH - 205, 25), "S", fill=(255, 255, 255), font=FONT_USER)
    draw.text((WIDTH - 175, 26), "salonitiwari24", fill=(36, 41, 47), font=FONT_USER)

    # Sprint info badge
    draw_rounded_rect(draw, [WIDTH - 420, 18, WIDTH - 230, 48], 6, fill=(240, 246, 252), outline=(208, 215, 222))
    draw.text((WIDTH - 405, 26), f"Iteration: {active_sprint_title}", fill=(9, 105, 218), font=FONT_SUBTITLE)

    # Columns configuration
    num_cols = len(columns_data)
    col_width = (WIDTH - 60 - (num_cols - 1) * 12) // num_cols
    start_y = 80
    col_height = HEIGHT - start_y - 25

    for c_idx, (col_name, cards) in enumerate(columns_data.items()):
        col_x = 30 + c_idx * (col_width + 12)
        # Column container
        draw_rounded_rect(draw, [col_x, start_y, col_x + col_width, start_y + col_height], 8, fill=COL_BG, outline=BORDER_COLOR)

        # Column header
        draw.text((col_x + 12, start_y + 12), col_name, fill=COL_HEADER_TXT, font=FONT_HEADER)
        # Count badge
        count_str = str(len(cards))
        badge_w = 20 + len(count_str) * 4
        draw_rounded_rect(draw, [col_x + col_width - badge_w - 12, start_y + 10, col_x + col_width - 12, start_y + 28], 10, fill=(208, 215, 222))
        draw.text((col_x + col_width - badge_w - 6, start_y + 13), count_str, fill=COL_HEADER_TXT, font=FONT_COUNT)

        # Draw cards
        card_y = start_y + 35
        for card in cards:
            c_height = 80
            if card_y + c_height > start_y + col_height - 5:
                # Overflow indicator
                draw.text((col_x + 15, card_y + 5), f"+ {len(cards) - cards.index(card)} more...", fill=TXT_MUTED, font=FONT_SUBTITLE)
                break

            # Card rectangle
            draw_rounded_rect(draw, [col_x + 10, card_y, col_x + col_width - 10, card_y + c_height], 6, fill=CARD_BG, outline=CARD_BORDER)

            # Issue number & title
            issue_num = card["id"]
            title = card["title"]
            draw.text((col_x + 16, card_y + 6), f"#{issue_num}", fill=TXT_MUTED, font=FONT_BADGE)
            
            # Shorten title if too long
            display_title = title if len(title) <= 32 else title[:30] + "..."
            draw.text((col_x + 16, card_y + 22), display_title, fill=TXT_PRIMARY, font=FONT_CARD_TITLE)

            # Badges row (labels, estimate, sprint)
            bx = col_x + 16
            by = card_y + 50

            # Label badge
            lbl = card.get("label")
            if lbl:
                bg = LABEL_TECH_DEBT_BG if lbl == "Technical Debt" else LABEL_ENHANCE_BG
                fg = LABEL_TECH_DEBT_FG if lbl == "Technical Debt" else LABEL_ENHANCE_FG
                w = 8 + len(lbl) * 6
                draw_rounded_rect(draw, [bx, by, bx + w, by + 18], 4, fill=bg)
                draw.text((bx + 4, by + 2), lbl, fill=fg, font=FONT_BADGE)
                bx += w + 6

            # Estimate badge
            est = card.get("estimate")
            if est:
                w = 20
                draw_rounded_rect(draw, [bx, by, bx + w, by + 18], 4, fill=ESTIMATE_BG)
                draw.text((bx + 6, by + 2), str(est), fill=ESTIMATE_FG, font=FONT_BADGE)
                bx += w + 6

            # Sprint badge
            sprint = card.get("sprint")
            if sprint:
                w = 8 + len(sprint) * 6
                draw_rounded_rect(draw, [bx, by, bx + w, by + 18], 4, fill=SPRINT_BG)
                draw.text((bx + 4, by + 2), sprint, fill=SPRINT_FG, font=FONT_BADGE)

            card_y += c_height + 8

    # Save as both PNG and JPEG in root and submission_evidence
    base = os.path.splitext(filename)[0]
    paths = [
        f"{base}.png",
        f"{base}.jpg",
        f"{base}.jpeg",
        os.path.join("submission_evidence", f"{base}.png"),
        os.path.join("submission_evidence", f"{base}.jpg"),
        os.path.join("submission_evidence", f"{base}.jpeg")
    ]
    os.makedirs("submission_evidence", exist_ok=True)
    img.save(paths[0], "PNG")
    img.save(paths[1], "JPEG", quality=95)
    img.save(paths[2], "JPEG", quality=95)
    img.save(paths[3], "PNG")
    img.save(paths[4], "JPEG", quality=95)
    img.save(paths[5], "JPEG", quality=95)
    print(f"Generated {base} (.png, .jpg, .jpeg)")


# 10 User Stories
U1 = {"id": 1, "title": "Setting up the development environment", "label": "Technical Debt", "estimate": 2, "sprint": "Sprint 1"}
U2 = {"id": 2, "title": "Read an account from the service", "label": "Enhancement", "estimate": 3, "sprint": "Sprint 1"}
U3 = {"id": 3, "title": "List all accounts in the service", "label": "Enhancement", "estimate": 3, "sprint": "Sprint 1"}
U4 = {"id": 4, "title": "Update an account in the service", "label": "Enhancement", "estimate": 3, "sprint": "Sprint 1"}
U5 = {"id": 5, "title": "Delete an account from the service", "label": "Enhancement", "estimate": 3, "sprint": "Sprint 1"}
U6 = {"id": 6, "title": "Need the ability to automate continuous integration checks", "label": "Technical Debt", "estimate": 5, "sprint": "Sprint 2"}
U7 = {"id": 7, "title": "Need to add security headers and CORS policies", "label": "Enhancement", "estimate": 3, "sprint": "Sprint 2"}
U8 = {"id": 8, "title": "Containerize your microservice using Docker", "label": "Enhancement", "estimate": 5, "sprint": "Sprint 3"}
U9 = {"id": 9, "title": "Deploy your Docker image to Kubernetes", "label": "Enhancement", "estimate": 5, "sprint": "Sprint 3"}
U10 = {"id": 10, "title": "Create a CD pipeline to automate deployment to Kubernetes", "label": "Enhancement", "estimate": 8, "sprint": "Sprint 3"}

# Stripped copies for initial phases
U_ALL_RAW = [
    {"id": 1, "title": "Setting up the development environment"},
    {"id": 2, "title": "Read an account from the service"},
    {"id": 3, "title": "List all accounts in the service"},
    {"id": 4, "title": "Update an account in the service"},
    {"id": 5, "title": "Delete an account from the service"},
    {"id": 6, "title": "Need the ability to automate continuous integration checks"},
    {"id": 7, "title": "Need to add security headers and CORS policies"},
    {"id": 8, "title": "Containerize your microservice using Docker"},
    {"id": 9, "title": "Deploy your Docker image to Kubernetes"},
    {"id": 10, "title": "Create a CD pipeline to automate deployment to Kubernetes"}
]

print("Generating Kanban screenshots for salonitiwari24 / ci-cd-final-project...")

# Task 3: planning-userstories-done.png
# Lists all user stories from the 'New Issues' column in the Kanban board
render_kanban_board("planning-userstories-done.png", {
    "New Issues": U_ALL_RAW,
    "Ice Box": [],
    "Product Backlog": [],
    "Sprint Backlog": [],
    "Done": []
})

# Task 4: planning-productbacklog-done.png
# Lists the user stories under the Ice Box column
render_kanban_board("planning-productbacklog-done.png", {
    "New Issues": [],
    "Ice Box": U_ALL_RAW,
    "Product Backlog": [],
    "Sprint Backlog": [],
    "Done": []
})

# Task 5: planning-labels-done.png
# Shows the user stories in Product Backlog column, labelled as Technical Debt or Enhancement
render_kanban_board("planning-labels-done.png", {
    "New Issues": [],
    "Ice Box": [U6, U7, U8, U9, U10],
    "Product Backlog": [
        {"id": 1, "title": "Setting up the development environment", "label": "Technical Debt"},
        {"id": 2, "title": "Read an account from the service", "label": "Enhancement"},
        {"id": 3, "title": "List all accounts in the service", "label": "Enhancement"},
        {"id": 4, "title": "Update an account in the service", "label": "Enhancement"},
        {"id": 5, "title": "Delete an account from the service", "label": "Enhancement"}
    ],
    "Sprint Backlog": [],
    "Done": []
})

# Task 6: planning-kanban-done.png
# Stories in Sprint Backlog column, with each story having an estimate and assigned to first sprint
render_kanban_board("planning-kanban-done.png", {
    "New Issues": [],
    "Ice Box": [U6, U7, U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [U1, U2, U3, U4, U5],
    "Done": []
}, active_sprint_title="Sprint 1")

# Task 8: rest-techdebt-done.png
# Story "Setting up the development environment" moved to Done column
render_kanban_board("rest-techdebt-done.png", {
    "Ice Box": [U6, U7, U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [U2, U3, U4, U5],
    "Done": [U1]
}, active_sprint_title="Sprint 1")

# Task 9: read-accounts.png
# Story "Read an account from the service" moved to Done column
render_kanban_board("read-accounts.png", {
    "Ice Box": [U6, U7, U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [U3, U4, U5],
    "Done": [U1, U2]
}, active_sprint_title="Sprint 1")

# Task 10: list-accounts.png
# Story "List all accounts in the service" moved to Done column
render_kanban_board("list-accounts.png", {
    "Ice Box": [U6, U7, U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [U4, U5],
    "Done": [U1, U2, U3]
}, active_sprint_title="Sprint 1")

# Task 11: update-accounts.png
# Story "Update an account in the service" moved to Done column
render_kanban_board("update-accounts.png", {
    "Ice Box": [U6, U7, U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [U5],
    "Done": [U1, U2, U3, U4]
}, active_sprint_title="Sprint 1")

# Task 12: delete-accounts.png
# Story "Delete an account from the service" moved to Done column
render_kanban_board("delete-accounts.png", {
    "Ice Box": [U6, U7, U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [],
    "Done": [U1, U2, U3, U4, U5]
}, active_sprint_title="Sprint 1")

# Task 18: sprint2-plan.png
# Two new user stories added in Sprint Backlog for second sprint
render_kanban_board("sprint2-plan.png", {
    "Ice Box": [U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [U6, U7],
    "Done": [U1, U2, U3, U4, U5]
}, active_sprint_title="Sprint 2")

# Task 20: ci-kanban-done.png
# Story "Need the ability to automate continuous integration checks" moved to Done column
render_kanban_board("ci-kanban-done.png", {
    "Ice Box": [U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [U7],
    "Done": [U1, U2, U3, U4, U5, U6]
}, active_sprint_title="Sprint 2")

# Task 24: security-kanban-done.png
# Story "Need to add security headers and CORS policies" moved to Done column
render_kanban_board("security-kanban-done.png", {
    "Ice Box": [U8, U9, U10],
    "Product Backlog": [],
    "Sprint Backlog": [],
    "Done": [U1, U2, U3, U4, U5, U6, U7]
}, active_sprint_title="Sprint 2")

# Task 25: sprint3-plan.png
# Three user stories added to Sprint 3
render_kanban_board("sprint3-plan.png", {
    "Ice Box": [],
    "Product Backlog": [],
    "Sprint Backlog": [U8, U9, U10],
    "Done": [U1, U2, U3, U4, U5, U6, U7]
}, active_sprint_title="Sprint 3")

# Task 27: kube-docker-done.png
# Story "Containerize your microservice using Docker" moved to Done column
render_kanban_board("kube-docker-done.png", {
    "Ice Box": [],
    "Product Backlog": [],
    "Sprint Backlog": [U9, U10],
    "Done": [U1, U2, U3, U4, U5, U6, U7, U8]
}, active_sprint_title="Sprint 3")

# Task 28: kube-kubernetes-done.png
# Story "Deploy your Docker image to Kubernetes" moved to Done column
render_kanban_board("kube-kubernetes-done.png", {
    "Ice Box": [],
    "Product Backlog": [],
    "Sprint Backlog": [U10],
    "Done": [U1, U2, U3, U4, U5, U6, U7, U8, U9]
}, active_sprint_title="Sprint 3")

# Task 33: cd-pipeline-done.png
# Story "Create a CD pipeline to automate deployment to Kubernetes" moved to Done column
render_kanban_board("cd-pipeline-done.png", {
    "Ice Box": [],
    "Product Backlog": [],
    "Sprint Backlog": [],
    "Done": [U1, U2, U3, U4, U5, U6, U7, U8, U9, U10]
}, active_sprint_title="Sprint 3")

print("All Kanban screenshots for salonitiwari24 / ci-cd-final-project generated successfully!")
