from enum import Enum
import re
from htmlnode import LeafNode, ParentNode
from textnode import text_node_to_html_node
from split_nodes import text_to_textnodes
import os
class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    final_blocks = []
    for block in blocks:
        clean_block = block.strip()
        if clean_block != "":
            final_blocks.append(clean_block)
    return final_blocks


def block_to_block_type(markdown):
    if re.match(r"^#{1,6} ", markdown):
        return BlockType.HEADING
    if markdown.startswith("```") and markdown.endswith("```"):
        return BlockType.CODE
    lines = markdown.split("\n")
    is_quote = True
    for line in lines:
        if not line.startswith(">"):
            is_quote = False
    if is_quote:
        return BlockType.QUOTE
    is_ul = True
    for line in lines:
        if not line.startswith("- "):
            is_ul = False
            break
    if is_ul:
        return BlockType.UNORDERED_LIST

    is_ol = True
    expected_num = 1
    for line in lines:
        if not line.startswith(f"{expected_num}. "):
            is_ol = False
            break
        expected_num += 1
    if is_ol:
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text) 
    html_nodes = []
    for node in text_nodes:
        html_nodes.append(text_node_to_html_node(node))
        
    return html_nodes

def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph_text = " ".join(lines)
    children = text_to_children(paragraph_text)
    return ParentNode("p", children)
def heading_to_html_node(block):
    level = len(block) - len(block.lstrip('#'))
    text = block.lstrip('#').strip()
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)
def code_to_html_node(block):
    text = block.strip("`")
    if text.startswith("\n"):
        text = text[1:]
        
    code_node = LeafNode("code", text)
    return ParentNode("pre", [code_node])
def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        new_lines.append(line.lstrip("> ").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)
def ulist_to_html_node(block):
    items = []
    for line in block.split("\n"):
        text = line[2:] 
        children = text_to_children(text)
        items.append(ParentNode("li", children))
    return ParentNode("ul", items)
def olist_to_html_node(block):
    items = []
    for line in block.split("\n"):
        text = line.split(". ", 1)[1]
        children = text_to_children(text)
        items.append(ParentNode("li", children))
    return ParentNode("ol", items)

def block_to_html_node(block, block_type):
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
        
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
        
    if block_type == BlockType.UNORDERED_LIST:
        return ulist_to_html_node(block)
        
    if block_type == BlockType.ORDERED_LIST:
        return olist_to_html_node(block)
    
    raise ValueError("Invalid block type")


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        node = block_to_html_node(block, block_type)
        children.append(node)
    return ParentNode("div", children)



def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    raise Exception("NO H1")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    with open(from_path, "r") as f:
        md_content = f.read()
    with open(template_path, "r") as f:
        template_content = f.read()
    md_content = md_content.replace("](/", f"]({basepath}")
    html_nodes = markdown_to_html_node(md_content)
    html_string = html_nodes.to_html()
    
    title = extract_title(md_content)
    
    template_content = template_content.replace("{{ Title }}", title)
    template_content = template_content.replace("{{ Content }}", html_string)
    
    template_content = template_content.replace("{{ BasePath }}", basepath)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(template_content)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        to_path = os.path.join(dest_dir_path, filename)

        if os.path.isfile(from_path):
            if from_path.endswith(".md"):
                dest_html_path = to_path.replace(".md", ".html")
                print(f"Generating page from {from_path} to {dest_html_path}")
                generate_page(from_path, template_path, dest_html_path, basepath) 
        else:
            if not os.path.exists(to_path):
                os.makedirs(to_path)
            generate_pages_recursive(from_path, template_path, to_path, basepath)