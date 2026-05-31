class HTMLNode():
    def __init__(self, tag: str = None, value: str = None, children: list = None, props: dict = None):
        self.tag = tag
        self.value = value
        self.children = children if children is not None else []
        self.props = props if props is not None else {}
    def to_html(self):
        raise NotImplementedError("to_html method not implemented")
    def props_to_html(self):
        if not self.props:
            return ""
        props_string = ""
        for key, value in self.props.items():
            props_string += f' {key}="{value}"'
        return props_string
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, children=None, props=props)
    def to_html(self):
        if self.value is None:
            raise ValueError("no value in value")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"    
    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, value=None, children=children, props=props)
    def to_html(self):
        if self.tag == None:
            raise ValueError("no tag")
        if self.children is None or len(self.children) == 0:
            raise ValueError("ParentNode must have children")
        children_html = ""
        for child in self.children:
            children_html += child.to_html()
            
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"