"""Stock-style construction icon sizes; width follows vehicle length."""
def construction_sizes(width):
    assert width > 0 and width % 2 == 0
    compact = max(2, 2 * round(width * .36 / 2))
    return [('icon_small@2x', (width, 112)), ('icon_small', (width//2, 56)),
            ('icon20@2x', (compact, 40)), ('icon20', (compact//2, 20))]
