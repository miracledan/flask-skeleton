# using peewee and gevent, belowing must be set. 
# refer to https://github.com/coleifer/flask-peewee/blob/master/docs/gevent.rst
from gevent import monkey; monkey.patch_all()

import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db, assets
from flask.ext.script import Manager, Shell, Command, Option

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def make_shell_context():
    '''add package here for shell debug.'''
    return dict(app=app, db=db)

manager = Manager(app)
manager.add_command("shell", Shell(make_context=make_shell_context))

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    tables = []

    db.drop_tables(tables)
    db.create_tables(tables)

    from app.core.models import mock_all_models
    mock_all_models()

@manager.command
def migrate():
    """Run migrate database tasks."""
    from playhouse.migrate import migrate
    from peewee import CharField, TextField, IntegerField

    migrate(
        # db.migrator.add_column('project', 'shares', IntegerField(default=0)),
    )

if __name__ == '__main__':
    manager.run()

