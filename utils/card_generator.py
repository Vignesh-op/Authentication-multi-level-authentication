from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import os
from datetime import datetime
from .qr_utils import generate_qr_code
import tempfile

def _load_logo():
    """Try known logo filenames and return PIL image or None."""
    candidate_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'authsafe-logo.png'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'authsafe_logo.png'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'logo.png'),
        os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'authsafe.png'),
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            try:
                return Image.open(path).convert("RGBA")
            except Exception:
                return None
    return None


def _draw_card_base(card, draw, title_font, text_font, small_font):
    """Draw a modern two-panel smart card background and heading."""
    card_width, card_height = card.size

    # Dark gradient-like left panel + light right panel for better UI fit.
    split_x = int(card_width * 0.46)
    for y in range(card_height):
        blend = y / max(card_height - 1, 1)
        r = int(22 + (35 - 22) * blend)
        g = int(55 + (82 - 55) * blend)
        b = int(119 + (153 - 119) * blend)
        draw.line([(0, y), (split_x, y)], fill=(r, g, b))
    draw.rectangle([(split_x, 0), (card_width, card_height)], fill=(244, 248, 255))
    draw.rounded_rectangle([(8, 8), (card_width - 8, card_height - 8)], radius=26, outline=(21, 35, 67), width=4)
    draw.line([(split_x, 16), (split_x, card_height - 16)], fill=(170, 190, 220), width=2)

    # Brand header area
    logo = _load_logo()
    if logo:
        logo = logo.resize((76, 76), Image.Resampling.LANCZOS)
        card.paste(logo, (24, 22), logo)
        draw.text((114, 30), "AuthSafe", fill=(255, 255, 255), font=title_font)
        draw.text((116, 76), "Smart Identity Card", fill=(220, 233, 255), font=small_font)
    else:
        draw.text((24, 30), "AuthSafe", fill=(255, 255, 255), font=title_font)
        draw.text((24, 76), "Smart Identity Card", fill=(220, 233, 255), font=small_font)

def _passport_photo_from_cv2(face_image_cv2, target_width, target_height):
    """Convert captured image to passport-style portrait crop."""
    face_rgb = cv2.cvtColor(face_image_cv2, cv2.COLOR_BGR2RGB)
    face_pil = Image.fromarray(face_rgb)

    src_w, src_h = face_pil.size
    target_ratio = target_width / target_height
    src_ratio = src_w / max(src_h, 1)

    # Center-crop to passport aspect ratio before resize.
    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        crop_box = (left, 0, left + new_w, src_h)
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        crop_box = (0, top, src_w, top + new_h)

    face_pil = face_pil.crop(crop_box)
    return face_pil.resize((target_width, target_height), Image.Resampling.LANCZOS)

def generate_smartcard(name, unique_id, face_image_cv2, output_path):
    """
    Generate a smart card image with user info and QR code.
    
    Args:
        name (str): User's name
        unique_id (str): User's unique ID
        face_image_cv2: OpenCV face image
        output_path (str): Path to save the card
        
    Returns:
        bool: True if card generated successfully
    """
    try:
        # Use a direct 16:9 smart card image (no A4 canvas).
        card_width = 1280
        card_height = 720

        card = Image.new('RGB', (card_width, card_height), color='white')
        draw = ImageDraw.Draw(card)
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            text_font = ImageFont.truetype("arial.ttf", 32)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        _draw_card_base(card, draw, title_font, text_font, small_font)
        
        # User Name
        draw.text((24, 170), "Name", fill=(220, 233, 255), font=text_font)
        draw.text((24, 214), name[:20], fill=(255, 255, 255), font=text_font)
        
        # Unique ID
        draw.text((24, 300), "Unique ID", fill=(220, 233, 255), font=text_font)
        draw.text((24, 344), unique_id, fill=(255, 255, 255), font=small_font)
        
        # Date
        date_str = datetime.now().strftime("%Y-%m-%d")
        draw.text((24, 462), f"Issued: {date_str}", fill=(220, 233, 255), font=small_font)
        
        # Passport-style photo region (portrait, not square)
        photo_x = 720
        photo_y = 65
        photo_w = 280
        photo_h = 360

        # Resize and place face image
        if face_image_cv2 is not None:
            try:
                face_pil = _passport_photo_from_cv2(face_image_cv2, photo_w, photo_h)
                # Clean photo placement without square framing box.
                card.paste(face_pil, (photo_x, photo_y))
            except Exception as e:
                print(f"Error processing face image: {e}")
        
        # Generate and embed QR code using a guaranteed-cleanup temp file.
        qr_temp_fd, qr_temp_path = tempfile.mkstemp(suffix='.png')
        os.close(qr_temp_fd)  # close fd; generate_qr_code opens the path itself
        try:
            if generate_qr_code(unique_id, qr_temp_path, secret_key=None):
                try:
                    qr_image = Image.open(qr_temp_path)
                    qr_image = qr_image.resize((190, 190), Image.Resampling.LANCZOS)
                    card.paste(qr_image, (730, 475))
                    draw.text((940, 560), "Scan to verify", fill=(55, 78, 118), font=small_font)
                except Exception as e:
                    print(f"Error embedding QR code: {e}")
        finally:
            if os.path.exists(qr_temp_path):
                os.remove(qr_temp_path)
        
        # Save direct 16:9 smart card image.
        card.save(output_path, 'PNG')
        return True
        
    except Exception as e:
        print(f"Error generating smart card: {e}")
        return False

def create_placeholder_card(name, unique_id, output_path):
    """
    Create a placeholder smart card when face image is not available.
    
    Args:
        name (str): User's name
        unique_id (str): User's unique ID
        output_path (str): Path to save the card
        
    Returns:
        bool: True if card created successfully
    """
    try:
        card_width = 1280
        card_height = 720
        
        card = Image.new('RGB', (card_width, card_height), color='white')
        draw = ImageDraw.Draw(card)
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            text_font = ImageFont.truetype("arial.ttf", 32)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        _draw_card_base(card, draw, title_font, text_font, small_font)
        
        # User Name
        draw.text((24, 170), "Name", fill=(220, 233, 255), font=text_font)
        draw.text((24, 214), name[:20], fill=(255, 255, 255), font=text_font)
        
        # Unique ID
        draw.text((24, 300), "Unique ID", fill=(220, 233, 255), font=text_font)
        draw.text((24, 344), unique_id, fill=(255, 255, 255), font=small_font)
        
        # Date
        date_str = datetime.now().strftime("%Y-%m-%d")
        draw.text((24, 462), f"Issued: {date_str}", fill=(220, 233, 255), font=small_font)
        
        # Placeholder for missing passport photo (portrait, no square frame)
        draw.rectangle([(720, 65), (1000, 425)], fill=(235, 241, 252))
        draw.text((800, 230), "NO PHOTO", fill=(115, 124, 144), font=text_font)
        
        # Generate and embed QR code using a guaranteed-cleanup temp file.
        qr_temp_fd, qr_temp_path = tempfile.mkstemp(suffix='.png')
        os.close(qr_temp_fd)
        try:
            if generate_qr_code(unique_id, qr_temp_path, secret_key=None):
                try:
                    qr_image = Image.open(qr_temp_path)
                    qr_image = qr_image.resize((190, 190), Image.Resampling.LANCZOS)
                    card.paste(qr_image, (730, 475))
                    draw.text((940, 560), "Scan to verify", fill=(55, 78, 118), font=small_font)
                except Exception as e:
                    print(f"Error embedding QR code: {e}")
        finally:
            if os.path.exists(qr_temp_path):
                os.remove(qr_temp_path)
        
        # Save card
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        card.save(output_path, 'PNG')
        return True
        
    except Exception as e:
        print(f"Error creating placeholder card: {e}")
        return False
