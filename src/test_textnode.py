import unittest
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode, LeafNode, ParentNode
from split_nodes import split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes
from extract import extract_markdown_images, extract_markdown_links
from block_markdown import markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node, extract_title
class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    def test_eq_url(self):
        # Sprawdzamy równość z URL
        node = TextNode("Link", TextType.LINK, "https://boot.dev")
        node2 = TextNode("Link", TextType.LINK, "https://boot.dev")
        self.assertEqual(node, node2)

    def test_not_eq(self):
        # Sprawdzamy czy różne typy są różne
        node = TextNode("Text", TextType.TEXT)
        node2 = TextNode("Text", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_url(self):
        # Sprawdzamy czy różne URL sprawiają, że obiekty są różne
        node = TextNode("Link", TextType.LINK, "https://boot.dev")
        node2 = TextNode("Link", TextType.LINK, "https://google.com")
        self.assertNotEqual(node, node2)
    def test_props_to_html(self):
        node = HTMLNode(
            tag="a", 
            props={"href": "https://www.google.com", "target": "_blank"}
        )
        self.assertEqual(
            node.props_to_html(), 
            ' href="https://www.google.com" target="_blank"'
        )
    def test_values(self):
        node = HTMLNode("div", "Hello, world!")
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello, world!")
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {})
    def test_repr(self):
        node = HTMLNode("h1", "Title", None, {"class": "primary"})
        # Sprawdź czy repr zwraca oczekiwany string
        self.assertEqual(
            repr(node), 
            "HTMLNode(h1, Title, [], {'class': 'primary'})"
        )
    def test_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    # Testowanie z atrybutami (props)
    def test_to_html_link(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    # Testowanie przypadku, gdy tag jest None (ma zwrócić tylko surowy tekst)
    def test_to_html_no_tag(self):
        node = LeafNode(None, "Just raw text")
        self.assertEqual(node.to_html(), "Just raw text")

    # Testowanie, czy wywala błąd, gdy nie ma wartości (ValueError)
    def test_to_html_no_value_raises_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    # Testowanie z wieloma atrybutami
    def test_to_html_multiple_props(self):
        node = LeafNode("div", "Content", {"class": "container", "id": "main"})
        # Kolejność atrybutów może zależeć od wersji Pythona, ale słowniki
        # od wersji 3.7+ zachowują kolejność dodawania
        self.assertEqual(node.to_html(), '<div class="container" id="main">Content</div>')

    # Test podstawowy z jednym dzieckiem
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    # Test zagnieżdżenia (rekurencja)
    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    # Test wielu dzieci na tym samym poziomie
    def test_to_html_many_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
            ],
        )
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i></p>")

    # Test z atrybutami (props)
    def test_to_html_with_props(self):
        node = ParentNode(
            "div",
            [LeafNode("b", "Bold")],
            {"class": "container", "id": "main"},
        )
        self.assertEqual(node.to_html(), '<div class="container" id="main"><b>Bold</b></div>')

    # Test braku dzieci (powinien rzucić ValueError)
    def test_to_html_no_children(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError):
            node.to_html()

    # Test braku tagu (powinien rzucić ValueError)
    def test_to_html_no_tag(self):
        node = ParentNode(None, [LeafNode("b", "Bold")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_link(self):
        node = TextNode("Click me", TextType.LINK, "https://boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props, {"href": "https://boot.dev"})

    def test_delimiter_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[1].text, "code block")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[2].text, " word")

    # 2. Test dla pogrubienia (wiele wystąpień)
    def test_delimiter_bold(self):
        node = TextNode("This is **bold** and **more bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(new_nodes), 4) # 4, bo mamy 2 "boldy" i 2 "texty" między nimi
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[3].text_type, TextType.BOLD)

    # 3. Test dla kursywy
    def test_delimiter_italic(self):
        node = TextNode("_italic_", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text_type, TextType.ITALIC)

    # 4. Test błędu składni (niedomknięty delimiter)
    def test_delimiter_missing_closing(self):
        node = TextNode("This is `broken code", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "`", TextType.CODE)

    # 5. Test pomijania węzłów, które nie są typu TEXT
    def test_delimiter_ignores_non_text(self):
        node = TextNode("Already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0].text_type, TextType.BOLD)

    def test_extract_markdown_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        expected = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")
        ]
        self.assertListEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        expected = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev")
        ]
        self.assertListEqual(extract_markdown_links(text), expected)

    def test_no_links_or_images(self):
        text = "To jest zwykły tekst bez linków."
        self.assertListEqual(extract_markdown_images(text), [])
        self.assertListEqual(extract_markdown_links(text), [])

    def test_mixed_content(self):
        # Sprawdzamy czy regex rozróżnia obrazek od linku (ten wykrzyknik na początku)
        text = "![image](https://img.com) [link](https://link.com)"
        self.assertEqual(extract_markdown_images(text), [("image", "https://img.com")])
        self.assertEqual(extract_markdown_links(text), [("link", "https://link.com")])


    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and [another](https://google.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.LINK, "https://google.com"),
            ],
            new_nodes,
        )

    def test_split_no_images(self):
        node = TextNode("No images here", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_image_at_start(self):
        node = TextNode("![start](https://test.com) is the beginning", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("start", TextType.IMAGE, "https://test.com"),
                TextNode(" is the beginning", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_simple(self):
        text = "Just plain text"
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just plain text", TextType.TEXT)]
        self.assertEqual(nodes, expected)



    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_excessive_newlines(self):
        md = """
# Heading





This is a paragraph
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Heading",
                "This is a paragraph",
            ],
        )

    def test_markdown_to_blocks_empty_input(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_whitespace(self):
        md = "   \n\n   \n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])



    def test_block_to_block_types(self):
        # Heading
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        
        # Code
        block = "```\ncode block\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
        
        # Quote
        block = "> this is a\n> quote block"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
        
        # Unordered List
        block = "- item 1\n- item 2"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
        
        # Ordered List
        block = "1. item 1\n2. item 2"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
        
        # Paragraph (domyślny)
        block = "This is just a normal paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_invalid_ordered_list(self):
        # Lista zaczynająca się od 2 powinna być akapitem
        block = "2. item 1\n3. item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
        
    def test_invalid_unordered_list(self):
        # Brak spacji po myślniku
        block = "-item 1\n-item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_extract_title(self):
        # Sprawdzenie poprawnego działania
        markdown = "# Tolkien Fan Club"
        self.assertEqual(extract_title(markdown), "Tolkien Fan Club")

    def test_extract_title_with_extra_spaces(self):
        # Sprawdzenie czy strip działa (usuwanie spacji wokół)
        markdown = "#    Tolkien Fan Club    "
        self.assertEqual(extract_title(markdown), "Tolkien Fan Club")

    def test_extract_title_no_header(self):
        # Sprawdzenie czy wyrzuca błąd, gdy brak #
        markdown = "To jest tylko paragraf bez nagłówka"
        with self.assertRaises(Exception):
            extract_title(markdown)

    def test_extract_title_multiple_headers(self):
        # Sprawdzenie czy wyłapuje tylko pierwszy napotkany #
        markdown = "# Pierwszy\n## Drugi"
        self.assertEqual(extract_title(markdown), "Pierwszy")
if __name__ == "__main__":
    unittest.main()