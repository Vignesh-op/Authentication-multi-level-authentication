"""
Create Authentication Logo - Professional Cybersecurity Logo with Wireframe Face, Smart Card, and Padlock
Dark theme with glowing accents, premium tech feel
"""
from PIL import Image, ImageDraw, ImageFont
import os
import math

def create_authentication_logo():
    """Create professional Authentication logo with advanced cybersecurity design"""
    
    # Create main image with dark background
    logo_width = 800
    logo_height = 1000
    logo = Image.new('RGB', (logo_width, logo_height), (10, 15, 35))
    draw = ImageDraw.Draw(logo, 'RGBA')
    
    # Define premium colors
    dark_bg = (10, 15, 35)  # Deep navy
    cyan_glow = (0, 255, 200)  # Bright cyan
    blue_accent = (0, 100, 255)  # Deep blue
    teal_accent = (0, 220, 220)  # Teal
    gold_accent = (255, 200, 0)  # Gold
    white_text = (255, 255, 255)  # White
    
    # Fill background with gradient effect
    for y in range(logo_height):
        alpha = int(10 + (y / logo_height) * 25)
        color = (10, 15 + alpha, 35 + alpha)
        draw.rectangle([(0, y), (logo_width, y + 1)], fill=color)
    
    # ===== WIREFRAME FACE (BACKGROUND) =====
    face_center_x, face_center_y = logo_width // 2, 150
    
    # Draw semi-transparent wireframe head (circle)
    head_radius = 80
    draw.ellipse(
        [(face_center_x - head_radius, face_center_y - head_radius),
         (face_center_x + head_radius, face_center_y + head_radius)],
        outline=(0, 150, 150, 80),
        width=2
    )
    
    # Wireframe face grid
    for i in range(3):
        y_pos = face_center_y - head_radius + (i + 1) * (head_radius * 2) // 4
        draw.line([(face_center_x - head_radius, y_pos), 
                  (face_center_x + head_radius, y_pos)],
                 fill=(0, 180, 180, 60), width=1)
    
    for i in range(3):
        x_pos = face_center_x - head_radius + (i + 1) * (head_radius * 2) // 4
        draw.line([(x_pos, face_center_y - head_radius), 
                  (x_pos, face_center_y + head_radius)],
                 fill=(0, 180, 180, 60), width=1)
    
    # Eyes (wireframe circles)
    eye_y = face_center_y - 20
    draw.ellipse([(face_center_x - 35, eye_y - 10), (face_center_x - 15, eye_y + 10)],
                outline=(0, 200, 200, 120), width=2)
    draw.ellipse([(face_center_x + 15, eye_y - 10), (face_center_x + 35, eye_y + 10)],
                outline=(0, 200, 200, 120), width=2)
    
    # Glowing dots in eyes
    draw.ellipse([(face_center_x - 30, eye_y - 5), (face_center_x - 20, eye_y + 5)],
                fill=(0, 255, 200, 150))
    draw.ellipse([(face_center_x + 20, eye_y - 5), (face_center_x + 30, eye_y + 5)],
                fill=(0, 255, 200, 150))
    
    # Nose
    draw.line([(face_center_x, face_center_y - 10), (face_center_x, face_center_y + 10)],
             fill=(0, 200, 200, 100), width=1)
    
    # Mouth
    draw.arc([(face_center_x - 30, face_center_y + 10), 
             (face_center_x + 30, face_center_y + 50)],
            0, 180, fill=(0, 200, 200, 100), width=2)
    
    # ===== CIRCUIT NETWORK LINES (AROUND) =====
    circuit_points = [
        (100, 300), (200, 250), (350, 280), (500, 260), (650, 300),
        (700, 350), (680, 450), (600, 500), (450, 520), (300, 500),
        (150, 480), (80, 400)
    ]
    
    for i in range(len(circuit_points)):
        p1 = circuit_points[i]
        p2 = circuit_points[(i + 1) % len(circuit_points)]
        draw.line([p1, p2], fill=cyan_glow, width=2)
        
        # Circuit nodes (glowing dots)
        draw.ellipse([(p1[0] - 4, p1[1] - 4), (p1[0] + 4, p1[1] + 4)],
                    fill=cyan_glow)
    
    # ===== SMART CARD =====
    card_x, card_y = logo_width // 2 - 140, 320
    card_w, card_h = 280, 180
    
    # Card background with gradient
    for i in range(card_h):
        color_intensity = int(20 + (i / card_h) * 40)
        color = (color_intensity, color_intensity + 30, color_intensity + 60)
        draw.rectangle([(card_x, card_y + i), (card_x + card_w, card_y + i + 1)],
                      fill=color)
    
    # Card border (glowing)
    for glow in range(3, 0, -1):
        alpha = int(100 - glow * 30)
        draw.rectangle([(card_x - glow, card_y - glow), 
                       (card_x + card_w + glow, card_y + card_h + glow)],
                      outline=(0, 255, 200, alpha), width=1)
    
    # Card border outline
    draw.rectangle([(card_x, card_y), (card_x + card_w, card_y + card_h)],
                  outline=cyan_glow, width=3)
    
    # Chip (gold rectangle)
    chip_x, chip_y = card_x + 30, card_y + 30
    chip_size = 50
    draw.rectangle([(chip_x, chip_y), (chip_x + chip_size, chip_y + chip_size)],
                  fill=gold_accent, outline=(255, 220, 0), width=2)
    
    # Chip contacts
    for i in range(8):
        contact_x = chip_x + 5 + i * (chip_size - 10) // 8
        draw.rectangle([(contact_x, chip_y + 5), (contact_x + 3, chip_y + 8)],
                      fill=(200, 150, 0))
    
    # QR Code pattern (right side of card)
    qr_x, qr_y = card_x + card_w - 70, card_y + 30
    qr_module = 8
    
    for i in range(7):
        for j in range(7):
            if (i + j) % 2 == 0:
                draw.rectangle([(qr_x + i * qr_module, qr_y + j * qr_module),
                               (qr_x + (i + 1) * qr_module, qr_y + (j + 1) * qr_module)],
                              fill=cyan_glow)
    
    # ===== PADLOCK ICON =====
    lock_x, lock_y = card_x + card_w // 2, card_y + card_h // 2 + 30
    
    # Lock body
    lock_body_w, lock_body_h = 50, 60
    draw.rectangle([(lock_x - lock_body_w // 2, lock_y),
                   (lock_x + lock_body_w // 2, lock_y + lock_body_h)],
                  fill=(0, 100, 150), outline=gold_accent, width=3)
    
    # Lock shackle
    shackle_radius = 35
    draw.arc([(lock_x - shackle_radius, lock_y - shackle_radius),
             (lock_x + shackle_radius, lock_y + 10)],
            0, 180, fill=gold_accent, width=4)
    
    # Keyhole
    draw.ellipse([(lock_x - 8, lock_y + 25), (lock_x + 8, lock_y + 40)],
                fill=dark_bg, outline=gold_accent, width=2)
    
    # Glow around lock
    for glow_size in range(8, 0, -2):
        alpha = int(50 - glow_size * 5)
        draw.ellipse([(lock_x - glow_size - 30, lock_y - glow_size),
                     (lock_x + glow_size + 30, lock_y + lock_body_h + glow_size)],
                    outline=(0, 255, 200, alpha), width=1)
    
    # ===== SHIELD OUTLINE WITH CIRCUIT =====
    shield_x = logo_width // 2
    shield_y = 380
    shield_w = 250
    shield_h = 140
    
    # Hexagonal shield points
    shield_points = [
        (shield_x - shield_w // 2, shield_y),  # Top left
        (shield_x + shield_w // 2, shield_y),  # Top right
        (shield_x + shield_w // 2 + 30, shield_y + shield_h // 2),  # Right
        (shield_x + shield_w // 2, shield_y + shield_h),  # Bottom right
        (shield_x - shield_w // 2, shield_y + shield_h),  # Bottom left
        (shield_x - shield_w // 2 - 30, shield_y + shield_h // 2),  # Left
    ]
    
    # Shield glow
    for glow in range(4, 0, -1):
        alpha = int(80 - glow * 15)
        glow_points = [(p[0] + (p[0] - shield_x) * glow * 0.05,
                       p[1] + (p[1] - shield_y) * glow * 0.05) for p in shield_points]
        draw.polygon(glow_points, outline=(0, 255, 200, alpha), width=1)
    
    # Shield
    draw.polygon(shield_points, fill=(0, 50, 100), outline=cyan_glow, width=3)
    
    # Additional circuit lines inside shield
    for i, point in enumerate(shield_points):
        next_point = shield_points[(i + 1) % len(shield_points)]
        mid_x, mid_y = (point[0] + next_point[0]) // 2, (point[1] + next_point[1]) // 2
        draw.line([point, (shield_x, shield_y + shield_h // 2)],
                 fill=(0, 200, 200, 100), width=1)
    
    # ===== TEXT: Authentication =====
    try:
        title_font = ImageFont.truetype("arial.ttf", 80)
        subtitle_font = ImageFont.truetype("arial.ttf", 28)
        footer_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
    
    # Authentication text with gradient effect (simulated with layering)
    auth_text = "Authentication"
    auth_y = logo_height - 280
    
    # Text shadow (dark blue)
    text_bbox = draw.textbbox((0, 0), auth_text, font=title_font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (logo_width - text_width) // 2
    
    draw.text((text_x + 3, auth_y + 3), auth_text, font=title_font,
             fill=(0, 50, 100))
    
    # Main text (white with cyan tint)
    draw.text((text_x, auth_y), auth_text, font=title_font,
             fill=white_text)
    
    # Cyan highlight on text
    draw.text((text_x, auth_y), auth_text, font=title_font,
             fill=(0, 255, 200, 100))
    
    # ===== TAGLINE =====
    tagline = "Multi-Level Authentication"
    tagline_y = logo_height - 180
    
    tagline_bbox = draw.textbbox((0, 0), tagline, font=subtitle_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (logo_width - tagline_width) // 2
    
    draw.text((tagline_x, tagline_y), tagline, font=subtitle_font,
             fill=cyan_glow)
    
    # Decorative line above text
    line_y = auth_y - 30
    draw.line([(logo_width // 2 - 100, line_y), (logo_width // 2 + 100, line_y)],
             fill=cyan_glow, width=2)
    
    # Decorative dots on line
    for x in [logo_width // 2 - 100, logo_width // 2, logo_width // 2 + 100]:
        draw.ellipse([(x - 4, line_y - 4), (x + 4, line_y + 4)],
                    fill=gold_accent)
    
    # Save logo
    output_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as PNG
    logo.save(os.path.join(output_dir, 'authentication-logo.png'), 'PNG')
    print("✓ Professional Authentication logo created: static/images/authentication-logo.png")
    
    # Create smaller version
    logo_small = logo.resize((256, 320), Image.Resampling.LANCZOS)
    logo_small.save(os.path.join(output_dir, 'authentication-logo-small.png'), 'PNG')
    print("✓ Small logo created: static/images/authentication-logo-small.png")

if __name__ == '__main__':
    create_authentication_logo()
