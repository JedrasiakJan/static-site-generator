from textnode import TextNode, TextType
import os 
import shutil
import sys 
from block_markdown import generate_page, generate_pages_recursive
def kopiarka():
    if os.path.exists("public"):
        shutil.rmtree("public")
    os.mkdir("public")
def rekursywna_kopia(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    for filename in os.listdir(source_dir):
        from_path = os.path.join(source_dir, filename)
        to_path = os.path.join(dest_dir, filename)
        if os.path.isfile(from_path):
            shutil.copy(from_path, to_path)
        else:
            rekursywna_kopia(from_path, to_path)


def main():
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    
    output_dir = "docs"
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)
    
    rekursywna_kopia("src/static", output_dir)
    
    generate_pages_recursive("content", "template.html", output_dir, basepath)

if __name__ == "__main__":
    main()