"""Fichas de referência para comparação manual de sintomas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Doenca:
    nome: str
    especies: tuple[str, ...]
    sintomas: str
    comparar: str
    fonte: str
    foto: str


DOENCAS = {
    "pedrado-macieira": Doenca(
        "Pedrado da macieira", ("Macieira",),
        "Manchas verde-azeitona nas folhas que escurecem. No fruto podem surgir lesões corticosas e fissuras.",
        "Observa a textura das manchas nas folhas e procura lesões também nos frutos.",
        "https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/yard-and-garden-problems/apple-scab",
        "https://extension.umn.edu/sites/extension.umn.edu/files/styles/caption_medium/public/Apple-scab-advanced-leaves-Grabowski.jpg?itok=T4Qvttai",
    ),
    "fogo-bacteriano": Doenca(
        "Fogo bacteriano", ("Macieira", "Pereira"),
        "Escurecimento e murchidão de rebentos. A ponta pode curvar-se em gancho.",
        "Observa se o escurecimento acompanha o rebento e se a ponta está encurvada. Regista também se houve geada recente.",
        "https://blog-fruit-vegetable-ipm.extension.umn.edu/2025/08/fire-blight-in-minnesota.html",
        "https://lh7-rt.googleusercontent.com/docsz/AD_4nXc_c5TaoMIKh0gQU7sgIQ_PdSvLXo55D0i_5A2BSjfFliJyIzcAiRgCG8AmKDKadylK7CdWmELtaisUYELVCP4QmANARkqH4mIexf1UGueQu28WBQnGoQB2yYhZ8xOnjo_bSAqxPw=w640-h244?key=BiM_3GZh5aKkT01lS9Xkhw",
    ),
    "mancha-cerejeira": Doenca(
        "Mancha foliar da cerejeira", ("Cerejeira",),
        "Manchas arroxeadas que se tornam castanhas. O centro pode desprender-se e deixar pequenos buracos.",
        "Os buracos podem ter várias causas. Compara também a cor e a forma das manchas nas folhas.",
        "https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/yard-and-garden-problems/cherry-leaf-spot",
        "https://extension.umn.edu/sites/extension.umn.edu/files/styles/caption_medium/public/Cherry-leaf-spot-onleaf.jpg?itok=E9MTgMpc",
    ),
}
