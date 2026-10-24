"""API FastAPI de ShopPulse. Les endpoints des modèles seront ajoutés au lot 5."""

from fastapi import FastAPI

from shoppulse import __version__

app = FastAPI(
    title="ShopPulse API",
    description="Prédiction du retard de livraison et du sentiment des avis.",
    version=__version__,
)


@app.get("/health", tags=["monitoring"])
def health() -> dict[str, str]:
    """Vérifie que l'API répond."""
    return {"status": "ok", "version": __version__}
