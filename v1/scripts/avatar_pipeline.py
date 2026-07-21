import io
import urllib.request

from PIL import Image, ImageDraw

SIZES = (32, 48, 96, 192, 256, 460)
PROFILE_AVATAR_SIZE = 96
TABLE_AVATAR_SIZE = 32
LOCAL_AVATAR_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
ORG_LOGO_URL = "https://raw.githubusercontent.com/MontageSubs/brand-assets/main/logos/png/web/logo-600.png"


def find_local_avatar(member_dir):
    avatar_dir = member_dir / "avatar"
    if not avatar_dir.is_dir():
        return None
    candidates = sorted(
        path
        for path in avatar_dir.iterdir()
        if path.is_file() and path.suffix.lower() in LOCAL_AVATAR_EXTENSIONS
    )
    return candidates[0] if candidates else None


def resolve_remote_url(avatar_source, github):
    if avatar_source:
        return avatar_source
    if github:
        return f"https://github.com/{github}.png"
    return ORG_LOGO_URL


def download_image(url):
    request = urllib.request.Request(url, headers={"User-Agent": "MontageSubs-Avatar-Sync"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return Image.open(io.BytesIO(response.read())).convert("RGBA")


def load_source(member_dir, frontmatter):
    local_avatar = find_local_avatar(member_dir)
    if local_avatar is not None:
        return Image.open(local_avatar).convert("RGBA")
    avatar_source = (frontmatter.get("avatar_source") or "").strip()
    github = (frontmatter.get("github") or "").strip()
    return download_image(resolve_remote_url(avatar_source, github))


def center_square(image):
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def circular(image):
    scale = 4
    mask_size = (image.size[0] * scale, image.size[1] * scale)
    mask = Image.new("L", mask_size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, mask_size[0], mask_size[1]), fill=255)
    mask = mask.resize(image.size, Image.LANCZOS)
    result = image.copy()
    result.putalpha(mask)
    return result


def render_variants(member_dir, frontmatter, output_dir):
    square_base = center_square(load_source(member_dir, frontmatter))
    usable_sizes = [size for size in SIZES if size <= min(square_base.size)]
    variants = {}
    for size in usable_sizes:
        square = square_base.resize((size, size), Image.LANCZOS)
        for shape, image in (("square", square), ("circle", circular(square))):
            asset_name = f"{shape}-{size}.png"
            local_path = output_dir / asset_name
            image.save(local_path)
            variants[asset_name] = local_path
    return variants
