#!flask/bin/python
import argparse
import os

parser = argparse.ArgumentParser(
    description='This is a managmnet script for flaskCamel app.'
)
parser.add_argument(
    '-c',
    '--create',
    help='Creates Database',
    required=False,
    action='store_true',
)
parser.add_argument(
    '-s',
    '--schemamigration',
    help='Creates new migration',
    required=False,
    action='store_true',
)
parser.add_argument(
    '-m',
    '--migrate',
    help='Migrate database forward',
    required=False,
    action='store_true',
)
parser.add_argument(
    '-d',
    '--downgrade',
    help='Migrates database backwards',
    required=False,
    action='store_true',
)
parser.add_argument(
    '-p',
    '--purge',
    help='Purges database',
    required=False,
    action='store_true',
)
parser.add_argument(
    '--settings',
    help='Provide path to settings file',
    required=False,
)
args = parser.parse_args()

# configure app if necessary
if args.settings:
    os.environ['FLASKCAMEL_SETTINGS'] = args.settings

# decide what action to take
from flaskcamel import app, db

if args.create:
    from migrate.versioning import api
    import os.path
    db.create_all()
    if not os.path.exists(app.config['SQLALCHEMY_MIGRATE_REPO']):
        api.create(
            app.config['SQLALCHEMY_MIGRATE_REPO'], 'database repository'
        )
        api.version_control(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO']
        )
    else:
        api.version_control(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO'],
            api.version(app.config['SQLALCHEMY_MIGRATE_REPO'])
        )

elif args.schemamigration:
    import imp
    from migrate.versioning import api
    migration = '%s/versions/%03d_migration.py' % (
        app.config['SQLALCHEMY_MIGRATE_REPO'],
        api.db_version(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO']
        ) + 1
    )
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO'],
        tmp_module.meta,
        db.metadata
    )
    open(migration, "wt").write(script)
    api.upgrade(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    print 'New migration saved as ' + migration
    print 'Current database version: ' + str(
        api.db_version(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO']
        )
    )

elif args.migrate:
    from migrate.versioning import api
    api.upgrade(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    print 'Current database version: ' + str(
        api.db_version(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO']
        )
    )

elif args.downgrade:
    from migrate.versioning import api
    v = api.db_version(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO']
    )
    api.downgrade(
        app.config['SQLALCHEMY_DATABASE_URI'],
        app.config['SQLALCHEMY_MIGRATE_REPO'],
        v - 1
    )
    print 'Current database version: ' + str(
        api.db_version(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config['SQLALCHEMY_MIGRATE_REPO']
        )
    )

elif args.purge:
    db.drop_all()
    print 'Dropped all tables'

else:
    if __name__ == '__main__':
        app.run(debug=app.config['DEBUG'])
        #app.run(host='0.0.0.0')
