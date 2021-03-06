from html import escape

from draftjs_exporter.engines.base import DOMEngine

# http://w3c.github.io/html/single-page.html#void-elements
# https://github.com/html5lib/html5lib-python/blob/0cae52b2073e3f2220db93a7650901f2200f2a13/html5lib/constants.py#L560
VOID_ELEMENTS = {
    'area',
    'base',
    'br',
    'col',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
}


class Elt(object):
    def __init__(self, type_, attr, markup=None):
        self.type = type_
        self.attr = attr
        self.children = []
        self.markup = markup

    @staticmethod
    def from_html(markup):
        return Elt('escaped_html', None, markup)


class DOMMarkwdown(DOMEngine):
    """
    Based on https://github.com/springload/draftjs_exporter/blob/main/draftjs_exporter/engines/string.py.
    The implementation is near-identical, except for escaping: no escaping is necessary for Markdown.
    """

    @staticmethod
    def create_tag(type_, attr=None):
        return Elt(type_, attr)

    @staticmethod
    def parse_html(markup):
        return Elt.from_html(markup)

    @staticmethod
    def append_child(elt, child):
        # This check is necessary because the current wrapper_state implementation
        # has an issue where it inserts elements multiple times.
        # This must be skipped for text, which can be duplicated.
        is_existing_ref = isinstance(child, Elt) and child in elt.children
        if not is_existing_ref:
            elt.children.append(child)

    @staticmethod
    def render_attrs(attr):
        return ''.join(sorted([' %s="%s"' % (k, escape(v)) for k, v in attr.items()]))

    @staticmethod
    def render_children(children):
        return ''.join([DOMMarkwdown.render(c) if isinstance(c, Elt) else c for c in children])

    @staticmethod
    def render(elt):
        type_ = elt.type
        attr = DOMMarkwdown.render_attrs(elt.attr) if elt.attr else ''
        children = DOMMarkwdown.render_children(
            elt.children) if elt.children else ''

        if type_ == 'fragment':
            return children

        if type_ in VOID_ELEMENTS:
            return '<%s%s/>' % (type_, attr)

        if type_ == 'escaped_html':
            return elt.markup

        return '<%s%s>%s</%s>' % (type_, attr, children, type_)

    @staticmethod
    def render_debug(elt):
        return DOMMarkwdown.render(elt)
