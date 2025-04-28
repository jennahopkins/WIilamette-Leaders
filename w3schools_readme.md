# 👋 Hello developer!

This project serves as an example of what can be achieved. It is not a fully functional product. Feel free to use the source code and ideas as a starting point for your own projects.

This is one of the many templates available from W3Schools. Check our [tutorials for frontend development](https://www.w3schools.com/where_to_start.asp) to learn the basics of [HTML](https://www.w3schools.com/html/default.asp), [CSS](https://www.w3schools.com/css/default.asp) and [JavaScript](https://www.w3schools.com/js/default.asp). 🦄  
Also check [Python](https://www.w3schools.com/python/) and [Django](https://www.w3schools.com/django/) tutorials to grasp the backend of this template.

## Knowledge requirements

To be able to fully understand and modify this template to your needs, there are several things you should know (or learn):

- [HTML](https://www.w3schools.com/html/default.asp)
- [CSS](https://www.w3schools.com/css/default.asp)
- [JavaScript](https://www.w3schools.com/js/default.asp)
- [Python](https://www.w3schools.com/python/)
- [Django](https://www.w3schools.com/django/)
- [SQLite](https://www.sqlite.org/docs.html)
- [Google reCAPTCHA v3](https://developers.google.com/recaptcha/docs/v3)

If you want to customize the editor:

- [Django-CKEditor](https://django-ckeditor.readthedocs.io/en/latest/)
- [CKEditor4](https://ckeditor.com/docs/ckeditor4/latest/)

## Warning - environment variables

Do not change DATABASE_URL and SECRET_KEY, as these are generated. If they are changed the space may not behave as predicted.
**Remember to switch DEBUG to false when going to production**

## 🔨 What's next?

Customize this template to make it your own.  
Remember to make your layout responsive - if you want your site to look good on smaller screens like mobile.  

## 🎨 Where to find everything?

This template is made by using several technologies.  
Below are explanations about where to find specific code.

### HTML

HTML files are stored in a folder called `templates`. Files have `.html` extension.
In `templates/base.html` you can add your external links and scripts, or change other meaningful things that is relevant on every page.
You can find other templates in `templates/`.

### CSS and Static Images

CSS files can be found in `/blog/static/css`.  
Icons and seeding images are stored in `/blog/static/img`.  

### Core files

You can find:
  - views in `blog/views.py`.
  - local URL configuration in `blog/urls.py`.
  - global URL configuration in `blog_template/urls.py`.
  - models (for tables) in `blog/models.py`.
  - utilities in `blog/utilities.py`.
  - static files in `blog/static/`.
  - decorators in `blog/decorators/`.
  - settings in `blog_template/settings.py`.

## Database

Dynamic spaces can use [SQLite](https://www.sqlite.org/docs.html) database.  
The database file is called `database.db`. It is placed inside the `w3s-dynamic-storage` folder.  
SQLite connection path to the database is `sqlite:///w3s-dynamic-storage/database.db` which you can use to connect to the SQLite database programmatically.   
For this template, the database connection path can also be found in the environment.  
You can modify the tables in `models.py` inside `blog`. Remember to run the commands for `makemigrations` and `migrate` when you change the models. 

---  
**Do not change the `w3s-dynamic-storage` folder name or `database.db` file name!**  
**By changing the `w3s-dynamic-storage` folder name or `database.db` file name, you risk the space not working properly.**

## Setup and start the project
### Generate admin user account

Superuser is an administration user account that will have access to administrative actions, such as
  - edit about blog content
  - create new article
  - edit existing article
  - delete articles
  - delete article comments

To create a superuser you have to run this command: `python manage.py createsuperuser`.  
It will prompt you to enter user data in the terminal:
- Username
- Email address
- Password
- Confirm password

**To change password of an existing admin user, run the following command: `python manage.py changepassword [username]`**.
**To change username of an existing user, run the following command `python manage.py changeusername [username]`**
**To list existing users, run the following command `python manage.py listusers`**
If you forget your username, feel free to create another admin account or use the command `listusers`.

## Enter in administration

Administration login is hidden from other users.  
Route to the administrator mode login can be found in your environment variables under `LOGIN_ROUTE_PATH` variable.
Example: `https://your-space.w3spaces.com/LOGIN_ROUTE_PATH`

## Google reCAPTCHA v3

**To make this template completely functional, you need to generate your own SITE key and SECRET key for Google reCAPTCHA and add them in your template.**

To do that, first, familiarize yourself with [Google reCAPTCHA v3](https://developers.google.com/recaptcha/docs/v3).  
Then go to the [reCAPTCHA admin site](https://www.google.com/recaptcha/admin). Here you will be asked to log in if you are not already.

### Label

Label is a name or an alias for your set of keys.

### reCAPTCHA type

Choose `reCAPTCHA v3` from the list of options. V2 is arguably obsolete.

### Domains

Add your space domain e.g. `your-space-id.w3spaces.com`.

### Submit the form

Read and accept the reCAPTCHA Terms of Service and submit the form.  
After that you should be able to see your set of keys that you need to add to your project.

### Add SECRET key and SITE key

Open settings by clicking on the gear icon in the upper right corner.
**NOTE:** These settings are inaccessible on mobile. Enable desktop mode in your browser settings.
Under the Environment tab change:
  - `RECAPTCHA_SECRET_KEY`
    - add your reCAPTCHA secret key
  - `RECAPTCHA_SITE_KEY`
    - add your reCAPTCHA site key

If you wish to deactivate reCAPTCHA for any reason you are free to do so. You will need to change some code in templates/article.html and templates/login.html.

## Misc: 
  - `python3 manage.py makemigrations`
    - If you change the models you have to run this command and then migrate to commit the changes.
  - `python3 manage.py migrate`
    - Migrate is needed to put the model changes into effect after making migrations. This will create new tables which means you may have conflicts to already stored data. In that case Django will ask in the terminal what you would like to do. This is the message:
      `It is impossible to add a non-nullable field <name> to <model> without specifying a default`. This is because the database needs something to populate existing rows.
      Please select a fix:
      1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
      2) Quit and manually define a default value in models.py.
      Select an option: `
    You avoid this by setting a default when you add the field to the model. E.g. `title = models.CharField(("title"), max_length=250)`

## 🔨 Please note
For now files created/uploaded or edited from within the terminal view will not be backed up or synced. 

## ⛑ Need support?
[Join our Discord community](https://discord.gg/6Z7UaRbUQM) and ask questions in the **#spaces-general** channel to get your space on the next level.  
[Send us a ticket](https://support.w3schools.com/hc/en-gb) if you have any technical issues with Spaces.

Happy learning!