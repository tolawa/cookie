from json import load
import os
from argparse import ArgumentParser

from PIL import Image

CELL_DIM = (200, 200)


def image_mat(images, rows, cols):
    canvas = Image.new('RGB', (cols * CELL_DIM[0], rows * CELL_DIM[1]), (255, 255, 255))
    if len(images) != rows * cols:
        raise ValueError()
    for r in range(rows):
        for c in range(cols):
            img = images[r * cols + c]
            y = r * CELL_DIM[1] + (CELL_DIM[1] - img.size[1]) // 2
            x = c * CELL_DIM[0] + (CELL_DIM[0] - img.size[0]) // 2
            canvas.paste(img, (x, y))
    return canvas


def load_image(image_path):
    img = Image.open(image_path)
    x, y = img.size
    ratio = min(CELL_DIM[0] / x, CELL_DIM[1] / y)
    x = int(x * ratio)
    y = int(y * ratio)
    return img.resize((x, y))


def load_dir(dir_path):
    names = os.listdir(dir_path)
    names.sort()
    for name in names:
        img_path = os.path.join(dir_path, name)
        yield load_image(img_path)


def main():
    parser = ArgumentParser()
    parser.add_argument('dirpath', type=str)
    parser.add_argument('dim', type=str)
    parser.add_argument('outpath', type=str)
    args = parser.parse_args()
    cols, rows = args.dim.lower().split('x')
    rows = int(rows)
    cols = int(cols)

    images = list(load_dir(args.dirpath))
    result = image_mat(images, rows, cols)
    result.save(args.outpath)


if __name__ == '__main__':
    main()
