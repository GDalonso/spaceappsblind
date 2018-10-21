from flask import Flask, render_template, request, redirect, session, flash, url_for
from Database import dbinsert,dbretrieveusuario, dbinsertusuario, dbretrievepost, dbretrievecategoria, \
    removepost, dbretrievenotaprovados
from werkzeug.security import check_password_hash
from markdown import markdown
from models import BlogPost, User
from Database import dbretrieve
from flask_compress import Compress
import os

# Configura a aplicação, os diretorios de CSS, JS, Imagens e fontes
app = Flask(__name__, template_folder='templates', static_folder='static')
# Define uma chave para o HEROKU
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'WYZ')

# GZIP - Utilizado para compactar a pagina
gzip = Compress(app)

# Index page
@app.route('/')
def index():
    posts = []
    if request.args.get('type_user') and not 'type_user' in session.keys():
        session['type_user'] = request.args.get('type_user')
    else:
        user = session['user_logged'] if 'user_logged' in session.keys() else None
        posts = dbretrieve()
        if 'type_user' in session.keys() and session['type_user'] == 'not_blind':
            user = session['user_logged'] if 'user_logged' in session.keys() else None
            return render_template('index.html', titulo="Anie", posts=posts, user=user, type=False)
        elif 'type_user' in session.keys() and session['type_user'] == 'blind':
            if session['type_user'] == 'blind':
                for b in posts:
                    b['imagemPost'] = 'https://s3.amazonaws.com/hackultura/placeholder.png'
            user = session['user_logged'] if 'user_logged' in session.keys() else None
            return render_template('index.html', titulo="Anie", posts=posts, user=user, blind=True)

    return render_template('select_type.html', titulo="Anie")

@app.route('/postagens')
def postlist():
        postagens = dbretrievenotaprovados()
        return render_template('postagenspendentes.html', titulo='Postagens pendentes', posts=postagens, blind=True if session['type_user'] == 'blind' else False)

@app.route('/post/<_postid>')
def postview(_postid: str):
    '''
    :param _postid: Post id in database
    :return: Render the post with given id to the user
    '''
    post = dbretrievepost(_postid)
    local_post = BlogPost(nomePost=post['nomePost'], conteudoPost=post['conteudoPost'],
                descPost=post['descPost'], categoriaPost=post['categoriaPost'],
                imagemPost=post['imagemPost'] if session['type_user'] == 'not_blind' else 'https://s3.amazonaws.com/hackultura/placeholder.png', dataPost=post['dataPost'])
    user = session['user_logged'] if 'user_logged' in session.keys() else None
    return render_template('postview.html', titulo=post['nomePost'], post=local_post, user=user, blind=True if session['type_user'] == 'blind' else False)

@app.route('/categoria/<_category>')
def categorie(_category: str):
    '''

    :param _category: string name if a category
    :return: The categories view with the posts by that category
    '''

    postsincategory = dbretrievecategoria(_category)
    if postsincategory:
        user = session['user_logged'] if 'user_logged' in session.keys() else None
        return render_template('categorie.html', titulo=_category, posts=postsincategory, user=user, blind=True if session['type_user'] == 'blind' else False)
    else:
        return render_template('notfound.html')

# Login related
@app.route('/login')
def formlogin():
    '''
    present to the user the login screen
    '''

    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

#Verify user password when logging in
def check_password(mongouser, password):
    return check_password_hash(mongouser['pw_hash'], password)

@app.route('/autenticar', methods=['POST', ])
def authenticatelogin():
    '''
    Verify the user and passwords inputed in the login page
    '''

    usuario = dbretrieveusuario(request.form['usuario'])

    if usuario:
        if check_password(usuario, request.form['senha']):
            session['user_logged'] = usuario["username"]
            flash(usuario["username"] + ' is now logged!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    # Show the error message if login fails
    flash('Senha ou usuário incorretos, tente novamente.')
    return redirect(url_for('formlogin'))

@app.route('/logout')
def logout():
    '''
    Nullify the logged user
    '''

    session['user_logged'] = None
    flash('You need to log in to see this page!')
    return redirect(url_for('index'))

@app.route('/novousuario')
def formcreateuser():
    '''
    Shows the new user creation screen to the user
    '''
    return render_template('criausuario.html', titulo='Novo usuario')


@app.route('/criarusuario', methods=['POST',])
def createuser():
    '''
    Create a User with the create user form contents
    '''

    # Form contents
    nomeusuario = request. form['nomeusuario']
    senha = request. form['senha']
    nomedisplay = request. form['nomedisplay']
    usuario = User(nomeusuario, nomedisplay, senha)

    # Insert the object converted to dict in the database
    dbinsertusuario(usuario.__dict__)

    # Dynamic route to the index function
    return redirect(url_for('index'))

#DELETE SHIT

@app.route('/remover/<_postid>')
def deletepost(_postid: str):
    '''
    Remove the post with the given id from the database
    :param _postid: Id of a post to be removed from database
    '''

    if 'user_logged' not in session or session['user_logged'] == None:
        # Dynamic route to the login function
        return redirect(url_for('formlogin', proxima=url_for('index')))

    removepost(_postid)
    return postlist()

# CRUDs
@app.route('/novo')
def formcreatepost():
    '''
    Show the view to create a new post
    '''

    if 'user_logged' not in session or session['user_logged'] == None:
        #build a dynamic url to the login function if user if not logged in
        return redirect(url_for('formlogin', proxima=url_for('formlogin')))
    return render_template('novapublicacao.html', titulo='Nova publicação')

@app.route('/criar', methods=['POST',])
def createpost():
    '''
    Create a new post object in the database with the form contents
    '''

    #Contents of the form
    nomePost = request.form['nomePost']
    conteudoPost = markdown(request.form['conteudoPost']).replace('<img alt', '<img style="max-width: 70%;" alt')
    descPost = request.form['descPost']
    categoriaPost = request.form['categoriaPost']
    imagemPost = request.form['imagemPost']
    post = BlogPost(nomePost=nomePost, conteudoPost=conteudoPost, descPost=descPost, categoriaPost=categoriaPost, imagemPost=imagemPost)

    #Insert the object converted to dict in the database
    dbinsert(post.__dict__)

    #Dynamic route to the index function
    return redirect(url_for('index'))

@app.route('/editar/<_postid>')
def editar(_postid: str):
    '''

    :param _postid: Post id in database
    :return: Render the post with given id to the user
    '''

    post = dbretrievepost(_postid)
    local_post = BlogPost(nomePost=post['nomePost'], conteudoPost=post['conteudoPost'],
                descPost=post['descPost'], categoriaPost=post['categoriaPost'],
                imagemPost=post['imagemPost'] if session['type_user'] == 'not_blind' else 'https://s3.amazonaws.com/hackultura/placeholder.png', dataPost=post['dataPost'])
    user = session['user_logged'] if 'user_logged' in session.keys() else None

    return render_template('editarpubicação.html', titulo=post['nomePost'], post=local_post, user=user, blind=True if session['type_user'] == 'blind' else False)

if __name__ == '__main__':
    app.run()


