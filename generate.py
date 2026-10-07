#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图库自动生成脚本
目录结构示例：
  images/
    LoveLive!/
      cover.jpg          ← 可选：直接放在一级目录的图片会当主图
      南小鸟/
        AA61.jpg
        AA62.jpg
"""
import os
import json
import re
from pathlib import Path

IMAGES_DIR = "images"
OUTPUT_FILE = "data.js"
SUPPORTED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def natural_sort_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]


def collect_images(folder):
    """收集文件夹内的图片（不含子文件夹）"""
    files = [f.name for f in folder.iterdir()
             if f.is_file() and f.suffix.lower() in SUPPORTED_EXT]
    files.sort(key=natural_sort_key)
    return files


def scan_gallery(root):
    data = {}
    if not root.exists():
        print(f"❌ 找不到图片目录：{root.resolve()}")
        print("请先创建 images 文件夹并放入图片")
        return data

    for cat_dir in sorted(root.iterdir(), key=lambda x: x.name.lower()):
        if not cat_dir.is_dir():
            continue
        cat_name = cat_dir.name
        subs = {}

        # 1. 扫描二级分类（角色文件夹）
        for sub_dir in sorted(cat_dir.iterdir(), key=lambda x: x.name.lower()):
            if not sub_dir.is_dir():
                continue
            imgs = collect_images(sub_dir)
            if not imgs:
                print(f"⚠️  跳过空文件夹：{cat_name}/{sub_dir.name}")
                continue
            paths = [f"{IMAGES_DIR}/{cat_name}/{sub_dir.name}/{i}" for i in imgs]
            subs[sub_dir.name] = {
                "cover": paths[0],
                "images": paths
            }
            print(f"✓ {cat_name} / {sub_dir.name}  →  {len(imgs)} 张")

        # 2. 一级目录下直接放的图片 → 作为该分类的主图(cover)
        top_imgs = collect_images(cat_dir)
        top_cover = None
        if top_imgs:
            top_cover = f"{IMAGES_DIR}/{cat_name}/{top_imgs[0]}"
            print(f"★ {cat_name} 主图 → {top_imgs[0]}")

        if subs:
            entry = {"subcategories": subs}
            if top_cover:
                entry["cover"] = top_cover   # 有专用主图就用专用的
            data[cat_name] = entry
        elif top_imgs:
            # 没有二级目录，一级目录下的图片就是相册
            paths = [f"{IMAGES_DIR}/{cat_name}/{i}" for i in top_imgs]
            data[cat_name] = {
                "cover": paths[0],
                "images": paths
            }
            print(f"✓ {cat_name}  →  {len(top_imgs)} 张（无二级）")

    return data


def main():
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    print("=" * 50)
    print("开始扫描图片目录...")
    print(f"工作目录：{script_dir}")
    print("=" * 50)

    gallery_data = scan_gallery(Path(IMAGES_DIR))

    if not gallery_data:
        print("\n没有找到任何图片，请检查目录结构。")
        input("\n按回车键退出...")
        return

    js = "// 本文件由 generate.py 自动生成，请勿手动修改\n"
    js += "// 重新运行 python generate.py 即可更新\n\n"
    js += "const galleryData = "
    js += json.dumps(gallery_data, ensure_ascii=False, indent=2)
    js += ";\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js)

    total_cats = len(gallery_data)
    total_subs = 0
    total_imgs = 0
    for v in gallery_data.values():
        if "subcategories" in v:
            total_subs += len(v["subcategories"])
            for s in v["subcategories"].values():
                total_imgs += len(s["images"])
        else:
            total_imgs += len(v.get("images", []))

    print("=" * 50)
    print(f"✅ 生成完成！")
    print(f"   一级分类：{total_cats} 个")
    print(f"   二级分类：{total_subs} 个")
    print(f"   图片总数：{total_imgs} 张")
    print(f"   输出文件：{OUTPUT_FILE}")
    print("=" * 50)
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
