# Chakra Petch

Bold Italic (700), served locally as WOFF2 for player-card scores and goalie save percentages through `--font-sport`.

Source: [Google Fonts](https://fonts.google.com/specimen/Chakra+Petch), [original font](https://github.com/google/fonts/blob/main/ofl/chakrapetch/ChakraPetch-BoldItalic.ttf).
The SIL Open Font License is included in `OFL.txt`.

Subset from the original TTF with FontTools to Latin and Latin-1 characters plus the en dash, euro sign and minus sign:

```bash
pyftsubset ChakraPetch-BoldItalic.ttf --unicodes=U+0020-007E,U+00A0-00FF,U+2013,U+20AC,U+2212 --flavor=woff2 --output-file=chakra-petch-bold-italic-latin.woff2
```
