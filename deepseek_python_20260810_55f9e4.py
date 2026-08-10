# ranking.py
from typing import List, Dict

class Ranking:
    """Ranking de señales por Expected Edge."""

    @staticmethod
    def rank(signals: List[Dict]) -> List[Dict]:
        """Ordena señales por Expected Edge descendente."""
        valid = [s for s in signals if s is not None]
        return sorted(valid, key=lambda x: x['edge'], reverse=True)

    @staticmethod
    def top_n(signals: List[Dict], n: int = 10) -> List[Dict]:
        """Retorna las N mejores señales."""
        ranked = Ranking.rank(signals)
        return ranked[:n]