#!/usr/bin/env python3
"""
Trinity VR QR Code Generator
Generates QR codes for quick Quest access
"""

import os
import sys
import socket
import subprocess

def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def get_tailscale_ip():
    """Get Tailscale IP address."""
    try:
        result = subprocess.run(['tailscale', 'ip', '-4'],
                              capture_output=True, text=True, timeout=2)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None

def generate_qr_code(url, filename):
    """Generate QR code using qrcode library."""
    try:
        import qrcode
        from PIL import Image, ImageDraw, ImageFont

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="#00ff00", back_color="#000000")

        # Convert to RGB for adding text
        img = img.convert('RGB')
        width, height = img.size

        # Create new image with space for text
        new_height = height + 100
        new_img = Image.new('RGB', (width, new_height), '#000000')
        new_img.paste(img, (0, 0))

        # Add text
        draw = ImageDraw.Draw(new_img)

        # Try to use a nice font, fall back to default if not available
        try:
            font_large = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
            font_small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 16)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Add title
        title = "TRINITY VR WORKSPACE"
        bbox = draw.textbbox((0, 0), title, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, height + 10), title, fill="#00ff00", font=font_large)

        # Add URL
        bbox = draw.textbbox((0, 0), url, font=font_small)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, height + 45), url, fill="#00ff00", font=font_small)

        # Add instructions
        instruction = "Scan with Quest Browser"
        bbox = draw.textbbox((0, 0), instruction, font=font_small)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, height + 70), instruction, fill="#00cc00", font=font_small)

        # Save image
        new_img.save(filename)
        print(f"✅ QR code saved to: {filename}")
        return True

    except ImportError:
        print("❌ Error: qrcode library not installed")
        print("Install with: pip3 install qrcode[pil]")
        return False
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        return False

def generate_ascii_qr(url):
    """Generate ASCII QR code for terminal display."""
    try:
        import qrcode

        qr = qrcode.QRCode(version=1, box_size=1, border=2)
        qr.add_data(url)
        qr.make(fit=True)

        # Print to terminal
        qr.print_ascii(invert=True)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("╔════════════════════════════════════════╗")
    print("║  TRINITY VR QR CODE GENERATOR          ║")
    print("╚════════════════════════════════════════╝")
    print()

    # Get IP addresses
    local_ip = get_local_ip()
    tailscale_ip = get_tailscale_ip()

    print("🌐 Network Information:")
    if local_ip:
        print(f"   Local WiFi: {local_ip}")
    else:
        print("   Local WiFi: Not available")

    if tailscale_ip:
        print(f"   Tailscale:  {tailscale_ip}")
    else:
        print("   Tailscale:  Not available")

    print()

    # Generate QR codes
    vr_port = 8503

    if local_ip:
        local_url = f"http://{local_ip}:{vr_port}/vr"
        print(f"📱 Generating QR code for: {local_url}")
        print()

        # Generate image QR code
        if generate_qr_code(local_url, "trinity_vr_qr_local.png"):
            print()

        # Generate ASCII QR code
        print("📟 ASCII QR Code (for terminal):")
        print()
        if generate_ascii_qr(local_url):
            print()

    if tailscale_ip:
        tailscale_url = f"http://{tailscale_ip}:{vr_port}/vr"
        print(f"📱 Generating QR code for: {tailscale_url}")
        print()

        # Generate image QR code
        if generate_qr_code(tailscale_url, "trinity_vr_qr_tailscale.png"):
            print()

    if not local_ip and not tailscale_ip:
        print("❌ No network connection available")
        return 1

    print("✅ QR codes generated successfully!")
    print()
    print("📄 Usage:")
    print("   1. Open generated PNG file")
    print("   2. Display on phone or print")
    print("   3. Scan with Quest browser")
    print("   4. Instant access to Trinity VR!")
    print()
    print("💡 Tip: Bookmark the URL in Quest browser for quick access")

    return 0

if __name__ == '__main__':
    sys.exit(main())
