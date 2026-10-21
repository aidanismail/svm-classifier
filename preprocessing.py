"""Cleaning deterministik yang identik dengan pipeline Athar."""
import re
import unicodedata

URL_PATTERN = re.compile(r'(?:https?://|www\.)[^\s<>]+', re.IGNORECASE)


def clean_comment(text: str) -> str:
    """Normalisasi teks mentah; pertahankan angka, simbol, dan emoji."""
    if not isinstance(text, str):
        raise TypeError('Komentar harus berupa string.')
    text = unicodedata.normalize('NFKC', text)
    text = ''.join('' if unicodedata.category(c) == 'Cf' else c for c in text)
    text = ''.join(' ' if unicodedata.category(c) == 'Cc' else c for c in text)
    text = URL_PATTERN.sub('<url>', text.lower())
    return re.sub(r'\s+', ' ', text).strip()
