from textnode import TextNode, TextType
import os 
import shutil

def kopiarka():
    if os.path.exists("public"):
        shutil.rmtree("public")
    os.mkdir("public")
def rekursywna_kopia(source_dir, dest_dir):
    if not os.path.exists(source_dir):
        return
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    for filename in os.listdir(source_dir):
        from_path = os.path.join(source_dir, filename)
        to_path = os.path.join(dest_dir, filename)
        if os.path.isfile(from_path):
            print(f"Kopiuję plik: {from_path} -> {to_path}")
            shutil.copy(from_path, to_path)
        else:
            print(f"Kopiuję folder: {from_path} -> {to_path}")
            rekursywna_kopia(from_path, to_path)


def main():
    kopiarka()
    rekursywna_kopia("src/static", "public")
if __name__ == "__main__":
    main()
