from nose.tools import *
from turbogears import config
from pkgdb.lib.test import slow, DBTest, current
from subprocess import Popen, PIPE
import sys

class TestPkgDBSyncYum(DBTest):

    def _clean_db(self):
        from pkgdb.model import Collection
        try:
            self.session.rollback()
        except:
            pass
        self.session.begin()
        conn = self.session.connection(Collection)
        conn.execute("DELETE FROM packagebuild")
        conn.execute("DELETE FROM collection")
        conn.execute("DELETE FROM repos")
        conn.execute("DELETE FROM package")
        conn.execute("DELETE FROM binarypackages")
        conn.execute("DELETE FROM applications")
        conn.execute("DELETE FROM tags")
        conn.execute("DELETE FROM comments")
        conn.execute("DELETE FROM usages")
        conn.execute("DELETE FROM executables")
        self.session.commit()

    def tearDown(self):
        self._clean_db()
        super(TestPkgDBSyncYum, self).tearDown()

    def _create_testing_active_collection(self):
        from pkgdb.model import Collection, SC_ACTIVE
        coll = Collection('Testing', '14', SC_ACTIVE, 'owner', 'master', '.f14')
        self.session.add(coll)
        return coll

    def _create_testing_devel_collection(self):
        from pkgdb.model import Collection, SC_UNDER_DEVELOPMENT
        coll = Collection('Testing', 'devel', SC_UNDER_DEVELOPMENT, 'owner', 'master', '.devel')
        self.session.add(coll)
        return coll

    def _create_eol_collection(self):
        from pkgdb.model import Collection, SC_EOL
        coll = Collection('Old', '1', SC_EOL, 'owner', 'o1', '.o1')
        self.session.add(coll)
        return coll

    def _create_testing_devel_active_repo(self):
        from pkgdb.model import Repo
        import pkgdb
        repo = Repo('Testing Devel', 'devel', '../tests/repo-minimal/', 
            'file://%s/'%pkgdb.__path__[0], True, None)
        self.session.add(repo)
        return repo

    def _create_testing_devel_basic_repo(self):
        from pkgdb.model import Repo
        import pkgdb
        repo = Repo('Testing Basic', 'devel', '../tests/repo-basic/', 
            'file://%s/'%pkgdb.__path__[0], True, None)
        self.session.add(repo)
        return repo

    def _create_inactive_repo(self):
        from pkgdb.model import Repo
        import pkgdb
        repo = Repo('Old 1', 'O-1', '../tests/repo-old/', 
            'file://%s/'%pkgdb.__path__[0], False, None)
        self.session.add(repo)
        return repo

    def _create_test_minimal_package(self):
        from pkgdb.model import Package, SC_APPROVED
        pkg = Package('test-minimal', 'old summary', SC_APPROVED, 'old description')
        self.session.add(pkg)
        return pkg

    def _create_pkg_listing(self, pkg, coll):
        from pkgdb.model import PackageListing, SC_APPROVED
        self.session.flush()
        pkg_listing = PackageListing('owner', SC_APPROVED, packageid=pkg.id, collectionid=coll.id)
        self.session.add(pkg_listing)
        return pkg_listing

    def _create_build(self, pkg):
        from pkgdb.model import PackageBuild, BinaryPackage
        build = PackageBuild('test-minimal', None, 0, '0.0', '0', 'i386', 0, 'GPL', '', '1990-01-01', 'committer')
        build.package = pkg
        self.session.add(build)
        binary_package = BinaryPackage('test-minimal')
        self.session.add(binary_package)
        return build
        
    def _setup_update_with_eol_repo(self):
        self.session.begin()

        coll = self._create_testing_active_collection()
        dev_repo = self._create_testing_devel_active_repo()
        coll.repos.append(dev_repo)

        old_coll = self._create_eol_collection()
        old_repo = self._create_inactive_repo()
        old_coll.repos.append(old_repo)

        pkg = self._create_test_minimal_package()
        pkg_listing = self._create_pkg_listing(pkg, coll)
        old_pkg_listing = self._create_pkg_listing(pkg, old_coll)

        build = self._create_build(pkg)
        build.repos.append(old_repo)

        self.session.commit()


    def _test_update_skip_inactive(self):
        msg = """
        FEATURE: As PkgDB Admin I want to have build records for just the builds being available
                 in the active repos
        FAILURE: %s 
        """
        from pkgdb.model import PackageBuild
        self._setup_update_with_eol_repo()

        output = Popen(['server-scripts/pkgdb-sync-yum', '--verbose', '-c', 'test.cfg', 'update', '--skip-inactive'], stdout=PIPE).communicate()[0]
        print output

        build_cnt = self.session.query(PackageBuild).filter_by(version='0.0', release='0').count()
        assert_equals(build_cnt, 1, msg % 'Builds from inactive repos were cleaned')

        self.session.rollback()
        self._clean_db()
   

    def _test_update_clean_builds(self):
        msg = """
        FEATURE: As PkgDB Admin I want to have build records for just the builds being available
                 in the active repos.
        FAILURE: %s
        """
        from pkgdb.model import PackageBuild
        self._setup_update_with_eol_repo()

        output = Popen(['server-scripts/pkgdb-sync-yum', '--verbose', '-c', 'test.cfg', 'update'], stdout=PIPE).communicate()[0]
        print output # output is shown if test fails, absorbed by nose otherwise

        build_cnt = self.session.query(PackageBuild).filter_by(version='0.0', release='0').count()
        assert_equals(build_cnt, 0, msg % 'Builds from inactive repos were not cleaned')

        self.session.rollback()
        self._clean_db()


    def _setup_simple_update(self, devel=True):
        self.session.begin()
        if devel:
            coll = self._create_testing_devel_collection()
        else:
            coll = self._create_testing_active_collection()
        repo = self._create_testing_devel_active_repo()
        coll.repos.append(repo)

        pkg = self._create_test_minimal_package()
        pkg_listing = self._create_pkg_listing(pkg, coll)
        self.session.commit()
        return (pkg, coll, repo)


    def _test_update_updates_description_devel(self):
        msg = """
        FEATURE: As PkgDB Admin I want package description beeing updated from RAWHIDE builds
        FAILURE: %s
        """
        (pkg, coll, repo) = self._setup_simple_update()

        output = Popen(['server-scripts/pkgdb-sync-yum', '--verbose', '-c', 'test.cfg', 'update'], stdout=PIPE).communicate()[0]
        print output # output is shown if test fails, absorbed by nose otherwise

        self.session.refresh(pkg)
        assert_equals(pkg.summary, 'Summary', msg % 'Summary was not updated')
        assert_equals(pkg.description, 'Description', msg % 'Description was not updated')

        self.session.rollback()
        self._clean_db()
       

    def _test_update_doesnt_update_description_non_devel(self):
        msg = """
        FEATURE: As PkgDB Admin I want package description beeing updated from RAWHIDE builds
        FAILURE: %s
        """
        (pkg, coll, repo) = self._setup_simple_update(devel=False)

        output = Popen(['server-scripts/pkgdb-sync-yum', '--verbose', '-c', 'test.cfg', 'update'], stdout=PIPE).communicate()[0]
        print output # output is shown if test fails, absorbed by nose otherwise

        self.session.refresh(pkg)
        assert_equals(pkg.summary, 'old summary', msg % 'Summary was modified')
        assert_equals(pkg.description, 'old description', msg % 'Description was modified')

        self.session.rollback()
        self._clean_db()
      

    def _test_update_basic(self):
        self.session.begin()
        coll = self.setup_collection('Test', '1', branch_name='tb1')
        repo = self.setup_repo('Testing Basic', 'tb1', '../tests/repo-basic/', coll) 
        pkg = self.setup_package('specto', colls=[coll])
        self.session.commit()

        output = Popen(['server-scripts/pkgdb-sync-yum', '--verbose', '-c', 'test.cfg', 'update', '--skip-inactive'], stdout=PIPE).communicate()[0]
        print output

        self.session.rollback()
        self._clean_db()

    def test_update(self):
        self.session.rollback()
        self._test_update_basic()
        self._test_update_skip_inactive()
        self._test_update_clean_builds()
        self._test_update_updates_description_devel()
        self._test_update_doesnt_update_description_non_devel()

    def test_clean(self):
        from pkgdb.model import Application, SC_ACTIVE, AppCollection, ApplicationTag
        # TODO: test deleting and pruning of the builds

        # type 1 - old imports - no command, no user added value
        app1 = self.setup_app('Name 1')

        # type 2 - new imports - command set
        coll = self.setup_collection('Test', '1', SC_ACTIVE)
        repo = self.setup_repo('Testing Devel', 'devel', 'tests/functional/repo/', coll) 
        pkg = self.setup_package('name', colls=[coll])
        app2 = self.setup_app('Name 2', command='command')
        app2.collections.append(AppCollection('Name 3', collection=coll, package=pkg))

        # type 3 - old imports, user added value, exist as alternative name 
        app3 = self.setup_app('Name 3')
        app3.tag('Tag')
        app3.comment('author', 'Comment body')
        app3.update_rating('Usage', 5, 'author')
        self.session.flush()

        # type 4 - old imports, user added value, doesn't exist as alternative name 
        app4 = self.setup_app('Name 4')
        app4.tag('Tag')

        self.session.commit()

        output = Popen(['server-scripts/pkgdb-sync-yum', '-c', 'test.cfg', '--verbose', 'clean'], stdout=PIPE).communicate()[0]
        print output

        x = self.session.query(ApplicationTag).all()

        # check apps of type 1 are removed
        apps = self.session.query(Application).filter_by(name='Name 1').all()
        assert_equals(len(apps), 0)

        # check apps of type 4 are untouched
        apps = self.session.query(Application).filter_by(name='Name 4').all()
        assert_equals(len(apps), 1)

        # check apps of type 3 are merged to appropriate apps of the type 2
        app = self.session.query(Application).filter_by(name='Name 2').one()
        assert_equals(len(app.comments), 1)
        assert_equals(app.comments[0].body, 'Comment body')
        assert_equals(len(app.tags), 1)
        assert_equals(app.tags[0].tag.name, 'Tag')
        assert_equals(app.tags[0].score, 1)
        assert_equals(len(app.usages), 1)
        assert_equals(app.usages[0].usage.name, 'Usage')

        apps = self.session.query(Application).filter_by(name='Name 3').all()
        assert_equals(len(apps), 0)
