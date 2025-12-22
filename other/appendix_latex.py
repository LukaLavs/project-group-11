import os
import re

# --- nastavitve ---
IMAGE_DIR = "docs/report/appendix"
LATEX_IMAGE_PREFIX = "appendix"  # pot za \includegraphics
OUTPUT_FILE = os.path.join(IMAGE_DIR, "figures_appendix.tex")

# regex za slike
pattern = re.compile(r"graph_(min|max)__n(\d+)_v(\d+)_cM2(\d+)\.png")

images = []

for fname in os.listdir(IMAGE_DIR):
    m = pattern.match(fname)
    if m:
        kind, n, v, cm2 = m.groups()
        images.append({
            "file": fname,
            "kind": kind,
            "n": int(n),
            "v": int(v),
            "cm2": int(cm2),
        })

# sortiranje
images.sort(key=lambda x: (x["kind"], x["n"], x["v"], x["cm2"]))

# layout
IMAGES_PER_FIGURE = 4   # 2x2
IMAGE_WIDTH = 0.48      # 2 na vrstico

latex_lines = []

for i in range(0, len(images), IMAGES_PER_FIGURE):
    chunk = images[i:i + IMAGES_PER_FIGURE]

    latex_lines.append(r"\begin{figure*}[t]")
    latex_lines.append(r"\centering")

    for j, img in enumerate(chunk):
        caption = f"{img['kind']}, $n={img['n']}$, $v={img['v']}$, $\\cM={img['cm2']}$"

        latex_lines.append(rf"\begin{{subfigure}}{{{IMAGE_WIDTH}\textwidth}}")
        latex_lines.append(rf"\includegraphics[width=\linewidth]{{{LATEX_IMAGE_PREFIX}/{img['file']}}}")
        latex_lines.append(rf"\caption{{{caption}}}")
        latex_lines.append(r"\end{subfigure}")

        # razmik med slikami
        if j % 2 == 0:
            latex_lines.append(r"\hfill")
        if j % 2 == 1 and j != len(chunk) - 1:
            latex_lines.append(r"\vspace{2mm}")

    first = i + 1
    last = min(i + IMAGES_PER_FIGURE, len(images))
    latex_lines.append(rf"\caption{{Grafi {first}--{last}}}")
    latex_lines.append(r"\end{figure*}")

# shrani datoteko
with open(OUTPUT_FILE, "w") as f:
    f.write("\n".join(latex_lines))

print(f"figures_appendix.tex uspešno ustvarjen: {OUTPUT_FILE}")
