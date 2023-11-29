from flask import request, render_template, abort
from flask import redirect, url_for
import random
import string

from . import app, db
from .forms import PersonForm
from .models import Loop, Person

@app.route("/loop/new", methods=["GET", "POST"])
def loop_create():
    if request.method == 'POST':
        new_id = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        loop = Loop(
            id = new_id,
            name = request.form["name"]
            )
        db.session.add(loop)
        db.session.commit()
        return redirect(url_for("loop_detail", loop_id=new_id))
    else :
        return render_template("loop/create.html")


@app.route("/loop/<loop_id>/", methods=["GET"])
def loop_detail(loop_id):
    loop = db.get_or_404(Loop, loop_id)
    if not loop:
        abort(404)
    person_form = PersonForm()
    # hey, loop has a special meaning inside jinja templates... 
    return render_template("loop/detail.html",
                           the_loop=loop,
                           person_form=person_form)


@app.route("/loop/<loop_id>/person", methods=["GET", "POST"])
@app.route("/loop/<loop_id>/person/<person_id>", methods=["GET", "POST", "PUT"])
def add_person(loop_id, person_id=None):
    loop = db.get_or_404(Loop, loop_id)
    if person_id :
        person = db.get_or_404(Person, person_id)
        form = PersonForm(name=person.name,
                          email=person.email,
                          avoids=[a.name for a in person.avoids])
    else :
        person = Person(loop=loop)
        form = PersonForm()
    form.avoids.choices = [(a.id, a.name) for a in loop.persons]
    request_partials = request.headers.get("HX-Request")
    if request.method == 'POST':
        if form.validate_on_submit():
            person.name=form.name.data
            person.email=form.email.data
            person.avoids = [db.session.get(Person, pid) for pid in form.avoids.data]
            db.session.add(person)
            db.session.commit()

            app.logger.info("updated//created %s", person)
            return ( render_template("loop/partials/person_details.html", p=person, the_loop=loop)
                    if request_partials
                    else redirect(url_for("loop_detail", loop_id=loop_id)))
        else :
            app.logger.warn("Errors in form:", form.errors)

    # Gettin' or form errors
    template_name = ("loop/partials/person_form.html"
                     if request_partials
                     else "loop/person_form.html")
    
    return render_template(template_name,
                           target=url_for("add_person",
                                          loop_id=loop_id,
                                          person_id=person_id),
                           p = person if person_id else None,
                           person_form=form)


@app.route("/person/<person_id>/avoids", methods=["POST"])
def avoid_person(person_id):
    person = db.session.get(Person, person_id)
    avoid_p = db.session.get(Person, request.form["avoid_person_id"])
    person.avoids.append(avoid_p)
    db.session.add(person)
    db.session.commit()
    return redirect(url_for("loop_detail", loop_id=person.loop.id))
    
                             
