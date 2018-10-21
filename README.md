# ANIE

Platform focused in blind and visually impaired people with objective to transform the NASA satellite images in a audio experience.
Built with Flask, MongoDB hosted in MLab with authentication, interface to create posts and users.

Post can be written in Markdown, for convenience.

Live version in [Umobiteam](http://blog.umobiteam.com/)

### Files tree

###### Root

    app.py : Contain all the Flask app structure, with routes and corresponding functions.

    Database.py: Contain all the operations involving mongodb, hosted in mlab.

    Setup.py: Dependencies.

    models.py: modelos de dados da aplicação

###### /templates

Blog Pages

    blind_template.html : HTML template without unnecessary content for visually impaired people.

    criausuario.html: User creation form.

    editarpublicação.html : Form to edit app posts.

    flash.html :

    index.html : Initial page with posts, record if the user have some visual disability in his first access.

    login.html : Login form.

    notfound.html: 404 page.

    novapublicação.html : Post creation form.

    postagenspendentes.html : Allow to view all not finalized posts, such as missing translations or approve from a community member.

    postview.html: Post visualization page.

    select_type.html :

    template.html : The base template of the application.


###### /static

The static files needed to the template such as CSS and JS scripts.


## Deploy with virtualEnv

Install pip3 if you're using Linux

`sudo apt-get install python3-pip`

When you install Python 3 in Windows it install pip3 too.

Create a virtualenv inside venvspace folder

`virtualenv venvspace`

Activate VirtualEnv

`source venvspace/bin/activate`

Install dependencies on the virtualenv

`python3 Setup.py install`

## Export and run the application

### Linux Script
`chmod 777 run.sh`

`./run.sh`

### Linux
`export FLASK_APP=Api.py`

`Python3 Api.py`

### Windows
`set FLASK_APP=Api.py`

`flask run`
