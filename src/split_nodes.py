from textnode import TextNode, TextType
from extract import extract_markdown_images, extract_markdown_links
def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_list_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_list_nodes.append(node)
            continue

        parts = node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise Exception("Invalid markdown split")

        split_nodes = []
        for index, part in enumerate(parts):
            if part == "":
                continue
            if index % 2 == 0:
                split_nodes.append(TextNode(text=part, text_type=TextType.TEXT))
            else:
                split_nodes.append(TextNode(text=part, text_type=text_type))
        
        new_list_nodes.extend(split_nodes)
    return new_list_nodes



def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        images = extract_markdown_images(node.text)
        if not images:
            new_nodes.append(node)
            continue
        current_text = node.text
        for alt, url in images:
            sections = current_text.split(f"![{alt}]({url})", 1)
            if len(sections) != 2:
                raise ValueError("Błąd składni markdown")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            current_text = sections[1]
        if current_text != "":
            new_nodes.append(TextNode(current_text, TextType.TEXT))
            
    return new_nodes
def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        if not links:
            new_nodes.append(node)
            continue
        current_text = node.text
        for alt, url in links:
            sections = current_text.split(f"[{alt}]({url})")
            if len(sections) != 2:
                raise ValueError("Błąd składni markdown")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.LINK, url))
            current_text = sections[1]
        if current_text != "":
            new_nodes.append(TextNode(current_text, TextType.TEXT))
            
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes
