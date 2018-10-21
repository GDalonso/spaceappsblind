from werkzeug.security import generate_password_hash
import datetime
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from flask import Markup

class User:
    def __init__(self, username, nome, senha):
        self.username = username
        self.nome = nome
        self.set_password(senha)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

oembed_providers = bootstrap_basic(OEmbedCache())

class BlogPost:
    def __init__(self, nomePost, conteudoPost, descPost, categoriaPost,
                 imagemPost=None, dataPost=None, aprovado=False):
        self.nomePost = nomePost
        self.conteudoPost = conteudoPost
        self.descPost = descPost
        self.categoriaPost = categoriaPost
        self.imagemPost = imagemPost
        self.dataPost = dataPost if dataPost else datetime.datetime.now()
        self.aprovado = aprovado

    @property
    def html_content(self):
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.conteudoPost, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True)
        return Markup(oembed_content)
