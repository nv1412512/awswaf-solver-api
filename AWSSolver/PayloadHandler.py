# fp_encrypt.py
import os
import base64
import json
import uuid
import random
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ====== CONSTANTS ======
ALPHABET = "0123456789abcdef"
IEEE_POLYNOMIAL = 0xEDB88320

KEY = bytes.fromhex(
    "6f71a512b1e035eaab53d8be73120d3fb68a0ca346b9560aab3e5cdf753d5e98"
)
AESGCM_INSTANCE = AESGCM(key=KEY)


# ====== CRYPTO ======
def encrypt_payload(payload_str: str) -> str:
    """
    Returns: "<iv_b64>::<tag_hex>::<ciphertext_hex>"
    """
    iv = os.urandom(12)
    plaintext = payload_str.encode("utf-8")
    cipher_bytes = AESGCM_INSTANCE.encrypt(iv, plaintext, None)

    tag = cipher_bytes[-16:]
    ciphertext = cipher_bytes[:-16]
    iv_b64 = base64.b64encode(iv).decode("utf-8")

    return f"{iv_b64}::{tag.hex()}::{ciphertext.hex()}"


# ====== FP BUILDING ======
def get_fp(user_agent) -> dict:
    start = int(time.time() * 1000)

    fingerprint = {
        "metrics": {
            "fp2": 1,
            "browser": 0,
            "capabilities": 1,
            "gpu": 7,
            "dnt": 0,
            "math": 0,
            "screen": 0,
            "navigator": 0,
            "auto": 1,
            "stealth": 0,
            "subtle": 0,
            "canvas": 5,
            "formdetector": 1,
            "be": 0,
        },
        "start": start,
        "flashVersion": None,
        "plugins": [
            {"name": "PDF Viewer", "str": "PDF Viewer "},
            {"name": "Chrome PDF Viewer", "str": "Chrome PDF Viewer "},
            {"name": "Chromium PDF Viewer", "str": "Chromium PDF Viewer "},
            {"name": "Microsoft Edge PDF Viewer", "str": "Microsoft Edge PDF Viewer "},
            {"name": "WebKit built-in PDF", "str": "WebKit built-in PDF "},
        ],
        "dupedPlugins": "PDF Viewer Chrome PDF Viewer Chromium PDF Viewer Microsoft Edge PDF Viewer WebKit built-in PDF ||1920-1080-1032-24-*-*-*",
        "screenInfo": "1920-1080-1032-24-*-*-*",
        "referrer": "",
        "userAgent": f"{user_agent}",
        "location": "",
        "webDriver": False,
        "capabilities": {
            "css": {
                "textShadow": 1,
                "WebkitTextStroke": 1,
                "boxShadow": 1,
                "borderRadius": 1,
                "borderImage": 1,
                "opacity": 1,
                "transform": 1,
                "transition": 1,
            },
            "js": {
                "audio": True,
                "geolocation": random.choice([True, False]),
                "localStorage": "supported",
                "touch": False,
                "video": True,
                "webWorker": random.choice([True, False]),
            },
            "elapsed": 1,
        },
        "gpu": {
            "vendor": "Google Inc. (Apple)",
            "model": "ANGLE (Apple, ANGLE Metal Renderer: Apple M2 Pro, Unspecified Version)",
            "extensions": "ANGLE_instanced_arrays;EXT_blend_minmax;EXT_clip_control;EXT_color_buffer_half_float;EXT_depth_clamp;EXT_disjoint_timer_query;EXT_float_blend;EXT_frag_depth;EXT_polygon_offset_clamp;EXT_shader_texture_lod;EXT_texture_compression_bptc;EXT_texture_compression_rgtc;EXT_texture_filter_anisotropic;EXT_texture_mirror_clamp_to_edge;EXT_sRGB;KHR_parallel_shader_compile;OES_element_index_uint;OES_fbo_render_mipmap;OES_standard_derivatives;OES_texture_float;OES_texture_float_linear;OES_texture_half_float;OES_texture_half_float_linear;OES_vertex_array_object;WEBGL_blend_func_extended;WEBGL_color_buffer_float;WEBGL_compressed_texture_astc;WEBGL_compressed_texture_etc;WEBGL_compressed_texture_etc1;WEBGL_compressed_texture_pvrtc;WEBGL_compressed_texture_s3tc;WEBGL_compressed_texture_s3tc_srgb;WEBGL_debug_renderer_info;WEBGL_debug_shaders;WEBGL_depth_texture;WEBGL_draw_buffers;WEBGL_lose_context;WEBGL_multi_draw;WEBGL_polygon_mode".split(
                ";"
            ),
        },
        "dnt": None,
        "math": {
            "tan": "-1.4214488238747245",
            "sin": "0.8178819121159085",
            "cos": "-0.5753861119575491",
        },
        "automation": {
            "wd": {"properties": {"document": [], "window": [], "navigator": []}},
            "phantom": {"properties": {"window": []}},
        },
        "stealth": {"t1": 0, "t2": 0, "i": 1, "mte": 0, "mtd": False},
        "crypto": {
            "crypto": 1,
            "subtle": 1,
            "encrypt": True,
            "decrypt": True,
            "wrapKey": True,
            "unwrapKey": True,
            "sign": True,
            "verify": True,
            "digest": True,
            "deriveBits": True,
            "deriveKey": True,
            "getRandomValues": True,
            "randomUUID": True,
        },
        "canvas": {"hash": random.randrange(645172295, 735192295), "emailHash": None, "histogramBins": [random.randrange(0, 40) for _ in range(256)]},
        "formDetected": False,
        "numForms": 0,
        "numFormElements": 0,
        "be": {"si": False},
        "end": start + random.randint(1,5),
        "errors": [],
        "version": "2.4.0",
        "id": str(uuid.uuid4()),
    }
    return fingerprint


def build_crc_table(ieee_polynomial: int = IEEE_POLYNOMIAL) -> list[int]:
    crc_table = []
    for i in range(256):
        v = i
        for _ in range(8):
            if v & 1:
                v = (v >> 1) ^ ieee_polynomial
            else:
                v >>= 1
        crc_table.append(v)
    return crc_table


def calculate_crc(data: str, crc_table: list[int]) -> int:
    v51 = 0 ^ 0xFFFFFFFF
    for char in data:
        charcode = ord(char)
        v50 = 255 & (v51 ^ charcode)
        v51 = (v51 & 0xFFFFFFFF) >> 8 ^ crc_table[v50]
    result = 0xFFFFFFFF ^ v51
    if result >= 0x80000000:
        result -= 0x100000000
    return result


def encode_number(encoded_payload: int) -> str:
    encoded_payload = encoded_payload & 0xFFFFFFFF
    return (
        ALPHABET[(encoded_payload >> 28) & 15]
        + ALPHABET[(encoded_payload >> 24) & 15]
        + ALPHABET[(encoded_payload >> 20) & 15]
        + ALPHABET[(encoded_payload >> 16) & 15]
        + ALPHABET[(encoded_payload >> 12) & 15]
        + ALPHABET[(encoded_payload >> 8) & 15]
        + ALPHABET[(encoded_payload >> 4) & 15]
        + ALPHABET[encoded_payload & 15]
    ).upper()


def encode_fp(user_agent) -> tuple[str, str]:
    """
    custom crc/table + encode_number variant you had:
    Returns: ("<CHECKSUM>#<json-string>", "<CHECKSUM>")
    """
    fp = get_fp(user_agent=user_agent)
    crc_table = build_crc_table()
    payload_str = json.dumps(fp, separators=(",", ":"))
    crc_result = calculate_crc(payload_str, crc_table)
    checksum = encode_number(crc_result)
    return f"{checksum}#{payload_str}", checksum


def build_everything(user_agent) -> dict:
    
    encoded, checksum = encode_fp(user_agent)
    if isinstance(encoded, bytes):
        encoded_str = encoded.decode("utf-8", errors="strict")
    else:
        encoded_str = encoded

    out = {
        "checksum": checksum,
        "encoded": encoded_str,
    }
    out["encrypted"] = encrypt_payload(encoded_str)
    return out
